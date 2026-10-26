<div align="center">

<img src="./docs/images/social-preview.png" alt="Open Cloud Agents - Autonomous Multi-Agent Cloud Engineering" width="100%" />

# ☁️ Open Cloud Agents

### *Autonomous, Well-Architected Cloud Engineering for Any AI Agent or IDE*

[![Release](https://img.shields.io/badge/Release-v1.0.0-success.svg)](CHANGELOG.md)
[![Docs](https://img.shields.io/badge/Docs-GitHub%20Pages-blue.svg)](https://ibrahimng.github.io/open-cloud-agents/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Well-Architected](https://img.shields.io/badge/Architecture-AWS%20%7C%20Azure%20%7C%20GCP-orange.svg)](#the-7-agent-master-suite)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Local-First](https://img.shields.io/badge/Philosophy-Local--First%20%26%20BYO--LLM-blueviolet.svg)](#the-core-philosophy)

**Open Cloud Agents** is an open-source, enterprise-grade multi-agent cloud engineering framework mapped 1:1 across the **AWS, Microsoft Azure, and Google Cloud Well-Architected Frameworks**.

From High-Level Design (HLD) and threat modeling to surgical code fixes, progressive GitOps rollouts, SRE incident response, and FinOps unit economics—this suite transforms your AI assistant into an elite, battle-tested cloud engineering organization.

[The Core Philosophy](#the-core-philosophy) •
[The 7-Agent Master Suite](#the-7-agent-master-suite) •
[Inviolable Rules](#inviolable-rules--operational-guardrails) •
[How to Use with Any AI Agent / IDE](#how-to-consume-with-any-ai-agent-or-ide) •
[Skills Catalog](#the-3-tier-enterprise-skills-ecosystem) •
[Contributing](#community--contributing)

</div>

---

## 💡 The Core Philosophy

### 1. The Anti-Pattern: The Overloaded Generalist Chatbot
Most AI coding setups fail in production cloud environments because they treat AI as a single, generalist prompt. 

One prompt is expected to design multi-region disaster recovery, evaluate SOC 2 compliance, audit Terraform for state destruction, execute surgical bug fixes, manage canary rollouts, triage 502/503 runtime incidents, and optimize NAT gateway egress costs.

The result? **Hallucinated topologies, deleted production databases, and cloud bill shock.**

In real engineering organizations, no single human does all of this. You have specialist teams with strict mandates, formal handoffs, and negative trade-off accounting. **Open Cloud Agents enforces this exact separation of concerns.**

### 2. Local-First & Bring-Your-Own-LLM (BYO-LLM)
Your infrastructure design, architectural decisions, operational runbooks, and internal policies belong to **you and your codebase**—not locked inside proprietary SaaS agent platforms.
* Works locally on your machine or private runner.
* Agnostic of the underlying model: use Claude 3.7/3.5, GPT-4o, Gemini 2.5/2.0, DeepSeek-R1, or local models via Ollama / vLLM.
* Built on open standards: Model Context Protocol (MCP), open agent skill specs, and declarative Policy-as-Code.

### 3. The Compounding Intelligence Flywheel
Textbook examples are not enough. In production, systems break in subtle, undocumented ways:
* An Aurora parameter group family change silently destroys a 4TB database cluster.
* A CoreDNS single-threaded UDP lookup bottlenecks a 35,000 QPS checkout service.
* A cross-AZ S3 data lake transfer generates a \$14,000 unbudgeted NAT Gateway bill.

Through our [Continual Learning Engine](./skills/continual-learning/), every real-life outage triage, SRE postmortem, and discovered cloud quota edge case **autonomously synthesizes into permanent DevSecOps pre-merge guardrails**. The engineering system gets smarter and safer with every single run.

---

## 🏛️ The 7-Agent Master Suite

Every formal pillar of the AWS, Azure, and Google Cloud Well-Architected Frameworks is represented by a dedicated specialist persona:

```text
                               1. STRATEGY & HIGH-LEVEL DESIGN
                            ┌───────────────────────────────────┐
                            │     Principal Cloud Architect     │
                            │   • HLD & ADRs • Multi-Region DR   │
                            └─────────────────┬─────────────────┘
                                              │
                      ┌───────────────────────┴───────────────────────┐
                      ▼                                               ▼
              GOVERNANCE & COMPLIANCE                           COST & FINOPS
      ┌─────────────────────────────────────┐         ┌─────────────────────────────────────┐
      │    Security Compliance Commander    │         │    FinOps Cloud Cost Optimizer      │
      │  • SOC 2 / ISO 27001 / NIST / CIS   │         │  • Rightsizing & Waste Elimination  │
      │  • WAF Telemetry & OWASP Defense    │         │  • S3 / Storage Lifecycle Tiering   │
      └──────────────────┬──────────────────┘         └──────────────────┬──────────────────┘
                         │ Policies & Directives                         │ Cost Targets
                         └──────────────────────┬────────────────────────┘
                                                ▼
                                   2. AUDIT & THREAT MODEL
                            ┌───────────────────────────────────┐
                            │        DevSecOps Reviewer         │
                            │   • Pre-merge PR & IaC Audits     │
                            │   • State Loss / Replace Traps    │
                            └─────────────────┬─────────────────┘
                                              │ Task Plan Handoff
                                              ▼
                                  3. SURGICAL IMPLEMENTATION
                            ┌───────────────────────────────────┐
                            │        DevSecOps Engineer         │
                            │   • Zero Scope Creep Code Fixes   │
                            │   • Non-Destructive Local Tests   │
                            └─────────────────┬─────────────────┘
                                              │ Merged / Tagged
                                              ▼
                                    4. CONTINUOUS DELIVERY
                            ┌───────────────────────────────────┐
                            │      GitOps Release Manager       │
                            │   • Dev ➔ UAT ➔ Prod Promotion    │
                            │   • Mandatory Human Prod Gate     │
                            └─────────────────┬─────────────────┘
                                              │ Production Traffic
                                              ▼
                                 5. RUNTIME RELIABILITY & SRE
                            ┌───────────────────────────────────┐
                            │     SRE Reliability Commander     │
                            │   • Four Golden Signals & SLI/SLO │
                            │   • Blameless Postmortems (PIR)   │
                            └───────────────────────────────────┘
```

| Well-Architected Pillar | Agent Spec | Primary Persona | Mandate & Capabilities |
|---|---|---|---|
| **Strategic Architecture** | [`principal-cloud-architect.md`](./agents/7-agent-master-suite/principal-cloud-architect.md) | **Technical Fellow & Systems Architect** | High-Level Design (HLD), Architecture Decision Records (ADRs), Domain-Driven Design (DDD), Multi-Region Active-Active DR. |
| **Security & Compliance** | [`security-compliance-commander.md`](./agents/7-agent-master-suite/security-compliance-commander.md) | **CISO & Cyber Defense Commander** | Security Command Centers (AWS Hub, Defender for Cloud, GCP SCC), SOC 2 Type II, ISO 27001, OWASP Top 10, WAF loops. |
| **Code & Pipeline Security** | [`devsecops-reviewer.md`](./agents/7-agent-master-suite/devsecops-reviewer.md) | **Defensive Auditor & Threat Modeler** | Pre-merge PR audits, state destruction prevention (`forces replacement`), threat paths, and machine-readable task handoffs. |
| **Operational Excellence** | [`devsecops-engineer.md`](./agents/7-agent-master-suite/devsecops-engineer.md) | **Surgical Implementer & Hardening Engineer** | Ingests task plans, applies zero-scope-creep fixes, executes non-destructive tests, and generates conventional commits. |
| **Continuous Delivery** | [`gitops-release-manager.md`](./agents/7-agent-master-suite/gitops-release-manager.md) | **Release & GitOps Specialist** | Multi-environment promotion (`dev` ➔ `uat` ➔ `prod`) via ArgoCD/Flux, progressive Canary rollouts, and human sign-off gates. |
| **Reliability & Performance** | [`sre-reliability-engineer.md`](./agents/7-agent-master-suite/sre-reliability-engineer.md) | **Site Reliability & Incident Commander** | Four Golden Signals, SLI/SLO/SLA burn-rate alerting, client endpoint RCA (`502/503/504`), and blameless postmortems. |
| **Cost Optimization (FinOps)** | [`finops-cloud-cost-optimizer.md`](./agents/7-agent-master-suite/finops-cloud-cost-optimizer.md) | **Cloud Financial Engineer (FinOps)** | Idle waste elimination, container/VM rightsizing, storage tiering lifecycles (S3/Glacier), and NAT gateway cost traps. |

---

## 🔌 How to Consume with ANY AI Agent or IDE

You can run Open Cloud Agents across **any AI coding assistant, IDE, or agent orchestrator**.

### Option 1: Claude Code
Copy or symlink the desired skills into your project's `.claude/skills` directory, or instruct Claude to use a specific persona:
```bash
# Example: Activate the SRE Incident Commander persona
claude "Read and adopt the instructions in ./agents/7-agent-master-suite/sre-reliability-engineer.md to triage the 502 outage in staging."
```

### Option 2: Cursor / Windsurf / Antigravity IDE
* **As Custom Agent Personas:** In your IDE's agent configuration, point custom subagents to the markdown files in `agents/7-agent-master-suite/`.
* **As Project Rules:** Add key architectural rules or link directly to [`skills/README.md`](./skills/README.md) in your `.cursorrules` or workspace prompt.
* **Direct Prompt Invocation:**
  ```text
  @principal-cloud-architect.md Draft an ADR for transitioning our payment service from single-region Aurora to multi-region active-active with conflict resolution.
  ```

### Option 3: GitHub Copilot / VS Code
* Open any agent file (e.g. [`devsecops-reviewer.md`](./agents/7-agent-master-suite/devsecops-reviewer.md)), open Copilot Chat, and invoke:
  ```text
  @workspace Review my open pull request using the instructions and guardrails in #file:devsecops-reviewer.md
  ```

### Option 4: Custom Frameworks (LangGraph, AutoGen, CrewAI, Raw APIs)
Because all agent instructions and skills are structured in standard Markdown with YAML frontmatter, you can load them programmatically in Python or TypeScript:
```python
with open("agents/7-agent-master-suite/finops-cloud-cost-optimizer.md", "r") as f:
    system_prompt = f.read()

# Pass directly as the system prompt to OpenAI, Anthropic, or Ollama clients
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Analyze our AWS CloudWatch and NAT Gateway bill for waste."}
    ]
)
```

---

## 🧰 The 3-Tier Enterprise Skills Ecosystem

Every skill in [`skills/`](./skills/README.md) follows a production-grade 3-tier architecture:

```text
skills/<domain>/<tech>/<skill-name>/
├── SKILL.md                 # 1. Autonomous instructions, real-life incidents, guardrails
├── references/              # 2. Architecture specs, decision trees, cheat sheets
└── scripts/                 # 3. Executable verification, linting, and recovery tools
```

* **Cloud Service Providers ([`skills/csp/`](./skills/csp/README.md)):** Curated **Remix Standards** for AWS (Core, Specialized, MCP Plugins), Azure (193 service skills), and Google Cloud (34 skills + WAF Suite).
* **DevOps & Delivery ([`skills/devops/`](./skills/devops/README.md)):** Terraform module architecture, state protection traps, Kubernetes pod diagnostics (CoreDNS throttling outage), Helm scaffolding, Dockerfile distroless hardening, GitHub Actions OIDC federation, ArgoCD promotion, PromQL Golden Signals, and OpenTelemetry tracing.
* **Security & Governance ([`skills/security/`](./skills/security/README.md)):** CIS Foundation audits, SOC 2 Type II evidence harvesting, IAM least-privilege synthesis, Workload Identity federation, emergency Git secret scrub runbooks, and KMS envelope encryption.
* **Programming Languages ([`skills/programming/`](./skills/programming/README.md)):** Idiomatic patterns and automated test suites across **Dart** (11 skills), **Python** (FastAPI / pytest), **TypeScript/JavaScript** (strict types), **Go** (structured concurrency), and **Java** (Spring Boot / HikariCP).
* **Continual Learning ([`skills/continual-learning/`](./skills/continual-learning/README.md)): Transcript mining loops and automated translation of SRE incident postmortems into pre-merge DevSecOps guardrails.
* **FinOps & Cost Optimization ([`skills/finops/`](./skills/finops/README.md)):** Autonomous discovery and reclamation of unattached disks, unassociated Elastic IPs, idle NAT gateways, and orphan snapshots with dry-run safety.

---

## 🛡️ Inviolable Rules & Operational Guardrails

While **Agents** define cognitive personas and **Skills** provide operational runbooks, **Rules ([`rules/`](./rules/README.md))** define non-negotiable boundaries that protect production systems from AI-induced failure:

| Rule | File | Mandate |
|---|---|---|
| **Zero Destruction** | [`rules/01-destructive-actions.md`](./rules/01-destructive-actions.md) | Bans `DROP`, `TRUNCATE`, bucket wipes, and IaC `forces replacement` without explicit human confirmation. |
| **Zero-Trust Secrets** | [`rules/02-secrets-and-identity.md`](./rules/02-secrets-and-identity.md) | Prohibits hardcoded credentials, static long-lived keys, and unredacted logs. Mandates OIDC token exchange. |
| **Surgical Scope** | [`rules/03-surgical-scope-discipline.md`](./rules/03-surgical-scope-discipline.md) | Banning unsolicited mass refactorings, global reformatting sweeps, and unsolicited dependency modifications. |
| **Well-Architected Defaults** | [`rules/04-cloud-well-architected-invariants.md`](./rules/04-cloud-well-architected-invariants.md) | Mandates explicit RTO/RPO targets, multi-AZ/region redundancy, KMS envelope encryption, and IAM least privilege. |
| **Path & Link Hygiene** | [`rules/05-repository-and-path-hygiene.md`](./rules/05-repository-and-path-hygiene.md) | Forbids leaking local workstation paths (`/Users/<username>/`) and enforces relative link resolution. |

Universal system directives are consolidated in [**`AGENTS.md`**](./AGENTS.md) and [**`.cursorrules`**](./.cursorrules).

---

## 🏗️ Open Cloud Agents Runtime Architecture

For teams building local-first development environments or dedicated IDE integrations, Open Cloud Agents is powered by a modular, local-first runtime architecture:
```text
┌────────────────────────────────────────────────────────┐
│                        IDE Host                        │
│   (Electron / Tauri + Monaco Editor + Diff Review UI)  │
└──────────────┬──────────────────────────┬──────────────┘
               │                          │
               ▼                          ▼
      ┌─────────────────┐        ┌─────────────────┐
      │    Agent API    │◄──────►│   MCP Gateway   │
      │  (Orchestrator) │        │ (Tools & ACLs)  │
      └────────┬────────┘        └────────┬────────┘
               │                          │
        ┌──────┴──────┐                   ▼
        ▼             ▼          ┌─────────────────┐
┌──────────────┐┌──────────────┐ │ Sandbox Runner  │
│ Model Router ││Memory Service│ │(Docker/gVisor/ │
│  (BYO-LLM)   ││(pgvector/SQL)│ │ Firecracker)    │
└──────────────┘└──────────────┘ └─────────────────┘
```
Detailed API contracts, service boundaries, and implementation roadmaps are available in [**`docs/architecture-mvp-spec.md`**](./docs/architecture-mvp-spec.md).

---

## 🤝 Community & Contributing

**Open Cloud Agents is an open, community-driven project.** We believe the future of autonomous cloud engineering is shaped by practitioners sharing their battle-tested experiences.

We actively welcome and review pull requests from everyone:
* **Propose New Personas:** Have an idea for a `database-reliability-architect`, `mlops-engineer`, or `zero-trust-identity-specialist`?
* **Share Real-Life Incident Postmortems:** Turn an outage you resolved into a real-time exploration protocol and a preventative guardrail.
* **Add New Skills & Automation Scripts:** Contribute verified Python/Bash scripts and reference documentation.
* **Harden Prompt Guardrails:** Help eliminate subtle hallucinations, destructive commands, and cloud quota edge cases.

### 🧪 Local Testing with `act`

Before opening a pull request, you can run the exact GitHub Actions CI suite locally on your machine using [`act`](https://github.com/nektos/act):

```bash
# 1. Install act (if not already installed)
brew install act

# 2. Run the complete CI suite locally inside Docker:
act --container-architecture linux/amd64

# 3. Or run the lightweight Python validators directly:
python3 scripts/ci/validate_repo.py
python3 scripts/agents/agent_pipeline.py --validate
```

Please review our [**Contributing Guide (CONTRIBUTING.md)**](./CONTRIBUTING.md) and [**Engineering Standards**](./docs/engineering-standards.md) to get started, and meet the engineers behind this project in our [**Contributor Hall of Fame (CONTRIBUTORS.md)**](./CONTRIBUTORS.md)!

---

## ⚖️ License & Attribution

* **Core Project:** Licensed under the [Apache License 2.0](./LICENSE) © 2026 Ibrahim Jimoh.
* **Provider Attributions:** Foundational CSP skills are remixed from open-source toolkits by AWS (Apache-2.0), Microsoft Azure (MIT/CC-BY-4.0), Google Cloud (Apache-2.0), and the Dart/Flutter teams (BSD-3-Clause). Full notices are documented in [`skills/csp/README.md`](./skills/csp/README.md).
