# -----------------------------------------------------------------------------
# Artifact Registry — Docker image repository
# -----------------------------------------------------------------------------

resource "google_artifact_registry_repository" "docker" {
  provider = google-beta
  project  = var.project_id

  location      = var.region
  repository_id = "ai-empower-${var.environment}"
  format        = "DOCKER"
  description   = "Docker images for AI-Empower-Coding-Pilot (${var.environment})"

  cleanup_policies {
    id     = "keep-recent"
    action = "KEEP"

    most_recent_versions {
      keep_count = 10
    }
  }
}
