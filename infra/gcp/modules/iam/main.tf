# -----------------------------------------------------------------------------
# IAM — Service accounts with least-privilege roles
# -----------------------------------------------------------------------------

# ---- Backend service account ----
resource "google_service_account" "backend" {
  project      = var.project_id
  account_id   = "ai-empower-backend-${var.environment}"
  display_name = "AI-Empower Backend (${var.environment})"
}

resource "google_project_iam_member" "backend_roles" {
  for_each = toset([
    "roles/cloudsql.client",
    "roles/secretmanager.secretAccessor",
    "roles/storage.objectUser",
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/cloudtrace.agent",
    "roles/redis.editor",
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.backend.email}"
}

# ---- Frontend service account ----
resource "google_service_account" "frontend" {
  project      = var.project_id
  account_id   = "ai-empower-frontend-${var.environment}"
  display_name = "AI-Empower Frontend (${var.environment})"
}

resource "google_project_iam_member" "frontend_roles" {
  for_each = toset([
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.frontend.email}"
}

# ---- Cloud Build service account permissions ----
resource "google_service_account" "cloudbuild" {
  project      = var.project_id
  account_id   = "ai-empower-cloudbuild-${var.environment}"
  display_name = "AI-Empower Cloud Build (${var.environment})"
}

resource "google_project_iam_member" "cloudbuild_roles" {
  for_each = toset([
    "roles/run.admin",
    "roles/iam.serviceAccountUser",
    "roles/artifactregistry.writer",
    "roles/logging.logWriter",
    "roles/storage.admin",
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.cloudbuild.email}"
}
