# Dangerous Attributes Matrix — IaC Forces Replacement Traps

This matrix documents the exact resource attributes across AWS, Azure, and Google Cloud that trigger **`forces replacement` (destruction and recreation)** in Terraform / OpenTofu.

> [!CAUTION]
> Applying modifications to any of the attributes below on a production database, storage volume, or network boundary will **DELETE the existing resource**.

---

## 1. Amazon Web Services (AWS)

| Resource | Dangerous Attribute | Operational Impact | Safe Migration Workaround |
|---|---|---|---|
| `aws_db_instance` | `allocated_storage` (downgrade) | **DELETES DATABASE** | Storage can only scale up, never down. |
| `aws_db_instance` | `db_name` | **DELETES DATABASE** | Rename is not supported in-place. Create new DB instance and replicate data. |
| `aws_db_instance` | `availability_zone` | **RECREATES DB** | Use Multi-AZ replication; never change single AZ directly. |
| `aws_rds_cluster` | `database_name` | **DELETES CLUSTER** | Immutable upon creation. |
| `aws_rds_cluster` | `engine_mode` | **DELETES CLUSTER** | E.g. Provisioned $\rightarrow$ Serverless v1 forces cluster recreation. |
| `aws_s3_bucket` | `bucket` (name) | **DELETES BUCKET** | Bucket names are immutable globally. Create new bucket and sync data via DataSync. |
| `aws_subnet` | `cidr_block` | **DESTROYS SUBNET** | All connected workloads (ENIs, EC2, RDS) must be evacuated first. |
| `aws_kms_key` | `customer_master_key_spec` | **DESTROYS KEY** | Key spec cannot be altered. Create new key and re-encrypt data. |

---

## 2. Microsoft Azure

| Resource | Dangerous Attribute | Operational Impact | Safe Migration Workaround |
|---|---|---|---|
| `azurerm_cosmosdb_account` | `name` | **DELETES COSMOS DB** | Account names are globally unique and immutable. |
| `azurerm_storage_account` | `name` | **DELETES STORAGE** | Storage account names cannot be modified in-place. |
| `azurerm_subnet` | `address_prefixes` | **DROPS SUBNET** | Fails if NICs or IP configurations are attached. |
| `azurerm_mssql_database` | `name` | **DELETES SQL DB** | Create target database, export BACPAC, import to new database. |

---

## 3. Google Cloud Platform (GCP)

| Resource | Dangerous Attribute | Operational Impact | Safe Migration Workaround |
|---|---|---|---|
| `google_sql_database_instance` | `name` | **DELETES SQL INSTANCE** | Instance names are permanently locked; cannot be reused for up to 1 week after deletion. |
| `google_sql_database_instance` | `database_version` (major) | **RECREATES DB** | In-place major version upgrade requires `gcloud sql instances patch --upgrade-database-version`. |
| `google_compute_subnetwork` | `ip_cidr_range` (shrink) | **FAILS / DESTROYS** | Subnets can only be expanded (`/24` $\rightarrow$ `/23`), never shrunk. |
| `google_storage_bucket` | `name` | **DELETES BUCKET** | Globally unique and immutable. |

