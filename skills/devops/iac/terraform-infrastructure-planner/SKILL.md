---
name: terraform-infrastructure-planner
description: Create comprehensive, machine-readable implementation plans for multi-cloud (AWS, Azure, GCP) and Docker infrastructure in .terraform-planning-files/INFRA.{provider}.{goal}.md before any code is written, incorporating Well-Architected Framework pillars, module-first patterns, security defaults, and dependency mapping.
---

# Centralized Terraform Infrastructure Planner

## Purpose & Scope
This skill provides the centralized end-to-end planning protocol for authoring machine-readable, deterministic infrastructure specifications across **AWS**, **Microsoft Azure**, **Google Cloud Platform (GCP)**, and **Docker**. Infrastructure planning is executed strictly before any HCL code is authored, ensuring rigorous architectural alignment, security baselines, and disaster recovery planning.

All implementation plans are written to `.terraform-planning-files/INFRA.{provider}.{goal}.md` (or `.terraform-planning-files/INFRA.{goal}.md`).

---

## Core Mandate & Multi-Cloud Expertise

- **AWS Architecture**: Compute (EC2, Lambda, ECS, EKS), storage (S3, EBS, EFS), databases (RDS/Aurora, DynamoDB), networking (VPC, ALB, Route 53), security (IAM least-privilege, KMS CMKs). Verified modules: `terraform-aws-modules` on the Terraform Registry. Remote state: S3 + DynamoDB locking.
- **Azure Architecture**: Compute (AKS, Linux VMs, Container Apps), storage (Storage Accounts with GRS), databases (Cosmos DB, Azure SQL), networking (VNet, NSGs, Private Endpoints), security (Entra ID RBAC, Key Vault CMK with purge protection). Verified modules: `Azure/` namespace. Remote state: `backend "azurerm"` with blob lease locking.
- **GCP Architecture**: Compute (GKE, Compute Engine), storage (Cloud Storage with CMEK), databases (Cloud SQL, Spanner), networking (Custom-mode VPC, Private Google Access, Cloud Armor), security (Cloud IAM least-privilege, Cloud KMS 90-day rotation). Verified modules: `terraform-google-modules/` namespace. Remote state: `backend "gcs"` with object versioning.
- **Docker Architecture**: Hardened container orchestration via `kreuzwerker/docker`: non-root execution (`user = "10001:10001"`), read-only root filesystems (`read_only = true`), dropped Linux capabilities (`ALL`), explicit CPU/memory boundaries, custom user-defined bridge networks, and immutable SHA256 image digests.
- **Well-Architected Frameworks**: Alignment with AWS, Azure, and Google Cloud Well-Architected Framework pillars (Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization, Sustainability).

---

## Planning Workflow Protocol

### 1. Pre-Planning Inspection
- Check `.terraform-planning-files/` for existing plans.
- If an existing plan for the goal exists, review and build on it.
- Never modify application code or write `.tf` files directly during this stage.

### 2. Workload Classification

Evaluate requirements to classify the workload tier:

| Workload Tier | Redundancy & Availability | Security Controls | Cost Profile |
|---|---|---|---|
| **Demo / Learning** | Single-AZ, minimal NAT, Spot/Burst | Basic IAM/RBAC, default encryption | Minimal (< $50/mo) |
| **Production** | Multi-AZ (3 AZs), redundant NAT, Aurora/Managed DB | Dedicated KMS CMK/CMEK, private subnets, strict SGs/NSGs | Optimized reserved / auto-scaled |
| **Enterprise / Regulated** | Multi-Region Active/Standby, Transit Gateway/WAN | Envelope encryption, WAF, Private Endpoints, Config/Audit | High assurance, SOC 2 / HIPAA / PCI |

### 3. Module Selection & Registry Verification

- Always adopt a **module-first** strategy using verified modules:
    - **AWS:** `terraform-aws-modules/*` (VPC, EKS, RDS, S3, ALB)
    - **Azure:** `Azure/*` (`Azure/vnet/azurerm`, `Azure/aks/azurerm`)
    - **GCP:** `terraform-google-modules/*` (`terraform-google-modules/network/google`)
    - **Docker:** `kreuzwerker/docker` provider with hardened container resource patterns
- Check and specify the latest semantic version constraints (e.g. `~> 5.0`).
- Favor module composition over writing raw primitives.

### 4. Dependency & Architecture Mapping
- Map explicit `dependsOn` relationships for each resource to prevent circular dependencies or race conditions.
- Produce comprehensive Mermaid diagrams illustrating both:
  1. System and application topology
  2. Subnet, network, and traffic routing flow

---

## Standard Plan Structure: `INFRA.{provider}.{goal}.md`

Every generated plan must follow this canonical anatomy:

```markdown
# Infrastructure Implementation Plan: {Provider} - {Goal}

## 1. Executive Summary & Workload Classification
- **Cloud Provider / Target:** AWS | Azure | GCP | Docker
- **Workload Tier:** Demo/Learning | Production | Enterprise/Regulated
- **Target Region / Environment:** e.g., us-east-1, eastus2, us-central1
- **State Backend:**
  - AWS: S3 Bucket (`<bucket>`) + DynamoDB (`<table>`)
  - Azure: Resource Group (`<rg>`) + Storage Account (`<sa>`) + Container (`tfstate`)
  - GCP: GCS Bucket (`<bucket>`) + Prefix (`<prefix>`)
  - Docker: Local or remote state configuration

## 2. Well-Architected Framework Alignment
- **Security:** Least-privilege IAM/RBAC, customer-managed key encryption (CMK/CMEK), private subnets, blocked public access.
- **Reliability:** Multi-AZ redundancy, automated backups, health checks, state locking.
- **Cost Optimization (FinOps):** Rightsized compute, lifecycle storage tiering, minimal NAT gateways for non-prod.
- **Operational Excellence:** Consistent tagging/labeling (`local.common_tags` / `local.common_labels`), outputs, pinned module versions.
- **Performance Efficiency:** Auto-scaling, caching, private Google/AWS access endpoints.
- **Sustainability:** Modern Graviton / efficient instance families.

## 3. Architecture & Network Topology Diagrams
(Mermaid diagrams for data flow and subnet/network segmentation)

## 4. Target Module & Resource Inventory
| Component | Module / Resource | Source / Provider | Target Version | dependsOn |
|---|---|---|---|---|
| Network | `module.network` | Provider verified module | `~> X.Y` | None |
| Storage | `resource / module` | Hardened storage | `~> X.Y` | Encryption key |
| Database | `module.db` | Managed database | `~> X.Y` | `module.network` |

## 5. Step-by-Step Implementation Phases for DevSecOps Engineer
- [ ] **Phase 1: Foundation:** Author backend, provider configurations, and root locals.
- [ ] **Phase 2: Networking:** Provision VPC/VNet, subnets, gateways, and firewall/security groups.
- [ ] **Phase 3: Security & Encryption:** Provision KMS CMK/CMEK keys, IAM/RBAC bindings, and secret references.
- [ ] **Phase 4: Workload & Storage:** Provision compute runtimes, hardened storage, and databases.
- [ ] **Phase 5: Verification & Quality Gate:** Execute `terraform fmt`, `terraform validate`, and dry-run plan.
```
