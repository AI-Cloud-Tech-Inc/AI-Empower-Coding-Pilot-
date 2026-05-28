output "secret_ids" {
  description = "Map of secret name to full secret resource ID"
  value = {
    for k, v in google_secret_manager_secret.secrets : k => v.id
  }
}
