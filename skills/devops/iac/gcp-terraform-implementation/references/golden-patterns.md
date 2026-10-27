# GCP Terraform Golden Patterns & Secure Defaults

## 1. Provider & State Backend (`versions.tf` / `backend.tf`)

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

---

## 2. Global Labels & Locals (`locals.tf`)

```hcl
locals {
  common_labels = {
    environment = var.environment
    project     = var.project_name
    managed_by  = "terraform"
    cost_center = var.cost_center
  }
}
```

---

## 3. Verified VPC Module (`main.tf`)

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
    },
    {
      subnet_name              = "subnet-db-private"
      subnet_ip                = "10.10.20.0/24"
      subnet_region            = var.region
      private_ip_google_access = true
    }
  ]
}
```

---

## 4. Cloud Storage (GCS) Secure Defaults

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

---

## 5. Cloud KMS CMEK Key Ring & Key with 90-Day Rotation

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

---

## 6. Least-Privilege IAM & Service Account Binding

```hcl
resource "google_service_account" "app_sa" {
  account_id   = "${var.project_name}-app-sa"
  display_name = "Application Service Account"
  project      = var.project_id
}

resource "google_project_iam_member" "storage_viewer" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.app_sa.email}"
}
```
