<p align="center">
  <img src="./docs/images/social-preview.png" alt="Open Cloud Agents - Autonomous Cloud Review and Guardrails" width="100%" />
</p>

# ☁️ Open Cloud Agents

### *AI-Powered Cloud Architecture & Security Review for Teams Using Any LLM*

[![Release](https://img.shields.io/badge/Release-v1.3.0-success.svg)](CHANGELOG.md)
[![Docs](https://img.shields.io/badge/Docs-GitHub%20Pages-blue.svg)](https://ibrahimng.github.io/open-cloud-agents/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Well-Architected](https://img.shields.io/badge/Architecture-AWS%20%7C%20Azure%20%7C%20GCP-orange.svg)](#the-7-agent-master-suite)
[![Local-First](https://img.shields.io/badge/Philosophy-Local--First%20%26%20BYO--LLM-blueviolet.svg)](#core-philosophy)

**Open Cloud Agents** is a local-first, bring-your-own-LLM framework for safer cloud engineering. Instead of relying on one overloaded generalist chatbot for architecture, security, delivery, reliability, and cost, it routes each task to a specialist cloud agent with defined responsibilities, guardrails, and operational boundaries.

This project is built for engineering teams that want AI to assist with **cloud architecture reviews, security posture auditing, IaC risk analysis, GitOps promotions, SRE incident triage, and FinOps waste elimination**—without handing production infrastructure decisions to an uncontrolled prompt.

---

## 💡 Why This Project Exists

Most AI coding setups fail in production cloud environments because they treat AI as a single generalist prompt.

While a generalist chatbot works for small code completions, it breaks down when managing complex cloud systems:
* **Multi-region disaster recovery:** Hallucinating active-active consensus models without accounting for data replication lag.
* **Infrastructure as Code (IaC):** Silent `forces replacement` traps on databases and storage volumes that trigger irreversible data loss.
* **Edge & Ingress Security:** Misconfiguring load balancer cipher suites, missing redirect query preservation, or exposing container task interfaces to `0.0.0.0/0`.
* **Cost Traps:** Accumulating thousands of dollars in unbudgeted NAT Gateway egress and idle unattached storage.

Open Cloud Agents introduces a disciplined, production-aware model:
1. **Personas ([`agents/`](./agents/README.md)):** Define the mandate, boundaries, and handoff contracts.
2. **Skills ([`skills/`](./skills/README.md)):** Provide 3-tier execution runbooks (`SKILL.md`, `references/`, `scripts/`).
3. **Rules ([`rules/`](./rules/README.md)):** Enforce non-negotiable safety guardrails that block destructive actions.

---

## 🏛️ Core Philosophy

### 1. Local-First & Bring-Your-Own-LLM (BYO-LLM)
Your architecture diagrams, IaC manifests, operational runbooks, and internal security policies remain **local to your environment and codebase**—never locked inside proprietary SaaS agent platforms.
* Runs locally on your workstation, private CI runner, or sovereign cloud.
* Model-agnostic: use Claude (3.7/3.5), GPT-4o, Gemini (2.5/2.0), DeepSeek-R1, or local models via Ollama / vLLM.
* Built on open standards: Model Context Protocol (MCP), open agent skill specs, and declarative Policy-as-Code.

### 2. Specialist Agents, Not One Overloaded Prompt
Engineering organizations divide responsibilities between architects, security engineers, DevOps reviewers, release managers, SREs, and FinOps analysts. Open Cloud Agents mirrors this exact organizational discipline. Each agent has a narrower role, a clear intake contract, and dedicated verification gates.

### 3. Safety-First Operational Design
Autonomous agents must not possess unbounded destructive authority:
* **Zero Destruction:** Blocks `DROP`, `TRUNCATE`, bucket wipes, and IaC `forces replacement` without explicit human confirmation.
* **Zero-Trust Secrets:** Prohibits plaintext credentials, static long-lived keys, and unredacted logs; mandates OIDC federation.
* **Human-in-the-Loop:** Enforces mandatory human sign-off gates prior to production deployments and canary promotions.

---

## 🔄 The Core Workflow (3 Steps)

```
   ┌───────────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────┐
   │ 1. Load Repo Context  │ ───► │ 2. Run Specialist Agent │ ───► │ 3. Actionable Findings  │
   │ (IaC, K8s, Git Diff)  │      │ (Reviewer, SRE, FinOps) │      │ (Risk, Diffs, Handoffs) │
   └───────────────────────┘      └─────────────────────────┘      └─────────────────────────┘
```

1. **Load Context:** Point the agent to your repository, Terraform directory, Kubernetes manifests, or PR diff.
2. **Run Specialist Agent:** Invoke the targeted persona (e.g. `DevSecOps Reviewer` for pre-merge PR audits, `FinOps Cost Optimizer` for idle waste elimination).
3. **Produce Actionable Output:** Receive an executive risk verdict, verified code diffs, composite validation commands, and machine-executable handoffs for downstream execution.

---

## 👥 The 7-Agent Master Suite

Every formal pillar of the **AWS, Microsoft Azure, and Google Cloud Well-Architected Frameworks** is represented by a dedicated specialist agent:

| Well-Architected Pillar | Agent Persona | Core Mandate & Primary Focus | Linked Skills |
|---|---|---|:---:|
| **Strategic Architecture** | [`principal-cloud-architect.md`](./agents/7-agent-master-suite/principal-cloud-architect.md) | High-Level Design (HLD), ADRs, multi-region DR (RTO/RPO), and centralized `.terraform-planning-files/`. | 9 Skills |
| **Security & Compliance** | [`security-compliance-commander.md`](./agents/7-agent-master-suite/security-compliance-commander.md) | Cloud Security Hubs (AWS Hub, GCP SCC, Defender), SOC 2, ISO 27001, CIS Benchmarks, WAF loops. | 13 Skills |
| **Cost Optimization (FinOps)** | [`finops-cloud-cost-optimizer.md`](./agents/7-agent-master-suite/finops-cloud-cost-optimizer.md) | Idle waste elimination, container requests/limits rightsizing, S3 tiering, NAT egress elimination. | 9 Skills |
| **Code & Pipeline Security** | [`devsecops-reviewer.md`](./agents/7-agent-master-suite/devsecops-reviewer.md) | Pre-merge PR audits, state destruction prevention (`forces replacement`), perimeter bypass detection. | 9 Skills |
| **Operational Excellence** | [`devsecops-engineer.md`](./agents/7-agent-master-suite/devsecops-engineer.md) | Surgical code/IaC fixes, zero-scope-creep hardening, non-destructive tests, Conventional Commits. | 12 Skills |
| **Continuous Delivery** | [`gitops-release-manager.md`](./agents/7-agent-master-suite/gitops-release-manager.md) | Multi-environment promotion (`dev` ➔ `uat` ➔ `prod`) via ArgoCD/Flux, progressive Canary rollouts, human gates. | 5 Skills |
| **Reliability & Performance** | [`sre-reliability-engineer.md`](./agents/7-agent-master-suite/sre-reliability-engineer.md) | Four Golden Signals, SLI/SLO burn alerts, client endpoint RCA (`502/503/504`), blameless postmortems. | 8 Skills |

*Explore the complete agent suite and handoff specifications in [`agents/`](./agents/README.md).*

---

## 🛡️ Inviolable Rules & Operational Guardrails

Rules define the non-negotiable boundaries that protect production systems from AI-induced drift and outages:

| Rule Specification | Scope & Enforcement | Primary Guardrail |
|---|---|---|
| [`rules/01-destructive-actions.md`](./rules/01-destructive-actions.md) | Databases, Buckets, Cloud Storage | Bans `DROP`, `TRUNCATE`, bucket wipes, and IaC `forces replacement` without human confirmation. |
| [`rules/02-secrets-and-identity.md`](./rules/02-secrets-and-identity.md) | Identity, Credentials, Auth | Prohibits hardcoded tokens and static cloud keys; mandates short-lived OIDC workload federation. |
| [`rules/03-surgical-scope-discipline.md`](./rules/03-surgical-scope-discipline.md) | Pull Requests, Git Diff Scopes | Prohibits unsolicited mass refactorings, global formatting sweeps, and unsolicited dependency bumps. |
| [`rules/04-cloud-well-architected-invariants.md`](./rules/04-cloud-well-architected-invariants.md) | Resilience, Encryption, DR | Mandates quantitative RTO/RPO targets, KMS envelope encryption, and multi-AZ redundancy by default. |
| [`rules/05-repository-and-path-hygiene.md`](./rules/05-repository-and-path-hygiene.md) | Path & Code Hygiene | Strictly forbids leaking local developer machine paths (`/Users/<username>/`) into code or documentation. |

---

## 🔌 How to Use with Any AI Agent or IDE

You can run Open Cloud Agents across any modern AI coding assistant, IDE, or agent orchestrator:

### 1. Claude Code
```bash
claude "Read and adopt ./agents/7-agent-master-suite/devsecops-reviewer.md to audit our open PR for state destruction risks."
```

### 2. GitHub Copilot / VS Code
```text
@workspace Review my open pull request using the instructions and guardrails in #file:devsecops-reviewer.md
```

### 3. Cursor / Windsurf / Antigravity IDE
Import personas as custom project agents or configure them in your IDE rules:
```text
@principal-cloud-architect.md Draft an ADR for transitioning our payment service to multi-region active-active with conflict resolution.
```

### 4. Universal Workspace Synchronizer CLI
Export and synchronize any agent and its linked skills directly into your project repository with one command:
```bash
# Export DevSecOps Reviewer into GitHub Copilot (.github/agents/ + .github/skills/)
python3 scripts/agents/sync_agents.py --agent devsecops-reviewer --format github --target /path/to/my-repo --sync-skills

# Export all 7 agents into Cursor Rules (.cursor/rules/*.mdc)
python3 scripts/agents/sync_agents.py --all --format cursor --target /path/to/my-repo

# Export into Claude Code (.claude/agents/ + .claude/skills/)
python3 scripts/agents/sync_agents.py --agent devsecops-reviewer --format claude --target /path/to/my-repo --sync-skills
```

### 5. Custom Agent Frameworks (LangGraph, AutoGen, Raw APIs)
Because all instructions are standard Markdown with YAML frontmatter, load them programmatically in Python or TypeScript:
```python
with open("agents/7-agent-master-suite/finops-cloud-cost-optimizer.md", "r") as f:
    system_prompt = f.read()

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Audit our AWS Terraform manifests for unattached EBS waste and NAT Gateway traps."}
    ]
)
```

---

## 🧰 The 3-Tier Enterprise Skills Ecosystem

Skills provide on-demand, deep-dive procedural execution runbooks:

```text
skills/<domain>/<tech>/<skill-name>/
├── SKILL.md                 # 1. Operational runbook, triage workflow, and guardrails
├── references/              # 2. Decision trees, cheat sheets, and architecture blueprints
└── scripts/                 # 3. Executable verification, linting, and diagnostic scripts (*.sh)
```

* **Cloud Providers ([`skills/csp/`](./skills/csp/README.md)):** AWS, Microsoft Azure (193 service skills), and Google Cloud.
* **DevOps & Delivery ([`skills/devops/`](./skills/devops/README.md)):** Terraform module architecture, state protection, Kubernetes pod diagnostics (`pod_diagnose.sh`), Helm scaffolding, Dockerfile hardening, GitHub Actions OIDC federation, and ArgoCD promotion.
* **Security & Governance ([`skills/security/`](./skills/security/README.md)):** CIS complete audits, SOC 2 evidence collection, WAF rules (Cloud Armor CRS 4.22), runtime threat detection (Falco, Sysdig, Wazuh), and KMS envelope encryption.
* **FinOps & Cost ([`skills/finops/`](./skills/finops/README.md)):** Cloud waste reaper for orphaned disks, unassociated IPs, and idle NAT gateways.
* **Continual Learning ([`skills/continual-learning/`](./skills/continual-learning/README.md)):** Autonomous feedback loop synthesizing SRE incident postmortems into permanent pre-merge DevSecOps guardrails.

*Browse the complete skills catalog in [`skills/README.md`](./skills/README.md).*

---

## ⚡ Quickstart

### Prerequisites
* Python 3.10+
* Git
* Any LLM provider or local runner (Claude, OpenAI, Gemini, Ollama)

### 1. Clone & Set Up
```bash
git clone https://github.com/Ibrahimng/open-cloud-agents.git
cd open-cloud-agents
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Validate Specifications & Tool Boundaries
```bash
python3 scripts/agents/agent_pipeline.py --validate
```

### 3. Run an End-to-End Multi-Agent Handoff Simulation
```bash
python3 scripts/agents/agent_pipeline.py --simulate
```

### 4. Execute a Custom Architectural Task
```bash
python3 scripts/agents/agent_pipeline.py --task "Architect zero-downtime payments failover with Aurora Global Database"
```

---

## 🎯 Example Use Cases

### 1. Pre-Merge IaC Risk Review
Use the **DevSecOps Reviewer** to audit a Terraform pull request before merge:
* Identifies database renames that trigger silent recreation (`forces replacement`).
* Flags perimeter bypasses (task ENIs with public IPs listening on `0.0.0.0/0`).
* Enforces modern TLS ciphers (banning deprecated `ELBSecurityPolicy-2016-08`).

### 2. SRE Outage Triage & RCA
Use the **SRE Reliability Engineer** during a production incident:
* Rapidly triages client endpoint 502/503 cascades.
* Profiles CFS CPU quota throttling and HikariCP connection pool starvation.
* Formulates immediate blast-radius mitigations and blameless postmortem action items.

### 3. Cloud Waste & FinOps Assessment
Use the **FinOps Cost Optimizer** to inspect cloud infrastructure:
* Identifies unattached EBS volumes and orphaned disk snapshots.
* Rightsizes Kubernetes container requests against p95 historical telemetry.
* Eliminates costly NAT Gateway intra-cloud data transfer via free Gateway VPC Endpoints.

---

## 📂 Repository Structure

```text
.
├── AGENTS.md                  # Master Agent Directive & runtime knowledge base
├── README.md                  # Project overview, quickstart & documentation
├── LICENSE                    # Apache 2.0 open-source license
├── CHANGELOG.md               # Version history and releases
├── CONTRIBUTING.md            # Community contribution guidelines
├── mkdocs.yml                 # Documentation site configuration
├── agents/                    # 7-Agent Master Suite specifications
├── rules/                     # Non-negotiable security and operational rules
├── skills/                    # 3-tier enterprise operational skills library
├── scripts/
│   ├── agents/                # Multi-agent pipeline runner & workspace synchronizer
│   ├── ci/                    # Repository hygiene and link integrity validators
│   └── docs/                  # MkDocs documentation preparation tools
└── docs/                      # Architectural specs and engineering standards
```

---

## 🗺️ Roadmap

### Current Focus
* **Core Review Workflows:** Sharpen the value proposition for cloud architecture and security review.
* **Onboarding & First-Run Experience:** Streamline multi-workspace synchronization (`sync_agents.py`) across Copilot, Cursor, and Claude Code.
* **Production Runbooks:** Expand specialist skills across multi-cloud and Kubernetes operational guardrails.
* **Real-World Case Studies:** Deliver architectural review walkthroughs and interactive terminal demos.

### Planned Enhancements
* Additional cloud service provider modules and governance frameworks.
* Controlled multi-agent orchestration runtime with structured handoff contracts.
* Deeper CI/CD automated gates and policy-as-code admission controllers.
* Community-contributed agent personas and shared operational skill packs.

---

## 🤝 Community & Contributing

Open Cloud Agents is an open, community-driven project. We welcome pull requests from cloud practitioners, security auditors, and platform engineers.

Before submitting contributions, please review:
* [**Contributing Guide (CONTRIBUTING.md)**](./CONTRIBUTING.md)
* [**Engineering Standards**](./docs/engineering-standards.md)

Run local verification suites before opening a PR:
```bash
# Validate repository hygiene, relative links, and path safety
python3 scripts/ci/validate_repo.py

# Validate agent specifications, token budgets, and tool boundaries
python3 scripts/agents/agent_pipeline.py --validate
```

---

## ⚖️ License & Attribution

* **Core Project:** Licensed under the [Apache License 2.0](./LICENSE) © 2026 Ibrahim Jimoh.
* **Attribution:** Collaborative pair co-authorship trailer: `Co-authored-by: Antigravity <antigravity@google.com>`.
* **Provider Standards:** Cloud skills remix open-source architectural patterns from AWS (Apache-2.0), Microsoft Azure (MIT/CC-BY-4.0), Google Cloud (Apache-2.0), and the Dart/Flutter teams (BSD-3-Clause). Full notices are documented in [`skills/csp/README.md`](./skills/csp/README.md).
