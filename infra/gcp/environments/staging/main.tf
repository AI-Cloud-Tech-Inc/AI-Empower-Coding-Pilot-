# -----------------------------------------------------------------------------
# Staging environment
# -----------------------------------------------------------------------------

terraform {
  backend "gcs" {
    # Bucket name is set via -backend-config during terraform init:
    #   terraform init -backend-config="bucket=${GCP_PROJECT_ID}-ai-empower-tf-state"
    prefix = "staging"
  }
}

module "infra" {
  source = "../../"

  project_id  = var.project_id
  region      = "us-central1"
  environment = "staging"

  db_tier         = "db-g1-small"
  redis_tier      = "BASIC"
  redis_memory_gb = 1

  backend_image         = var.backend_image
  frontend_image        = var.frontend_image
  backend_cpu           = "2"
  backend_memory        = "2Gi"
  backend_min_instances = 1
  backend_max_instances = 5

  notification_email = var.notification_email
}

variable "project_id" {
  type = string
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
