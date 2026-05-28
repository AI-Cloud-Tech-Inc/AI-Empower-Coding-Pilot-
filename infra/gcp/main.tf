# -----------------------------------------------------------------------------
# AI-Empower-Coding-Pilot — GCP Infrastructure
# Root module that composes all sub-modules.
# -----------------------------------------------------------------------------

terraform {
  required_version = ">= 1.5"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# ---- Enable Required APIs ----
resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "redis.googleapis.com",
    "secretmanager.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "compute.googleapis.com",
    "vpcaccess.googleapis.com",
    "servicenetworking.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
  ])

  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

# ---- Networking ----
module "networking" {
  source = "./modules/networking"

  project_id  = var.project_id
  region      = var.region
  environment = var.environment

  depends_on = [google_project_service.apis]
}

# ---- IAM / Service Accounts ----
module "iam" {
  source = "./modules/iam"

  project_id  = var.project_id
  environment = var.environment

  depends_on = [google_project_service.apis]
}

# ---- Artifact Registry ----
module "artifact_registry" {
  source = "./modules/artifact-registry"

  project_id  = var.project_id
  region      = var.region
  environment = var.environment

  depends_on = [google_project_service.apis]
}

# ---- Cloud SQL (PostgreSQL) ----
module "cloud_sql" {
  source = "./modules/cloud-sql"

  project_id         = var.project_id
  region             = var.region
  environment        = var.environment
  vpc_id             = module.networking.vpc_id
  private_network_id = module.networking.private_network_id
  db_tier            = var.db_tier
  db_name            = var.db_name

  depends_on = [
    google_project_service.apis,
    module.networking,
  ]
}

# ---- Memorystore (Redis) ----
module "redis" {
  source = "./modules/redis"

  project_id   = var.project_id
  region       = var.region
  environment  = var.environment
  vpc_id       = module.networking.vpc_id
  redis_tier   = var.redis_tier
  redis_memory = var.redis_memory_gb

  depends_on = [
    google_project_service.apis,
    module.networking,
  ]
}

# ---- Cloud Storage ----
module "storage" {
  source = "./modules/storage"

  project_id       = var.project_id
  region           = var.region
  environment      = var.environment
  backend_sa_email = module.iam.backend_sa_email

  depends_on = [google_project_service.apis]
}

# ---- Secret Manager ----
module "secrets" {
  source = "./modules/secrets"

  project_id       = var.project_id
  environment      = var.environment
  backend_sa_email = module.iam.backend_sa_email
  db_password      = module.cloud_sql.db_password

  depends_on = [google_project_service.apis]
}

# ---- Cloud Run Services ----
module "cloud_run" {
  source = "./modules/cloud-run"

  project_id         = var.project_id
  region             = var.region
  environment        = var.environment
  backend_sa_email   = module.iam.backend_sa_email
  frontend_sa_email  = module.iam.frontend_sa_email
  vpc_connector_id   = module.networking.vpc_connector_id
  registry_url       = module.artifact_registry.repository_url
  db_connection_name = module.cloud_sql.connection_name
  db_name            = var.db_name
  redis_host         = module.redis.host
  redis_port         = module.redis.port
  secret_ids         = module.secrets.secret_ids
  data_bucket        = module.storage.data_bucket_name

  backend_image         = var.backend_image
  frontend_image        = var.frontend_image
  backend_cpu           = var.backend_cpu
  backend_memory        = var.backend_memory
  backend_min_instances = var.backend_min_instances
  backend_max_instances = var.backend_max_instances

  depends_on = [
    google_project_service.apis,
    module.networking,
    module.iam,
    module.cloud_sql,
    module.redis,
    module.secrets,
    module.storage,
    module.artifact_registry,
  ]
}

# ---- Load Balancer ----
module "load_balancer" {
  source = "./modules/load-balancer"

  project_id              = var.project_id
  region                  = var.region
  environment             = var.environment
  domain                  = var.domain
  backend_cloud_run_name  = module.cloud_run.backend_service_name
  frontend_cloud_run_name = module.cloud_run.frontend_service_name
  enable_ssl              = var.enable_ssl

  depends_on = [module.cloud_run]
}

# ---- Monitoring & Alerting ----
module "monitoring" {
  source = "./modules/monitoring"

  project_id            = var.project_id
  environment           = var.environment
  notification_email    = var.notification_email
  backend_service_name  = module.cloud_run.backend_service_name
  backend_url           = module.cloud_run.backend_url
  frontend_service_name = module.cloud_run.frontend_service_name
  db_instance_name      = module.cloud_sql.instance_name
  redis_instance_name   = module.redis.instance_name

  depends_on = [module.cloud_run, module.cloud_sql, module.redis]
}
