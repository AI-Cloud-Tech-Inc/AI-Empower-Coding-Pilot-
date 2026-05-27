# -----------------------------------------------------------------------------
# Cloud Run — Backend and Frontend services
# -----------------------------------------------------------------------------

# ---- Backend Service ----
resource "google_cloud_run_v2_service" "backend" {
  provider = google-beta
  project  = var.project_id
  name     = "ai-empower-backend-${var.environment}"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER"

  template {
    service_account = var.backend_sa_email

    scaling {
      min_instance_count = var.backend_min_instances
      max_instance_count = var.backend_max_instances
    }

    vpc_access {
      connector = var.vpc_connector_id
      egress    = "PRIVATE_RANGES_ONLY"
    }

    containers {
      image = "${var.registry_url}/${var.backend_image}"

      ports {
        container_port = 8000
      }

      resources {
        limits = {
          cpu    = var.backend_cpu
          memory = var.backend_memory
        }
        cpu_idle          = var.environment != "prod"
        startup_cpu_boost = true
      }

      # Database — password injected via DB_PASSWORD; entrypoint builds DATABASE_URL
      env {
        name = "DB_PASSWORD"
        value_source {
          secret_key_ref {
            secret  = var.secret_ids["db-password"]
            version = "latest"
          }
        }
      }
      env {
        name  = "DB_USER"
        value = "ai_empower_app"
      }
      env {
        name  = "DB_NAME"
        value = var.db_name
      }
      env {
        name  = "DB_SOCKET"
        value = "/cloudsql/${var.db_connection_name}"
      }

      command = ["/bin/sh", "-c"]
      args    = ["export DATABASE_URL=\"postgresql+asyncpg://$${DB_USER}:$${DB_PASSWORD}@/$${DB_NAME}?host=$${DB_SOCKET}\" && exec uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 2"]

      # Redis
      env {
        name  = "REDIS_URL"
        value = "redis://${var.redis_host}:${var.redis_port}/0"
      }

      # GCS bucket for data
      env {
        name  = "GCS_DATA_BUCKET"
        value = var.data_bucket
      }

      # OpenAI API key from Secret Manager
      env {
        name = "OPENAI_API_KEY"
        value_source {
          secret_key_ref {
            secret  = var.secret_ids["openai-api-key"]
            version = "latest"
          }
        }
      }

      # JWT secret from Secret Manager
      env {
        name = "JWT_SECRET_KEY"
        value_source {
          secret_key_ref {
            secret  = var.secret_ids["jwt-secret-key"]
            version = "latest"
          }
        }
      }

      # API secret from Secret Manager
      env {
        name = "API_SECRET_KEY"
        value_source {
          secret_key_ref {
            secret  = var.secret_ids["api-secret-key"]
            version = "latest"
          }
        }
      }

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      env {
        name  = "PYTHONUNBUFFERED"
        value = "1"
      }

      startup_probe {
        http_get {
          path = "/api/health"
          port = 8000
        }
        initial_delay_seconds = 5
        period_seconds        = 10
        timeout_seconds       = 5
        failure_threshold     = 3
      }

      liveness_probe {
        http_get {
          path = "/api/health"
          port = 8000
        }
        period_seconds    = 30
        timeout_seconds   = 10
        failure_threshold = 3
      }
    }

    # Cloud SQL sidecar
    volumes {
      name = "cloudsql"
      cloud_sql_instance {
        instances = [var.db_connection_name]
      }
    }

    timeout                          = "300s"
    max_instance_request_concurrency = 80
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# ---- Frontend Service ----
resource "google_cloud_run_v2_service" "frontend" {
  provider = google-beta
  project  = var.project_id
  name     = "ai-empower-frontend-${var.environment}"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER"

  template {
    service_account = var.frontend_sa_email

    scaling {
      min_instance_count = 0
      max_instance_count = 5
    }

    containers {
      image = "${var.registry_url}/${var.frontend_image}"

      ports {
        container_port = 80
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "256Mi"
        }
        cpu_idle = true
      }

      startup_probe {
        http_get {
          path = "/"
          port = 80
        }
        initial_delay_seconds = 2
        period_seconds        = 5
        timeout_seconds       = 3
        failure_threshold     = 3
      }
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# ---- Allow unauthenticated access via load balancer ----
resource "google_cloud_run_v2_service_iam_member" "backend_invoker" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.backend.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_v2_service_iam_member" "frontend_invoker" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.frontend.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
