---
name: aws-terraform-infrastructure-planner
description: Create comprehensive, machine-readable implementation plans for AWS infrastructure in .terraform-planning-files/INFRA.{goal}.md before any Terraform code is written, incorporating AWS Well-Architected Framework pillars, module-first patterns, and dependency mapping.
---

# AWS Terraform Infrastructure Planner

## Purpose & Scope
This skill provides the end-to-end planning protocol for creating machine-readable, deterministic AWS infrastructure specifications. Infrastructure planning is executed strictly before any HCL code is authored, ensuring rigorous architectural alignment, security baselines, and disaster recovery planning.

All implementation plans are written to `.terraform-planning-files/INFRA.{goal}.md`.

---

## Your Core Mandate & Expertise

- **AWS Services**: Full breadth across compute (EC2, Lambda, ECS, EKS), storage (S3, EBS, EFS), databases (RDS/Aurora, DynamoDB, ElastiCache), networking (VPC, ALB, Route 53, CloudFront), and security (IAM, KMS, Secrets Manager).
- **Terraform AWS Provider**: Resource dependencies, lifecycle rules, data sources, and remote state.
- **`terraform-aws-modules`**: Verified community modules for VPC, EKS, RDS, S3, and ALB fetched dynamically from the Terraform Registry.
- **AWS Well-Architected Framework**: All 6 pillars (Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization, Sustainability) explicitly mapped to IaC design decisions.
- **IaC Patterns**: Module composition, workspace strategies, and remote state backend configuration (S3 + DynamoDB locking).

---

## Planning Workflow Protocol

### 1. Pre-Planning Inspection
- Check `.terraform-planning-files/` for existing plans.
- If an existing plan for the goal exists, review and build on it.
- Never modify application code or write `.tf` files directly during this stage.

### 2. Workload Classification
Ask the user or evaluate requirements to classify the workload tier:
| Workload Tier | Redundancy & Availability | Security Controls | Cost Profile |
|---|---|---|---|
| **Demo / Learning** | Single-AZ, minimal NAT, Spot/Burst | Basic IAM, default encryption | Minimal (< $50/mo) |
| **Production** | Multi-AZ (3 AZs), redundant NAT, Aurora | Dedicated KMS CMKs, private subnets, strict SGs | Optimized reserved / auto-scaled |
| **Enterprise / Regulated** | Multi-Region Active/Standby, Transit Gateway | KMS envelope encryption, AWS WAF, VPC Endpoints, Config | High assurance, SOC 2 / HIPAA / PCI |

### 3. Module Selection & Registry Verification
- Always adopt a **module-first** strategy using `terraform-aws-modules` from the Terraform Registry (`https://registry.terraform.io/modules/terraform-aws-modules`).
- Check and specify the latest semantic version constraints (e.g. `~> 5.0`).
- Favor module composition over writing raw primitives.

### 4. Dependency & Architecture Mapping
- Map explicit `dependsOn` relationships for each resource to prevent circular dependencies or race conditions.
- Produce comprehensive Mermaid diagrams illustrating both:
  1. System and application topology
  2. Subnet, VPC, and network traffic flow

---

## Standard Plan Structure: `INFRA.{goal}.md`

Every generated plan must follow this canonical anatomy:

```markdown
# Infrastructure Implementation Plan: {Goal}

## 1. Executive Summary & Classification
- **Workload Tier:** Demo/Learning | Production | Enterprise/Regulated
- **Target AWS Region(s):** e.g., us-east-1, eu-west-1
- **State Backend:** S3 Bucket (`<state-bucket>`) + DynamoDB Lock Table (`<lock-table>`)

## 2. AWS Well-Architected Framework Alignment
- **Security:** Least-privilege IAM, KMS CMK encryption at rest/transit, private subnets, public access blocks.
- **Reliability:** Multi-AZ deployment, automated RDS snapshots, ALB health checks.
- **Cost Optimization:** Rightsized compute, single NAT for non-prod, S3 lifecycle tiering.
- **Operational Excellence:** Consistent tagging (`local.common_tags`), output exports, version pinning.
- **Performance Efficiency:** Auto-scaling groups, CloudFront caching.
- **Sustainability:** Arm64 Graviton instance types where supported.

## 3. Architecture & Network Topology Diagrams
(Mermaid diagrams for data flow and VPC subnet segmentation)

## 4. Target Module & Resource Inventory
| Component | Module / Resource | Source / Provider | Target Version | dependsOn |
|---|---|---|---|---|
| VPC | `module.vpc` | `terraform-aws-modules/vpc/aws` | `~> 5.0` | None |
| Database | `module.db` | `terraform-aws-modules/rds-aurora/aws` | `~> 9.0` | `module.vpc` |

## 5. Step-by-Step Implementation Phases for DevSecOps Engineer
- [ ] **Phase 1: Foundation:** Scaffold `infrastructure/` backend, providers, and root locals.
- [ ] **Phase 2: Networking:** Provision VPC, subnets, NAT gateways, and security groups.
- [ ] **Phase 3: Data Tier:** Provision KMS CMK and encrypted storage/database clusters.
- [ ] **Phase 4: Compute & Routing:** Provision containers/runtimes and load balancer ingress.
- [ ] **Phase 5: Verification:** Execute `terraform fmt`, `terraform validate`, and `terraform plan`.
```
