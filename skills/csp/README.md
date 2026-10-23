# Cloud Service Provider (CSP) Skills — The Remix Standard

This directory houses the foundational and specialized skills for the three major cloud providers: **Amazon Web Services (AWS)**, **Microsoft Azure**, and **Google Cloud Platform (GCP)**.

In **Open Cloud Agents**, these skills are not merely cloned upstream dependencies—they form the **CSP Remix Standard**: a curated, standardized foundation that our **7-Agent Master Suite** remixes and builds upon to execute autonomous architecture design, security enforcement, GitOps delivery, SRE triage, and FinOps cost optimization.

---

## Directory Overview

```text
skills/csp/
├── aws/                        # AWS Well-Architected, Core & Specialized Skills, MCP Plugins
│   ├── skills/                 # Core skills (Bedrock, IAM, Serverless) & Specialized skills
│   ├── plugins/                # MCP Plugins (DevSecOps Agent, Data Analytics, Core)
│   ├── rules/                  # AWS Agent Operational Rules
│   └── README.md
├── azure/                      # Microsoft Azure Skills (193 curated service skills)
│   ├── skills/                 # App Service, AKS, Cosmos DB, Functions, Network, Entra ID
│   └── README.md
└── gcp/                        # Google Cloud Platform Skills & Well-Architected Suite
    ├── skills/                 # GKE, Cloud Run, BigQuery, AlloyDB, WAF Security, Cost
    └── README.md
```

---

## How the 7-Agent Master Suite Uses CSP Skills

Each specialist agent in the suite combines cross-cloud architectural standards with provider-specific depth:

| Agent Persona | How It Utilizes CSP Skills |
|---|---|
| **Principal Cloud Architect** | Evaluates multi-region disaster recovery, database paradigms (Aurora vs Cosmos DB vs Spanner), and messaging topologies across AWS, Azure, and GCP. |
| **Security Compliance Commander** | Maps CIS benchmarks and SOC 2 controls to native command centers (AWS Security Hub, Microsoft Defender for Cloud, GCP Security Command Center). |
| **FinOps Cloud Cost Optimizer** | Eliminates idle waste using CSP-specific tiering: AWS S3 Intelligent-Tiering / Glacier, Azure Blob Cool/Archive, and Google Cloud Storage nearline/coldline. |
| **DevSecOps Reviewer & Engineer** | Audits and implements IaC for AWS CDK/CloudFormation, Azure Bicep/ARM, and Google Cloud Resource Manager templates. |
| **SRE Reliability Commander** | Interacts with CloudWatch / Container Insights, Azure Monitor / Log Analytics, and Google Cloud Operations (Cloud Logging/Monitoring). |

---

## The Remix Principles

1. **Curated & Lean:** All dead scraper caches, raw CSV catalog dumps, and upstream repository-management overhead (`.github`, `.claude-plugin`, `mise.toml`, etc.) have been removed. Only production-ready skills, tool definitions, and MCP configurations are retained.
2. **Standardized Anatomy:** Every skill adheres to the open standard: frontmatter metadata, trigger conditions, procedural workflows, and non-destructive guardrails.
3. **Compound Intelligence:** Through our [Continual Learning Engine](../continual-learning/), every real-time incident exploration or discovered cloud quota edge case dynamically feeds back into these provider skill sets.

---

## Upstream Attributions & Open Source Licenses

The foundational skills in this directory are adapted and remixed from open-source provider projects under their respective licenses:

* **AWS Skills:** Adapted from [AWS Agent Toolkit](https://github.com/aws/agent-toolkit-for-aws), licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).
* **Azure Skills:** Adapted from [Azure Agent Skills](https://github.com/azure/agent-skills), licensed under the [MIT License](https://opensource.org/licenses/MIT) and [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).
* **Google Cloud Skills:** Adapted from [Google Agent Skills](https://github.com/google/skills), licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).

