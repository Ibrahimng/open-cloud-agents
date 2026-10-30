# ☁️ Open Cloud Agents

### *Local-first AI agents for safer cloud architecture, security review, and production operations.*

**Open Cloud Agents** helps teams use AI more safely for cloud work. Instead of one overloaded generalist chatbot, it routes tasks to specialist agents for architecture review, IaC security analysis, release governance, operational resilience, and cloud cost optimization.

---

### Built for:
- **Cloud architects**
- **Platform engineering teams**
- **Security and compliance reviewers**
- **SRE teams**
- **Teams that want AI without giving up local control**

---

## 💡 Why It Exists

Most AI tools fail in real cloud environments because they try to do too much with one prompt.

Cloud work requires:
- **Specialized reasoning**
- **Rule-based safety controls**
- **Architecture trade-off analysis**
- **Controlled delivery flows**
- **Production guardrails**

Open Cloud Agents separates these concerns into **agents**, **skills**, and **rules** so the system behaves more like a disciplined engineering team than a single hallucinating assistant.

---

## ⚡ Core Capabilities

- **Architecture review and design guidance**
- **Security and compliance analysis**
- **IaC and PR risk review**
- **Release and deployment governance**
- **SRE and reliability checks**
- **FinOps and waste analysis**

---

## 🔒 Local-First and BYO-LLM

Open Cloud Agents is designed to run where you want it to run:
- **Local machines**
- **Private runners**
- **Your own model providers**
- **Your own repo and infrastructure context**

It does not lock teams into a proprietary AI platform.

---

## 👥 The Specialist Agent Model

The project organizes cloud work into specialist roles:

| Specialist Agent | Mandate & Focus |
|---|---|
| [**Principal Cloud Architect**](../agents/7-agent-master-suite/principal-cloud-architect.md) | High-Level Design (HLD), ADRs, multi-region disaster recovery, and architecture trade-offs. |
| [**Security Compliance Commander**](../agents/7-agent-master-suite/security-compliance-commander.md) | Cloud Security Hubs, Falco eBPF kernel defense, Wazuh SIEM, Sentinel, ISO 42001, and CIS audits. |
| [**DevSecOps Reviewer**](../agents/7-agent-master-suite/devsecops-reviewer.md) | Pre-merge PR audits, state destruction prevention (`forces replacement`), perimeter checks. |
| [**DevSecOps Engineer**](../agents/7-agent-master-suite/devsecops-engineer.md) | Surgical code/IaC fixes, zero-scope-creep hardening, non-destructive validation scripts. |
| [**GitOps Release Manager**](../agents/7-agent-master-suite/gitops-release-manager.md) | Multi-environment promotion (`dev` ➔ `uat` ➔ `prod`), canary rollouts, human sign-off gates. |
| [**SRE Reliability Engineer**](../agents/7-agent-master-suite/sre-reliability-engineer.md) | Four Golden Signals, SLI/SLO burn alerts, client endpoint RCA (`502/503/504`), blameless postmortems. |
| [**FinOps Cloud Cost Optimizer**](../agents/7-agent-master-suite/finops-cloud-cost-optimizer.md) | Idle waste elimination, container request rightsizing, S3 tiering, NAT egress elimination. |

Each agent has a narrow mandate, making the system easier to reason about and safer to use.

---

## 🛡️ Safety First

Open Cloud Agents is built around operational discipline:
- **No destructive actions without human approval**
- **No secret leakage**
- **No broad unscoped refactors**
- **No unsafe deployment pathways**
- **Well-architected defaults are treated as guardrails**

---

## 🚀 Quick Start

### Install

#### Option A: Standalone CLI (`ocagents`)
```bash
# macOS & Linux (Homebrew):
brew install open-cloud-agents/tap/ocagents

# Universal Shell (macOS & Linux):
curl -fsSL https://open-cloud-agents.github.io/ocagents/install.sh | bash

# Windows (PowerShell):
irm https://open-cloud-agents.github.io/ocagents/install.ps1 | iex
```

#### Option B: From Source
```bash
git clone https://github.com/open-cloud-agents/ocagents.git
cd ocagents
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Validate
```bash
python3 scripts/agents/agent_pipeline.py --validate
```
*(Or via standalone CLI: `ocagents validate`)*

### Run a Workflow
```bash
python3 scripts/agents/agent_pipeline.py --simulate
```
*(Or via standalone CLI: `ocagents run`)*

---

## 🎯 Example Use Cases

- **Review a cloud architecture** for resilience and security gaps
- **Audit Terraform or Kubernetes changes** before merge
- **Guide post-incident SRE investigation**
- **Identify wasted cloud spend**
- **Reduce risk of unsafe rollout decisions**

---

## 📚 Docs

- [**Master Agent Directive (AGENTS.md)**](../AGENTS.md)
- [**Agent Reference**](../agents/README.md)
- [**Skills Catalog**](../skills/README.md)
- [**Rules and Guardrails**](../rules/README.md)
- [**Package Distribution & Updates**](./package-distribution-and-updates.md)
- [**Architecture Overview**](./architecture-mvp-spec.md)
- [**Contributing Guide**](../CONTRIBUTING.md)

---

## 🤝 Open Source and Community-Driven

Open Cloud Agents is built to be a shared engineering resource for teams working at the intersection of AI and cloud operations.

We welcome:
- New agent personas
- Better security and reliability practices
- More cloud skills
- Real-world runbooks
- Contributor improvements

### ⚖️ License & Attribution
- **License:** [Apache License 2.0](../LICENSE)
- **Co-Authorship:** `Co-authored-by: Antigravity <antigravity@google.com>`
- **Founding Architect:** Ibrahim Jimoh ([GitHub](https://github.com/Ibrahimng) | [LinkedIn](https://www.linkedin.com/in/ijimoh))
