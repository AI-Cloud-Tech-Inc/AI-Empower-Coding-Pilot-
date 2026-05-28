variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "environment" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "redis_tier" {
  type    = string
  default = "BASIC"
}

variable "redis_memory" {
  type    = number
  default = 1
}
