#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Quick deploy — build images locally, push to Artifact Registry, and update
# Cloud Run services.
#
# Usage:
#   export GCP_PROJECT_ID=my-project
#   ./infra/gcp/scripts/deploy.sh [dev|staging|prod]
# ---------------------------------------------------------------------------
set -euo pipefail

ENVIRONMENT="${1:-dev}"
PROJECT_ID="${GCP_PROJECT_ID:?Set GCP_PROJECT_ID}"
REGION="${GCP_REGION:-us-central1}"
REGISTRY="${REGION}-docker.pkg.dev/${PROJECT_ID}/ai-empower-${ENVIRONMENT}"
TAG="$(git rev-parse --short HEAD)"

echo "==> Deploying ${ENVIRONMENT} (commit ${TAG})"

# ---- Authenticate Docker ----
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet

# ---- Build images ----
echo "==> Building backend image..."
docker build -t "${REGISTRY}/backend:${TAG}" \
  -t "${REGISTRY}/backend:latest" \
  -f docker/Dockerfile.backend --target production .

echo "==> Building frontend image..."
docker build -t "${REGISTRY}/frontend:${TAG}" \
  -t "${REGISTRY}/frontend:latest" \
  -f docker/Dockerfile.frontend --target production .

# ---- Push images ----
echo "==> Pushing images..."
docker push "${REGISTRY}/backend:${TAG}"
docker push "${REGISTRY}/backend:latest"
docker push "${REGISTRY}/frontend:${TAG}"
docker push "${REGISTRY}/frontend:latest"

# ---- Deploy to Cloud Run ----
echo "==> Deploying backend to Cloud Run..."
gcloud run services update "ai-empower-backend-${ENVIRONMENT}" \
  --image="${REGISTRY}/backend:${TAG}" \
  --region="${REGION}" \
  --quiet

echo "==> Deploying frontend to Cloud Run..."
gcloud run services update "ai-empower-frontend-${ENVIRONMENT}" \
  --image="${REGISTRY}/frontend:${TAG}" \
  --region="${REGION}" \
  --quiet

# ---- Verify ----
BACKEND_URL=$(gcloud run services describe "ai-empower-backend-${ENVIRONMENT}" \
  --region="${REGION}" --format='value(status.url)')

echo ""
echo "==> Deployment complete!"
echo "    Backend:  ${BACKEND_URL}"
echo "    Health:   ${BACKEND_URL}/api/health"
echo ""
echo "Verifying health..."
curl -sf "${BACKEND_URL}/api/health" && echo " ✓ healthy" || echo " ✗ unhealthy"
