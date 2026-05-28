output "backend_sa_email" {
  value = google_service_account.backend.email
}

output "frontend_sa_email" {
  value = google_service_account.frontend.email
}

output "cloudbuild_sa_email" {
  value = google_service_account.cloudbuild.email
}
