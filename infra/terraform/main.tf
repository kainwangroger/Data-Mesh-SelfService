provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

resource "azurerm_postgresql_flexible_server" "domains" {
  name                   = "${var.prefix}-postgres"
  resource_group_name    = azurerm_resource_group.main.name
  location               = azurerm_resource_group.main.location
  version                = "16"
  administrator_login    = var.db_admin_user
  administrator_password = var.db_admin_password
  sku_name               = var.db_sku
  storage_mb             = var.db_storage_mb
  tags                   = var.tags
}

resource "azurerm_postgresql_flexible_server_database" "sales" {
  name      = "sales_db"
  server_id = azurerm_postgresql_flexible_server.domains.id
  collation = "en_US.UTF8"
  charset   = "UTF8"
}

resource "azurerm_postgresql_flexible_server_database" "marketing" {
  name      = "marketing_db"
  server_id = azurerm_postgresql_flexible_server.domains.id
  collation = "en_US.UTF8"
  charset   = "UTF8"
}

resource "azurerm_postgresql_flexible_server_database" "finance" {
  name      = "finance_db"
  server_id = azurerm_postgresql_flexible_server.domains.id
  collation = "en_US.UTF8"
  charset   = "UTF8"
}

resource "azurerm_postgresql_flexible_server_database" "datamesh" {
  name      = "datamesh"
  server_id = azurerm_postgresql_flexible_server.domains.id
  collation = "en_US.UTF8"
  charset   = "UTF8"
}

resource "azurerm_container_group" "governance" {
  name                = "${var.prefix}-governance"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  os_type             = "Linux"

  container {
    name   = "governance-api"
    image  = var.governance_image
    cpu    = "0.5"
    memory = "1.5"

    ports {
      port     = 8100
      protocol = "TCP"
    }

    environment_variables = {
      POSTGRES_HOST     = azurerm_postgresql_flexible_server.domains.fqdn
      POSTGRES_PORT     = "5432"
      POSTGRES_USER     = var.db_admin_user
      POSTGRES_PASSWORD = var.db_admin_password
      GOVERNANCE_DB     = "sqlite:///data/governance.db"
    }
  }

  tags = var.tags
}

resource "azurerm_container_group" "portal" {
  name                = "${var.prefix}-portal"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  os_type             = "Linux"

  container {
    name   = "portal"
    image  = var.portal_image
    cpu    = "0.5"
    memory = "1.5"

    ports {
      port     = 8501
      protocol = "TCP"
    }

    environment_variables = {
      GOVERNANCE_API_URL = "http://${azurerm_container_group.governance.fqdn}:8100"
    }
  }

  depends_on = [azurerm_container_group.governance]
  tags       = var.tags
}

resource "azurerm_storage_account" "datalake" {
  name                     = "${var.prefix}datalake"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  tags                     = var.tags
}

resource "azurerm_storage_container" "datalake" {
  name                  = "data-lake"
  storage_account_name  = azurerm_storage_account.datalake.name
  container_access_type = "private"
}
