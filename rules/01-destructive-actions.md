---
name: Zero Unplanned Destruction & State Loss Prevention
severity: BLOCKING
scope: ALL_AGENTS
---

# Rule 01: Zero Unplanned Destruction & State Loss Prevention

## Principle
AI agents possess significant automation power. Under no circumstances may an agent execute destructive, irreversible actions on production state, cloud infrastructure, or local repositories without explicit, verified human authorization.

---

## Prohibited Autonomous Actions

### 1. Database & Persistent Storage Operations
The following operations must **NEVER** be executed autonomously:
- `DROP DATABASE`, `DROP TABLE`, `DROP SCHEMA`, `DROP VIEW`
- `TRUNCATE TABLE`
- Unbounded `DELETE FROM ...` (missing `WHERE` clause or containing `WHERE 1=1`)
- Cloud bucket wipes: `aws s3 rm --recursive`, `gcloud storage rm --recursive`, `az storage blob delete-batch`
- Persistent disk deletions without prior snapshot or replication confirmation.

### 2. Infrastructure as Code (IaC) State Destruction
When generating or applying Terraform, OpenTofu, Pulumi, or CloudFormation:
- **Forces Replacement Traps:** If an IaC plan indicates resource recreation (`# aws_rds_cluster.main must be replaced`), the agent must **HALT** and alert the user immediately.
- **State Deletions:** Never run `terraform state rm`, `terraform state mv`, or manual state edits without a pre-existing state backup.
- **Mandatory Lifecycle Blocks:** All critical persistent resources (databases, storage buckets, KMS keys, VPC peering) must include:
  ```hcl
  lifecycle {
    prevent_destroy = true
  }
  ```

### 3. File System & Git Operations
- Never run `rm -rf /` or delete uncommitted user workspace files.
- Never run `git reset --hard` or `git clean -fd` if uncommitted modifications exist.
- Never force-push (`git push --force`) to default branches (`main`, `master`, `production`).

---

## Required Agent Protocol for High-Risk Tasks

When a user explicitly asks to destroy or replace a resource:
1. **Analyze Blast Radius:** List affected dependencies, downstream consumers, and anticipated downtime.
2. **Verify Backup:** Check for existing snapshots or state backups.
3. **Present Warning:** Present an executive warning detailing the irreversible impact.
4. **Await User Confirmation:** Do not proceed until the user explicitly responds with affirmative approval.

