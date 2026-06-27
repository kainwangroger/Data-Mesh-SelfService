output "resource_group_name" {
  value = azurerm_resource_group.main.name
}

output "postgres_fqdn" {
  value = azurerm_postgresql_flexible_server.domains.fqdn
}

output "governance_url" {
  value = "http://${azurerm_container_group.governance.fqdn}:8100"
}

output "portal_url" {
  value = "http://${azurerm_container_group.portal.fqdn}:8501"
}

output "storage_account" {
  value = azurerm_storage_account.datalake.name
}
