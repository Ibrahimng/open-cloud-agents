# 📊 Cloud Waste & Idle Resource Identification Matrix

This reference documents the industry-standard criteria and quantitative metrics used by the FinOps Cloud Waste Reaper to distinguish genuinely abandoned cloud resources from low-traffic production assets.

---

## 1. Waste Category Thresholds

| Resource Type | Cloud Provider | Idle / Abandonment Threshold | Average Waste Cost | False Positive Risk | Safe Reclamation Protocol |
|---|---|---|---|---|---|
| **Unattached EBS / Persistent Disks** | AWS, Azure, GCP | Status = `available` (unattached) for > 14 days, 0 read/write IOPS | \$0.08–\$0.12 / GB-month (gp3 / pd-ssd) | **Medium** (May contain unmounted manual data) | Force final snapshot ➔ tag `PendingReap` for 7 days ➔ delete |
| **Unassociated Elastic / Static IPs** | AWS, Azure, GCP | Association ID = `null` for > 2 hours | \$0.005 / hour (~$3.65 / IP / month) | **Low** (IPs can be reallocated dynamically) | Release IP immediately if untagged with `DoNotRelease` |
| **Abandoned Cloud NAT Gateways** | AWS (NAT Gateway), GCP (Cloud NAT) | Active Connections = 0, Throughput < 1MB over 7 consecutive days | \$0.045 / hour (~$32.40 / month / NAT base fee) | **Medium** (Private VPC may only have sporadic egress) | Check route tables for active private subnets before tearing down |
| **Idle Application Load Balancers** | AWS (ALB), Azure (ALB), GCP (HTTP(S) LB) | `RequestCount` = 0 over 14 consecutive days; 0 healthy targets | \$0.0225 / hour (~$16.20 / month base fee + LCU) | **Low** (No traffic and no targets indicates dead endpoint) | Deregister listeners ➔ notify service owners ➔ delete |
| **Orphaned VM Snapshots** | AWS (EBS Snapshots), GCP, Azure | Parent Volume ID = Non-existent; Snapshot Age > 90 days without tag | \$0.05 / GB-month | **Low** (Historical orphaned snapshots rarely needed) | Archive oldest snapshots to cold storage or purge |
| **Abandoned Elasticache / Memorystore** | AWS (Redis/Valkey), GCP (Memorystore) | `CurrConnections` = 0 and `CmdProcessed` = 0 for > 7 days | \$25–\$250 / month (cache node size dependent) | **High** (Staging/dev cluster may be intermittently idle) | Require explicit confirmation from team lead before deletion |

---

## 2. Cloud Waste Pricing Formula

The monthly waste footprint is calculated as:

$$\text{Monthly Waste} = \sum (\text{Unattached Storage GB} \times \text{Rate}_{\text{storage}}) + \sum (\text{Idle IPs} \times \$3.65) + \sum (\text{Idle NATs} \times \$32.40) + \sum (\text{Empty ALBs} \times \$16.20)$$

Example: An uncleaned Kubernetes test cluster with:
- 12 unattached 200GB gp3 volumes: $12 \times 200 \times \$0.08 = \$192/\text{mo}$
- 4 unassociated Elastic IPs: $4 \times \$3.65 = \$14.60/\text{mo}$
- 2 idle NAT Gateways: $2 \times \$32.40 = \$64.80/\text{mo}$
- **Total Burn:** **\$271.40 / month** (\$3,256.80 annually) for zero production value.

---

## 3. Mandatory Safety Tag Exemption List

Resources carrying ANY of the following case-insensitive tags MUST be automatically excluded from the Reaper scan:

```yaml
exempt_tags:
  - key: "Environment"
    values: ["production", "prod", "critical", "live"]
  - key: "DoNotDelete"
    values: ["true", "1", "yes"]
  - key: "KeepAlive"
    values: ["true", "1", "yes"]
  - key: "Owner"
    values: ["security", "audit", "compliance"]
```
