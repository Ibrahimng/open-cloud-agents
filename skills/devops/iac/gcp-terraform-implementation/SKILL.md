---
name: gcp-terraform-implementation
description: Implement, structure, and validate secure, production-grade Google Cloud Platform (GCP) Terraform infrastructure based on machine-readable plans in .terraform-planning-files/, enforcing verified Google modules, least-privilege Cloud IAM, Cloud KMS CMEK encryption, and Cloud Storage secure defaults.
---

# GCP Terraform Implementation & Quality Standard

## Purpose & Scope
This skill provides the operational standards, code patterns, and validation commands for implementing Google Cloud Platform (GCP) infrastructure in `infrastructure/` based on machine-readable architecture plans from `.terraform-planning-files/`.

---

## Core Engineering Principles

1. **Least-Privilege Cloud IAM**: Standardize on narrow predefined roles or custom roles. Strictly forbid primitive roles (`roles/owner`, `roles/editor`). Prefer Workload Identity Federation over downloading static JSON service account keys.
2. **Customer-Managed Encryption Keys (CMEK)**: Enforce Cloud KMS keys with automated 90-day key rotation for BigQuery, Cloud Storage (GCS), and Persistent Disks.
3. **Custom-Mode VPC & Private Access**: Deploy custom-mode VPCs with Private Google Access enabled. Nodes must be private with no public IPs (`nat_ip = null`). Front external HTTP(S) workloads with Cloud Armor.
4. **Labeling Strategy**: Enforce lowercase, hyphenated labels across all resources (`local.common_labels`: `environment`, `project`, `managed_by = "terraform"`, `cost_center`).
5. **State Management**: Utilize Google Cloud Storage (`backend "gcs"`) with object versioning enabled and uniform bucket-level access. Never commit local state for shared infrastructure.
6. **Module-First**: Standardize on verified modules from the Terraform Google Modules organization (`terraform-google-modules/` namespace, e.g. `terraform-google-modules/network/google`). Fetch the latest semantic version before implementing.

---

## Step-by-Step Implementation Workflow

### Step 1: Read the Plan
- Check `.terraform-planning-files/` for an existing plan (`INFRA.gcp.{goal}.md` or `INFRA.{goal}.md`).
- If found, implement exactly what the plan specifies without unauthorized deviation.
- If not found, request that the planning agent produce the plan or confirm minimal scope.

### Step 2: Implement Resources
- **Verified VPC Module**:
  ```hcl
  module "vpc" {
    source  = "terraform-google-modules/network/google"
    version = "~> 9.0"

    project_id   = var.project_id
    network_name = "${var.project_name}-${var.environment}-vpc"
    routing_mode = "GLOBAL"

    subnets = [
      {
        subnet_name              = "subnet-app-private"
        subnet_ip                = "10.10.10.0/24"
        subnet_region            = var.region
        private_ip_google_access = true
      }
    ]
  }
  ```
- **Cloud Storage (GCS) Secure Defaults**:
  ```hcl
  resource "google_storage_bucket" "secure_bucket" {
    name          = "${var.project_id}-secure-data"
    location      = var.region
    force_destroy = false

    uniform_bucket_level_access = true
    public_access_prevention    = "enforced"

    versioning {
      enabled = true
    }

    encryption {
      default_kms_key_name = google_kms_crypto_key.storage_key.id
    }

    lifecycle {
      prevent_destroy = true
    }

    labels = local.common_labels
  }
  ```
- **Cloud KMS CMEK with Rotation**:
  ```hcl
  resource "google_kms_key_ring" "main" {
    name     = "${var.project_name}-${var.environment}-keyring"
    location = var.region
    project  = var.project_id
  }

  resource "google_kms_crypto_key" "storage_key" {
    name            = "storage-cmek"
    key_ring        = google_kms_key_ring.main.id
    rotation_period = "7776000s" # 90 days

    lifecycle {
      prevent_destroy = true
    }
  }
  ```

### Step 3: Code Review Checklist
Before submitting code for review, verify:
- [ ] Cloud IAM roles strictly use predefined or custom roles (no primitive `roles/owner` or `roles/editor`)
- [ ] Service accounts utilize Workload Identity Federation rather than static JSON credentials
- [ ] Cloud KMS CMEK encryption configured with automated 90-day rotation
- [ ] GCS buckets enforce `uniform_bucket_level_access = true`, `public_access_prevention = "enforced"`, and object versioning
- [ ] Custom-mode VPC with Private Google Access enabled; compute nodes private without public IPs
- [ ] Labels applied consistently (`local.common_labels`)
- [ ] `lifecycle` blocks configured (`prevent_destroy` for databases and persistent storage)
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
├── locals.tf     # Local values and common labels
├── versions.tf   # Required providers and versions
├── backend.tf    # GCS state backend
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
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  backend "gcs" {
    bucket = "tfstate-production-storage"
    prefix = "core/networking"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}
```

