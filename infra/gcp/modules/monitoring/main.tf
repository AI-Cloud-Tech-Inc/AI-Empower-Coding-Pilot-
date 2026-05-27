# -----------------------------------------------------------------------------
# Monitoring & Alerting — Cloud Monitoring alert policies
# -----------------------------------------------------------------------------

# ---- Notification channel ----
resource "google_monitoring_notification_channel" "email" {
  count   = var.notification_email != "" ? 1 : 0
  project = var.project_id

  display_name = "AI-Empower Alerts (${var.environment})"
  type         = "email"

  labels = {
    email_address = var.notification_email
  }
}

locals {
  notification_channels = var.notification_email != "" ? [google_monitoring_notification_channel.email[0].id] : []
}

# ---- Backend latency alert ----
resource "google_monitoring_alert_policy" "backend_latency" {
  project      = var.project_id
  display_name = "Backend High Latency (${var.environment})"
  combiner     = "OR"

  conditions {
    display_name = "Cloud Run request latency > 5s"

    condition_threshold {
      filter          = "resource.type = \"cloud_run_revision\" AND resource.labels.service_name = \"${var.backend_service_name}\" AND metric.type = \"run.googleapis.com/request_latencies\""
      comparison      = "COMPARISON_GT"
      threshold_value = 5000
      duration        = "300s"

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_PERCENTILE_99"
      }
    }
  }

  notification_channels = local.notification_channels
  alert_strategy {
    auto_close = "1800s"
  }
}

# ---- Backend error rate alert ----
resource "google_monitoring_alert_policy" "backend_errors" {
  project      = var.project_id
  display_name = "Backend High Error Rate (${var.environment})"
  combiner     = "OR"

  conditions {
    display_name = "Cloud Run 5xx error rate > 5%"

    condition_threshold {
      filter          = "resource.type = \"cloud_run_revision\" AND resource.labels.service_name = \"${var.backend_service_name}\" AND metric.type = \"run.googleapis.com/request_count\" AND metric.labels.response_code_class = \"5xx\""
      comparison      = "COMPARISON_GT"
      threshold_value = 5
      duration        = "300s"

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = local.notification_channels
  alert_strategy {
    auto_close = "1800s"
  }
}

# ---- Cloud SQL CPU alert ----
resource "google_monitoring_alert_policy" "db_cpu" {
  project      = var.project_id
  display_name = "Cloud SQL High CPU (${var.environment})"
  combiner     = "OR"

  conditions {
    display_name = "Cloud SQL CPU > 80%"

    condition_threshold {
      filter          = "resource.type = \"cloudsql_database\" AND resource.labels.database_id = \"${var.project_id}:${var.db_instance_name}\" AND metric.type = \"cloudsql.googleapis.com/database/cpu/utilization\""
      comparison      = "COMPARISON_GT"
      threshold_value = 0.8
      duration        = "300s"

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  notification_channels = local.notification_channels
  alert_strategy {
    auto_close = "1800s"
  }
}

# ---- Redis memory alert ----
resource "google_monitoring_alert_policy" "redis_memory" {
  project      = var.project_id
  display_name = "Redis High Memory (${var.environment})"
  combiner     = "OR"

  conditions {
    display_name = "Redis memory usage > 80%"

    condition_threshold {
      filter          = "resource.type = \"redis_instance\" AND resource.labels.instance_id = \"${var.redis_instance_name}\" AND metric.type = \"redis.googleapis.com/stats/memory/usage_ratio\""
      comparison      = "COMPARISON_GT"
      threshold_value = 0.8
      duration        = "300s"

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  notification_channels = local.notification_channels
  alert_strategy {
    auto_close = "1800s"
  }
}

# ---- Uptime check for the backend health endpoint ----
resource "google_monitoring_uptime_check_config" "backend_health" {
  project      = var.project_id
  display_name = "Backend Health Check (${var.environment})"
  timeout      = "10s"
  period       = "300s"

  http_check {
    path         = "/api/health"
    port         = 443
    use_ssl      = true
    validate_ssl = true
  }

  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = trimprefix(trimprefix(var.backend_service_name, "https://"), "http://")
    }
  }
}

# ---- Dashboard ----
resource "google_monitoring_dashboard" "overview" {
  project = var.project_id
  dashboard_json = jsonencode({
    displayName = "AI-Empower Overview (${var.environment})"
    gridLayout = {
      columns = 2
      widgets = [
        {
          title = "Backend Request Count"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type = \"cloud_run_revision\" AND resource.labels.service_name = \"${var.backend_service_name}\" AND metric.type = \"run.googleapis.com/request_count\""
                  aggregation = {
                    alignmentPeriod  = "60s"
                    perSeriesAligner = "ALIGN_RATE"
                  }
                }
              }
            }]
          }
        },
        {
          title = "Backend Latency (p99)"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type = \"cloud_run_revision\" AND resource.labels.service_name = \"${var.backend_service_name}\" AND metric.type = \"run.googleapis.com/request_latencies\""
                  aggregation = {
                    alignmentPeriod  = "60s"
                    perSeriesAligner = "ALIGN_PERCENTILE_99"
                  }
                }
              }
            }]
          }
        },
        {
          title = "Cloud SQL CPU"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type = \"cloudsql_database\" AND metric.type = \"cloudsql.googleapis.com/database/cpu/utilization\""
                  aggregation = {
                    alignmentPeriod  = "60s"
                    perSeriesAligner = "ALIGN_MEAN"
                  }
                }
              }
            }]
          }
        },
        {
          title = "Redis Memory Usage"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type = \"redis_instance\" AND metric.type = \"redis.googleapis.com/stats/memory/usage_ratio\""
                  aggregation = {
                    alignmentPeriod  = "60s"
                    perSeriesAligner = "ALIGN_MEAN"
                  }
                }
              }
            }]
          }
        },
      ]
    }
  })
}
