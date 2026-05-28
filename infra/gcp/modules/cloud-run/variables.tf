variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "environment" {
  type = string
}

variable "backend_sa_email" {
  type = string
}

variable "frontend_sa_email" {
  type = string
}

variable "vpc_connector_id" {
  type = string
}

variable "registry_url" {
  type = string
}

variable "db_connection_name" {
  type = string
}

variable "db_name" {
  type = string
}

variable "redis_host" {
  type = string
}

variable "redis_port" {
  type = number
}

variable "secret_ids" {
  type = map(string)
}

variable "data_bucket" {
  type = string
}

variable "backend_image" {
  type = string
}

variable "frontend_image" {
  type = string
}

variable "backend_cpu" {
  type    = string
  default = "2"
}

variable "backend_memory" {
  type    = string
  default = "2Gi"
}

variable "backend_min_instances" {
  type    = number
  default = 0
}

variable "backend_max_instances" {
  type    = number
  default = 10
}
