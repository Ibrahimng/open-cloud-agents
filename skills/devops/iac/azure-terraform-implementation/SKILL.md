---
name: azure-terraform-implementation
description: Implement, structure, and validate secure, production-grade Azure Terraform infrastructure based on machine-readable plans in .terraform-planning-files/, enforcing verified Azure modules, least-privilege Entra ID RBAC, Key Vault CMK encryption, and Storage Account secure defaults.
---

# Azure Terraform Implementation & Quality Standard

## Purpose & Scope
This skill provides the operational standards, code patterns, and validation commands for implementing Microsoft Azure infrastructure in `infrastructure/` based on machine-readable architecture plans from `.terraform-planning-files/`.

---

## Core Engineering Principles

1. **Least-Privilege Entra ID (Azure AD) RBAC**: Scope role definitions strictly to resource groups or individual resources. Forbid subscription-wide `Contributor` or `Owner` role assignments.
2. **Customer-Managed Key (CMK) Encryption**: Protect disks, databases, and blob storage accounts using Azure Key Vault with 90-day soft-delete and purge protection enabled.
3. **VNet Isolation & Zero-Trust**: Place workloads into dedicated private subnets protected by Network Security Groups (NSGs). Never allow unrestricted `0.0.0.0/0` ingress on management ports (SSH 22, RDP 3389).
4. **Tagging Strategy**: Enforce standardized tagging across all resources (`local.common_tags`: `Project`, `Environment`, `ManagedBy = "Terraform"`, `CostCenter`).
5. **State Management**: Utilize Azure Blob Storage with automated lease locking (`backend "azurerm"`). Never commit local state for shared infrastructure.
6. **Module-First**: Standardize on verified modules from the Azure Registry (`Azure/` namespace, e.g. `Azure/vnet/azurerm`, `Azure/aks/azurerm`). Fetch the latest semantic version before implementing.

---

## Step-by-Step Implementation Workflow

### Step 1: Read the Plan
- Check `.terraform-planning-files/` for an existing plan (`INFRA.azure.{goal}.md` or `INFRA.{goal}.md`).
- If found, implement exactly what the plan specifies without unauthorized deviation.
- If not found, request that the planning agent produce the plan or confirm minimal scope.

### Step 2: Implement Resources
- **Verified VNet Module**:
  ```hcl
  module "vnet" {
    source  = "Azure/vnet/azurerm"
    version = "~> 4.0"

    vnet_name           = "${var.project_name}-${var.environment}-vnet"
    resource_group_name = azurerm_resource_group.main.name
    address_space       = ["10.0.0.0/16"]
    subnet_prefixes     = var.private_subnet_prefixes
    subnet_names        = var.private_subnet_names

    tags = local.common_tags
  }
  ```
- **Storage Account Secure Defaults**:
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
- **Key Vault with Purge Protection**:
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
  ```

### Step 3: Code Review Checklist
Before submitting code for review, verify:
- [ ] Entra ID (Azure AD) RBAC roles are scoped to resource groups or resources (no subscription-level `Owner`/`Contributor`)
- [ ] Azure Key Vault has soft-delete (90 days) and purge protection enabled
- [ ] Storage Accounts enforce `public_network_access_enabled = false`, `allow_nested_items_to_be_public = false`, and `min_tls_version = "TLS1_2"`
- [ ] VNets isolate workloads into private subnets with NSGs (no `0.0.0.0/0` on 22/3389)
- [ ] Tagging applied consistently (`local.common_tags`)
- [ ] `lifecycle` blocks configured (`prevent_destroy` for databases and stateful storage)
- [ ] Outputs cleanly defined and marked `sensitive = true` where appropriate
- [ ] Variables have descriptions, explicit types, and validation blocks

### Step 4: Validation
Execute and fix any findings:
```bash
terraform fmt -recursive
terraform validate
terraform plan -out=tfplan
```

---

## File Structure Standards

Standard directory layout for `infrastructure/`:
```text
infrastructure/
├── main.tf       # Root module, primary resource wiring
├── variables.tf  # Input variables with descriptions and validation
├── outputs.tf    # Root outputs
├── locals.tf     # Local values and common tags
├── versions.tf   # Required providers and versions
├── backend.tf    # Azure Blob Storage state backend
└── modules/
    └── <module>/
        ├── main.tf
        ├── variables.tf
        └── outputs.tf
```

Standard provider and backend configuration:
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
    resource_group_name  = "rg-terraform-state"
    storage_account_name = "tfstateproduction"
    container_name       = "tfstate"
    key                  = "infrastructure.tfstate"
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy    = false
      recover_soft_deleted_key_vaults = true
    }
  }
}
```

