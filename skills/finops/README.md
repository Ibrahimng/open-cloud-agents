# 💰 FinOps & Cloud Cost Optimization Skills

Welcome to the **FinOps & Cloud Cost Optimization** skill catalog for Open Cloud Agents.

FinOps is an operational framework and cultural practice that maximizes business value by enabling engineering, finance, and technology teams to collaborate on data-driven cloud spending decisions.

---

## Pillar Alignment

This domain is championed by the [**FinOps & Cloud Cost Optimizer**](../../agents/7-agent-master-suite/finops-cloud-cost-optimizer.md) persona and strictly follows the safety mandates in [`rules/01-destructive-actions.md`](../../rules/01-destructive-actions.md).

```text
┌────────────────────────────────────────────────────────┐
│             FinOps Cost Optimization Loop              │
├─────────────────┬──────────────────┬───────────────────┤
│   1. INFORM     │   2. OPTIMIZE    │    3. OPERATE     │
│ Visibility &    │ Rightsizing &    │ Continuous Waste  │
│ Cost Allocation │ Waste Elimination│ Reaper Automation │
└─────────────────┴──────────────────┴───────────────────┘
```

---

## 3-Tier FinOps Skills Index

| Skill | Focus | Tier 1 (Runbook) | Tier 2 (References) | Tier 3 (Automation) |
|---|---|---|---|---|
| [**`cloud-waste-reaper`**](./cloud-waste-reaper/SKILL.md) | Autonomous discovery and safe reclamation of unattached disks, idle IPs, abandoned NAT gateways, and orphan snapshots. | [`SKILL.md`](./cloud-waste-reaper/SKILL.md) | [`waste-matrix.md`](./cloud-waste-reaper/references/waste-matrix.md) | [`reap_cloud_waste.sh`](./cloud-waste-reaper/scripts/reap_cloud_waste.sh) |

---

## Inviolable Safety Guardrails for FinOps
1. **Dry-Run by Default:** FinOps automation scripts must **NEVER** autonomously delete resources. All scripts default to discovery, logging, and blast-radius quantification.
2. **Tag-Based Exemption:** Production resources tagged `Environment=Production`, `DoNotDelete=true`, or `KeepAlive` are strictly protected from reclamation.
3. **Snapshot Before Reclamation:** Any storage disk flagged for termination must have a final snapshot taken before deletion approval.
