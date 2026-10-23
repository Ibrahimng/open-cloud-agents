# Agent Skills Catalog

This directory houses the domain-specific capabilities, workflows, and guardrails utilized by **Open Cloud Agents**. 

Skills empower autonomous agents with deep procedural knowledge, tool configurations, and best practices across Cloud Service Providers (CSPs), Programming Languages, DevOps, Security, and Data Science.

---

## Skills Taxonomy

```text
skills/
├── csp/                        # Cloud Service Providers
│   ├── aws/                    # Amazon Web Services (Well-Architected, CLI, MCP)
│   ├── azure/                  # Microsoft Azure (Azure Developer CLI, Bicep, SDKs)
│   └── gcp/                    # Google Cloud Platform (gcloud, GKE, BigQuery, WAF)
├── programming/                # Language-specific idiomatic patterns & testing
│   ├── dart/                   # Dart & Flutter engineering skills
│   ├── python/                 # Python, FastAPI, Pytest, Asyncio
│   ├── javascript/             # TypeScript, Node.js, Frontend & Backend frameworks
│   ├── go/                     # Golang concurrency, microservices, testing
│   └── java/                   # Java, Spring Boot, JVM performance
├── devops/                     # Infrastructure & Continuous Delivery
│   ├── iac/                    # Terraform, OpenTofu, Pulumi, Helm
│   ├── kubernetes/             # Cluster operations, manifests, ingress, debugging
│   ├── docker/                 # Container hardening, multi-stage builds
│   ├── ci-cd/                  # GitHub Actions, ArgoCD, Flux, pipelines
│   └── observability/          # OpenTelemetry, PromQL, Grafana, Golden Signals
├── security/                   # Enterprise Governance & Hardening
│   ├── compliance/             # CIS Benchmarks, SOC 2 Type II, NIST, ISO 27001
│   ├── iam-least-privilege/    # Zero trust, role boundaries, IAM condition keys
│   └── secret-management/      # HashiCorp Vault, AWS Secrets Manager, KMS, SOPS
└── data-science/               # Data & Machine Learning Operations
    ├── mlops/                  # Model serving, training pipelines, evaluation
    └── data-analysis/          # SQL analytics, data pipelines, notebook execution
```

---

## Anatomy of a Skill

Every skill is a self-contained package inside its respective category folder:

```text
<skill-name>/
├── SKILL.md                 # Required: YAML frontmatter + structured instructions
├── references/              # Optional: API docs, cheatsheets, configuration specs
└── scripts/                 # Optional: Automated verification or helper scripts
```

### `SKILL.md` Specification
Every `SKILL.md` must start with YAML frontmatter:
```markdown
---
name: sample-skill-name
description: A clear 1-2 sentence description explaining what the skill enables and when agents should activate it.
tools: [read, search, edit, execute]
---

# Skill Title

## Purpose & Trigger Context
When and why an agent should activate this skill.

## Step-by-Step Instructions
The procedural workflow, commands, and rules the agent must execute.

## Guardrails & Non-Goals
Explicit safety boundaries, forbidden commands, and destructive action preventions.
```
