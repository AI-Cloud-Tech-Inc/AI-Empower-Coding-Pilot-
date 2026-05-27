# -----------------------------------------------------------------------------
# Root-level outputs
# -----------------------------------------------------------------------------

output "backend_url" {
  description = "Backend Cloud Run service URL"
  value       = module.cloud_run.backend_url
}

output "frontend_url" {
  description = "Frontend Cloud Run service URL"
  value       = module.cloud_run.frontend_url
}

output "load_balancer_ip" {
  description = "Global load balancer IP address"
  value       = module.load_balancer.ip_address
}

output "artifact_registry_url" {
  description = "Artifact Registry repository URL for Docker images"
  value       = module.artifact_registry.repository_url
}

output "db_connection_name" {
  description = "Cloud SQL connection name for Cloud SQL Proxy"
  value       = module.cloud_sql.connection_name
}

output "redis_host" {
  description = "Memorystore Redis host"
  value       = module.redis.host
}

output "data_bucket" {
  description = "Cloud Storage bucket for application data"
  value       = module.storage.data_bucket_name
}

output "backend_service_account" {
  description = "Backend service account email"
  value       = module.iam.backend_sa_email
}
