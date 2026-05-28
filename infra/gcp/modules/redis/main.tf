# -----------------------------------------------------------------------------
# Memorystore — Redis instance
# -----------------------------------------------------------------------------

resource "google_redis_instance" "cache" {
  project = var.project_id
  name    = "ai-empower-redis-${var.environment}"
  region  = var.region

  tier           = var.redis_tier
  memory_size_gb = var.redis_memory
  redis_version  = "REDIS_7_0"

  authorized_network = var.vpc_id
  connect_mode       = "PRIVATE_SERVICE_ACCESS"

  redis_configs = {
    maxmemory-policy       = "allkeys-lru"
    notify-keyspace-events = ""
  }

  maintenance_policy {
    weekly_maintenance_window {
      day = "SUNDAY"
      start_time {
        hours   = 4
        minutes = 0
      }
    }
  }

  lifecycle {
    prevent_destroy = false
  }
}
