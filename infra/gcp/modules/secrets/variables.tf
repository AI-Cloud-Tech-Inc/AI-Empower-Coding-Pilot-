variable "project_id" {
  type = string
}

variable "environment" {
  type = string
}

variable "backend_sa_email" {
  type = string
}

variable "db_password" {
  type      = string
  sensitive = true
}
