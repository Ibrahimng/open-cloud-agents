---
name: iac-state-protection
description: Detect, prevent, and remediate state-destroying traps, unintended resource recreations (forces replacement), and concurrent state locking issues in Terraform/OpenTofu pipelines.
---

# IaC State Destruction Prevention & Safe Replacement

## Purpose & Scope
This skill provides automated checks and operational workflows to guarantee that infrastructure modifications never inadvertently destroy production databases, storage volumes, networking backbones, or stateful resources without human authorization.

## Critical Traps to Detect

### 1. `forces replacement` Detection
When reviewing `terraform plan` or `tofu plan` outputs, search explicitly for:
```text
# aws_rds_cluster.this must be replaced
-/+ resource "aws_rds_cluster" "this" {
      ~ id = "cluster-prod-01" -> (known after apply) # forces replacement
```
**RULE:** Any plan that indicates `forces replacement` on a stateful resource (`aws_db_instance`, `azurerm_cosmosdb_account`, `google_sql_database_instance`, `aws_s3_bucket`, `google_storage_bucket`) is a **BLOCKING DEFECT** requiring immediate rejection or safe migration.

### 2. Zero-Downtime Resource Replacement Lifecycle
When replacement is genuinely required (e.g. changing an immutable VPC subnet attribute or database engine version):
1. Enforce `lifecycle { create_before_destroy = true }`.
2. Guard production databases with `lifecycle { prevent_destroy = true }`.
3. Require explicit state manipulation via `tofu state mv` or `import` blocks rather than destroy-and-recreate loops.

## Verification Checklist
- [ ] 1. Generate execution plan:
  ```bash
  tofu plan -out=tfplan.binary
  tofu show -json tfplan.binary > tfplan.json
  ```
- [ ] 2. Parse plan for resource destruction count:
  ```bash
  jq '.resource_changes[] | select(.change.actions[] | contains("delete")) | .address' tfplan.json
  ```
- [ ] 3. Verify that all stateful resources have `deletion_protection = true` enabled in source HCL.
- [ ] 4. If a resource must be renamed without recreation, use standard `moved` blocks:
  ```hcl
  moved {
    from = aws_security_group.legacy
    to   = aws_security_group.app_ingress
  }
  ```

