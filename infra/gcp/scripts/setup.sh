#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# GCP project bootstrap — run once before the first `terraform apply`.
#
# Usage:
#   export GCP_PROJECT_ID=my-project
#   ./infra/gcp/scripts/setup.sh [dev|staging|prod]
# ---------------------------------------------------------------------------
set -euo pipefail

ENVIRONMENT="${1:-dev}"
PROJECT_ID="${GCP_PROJECT_ID:?Set GCP_PROJECT_ID}"
REGION="${GCP_REGION:-us-central1}"
TF_STATE_BUCKET="${PROJECT_ID}-ai-empower-tf-state"

echo "==> Bootstrapping GCP project: ${PROJECT_ID} (${ENVIRONMENT})"

# ---- Set project ----
gcloud config set project "${PROJECT_ID}"

# ---- Enable required APIs ----
echo "==> Enabling APIs..."
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com \
  secretmanager.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  compute.googleapis.com \
  vpcaccess.googleapis.com \
  servicenetworking.googleapis.com \
  cloudresourcemanager.googleapis.com \
  iam.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com

# ---- Create Terraform state bucket ----
echo "==> Creating Terraform state bucket: ${TF_STATE_BUCKET}"
if ! gsutil ls -b "gs://${TF_STATE_BUCKET}" &>/dev/null; then
  gsutil mb -p "${PROJECT_ID}" -l "${REGION}" "gs://${TF_STATE_BUCKET}"
  gsutil versioning set on "gs://${TF_STATE_BUCKET}"
  echo "    Bucket created with versioning enabled."
else
  echo "    Bucket already exists."
fi

# ---- Seed initial secrets ----
echo "==> Seeding secrets (skip if already exist)..."
for SECRET_NAME in \
  "ai-empower-openai-api-key-${ENVIRONMENT}" \
  "ai-empower-jwt-secret-key-${ENVIRONMENT}" \
  "ai-empower-api-secret-key-${ENVIRONMENT}"; do

  if ! gcloud secrets describe "${SECRET_NAME}" --project="${PROJECT_ID}" &>/dev/null; then
    echo "    Creating secret: ${SECRET_NAME} (add a version via console or CLI)"
    gcloud secrets create "${SECRET_NAME}" --project="${PROJECT_ID}" --replication-policy="automatic"
  else
    echo "    Secret ${SECRET_NAME} already exists."
  fi
done

echo ""
echo "==> Bootstrap complete!"
echo ""
echo "Next steps:"
echo "  1. Add secret versions:"
echo "     echo -n 'sk-...' | gcloud secrets versions add ai-empower-openai-api-key-${ENVIRONMENT} --data-file=-"
echo "     echo -n '<random>' | gcloud secrets versions add ai-empower-jwt-secret-key-${ENVIRONMENT} --data-file=-"
echo "     echo -n '<random>' | gcloud secrets versions add ai-empower-api-secret-key-${ENVIRONMENT} --data-file=-"
echo ""
echo "  2. Initialize Terraform:"
echo "     cd infra/gcp/environments/${ENVIRONMENT}"
echo "     terraform init"
echo "     terraform plan -var project_id=${PROJECT_ID}"
echo "     terraform apply -var project_id=${PROJECT_ID}"
echo ""
echo "  3. Build & push images (or use Cloud Build):"
echo "     gcloud builds submit --config infra/gcp/cloudbuild.yaml \\"
echo "       --substitutions=_ENVIRONMENT=${ENVIRONMENT},_REGION=${REGION}"
