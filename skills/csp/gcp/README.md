# Google Cloud Platform (GCP) Skills — Open Cloud Agents Remix

Curated agent skills for Google Cloud Platform (GCP), remixed and integrated into the **Open Cloud Agents** ecosystem.

This catalog provides deep operational expertise across Google Cloud runtime services, data warehouse platforms, networking observability, and the **Google Cloud Well-Architected Framework (WAF)**.

---

## Directory Structure

```text
skills/csp/gcp/
├── skills/
│   ├── gke-basics/             # Google Kubernetes Engine cluster creation, autoscaling, security
│   ├── gke-upgrades/           # GKE cluster control plane & node pool upgrade runbooks
│   ├── cloud-run-basics/       # Serverless container deployments, traffic splitting, env configuration
│   ├── bigquery-basics/        # Dataset creation, SQL transformations, table optimizations
│   ├── cloud-sql-basics/       # Managed MySQL/PostgreSQL/SQL Server provisioning & backup
│   ├── alloydb-basics/         # High-performance PostgreSQL-compatible database clustering
│   ├── google-cloud-storage/   # Object lifecycles, IAM uniform bucket access, CMEK encryption
│   ├── google-cloud-networking-observability/ # VPC Flow Logs, Connectivity Tests, Firewall insights
│   ├── google-cloud-waf-security/              # WAF Security Pillar controls
│   ├── google-cloud-waf-reliability/           # WAF Reliability Pillar designs
│   ├── google-cloud-waf-cost-optimization/     # WAF Cost Optimization (FinOps)
│   ├── google-cloud-waf-operational-excellence/# WAF Operational Excellence standards
│   ├── google-cloud-waf-performance-optimization/ # WAF Performance Efficiency
│   └── google-cloud-waf-sustainability/        # WAF Carbon footprint reduction
└── README.md
```

---

## Key Capabilities by Well-Architected Pillar

* **Security:** SAIF (Secure AI Framework) risk factors, GCS uniform bucket-level access, Workload Identity federation.
* **Reliability:** Regional GKE clusters, Cloud SQL cross-region read replicas, and Spanner multi-region configurations.
* **Cost Optimization (FinOps):** BigQuery slot reservations vs on-demand pricing, GCS Nearline/Coldline tiering, and idle VM downsizing.
* **Operational Excellence:** `gcloud` CLI workflows, Workload Manager compliance evaluation, and automated runbook templates.

---

## Upstream Attribution

Original foundation adapted from the [Google Agent Skills](https://github.com/google/skills) repository, licensed under the [Apache License 2.0](./LICENSE).
