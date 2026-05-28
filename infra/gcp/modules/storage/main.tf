# -----------------------------------------------------------------------------
# Cloud Storage — Buckets for application data, logs, and ML artifacts
# -----------------------------------------------------------------------------

resource "google_storage_bucket" "data" {
  project  = var.project_id
  name     = "${var.project_id}-ai-empower-data-${var.environment}"
  location = var.region

  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  force_destroy               = var.environment != "prod"

  versioning {
    enabled = var.environment == "prod"
  }

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }
}

resource "google_storage_bucket" "logs" {
  project  = var.project_id
  name     = "${var.project_id}-ai-empower-logs-${var.environment}"
  location = var.region

  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  force_destroy               = var.environment != "prod"

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  lifecycle_rule {
    condition {
      age = 180
    }
    action {
      type = "Delete"
    }
  }
}

resource "google_storage_bucket" "chroma" {
  project  = var.project_id
  name     = "${var.project_id}-ai-empower-chroma-${var.environment}"
  location = var.region

  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  force_destroy               = var.environment != "prod"

  versioning {
    enabled = true
  }
}

# ---- IAM bindings ----
resource "google_storage_bucket_iam_member" "data_access" {
  bucket = google_storage_bucket.data.name
  role   = "roles/storage.objectUser"
  member = "serviceAccount:${var.backend_sa_email}"
}

resource "google_storage_bucket_iam_member" "logs_access" {
  bucket = google_storage_bucket.logs.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${var.backend_sa_email}"
}

resource "google_storage_bucket_iam_member" "chroma_access" {
  bucket = google_storage_bucket.chroma.name
  role   = "roles/storage.objectUser"
  member = "serviceAccount:${var.backend_sa_email}"
}
