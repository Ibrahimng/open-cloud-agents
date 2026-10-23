---
name: iac-state-protection
description: Detect, prevent, and remediate state-destroying traps, unintended resource recreations (forces replacement), and concurrent state locking issues in Terraform/OpenTofu pipelines based on real-world outage postmortems.
---

# IaC State Destruction Prevention & Safe Replacement

## Purpose & Scope
This skill provides automated checks, live exploration commands, and self-learning guardrails to guarantee that infrastructure modifications never inadvertently destroy production databases, storage volumes, networking backbones, or stateful resources without human authorization.

---

## Real-Life Production Incident Case: The Silent Aurora RDS Cluster Replacement

### Background & What Happened
During a routine sprint, an engineer updated an Amazon Aurora PostgreSQL Terraform module to enable a new parameter group. 
Because the parameter group family differed (`postgres14` to `postgres15`), Terraform marked the underlying database cluster as:
```text
-/+ resource "aws_rds_cluster" "primary" {
      ~ parameter_group_name = "default.aurora-postgresql14" -> "custom.aurora-postgresql15" # forces replacement
```
The automated CI pipeline ran without adequate plan inspection. The existing primary cluster containing 4.2 TB of production customer data was destroyed and recreated. Recovery took 42 minutes via AWS snapshot point-in-time recovery, resulting in an SLA breach and executive escalation.

---

## Real-Time Live Exploration Protocol

When a plan indicates potential state replacement, the agent must execute this real-time forensic exploration sequence:

### 1. Extract JSON State Delta & Identify Destruction Vectors
```bash
tofu plan -out=tfplan.binary
tofu show -json tfplan.binary > tfplan.json

# Extract exact resource addresses marked for deletion or replacement
jq -r '.resource_changes[] | select(.change.actions[] | contains("delete")) | "\(.address) -> \(.change.actions | join(","))"' tfplan.json
```

### 2. Drill Into the Specific "Forces Replacement" Attribute
```bash
# Isolate the exact attribute triggering replacement
jq -r '.resource_changes[] | select(.change.actions[] | contains("delete")) | .change.after_unknown, .change.before, .change.after' tfplan.json
```

### 3. Cross-Check with Live Cloud API (Verify Reality vs State)
Confirm whether the target cloud provider actually requires destruction or supports in-place modification:
```bash
# Query AWS API directly to inspect live resource configuration
aws rds describe-db-clusters --db-cluster-identifier <cluster-id> --query 'DBClusters[*].[Status,EngineVersion,DBClusterParameterGroup]'
```

---

## Production Remediation Protocol

1. **State Preservation Locks:**
   Enforce non-negotiable protection in root HCL:
   ```hcl
   lifecycle {
     prevent_destroy       = true
     create_before_destroy = true
   }
   ```
2. **In-Place Modification via `moved` Blocks:**
   If a refactor changed module hierarchy or resource names:
   ```hcl
   moved {
     from = module.database.aws_rds_cluster.this
     to   = module.rds_aurora.aws_rds_cluster.primary
   }
   ```
3. **State Disassociation Recovery:**
   If a resource must be unlinked from state without destroying the live cloud resource:
   ```bash
   tofu state rm module.database.aws_rds_cluster.this
   # Re-import cleanly into the updated resource address
   tofu import module.rds_aurora.aws_rds_cluster.primary <live-cluster-id>
   ```

---

## Continuous Self-Knowledge Enhancement Loop

Whenever an agent discovers an unexpected attribute causing `forces replacement`:
1. **Record the Incident Delta:** Document the cloud provider's attribute immutability rule.
2. **Update the Module Guardrail:** Add a pre-apply check or HCL validation warning to the module's `variables.tf`.
3. **Reflect in Project Knowledge:** Append the discovered cloud trap to the project's root `AGENTS.md` under `## Learned Cloud Traps` so all agents prevent the issue across future sprints.
