# -----------------------------------------------------------------------------
# Secret Manager — Application secrets
# -----------------------------------------------------------------------------

locals {
  secrets = {
    openai-api-key = ""
    jwt-secret-key = ""
    api-secret-key = ""
    db-password    = var.db_password
  }
}

resource "google_secret_manager_secret" "secrets" {
  for_each  = local.secrets
  project   = var.project_id
  secret_id = "ai-empower-${each.key}-${var.environment}"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.secrets["db-password"].id
  secret_data = var.db_password
}

# ---- Grant backend SA access ----
resource "google_secret_manager_secret_iam_member" "backend_access" {
  for_each  = google_secret_manager_secret.secrets
  project   = var.project_id
  secret_id = each.value.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.backend_sa_email}"
}
