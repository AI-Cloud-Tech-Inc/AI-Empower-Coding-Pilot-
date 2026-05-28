output "connection_name" {
  value = google_sql_database_instance.postgres.connection_name
}

output "instance_name" {
  value = google_sql_database_instance.postgres.name
}

output "private_ip" {
  value = google_sql_database_instance.postgres.private_ip_address
}

output "db_password" {
  value     = random_password.db_password.result
  sensitive = true
}

output "db_user" {
  value = google_sql_user.app.name
}

output "db_name" {
  value = google_sql_database.app.name
}
