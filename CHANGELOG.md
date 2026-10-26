# 📜 Changelog

All notable changes to **Open Cloud Agents** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.0] - 2026-10-26

### 💰 FinOps Cloud Waste Reaper, Docs-as-Code & Automated Governance
This minor release introduces the complete **FinOps & Cost Optimization** domain, an automated **Docs-as-Code** static site on GitHub Pages, selective CI change detection, and automated **Dependabot** daily security auditing across 12 merged Pull Requests (#1–#12).

---

### ✨ Added

#### 1. FinOps Cloud Waste Reaper ([`skills/finops/cloud-waste-reaper/`](./skills/finops/cloud-waste-reaper/SKILL.md))
* **3-Tier Skill Architecture:** Runbook, quantitative metrics matrix, multi-cloud query syntax, and executable automation script.
* **Multi-Cloud Waste Hunter Script (`reap_cloud_waste.sh`):**
  * **AWS Scanning:** Unattached EBS volumes (`gp3`/`io2`), unassociated Elastic IPs, idle NAT Gateways, and empty ALBs.
  * **GCP Scanning:** Unattached Persistent Disks (`pd-standard`/`pd-ssd`) and reserved static IPs.
  * **Azure Scanning:** Unattached Managed Disks and unassociated Public IPs.
  * **Deterministic Mock Engine:** Simulated multi-cloud environment producing \$107.90/mo (\$1,294.80/yr) waste baseline for CI and local verification.
  * **Reporting Formats:** Generates structured JSON (`--export-json`) and GitHub-flavored Markdown PR summary tables (`--export-markdown`).
* **Real-World Incident Cases:** Documented root-cause postmortems for the \$14,000 Abandoned NAT Gateway, 80,000 Orphaned Snapshots, and Ghost Kubernetes StatefulSet PVC leaks.
* **Non-Destructive Safety Gate:** Strict compliance with Rule 01 (dry-run by default; requires explicit DevSecOps handoff and human sign-off before reclamation).

#### 2. Docs-as-Code Static Site on GitHub Pages
* **Live Documentation Portal:** Public searchable documentation website hosted at [https://ibrahimng.github.io/open-cloud-agents/](https://ibrahimng.github.io/open-cloud-agents/).
* **Single Source of Truth (`scripts/docs/prepare_docs.py`):** Automatically aggregates in-repo Markdown documents (agents, skills, rules, specs, changelog) with zero documentation drift.
* **Theme & Features (`mkdocs.yml`):** MkDocs Material with light/dark mode auto-detection, Mermaid diagram rendering, instant client-side search, and hierarchical sidebar navigation.
* **Automated CD Workflow (`.github/workflows/docs.yml`):** Automatic deployment to GitHub Pages upon pushes to `main`.

#### 3. Subsystem Selective Change Detection in CI
* **Pre-Flight Filter (`dorny/paths-filter`):** Evaluates changed files in ~1.5s to trigger only relevant test jobs (`scripts`, `finops`, `docs_only`).
* **Conventional Branch Triggers:** Expanded CI triggers across `feat/**`, `fix/**`, `docs/**`, `chore/**`, and `refactor/**`.
* **Zero Runner Waste:** Documentation-only pull requests complete in ~3 seconds while preserving all branch protection status checks.

#### 4. Automated Governance & Daily Auditing
* **Code Ownership ([`.github/CODEOWNERS`](./.github/CODEOWNERS)):** Enforces mandatory review and sign-off from `@ibrahimng` on protected branches.
* **Dependabot Configuration ([`.github/dependabot.yml`](./.github/dependabot.yml)):** Daily automated dependency and vulnerability scanning at 04:00 UTC for GitHub Actions and Python tooling.
* **Scheduled Daily Codebase Audit ([`.github/workflows/scheduled-audit.yml`](./.github/workflows/scheduled-audit.yml)):** Daily 4:00 AM regression runner testing repository hygiene, agent contracts, simulation, and FinOps reaper, with automated GitHub Issue alerts on failure.

---

### 🔄 Changed
* **Upgraded GitHub Actions Toolchain (PRs #3–#12):** Bumped all workflow actions to Node 24–compatible releases (`actions/checkout@v7`, `actions/deploy-pages@v5`, `actions/upload-pages-artifact@v5`, `actions/configure-pages@v6`, `actions/setup-python@v7`, `actions/upload-artifact@v7`, `actions/github-script@v9`, `softprops/action-gh-release@v3`, `dorny/paths-filter@v4`).
* **Python Tooling:** Pinned `requirements.txt` with `mkdocs-material` and `pyyaml>=6.0.3` (PR #2, PR #3).
* **Local `act` Runner:** Configured `.actrc` with `catthehacker/ubuntu:act-latest` on `linux/amd64` to prevent interactive prompts and Apple Silicon warnings.

---

### 🏆 Merged Pull Requests in this Release
* **PR #1:** `feat(finops): introduce cloud waste reaper 3-tier skill and automated discovery script`
* **PR #2:** `chore(deps): update mkdocs-material requirement`
* **PR #3:** `chore(deps): update pyyaml requirement from >=6.0.1 to >=6.0.3`
* **PR #4:** `ci(deps): bump actions/upload-artifact from 4 to 7`
* **PR #5:** `ci(deps): bump actions/checkout from 4 to 7`
* **PR #6:** `ci(deps): bump softprops/action-gh-release from 2 to 3`
* **PR #7:** `ci(deps): bump actions/configure-pages from 5 to 6`
* **PR #8:** `ci(deps): bump actions/deploy-pages from 4 to 5`
* **PR #9:** `ci(deps): bump dorny/paths-filter from 3 to 4`
* **PR #10:** `ci(deps): bump actions/upload-pages-artifact from 3 to 5`
* **PR #11:** `ci(deps): bump actions/setup-python from 5 to 7`
* **PR #12:** `ci(deps): bump actions/github-script from 7 to 9`

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

