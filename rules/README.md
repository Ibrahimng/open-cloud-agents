# 📜 Open Cloud Agents: Rule Governance & Operational Invariants

Welcome to the **Rule Governance Specification** for Open Cloud Agents.

Rules represent **non-negotiable system invariants and behavioral guardrails** that apply across all 7 specialist agents, AI models, and human contributors.

---

## The Three Pillars of Open Cloud Agents

```text
┌────────────────────────────────────────────────────────┐
│                   Open Cloud Agents                    │
├─────────────────┬──────────────────┬───────────────────┤
│   1. PERSONAS   │    2. SKILLS     │     3. RULES      │
│    (agents/)    │    (skills/)     │     (rules/)      │
│   WHO does it   │   HOW it's done  │  WHAT IS FORBIDDEN│
│  Role & Mandate │ Runbooks/Scripts │ Inviolable Guards │
└─────────────────┴──────────────────┴───────────────────┘
```

1. **Personas ([`agents/`](../agents/README.md)):** Define operational roles, cognitive scopes, and handoff contracts.
2. **Skills ([`skills/`](../skills/README.md)):** Provide procedural runbooks, API references, and automated verification scripts.
3. **Rules ([`rules/`](./README.md)):** Enforce strict safety boundaries, preventing catastrophic state loss, data corruption, and security breaches.

---

## Core Rule Catalog

| Rule File | Name | Mandate | Enforcement Level |
|---|---|---|---|
| [**`01-destructive-actions.md`**](./01-destructive-actions.md) | **Zero Unplanned Destruction** | Bans irreversible data deletion (`DROP`, `TRUNCATE`, `rm -rf`, and IaC `forces replacement`) without explicit human confirmation. | **BLOCKING / MANDATORY** |
| [**`02-secrets-and-identity.md`**](./02-secrets-and-identity.md) | **Zero-Trust Identity & Secrets** | Zero plaintext tokens, API keys, or private keys. Enforces KMS encryption, short-lived OIDC tokens, and log redaction. | **BLOCKING / MANDATORY** |
| [**`03-surgical-scope-discipline.md`**](./03-surgical-scope-discipline.md) | **Surgical Scope & Non-Interference** | Prohibits unasked refactoring, formatting sweeps, or dependency changes outside the active user prompt. | **STRICT BEHAVIORAL** |
| [**`04-cloud-well-architected-invariants.md`**](./04-cloud-well-architected-invariants.md) | **Well-Architected Defaults** | Mandates multi-AZ/multi-region DR targets (RTO/RPO), IAM least privilege, and TLS 1.3/KMS encryption defaults. | **ARCHITECTURAL STANDARD** |
| [**`05-repository-and-path-hygiene.md`**](./05-repository-and-path-hygiene.md) | **Path & Link Sanitization** | Forbids leaking local workstation paths (`/Users/<name>/`) and mandates relative links for multi-agent interoperability. | **CI VERIFIED** |

---

## How AI Agents Ingest These Rules

- **Native Agent Runtimes (Antigravity / Gemini / Claude Code / Cline):** Automatically read and enforce [`AGENTS.md`](../AGENTS.md) at the repository root.
- **Cursor / VS Code:** Configured via [`.cursorrules`](../.cursorrules) to reference the canonical `rules/` directory.
- **CI Enforcement:** The automated GitHub Actions CI pipeline ([`.github/workflows/autonomous-gatekeeper.yml`](../.github/workflows/autonomous-gatekeeper.yml)) tests all commits against these rules.

