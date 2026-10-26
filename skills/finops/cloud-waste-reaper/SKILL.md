---
name: Cloud Waste Reaper & Idle Asset Elimination
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
Run the automated discovery script in dry-run mode:
```bash
./scripts/reap_cloud_waste.sh --provider aws --dry-run --export-json /tmp/waste_report.json
```
For testing without live cloud credentials, run mock mode:
```bash
./scripts/reap_cloud_waste.sh --mock --export-json /tmp/waste_report.json
```

### Phase 2: Exemption Filtering
Consult [`references/waste-matrix.md`](./references/waste-matrix.md) to ensure no production-tagged assets are touched:
* Reject any resource tagged `Environment=Production` or `DoNotDelete=true`.
* Verify that unattached storage disks have had zero read/write IOPS for at least 14 days.

### Phase 3: Blast Radius Review & Task Handoff
Do **NOT** execute autonomous deletion. In accordance with [`rules/01-destructive-actions.md`](../../../rules/01-destructive-actions.md):
1. Format a structured Task Plan for the [**DevSecOps Engineer**](../../../agents/7-agent-master-suite/devsecops-engineer.md).
2. Create final safety snapshots of any volumes targeted for reclamation.
3. Present the estimated monthly cost savings to the human operator for approval.

---

## Continuous Self-Knowledge Enhancement Loop

When the agent identifies an unbudgeted cloud cost leak:
1. **Isolate Waste Vector:** (e.g. idle NAT Gateway, orphaned snapshot accumulation).
2. **Auto-Generate Preventative Policy:** Add a check to [`skills/devops/iac/terraform-opentofu-modules/SKILL.md`](../../devops/iac/terraform-opentofu-modules/SKILL.md) requiring lifecycle retention policies on all snapshots and dynamic NAT scaling.
3. **Update Memory:** Record the discovered cloud pricing edge case in [`AGENTS.md`](../../../AGENTS.md) under `## Learned Cloud FinOps Facts`.
