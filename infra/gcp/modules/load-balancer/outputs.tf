output "ip_address" {
  value = google_compute_global_address.lb_ip.address
}

output "http_url" {
  value = "http://${google_compute_global_address.lb_ip.address}"
}

output "https_url" {
  value = var.domain != "" ? "https://${var.domain}" : "http://${google_compute_global_address.lb_ip.address}"
}
