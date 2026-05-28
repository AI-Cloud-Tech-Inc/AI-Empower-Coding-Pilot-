variable "project_id" {
  type = string
}

variable "environment" {
  type = string
}

variable "notification_email" {
  type    = string
  default = ""
}

variable "backend_service_name" {
  type = string
}

variable "backend_url" {
  description = "Backend Cloud Run service URL (for uptime check)"
  type        = string
}

variable "frontend_service_name" {
  type = string
}

variable "db_instance_name" {
  type = string
}

variable "redis_instance_name" {
  type = string
}
