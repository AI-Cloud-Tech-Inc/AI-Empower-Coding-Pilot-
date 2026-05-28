variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "environment" {
  type = string
}

variable "domain" {
  type    = string
  default = ""
}

variable "backend_cloud_run_name" {
  type = string
}

variable "frontend_cloud_run_name" {
  type = string
}

variable "enable_ssl" {
  type    = bool
  default = true
}
