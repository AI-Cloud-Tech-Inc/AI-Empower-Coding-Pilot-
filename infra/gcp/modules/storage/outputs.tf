output "data_bucket_name" {
  value = google_storage_bucket.data.name
}

output "logs_bucket_name" {
  value = google_storage_bucket.logs.name
}

output "chroma_bucket_name" {
  value = google_storage_bucket.chroma.name
}
