---
name: cloud-waste-reaper
description: "Autonomous FinOps discovery and safe reclamation of abandoned, unattached, and orphaned cloud resources across AWS, GCP, and Azure. Safely identifies unattached EBS/Persistent disks, unassociated Elastic IPs, abandoned NAT gateways, idle load balancers, and expired snapshots without disrupting production traffic."
---

# Cloud Waste Reaper & Idle Asset Elimination

## Overview
Cloud infrastructure bills suffer from silent, compounding waste: abandoned test environments, unattached persistent storage volumes left behind after pod deletions, unassociated static IPs, and forgotten NAT gateways.

This skill equips the [**FinOps & Cloud Cost Optimizer**](../../../agents/7-agent-master-suite/finops-cloud-cost-optimizer.md) with automated discovery runbooks and safe reclamation procedures compliant with [`rules/01-destructive-actions.md`](../../../rules/01-destructive-actions.md).

---

## 💥 Real-World Incident Case Studies

### Incident 1: The $14,000 Abandoned NAT Gateway
* **Outage / Incident Root Cause:** A short-lived load-testing Kubernetes namespace was torn down using `kubectl delete ns load-test`. While the Kubernetes pods were removed, the cloud NAT Gateway and VPC peering provisioned by an underlying Terraform workspace remained active.
* **Impact:** For 4 months, the idle NAT Gateway accrued \$0.045/hour base charges plus cross-AZ data processing fees, totaling over \$14,000 in unbudgeted cloud spend before detection.
* **Reaper Prevention:** The FinOps agent runs weekly telemetry checks: any NAT Gateway with 0 active connections for > 7 consecutive days triggers an automated reclamation task.

### Incident 2: The 80,000 Orphaned Snapshot Accumulation
* **Outage / Incident Root Cause:** A legacy automated backup cron script created hourly EBS snapshots of temporary worker nodes without an automated lifecycle deletion policy.
* **Impact:** Over two years, 80,000 orphaned snapshots accumulated, costing \$8,500 every month for storage of deleted virtual machines.
* **Reaper Prevention:** Identify snapshots whose parent volume has been deleted for > 90 days and transition them to cold storage or purge.

### Incident 3: The Ghost Kubernetes StatefulSet PVC Leak
* **Outage / Incident Root Cause:** A continuous integration pipeline created ephemeral preview environments running Elasticsearch and Kafka on Kubernetes StatefulSets. When the namespaces were deleted (`kubectl delete ns preview-pr-412`), the StatefulSet pods were destroyed, but the cloud PersistentVolumeClaims (PVCs) backed by provisioned AWS gp3 EBS volumes retained an `Available` status because Kubernetes volumes are decoupled from namespace deletion lifecycles.
* **Impact:** 240 unattached 100 GB EBS volumes accumulated silently across 6 months, generating \$1,920/month in compounding storage spend with 0 read/write IOPS.
* **Reaper Prevention:** The FinOps agent filters for all cloud storage volumes whose attachment state is `available` for > 14 days and cross-references active Kubernetes cluster nodes to ensure no detached volumes persist.

---

## 3-Tier Operational Runbook

```text
skills/finops/cloud-waste-reaper/
├── SKILL.md                 # 1. Autonomous instructions, incident cases, guardrails
├── references/
│   ├── waste-matrix.md      # 2. Metric thresholds, pricing formulas, exemption tags
│   └── multi-cloud-queries.md# 2. Raw AWS, GCP, and Azure discovery commands
└── scripts/
    └── reap_cloud_waste.sh  # 3. Executable multi-cloud waste hunter with dry-run
```

### Phase 1: Autonomous Waste Discovery (Dry-Run Only)
Run the automated discovery script in dry-run mode across targeted clouds:

```bash
# --- From repository root ---
# AWS scan with JSON and Markdown export
./skills/finops/cloud-waste-reaper/scripts/reap_cloud_waste.sh --provider aws --dry-run --export-json /tmp/waste_report.json --export-markdown /tmp/waste_report.md

# GCP scan
./skills/finops/cloud-waste-reaper/scripts/reap_cloud_waste.sh --provider gcp --dry-run

# Azure scan
./skills/finops/cloud-waste-reaper/scripts/reap_cloud_waste.sh --provider azure --dry-run

# Mock / CI demonstration mode (no credentials required)
./skills/finops/cloud-waste-reaper/scripts/reap_cloud_waste.sh --mock --export-json /tmp/waste_report.json --export-markdown /tmp/waste_report.md
```

### Phase 2: Exemption Filtering
Consult [`references/waste-matrix.md`](./references/waste-matrix.md) to ensure no production-tagged assets are touched:
* Reject any resource tagged `Environment=Production` or `DoNotDelete=true`.
* Verify that unattached storage disks have had zero read/write IOPS for at least 14 days.

### Phase 3: Blast Radius Review & Task Handoff
Do **NOT** execute autonomous deletion. In accordance with [`rules/01-destructive-actions.md`](../../../rules/01-destructive-actions.md):

1. **Format Structured Task Plan:** Deliver an atomic, human-reviewable plan for the [**DevSecOps Engineer**](../../../agents/7-agent-master-suite/devsecops-engineer.md):

```markdown
### 🛡️ DevSecOps Handoff Task Plan: FinOps Waste Reclamation
- **Target Provider:** AWS (us-east-1)
- **Monthly Waste Savings:** $107.90 USD ($1,294.80/year)
- **Destructive Action Risk:** MEDIUM (Block storage deletion requires safety snapshot)

#### Surgical Action Items
- [ ] **Task 1 (Storage):** Create point-in-time safety snapshot `snap-safety-vol-0a1b2c3d4e5f6g7h8` before purging unattached volume `vol-0a1b2c3d4e5f6g7h8` (150 GB gp3, idle 24d).
- [ ] **Task 2 (Storage):** Create point-in-time safety snapshot `snap-safety-vol-0987654321fedcba0` before purging unattached volume `vol-0987654321fedcba0` (500 GB gp3, idle 41d).
- [ ] **Task 3 (Networking):** Release unassociated Elastic IP `54.210.12.89` (Allocation ID `eipalloc-01234567`).
- [ ] **Task 4 (Networking):** Release unassociated Elastic IP `52.87.110.45` (Allocation ID `eipalloc-89abcdef`).
- [ ] **Task 5 (Gateways):** Audit VPC route tables for `vpc-0123456789abcdef0`; de-provision idle NAT Gateway `nat-0f1e2d3c4b5a6978` after human sign-off.

#### Human Operator Sign-Off Gate
- [ ] Verified no production tags (`Environment=Production`, `DoNotDelete=true`).
- [ ] Signed off by Cloud Lead / SRE Commander.
```

2. **Snapshot Safety:** Final point-in-time snapshots must be taken prior to deleting any persistent storage volumes.
3. **Present Savings:** Display total monthly and annualized savings to the human operator for explicit authorization before executing IaC de-provisioning.

---

## Continuous Self-Knowledge Enhancement Loop

When the agent identifies an unbudgeted cloud cost leak:
1. **Isolate Waste Vector:** (e.g. idle NAT Gateway, orphaned snapshot accumulation, ghost PVCs).
2. **Auto-Generate Preventative Policy:** Add a check to [`skills/devops/iac/terraform-opentofu-modules/SKILL.md`](../../devops/iac/terraform-opentofu-modules/SKILL.md) requiring lifecycle retention policies on all snapshots and dynamic NAT scaling.
3. **Update Memory:** Record the discovered cloud pricing edge case in [`AGENTS.md`](../../../AGENTS.md) under `## Learned Cloud FinOps Facts`.
