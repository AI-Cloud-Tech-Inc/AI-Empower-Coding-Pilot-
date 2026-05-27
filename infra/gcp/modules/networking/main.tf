# -----------------------------------------------------------------------------
# Networking — VPC, subnets, Cloud NAT, VPC connector, firewall
# -----------------------------------------------------------------------------

resource "google_compute_network" "vpc" {
  project                 = var.project_id
  name                    = "ai-empower-vpc-${var.environment}"
  auto_create_subnetworks = false
  routing_mode            = "REGIONAL"
}

resource "google_compute_subnetwork" "private" {
  project                  = var.project_id
  name                     = "ai-empower-private-${var.region}-${var.environment}"
  ip_cidr_range            = "10.0.0.0/20"
  region                   = var.region
  network                  = google_compute_network.vpc.id
  private_ip_google_access = true

  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = "10.1.0.0/20"
  }
}

resource "google_compute_subnetwork" "connector" {
  project       = var.project_id
  name          = "ai-empower-connector-${var.environment}"
  ip_cidr_range = "10.8.0.0/28"
  region        = var.region
  network       = google_compute_network.vpc.id
}

# ---- Serverless VPC Access Connector (Cloud Run → VPC) ----
resource "google_vpc_access_connector" "connector" {
  provider = google-beta
  project  = var.project_id
  name     = "ai-empower-conn-${var.environment}"
  region   = var.region

  subnet {
    name = google_compute_subnetwork.connector.name
  }

  min_instances = 2
  max_instances = 3
  machine_type  = "f1-micro"
}

# ---- Cloud NAT (outbound internet for private resources) ----
resource "google_compute_router" "router" {
  project = var.project_id
  name    = "ai-empower-router-${var.environment}"
  region  = var.region
  network = google_compute_network.vpc.id
}

resource "google_compute_router_nat" "nat" {
  project                            = var.project_id
  name                               = "ai-empower-nat-${var.environment}"
  router                             = google_compute_router.router.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# ---- Private Services Access (for Cloud SQL, Redis) ----
resource "google_compute_global_address" "private_ip_range" {
  project       = var.project_id
  name          = "ai-empower-private-ip-${var.environment}"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_range.name]
}

# ---- Firewall ----
resource "google_compute_firewall" "allow_internal" {
  project = var.project_id
  name    = "ai-empower-allow-internal-${var.environment}"
  network = google_compute_network.vpc.name

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }
  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }
  allow {
    protocol = "icmp"
  }

  source_ranges = ["10.0.0.0/8"]
  priority      = 1000
}

resource "google_compute_firewall" "allow_health_checks" {
  project = var.project_id
  name    = "ai-empower-allow-health-checks-${var.environment}"
  network = google_compute_network.vpc.name

  allow {
    protocol = "tcp"
    ports    = ["8000", "80", "443"]
  }

  # Google health check IP ranges
  source_ranges = ["130.211.0.0/22", "35.191.0.0/16"]
  priority      = 900
}
