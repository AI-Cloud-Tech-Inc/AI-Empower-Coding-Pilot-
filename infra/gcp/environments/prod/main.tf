# -----------------------------------------------------------------------------
# Production environment
# -----------------------------------------------------------------------------

terraform {
  backend "gcs" {
    # Bucket name is set via -backend-config during terraform init:
    #   terraform init -backend-config="bucket=${GCP_PROJECT_ID}-ai-empower-tf-state"
    prefix = "prod"
  }
}

module "infra" {
  source = "../../"

  project_id  = var.project_id
  region      = "us-central1"
  environment = "prod"
  domain      = var.domain
  enable_ssl  = true

  db_tier         = "db-custom-2-7680"
  redis_tier      = "STANDARD_HA"
  redis_memory_gb = 2

  backend_image         = var.backend_image
  frontend_image        = var.frontend_image
  backend_cpu           = "2"
  backend_memory        = "4Gi"
  backend_min_instances = 2
  backend_max_instances = 20

  notification_email = var.notification_email
}

variable "project_id" {
  type = string
}

variable "domain" {
  type    = string
  default = ""
}

variable "backend_image" {
  type    = string
  default = "backend:latest"
}

variable "frontend_image" {
  type    = string
  default = "frontend:latest"
}

variable "notification_email" {
  type    = string
  default = ""
}

output "backend_url" {
  value = module.infra.backend_url
}

output "frontend_url" {
  value = module.infra.frontend_url
}

output "load_balancer_ip" {
  value = module.infra.load_balancer_ip
}
