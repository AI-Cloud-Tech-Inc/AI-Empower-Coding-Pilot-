# -----------------------------------------------------------------------------
# Root-level input variables
# -----------------------------------------------------------------------------

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for all resources"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "domain" {
  description = "Custom domain for the application (leave empty to use default Cloud Run URLs)"
  type        = string
  default     = ""
}

variable "enable_ssl" {
  description = "Enable managed SSL certificate for the load balancer"
  type        = bool
  default     = true
}

# ---- Database ----
variable "db_tier" {
  description = "Cloud SQL machine tier"
  type        = string
  default     = "db-f1-micro"
}

variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "ai_empower_db"
}

# ---- Redis ----
variable "redis_tier" {
  description = "Memorystore Redis tier (BASIC or STANDARD_HA)"
  type        = string
  default     = "BASIC"
}

variable "redis_memory_gb" {
  description = "Redis memory size in GB"
  type        = number
  default     = 1
}

# ---- Cloud Run ----
variable "backend_image" {
  description = "Backend container image (tag). Set to a full Artifact Registry path after first build."
  type        = string
  default     = "backend:latest"
}

variable "frontend_image" {
  description = "Frontend container image (tag). Set to a full Artifact Registry path after first build."
  type        = string
  default     = "frontend:latest"
}

variable "backend_cpu" {
  description = "CPU allocation for backend Cloud Run service"
  type        = string
  default     = "2"
}

variable "backend_memory" {
  description = "Memory allocation for backend Cloud Run service"
  type        = string
  default     = "2Gi"
}

variable "backend_min_instances" {
  description = "Minimum number of backend instances"
  type        = number
  default     = 0
}

variable "backend_max_instances" {
  description = "Maximum number of backend instances"
  type        = number
  default     = 10
}

# ---- Monitoring ----
variable "notification_email" {
  description = "Email address for monitoring alert notifications"
  type        = string
  default     = ""
}
