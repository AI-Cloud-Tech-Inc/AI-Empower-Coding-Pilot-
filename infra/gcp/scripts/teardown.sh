#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Destroy all GCP resources for a given environment.
#
# Usage:
#   export GCP_PROJECT_ID=my-project
#   ./infra/gcp/scripts/teardown.sh [dev|staging|prod]
# ---------------------------------------------------------------------------
set -euo pipefail

ENVIRONMENT="${1:-dev}"
PROJECT_ID="${GCP_PROJECT_ID:?Set GCP_PROJECT_ID}"

echo "==> WARNING: This will destroy ALL resources for environment '${ENVIRONMENT}'"
echo "    Project: ${PROJECT_ID}"
echo ""
read -rp "Type '${ENVIRONMENT}' to confirm: " CONFIRM

if [ "${CONFIRM}" != "${ENVIRONMENT}" ]; then
  echo "Aborted."
  exit 1
fi

cd "$(dirname "$0")/../environments/${ENVIRONMENT}"

terraform init
terraform destroy -var "project_id=${PROJECT_ID}" -auto-approve

echo "==> Resources destroyed for ${ENVIRONMENT}."
