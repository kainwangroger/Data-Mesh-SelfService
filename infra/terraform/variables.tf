variable "prefix" {
  description = "Prefix for all resource names"
  type        = string
  default     = "datamesh"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "West Europe"
}

variable "resource_group_name" {
  description = "Azure Resource Group name"
  type        = string
  default     = "rg-data-mesh"
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default = {
    environment = "development"
    project     = "data-mesh-selfservice"
    managed-by  = "terraform"
  }
}

variable "db_admin_user" {
  description = "PostgreSQL admin username"
  type        = string
  sensitive   = true
}

variable "db_admin_password" {
  description = "PostgreSQL admin password"
  type        = string
  sensitive   = true
}

variable "db_sku" {
  description = "PostgreSQL SKU name"
  type        = string
  default     = "B_Standard_B1ms"
}

variable "db_storage_mb" {
  description = "PostgreSQL storage in MB"
  type        = number
  default     = 32768
}

variable "governance_image" {
  description = "Governance API Docker image"
  type        = string
  default     = "datamesh-governance:latest"
}

variable "portal_image" {
  description = "Portal Docker image"
  type        = string
  default     = "datamesh-portal:latest"
}
