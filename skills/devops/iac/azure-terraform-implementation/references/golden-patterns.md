# Azure Terraform Golden Patterns & Secure Defaults

## 1. Provider & State Backend (`versions.tf` / `backend.tf`)

```hcl
terraform {
  required_version = ">= 1.5"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
  backend "azurerm" {
    resource_group_name  = "rg-terraform-state-prod"
    storage_account_name = "tfstateproductionapp"
    container_name       = "tfstate"
    key                  = "networking.terraform.tfstate"
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy    = false
      recover_soft_deleted_key_vaults = true
    }
    resource_group {
      prevent_deletion_if_contains_resources = true
    }
  }
}
```

---

## 2. Resource Group & Global Tags (`locals.tf` / `main.tf`)

```hcl
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
    CostCenter  = var.cost_center
  }
}

resource "azurerm_resource_group" "main" {
  name     = "rg-${var.project_name}-${var.environment}"
  location = var.location

  tags = local.common_tags
}
```

---

## 3. Verified VNet Module (`main.tf`)

```hcl
module "vnet" {
  source  = "Azure/vnet/azurerm"
  version = "~> 4.0"

  vnet_name           = "${var.project_name}-${var.environment}-vnet"
  resource_group_name = azurerm_resource_group.main.name
  address_space       = ["10.100.0.0/16"]
  subnet_prefixes     = ["10.100.1.0/24", "10.100.2.0/24"]
  subnet_names        = ["snet-app-private", "snet-db-private"]

  nsg_ids = {
    "snet-app-private" = azurerm_network_security_group.app_nsg.id
    "snet-db-private"  = azurerm_network_security_group.db_nsg.id
  }

  tags = local.common_tags
}
```

---

## 4. Hardened Storage Account

```hcl
resource "azurerm_storage_account" "secure" {
  name                     = "${var.project_clean}${var.env_clean}sa"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "GRS"

  min_tls_version                 = "TLS1_2"
  allow_nested_items_to_be_public = false
  public_network_access_enabled   = false

  blob_properties {
    versioning_enabled = true
    delete_retention_policy {
      days = 30
    }
  }

  lifecycle {
    prevent_destroy = true
  }

  tags = local.common_tags
}
```

---

## 5. Key Vault with Purge Protection & CMK

```hcl
resource "azurerm_key_vault" "main" {
  name                        = "${var.project_clean}-${var.environment}-kv"
  location                    = azurerm_resource_group.main.location
  resource_group_name         = azurerm_resource_group.main.name
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  sku_name                    = "premium"
  soft_delete_retention_days  = 90
  purge_protection_enabled    = true
  enable_rbac_authorization   = true

  network_acls {
    default_action = "Deny"
    bypass         = "AzureServices"
  }

  tags = local.common_tags
}

resource "azurerm_key_vault_key" "disk_cmk" {
  name         = "disk-encryption-cmk"
  key_vault_id = azurerm_key_vault.main.id
  key_type     = "RSA"
  key_size     = 4096

  key_opts = [
    "decrypt",
    "encrypt",
    "sign",
    "unwrapKey",
    "verify",
    "wrapKey",
  ]
}
```

---

## 6. Granular Entra ID (Azure AD) RBAC Assignment

```hcl
resource "azurerm_role_assignment" "app_storage_blob_contributor" {
  scope                = azurerm_storage_account.secure.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_user_assigned_identity.app.principal_id
}
```

