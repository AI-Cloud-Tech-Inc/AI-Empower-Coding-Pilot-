# -----------------------------------------------------------------------------
# Cloud SQL — PostgreSQL instance (replaces SQLite for production)
# -----------------------------------------------------------------------------

resource "random_password" "db_password" {
  length  = 32
  special = true
}

resource "google_sql_database_instance" "postgres" {
  project          = var.project_id
  name             = "ai-empower-db-${var.environment}"
  database_version = "POSTGRES_15"
  region           = var.region

  deletion_protection = var.environment == "prod" ? true : false

  settings {
    tier              = var.db_tier
    availability_type = var.environment == "prod" ? "REGIONAL" : "ZONAL"
    disk_autoresize   = true
    disk_size         = 20
    disk_type         = "PD_SSD"

    ip_configuration {
      ipv4_enabled                                  = false
      private_network                               = var.private_network_id
      enable_private_path_for_google_cloud_services = true
    }

    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = var.environment == "prod" ? true : false
      backup_retention_settings {
        retained_backups = var.environment == "prod" ? 30 : 7
      }
    }

    maintenance_window {
      day          = 7
      hour         = 4
      update_track = "stable"
    }

    database_flags {
      name  = "max_connections"
      value = "100"
    }

    insights_config {
      query_insights_enabled  = true
      record_application_tags = true
      record_client_address   = false
    }
  }
}

resource "google_sql_database" "app" {
  project  = var.project_id
  name     = var.db_name
  instance = google_sql_database_instance.postgres.name
}

resource "google_sql_user" "app" {
  project  = var.project_id
  name     = "ai_empower_app"
  instance = google_sql_database_instance.postgres.name
  password = random_password.db_password.result
}
