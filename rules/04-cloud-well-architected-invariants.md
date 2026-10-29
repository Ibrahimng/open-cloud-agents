---
name: Cloud Well-Architected Invariants
severity: STANDARD
scope: ALL_AGENTS
---

# Rule 04: Cloud Well-Architected Invariants

## Principle
Every architectural recommendation and infrastructure configuration must adhere to the 6 pillars of the **AWS, Google Cloud, and Azure Well-Architected Frameworks**. Production topologies must be resilient, secure, high-performing, cost-effective, and operationally maintainable.

---

## Architectural Invariants

### 1. Resiliency & Disaster Recovery (Pillar 1)
- **No Single Point of Failure (SPOF):** Production workloads must span multiple Availability Zones (AZs) or regions.
- **Explicit RTO & RPO:** System architectures must quantify Recovery Time Objective (RTO) and Recovery Point Objective (RPO).
- **Graceful Degradation:** Use circuit breakers, retries with exponential backoff and jitter, and dead-letter queues (DLQs) for asynchronous event processing.

### 2. Security & Compliance (Pillar 2)
- **Encryption by Default:**
    - *At Rest:* Customer-managed or cloud-managed KMS keys (AES-256) on all disks, tables, and buckets.
    - *In Transit:* TLS 1.3 mandated across all public and internal service-to-service endpoints.
- **Least-Privilege Access:** IAM policies must be resource-scoped and action-scoped. Never use wildcard `*` permissions in production IAM policies.
- **Network Isolation:** Workloads must run in private subnets with egress via NAT Gateways / Cloud NAT and private connectivity via VPC Endpoints / Private Service Connect.

### 3. Cost & Cloud Economics (Pillar 3)
- **Storage Lifecycle Policies:** Mandate lifecycle tiering (e.g., S3 Standard ➔ Glacier Instant Retrieval ➔ Deep Archive) on data buckets.
- **Avoid NAT Data Egress Traps:** Ensure intra-cloud traffic to object storage and managed databases uses private VPC endpoints to eliminate expensive cross-AZ NAT traversal charges.
- **Rightsizing:** Prefer autoscaling serverless compute (Cloud Run, Lambda, Fargate) or rightsized instances over static oversized VMs.

### 4. Operational Excellence & Reliability (Pillar 4)
- **The Four Golden Signals:** All service designs must output telemetry for **Latency**, **Traffic**, **Errors**, and **Saturation**.
- **SLI/SLO Alerting:** Alerts must be based on multi-window SLO burn rates rather than noisy static CPU spikes.

