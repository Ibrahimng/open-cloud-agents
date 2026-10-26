# 📜 Changelog

All notable changes to **Open Cloud Agents** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-10-26

### 🚀 Initial General Availability (GA) Release
This foundational release establishes **Open Cloud Agents** as an open-source, enterprise-grade multi-agent cloud engineering framework mapped 1:1 across the **AWS, Microsoft Azure, and Google Cloud Well-Architected Frameworks**.

---

### ✨ Added

#### 1. The 7-Agent Master Suite ([`agents/`](./agents/README.md))
* **Principal Cloud Architect & System Designer:** High-Level Design (HLD), authoritative Architecture Decision Records (ADRs), Domain-Driven Design (DDD), and quantitative multi-region RTO/RPO disaster recovery models.
* **Security Compliance & Cyber Defense Commander:** Automated compliance mapping across SOC 2 Type II, ISO 27001, CIS Benchmarks, and continuous WAF defense loops.
* **FinOps & Cloud Cost Optimizer:** Rightsizing, idle waste elimination, S3/storage lifecycle tiering, and intra-cloud NAT data egress trap prevention.
* **DevSecOps Reviewer:** Pre-merge PR defensive auditing, threat modeling, and state-destruction prevention (`forces replacement`).
* **DevSecOps Engineer:** Surgical code generation, zero-scope-creep bug fixes, executable test verification, and conventional commit generation.
* **GitOps Release Manager:** Progressive multi-environment promotion (`dev` ➔ `uat` ➔ `prod`) via ArgoCD/Kustomize with mandatory human sign-off gates.
* **SRE & Reliability Incident Engineer:** Four Golden Signals monitoring, multi-window SLI/SLO burn alerts, endpoint root-cause analysis (502/503/504), and blameless postmortems.

#### 2. The 3-Tier Enterprise Skills Ecosystem ([`skills/`](./skills/README.md))
* Over 360 skills standardized into a structured 3-tier architecture:
  * **Tier 1:** Autonomous runbooks (`SKILL.md`) with YAML frontmatter, incident case studies, and safety guardrails.
  * **Tier 2:** Deep architectural specs, decision trees, and cheatsheets (`references/`).
  * **Tier 3:** Executable verification and linting tools (`scripts/`).
* **Cloud Service Provider (CSP) Remix Standards:** Curated toolkits for AWS, Microsoft Azure, and Google Cloud.
* **Core Domains:** DevOps (Terraform, Kubernetes, Docker, Helm, ArgoCD, Prometheus, OpenTelemetry), Security (CIS, SOC 2, IAM, Secret Scrubbing, KMS), and modern programming languages (Dart, Python, TypeScript, Go, Java).

#### 3. Inviolable Rule Governance ([`rules/`](./rules/README.md))
* Canonical, non-negotiable guardrails protecting cloud systems from autonomous AI mistakes:
  * `01-destructive-actions.md`: Zero unplanned destruction (`DROP`, `TRUNCATE`, bucket wipes, IaC `forces replacement`).
  * `02-secrets-and-identity.md`: Zero hardcoded credentials, short-lived OIDC tokens, and log redaction.
  * `03-surgical-scope-discipline.md`: Zero unsolicited refactorings, whole-repo formatting sweeps, or unrequested dependency bumps.
  * `04-cloud-well-architected-invariants.md`: Multi-AZ/region redundancy, KMS envelope encryption, and least-privilege IAM defaults.
  * `05-repository-and-path-hygiene.md`: Mandatory relative Markdown links and strict prohibition of leaking `/Users/<username>/` workstation paths.

#### 4. Universal IDE & Agent Directives
* **`AGENTS.md`:** Universal root directive for Google Antigravity, Claude Code, Cline, and terminal agents, featuring the dynamic **Continual Learning Memory**.
* **`.cursorrules`:** System instructions for Cursor and VS Code AI assistants.

#### 5. CI Guardrails & Multi-Agent Orchestration Pipeline
* **GitHub Actions CI (`.github/workflows/ci.yml`):** Automated Gitleaks secret detection, ShellCheck script linting, and repository hygiene validation.
* **Multi-Agent Pipeline (`scripts/agents/agent_pipeline.py` & `.github/workflows/agents-pipeline.yml`):** Executable 6-stage handoff simulation runner verifying schema contracts between agents.
* **Local Runner Support (`act`):** Verified support for executing the full CI suite locally in Docker.

#### 6. Community & Open Governance
* **Contributor Hall of Fame (`CONTRIBUTORS.md`):** Roster acknowledging founding and community contributors.
* **Pull Request Template (`.github/pull_request_template.md`):** Automated PR checklist with Developer Certificate of Origin (DCO) sign-off and GitHub Privacy Alias standard.
* **Social Preview & Hero Banner (`docs/images/social-preview.png`):** High-resolution branding card.

