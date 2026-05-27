# -----------------------------------------------------------------------------
# Global HTTPS Load Balancer — Routes /api/* to backend, /* to frontend
# -----------------------------------------------------------------------------

# ---- Static IP ----
resource "google_compute_global_address" "lb_ip" {
  project = var.project_id
  name    = "ai-empower-lb-ip-${var.environment}"
}

# ---- Serverless NEGs ----
resource "google_compute_region_network_endpoint_group" "backend_neg" {
  project               = var.project_id
  name                  = "ai-empower-backend-neg-${var.environment}"
  network_endpoint_type = "SERVERLESS"
  region                = var.region

  cloud_run {
    service = var.backend_cloud_run_name
  }
}

resource "google_compute_region_network_endpoint_group" "frontend_neg" {
  project               = var.project_id
  name                  = "ai-empower-frontend-neg-${var.environment}"
  network_endpoint_type = "SERVERLESS"
  region                = var.region

  cloud_run {
    service = var.frontend_cloud_run_name
  }
}

# ---- Backend Services ----
resource "google_compute_backend_service" "backend" {
  project = var.project_id
  name    = "ai-empower-backend-svc-${var.environment}"

  protocol              = "HTTP"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  timeout_sec           = 300
  enable_cdn            = false

  backend {
    group = google_compute_region_network_endpoint_group.backend_neg.id
  }

  log_config {
    enable      = true
    sample_rate = var.environment == "prod" ? 0.5 : 1.0
  }
}

resource "google_compute_backend_service" "frontend" {
  project = var.project_id
  name    = "ai-empower-frontend-svc-${var.environment}"

  protocol              = "HTTP"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  timeout_sec           = 30
  enable_cdn            = true

  backend {
    group = google_compute_region_network_endpoint_group.frontend_neg.id
  }

  cdn_policy {
    cache_mode                   = "CACHE_ALL_STATIC"
    default_ttl                  = 3600
    max_ttl                      = 86400
    client_ttl                   = 3600
    signed_url_cache_max_age_sec = 0
  }

  log_config {
    enable      = true
    sample_rate = var.environment == "prod" ? 0.1 : 1.0
  }
}

# ---- URL Map (path-based routing) ----
resource "google_compute_url_map" "default" {
  project         = var.project_id
  name            = "ai-empower-lb-${var.environment}"
  default_service = google_compute_backend_service.frontend.id

  host_rule {
    hosts        = ["*"]
    path_matcher = "paths"
  }

  path_matcher {
    name            = "paths"
    default_service = google_compute_backend_service.frontend.id

    path_rule {
      paths   = ["/api/*", "/docs", "/docs/*", "/redoc", "/redoc/*", "/openapi.json"]
      service = google_compute_backend_service.backend.id
    }
  }
}

# ---- SSL Certificate (managed) ----
resource "google_compute_managed_ssl_certificate" "default" {
  count   = var.enable_ssl && var.domain != "" ? 1 : 0
  project = var.project_id
  name    = "ai-empower-cert-${var.environment}"

  managed {
    domains = [var.domain]
  }
}

# ---- HTTPS Proxy ----
resource "google_compute_target_https_proxy" "default" {
  count   = var.enable_ssl && var.domain != "" ? 1 : 0
  project = var.project_id
  name    = "ai-empower-https-proxy-${var.environment}"
  url_map = google_compute_url_map.default.id

  ssl_certificates = [google_compute_managed_ssl_certificate.default[0].id]
}

# ---- HTTP Proxy (fallback when no domain/SSL) ----
resource "google_compute_target_http_proxy" "default" {
  project = var.project_id
  name    = "ai-empower-http-proxy-${var.environment}"
  url_map = google_compute_url_map.default.id
}

# ---- Forwarding Rules ----
resource "google_compute_global_forwarding_rule" "https" {
  count      = var.enable_ssl && var.domain != "" ? 1 : 0
  project    = var.project_id
  name       = "ai-empower-https-rule-${var.environment}"
  target     = google_compute_target_https_proxy.default[0].id
  port_range = "443"
  ip_address = google_compute_global_address.lb_ip.address

  load_balancing_scheme = "EXTERNAL_MANAGED"
}

resource "google_compute_global_forwarding_rule" "http" {
  project    = var.project_id
  name       = "ai-empower-http-rule-${var.environment}"
  target     = google_compute_target_http_proxy.default.id
  port_range = "80"
  ip_address = google_compute_global_address.lb_ip.address

  load_balancing_scheme = "EXTERNAL_MANAGED"
}

# ---- Cloud Armor security policy ----
resource "google_compute_security_policy" "default" {
  project = var.project_id
  name    = "ai-empower-armor-${var.environment}"

  # Rate limiting
  rule {
    action   = "throttle"
    priority = 1000
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    rate_limit_options {
      conform_action = "allow"
      exceed_action  = "deny(429)"
      rate_limit_threshold {
        count        = 100
        interval_sec = 60
      }
    }
    description = "Rate limit all traffic to 100 req/min per IP"
  }

  # Default allow
  rule {
    action   = "allow"
    priority = 2147483647
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    description = "Default allow"
  }
}
