variable "resource_type" {
  description = "Type of resource (vpc, subnet, instance, etc.)"
  type        = string
}

variable "host" {
  description = "Cloud or platform host (aws, azure, gcp, etc.)"
  type        = string
}

variable "data_map" {
  description = "All metadata and required fields as a flat key-value map"
  type        = map(string)
}
variable "revision" {
  type = bool
  default = true
}
