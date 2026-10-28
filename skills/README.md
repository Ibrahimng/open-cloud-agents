# Agent Skills Catalog

This directory houses the domain-specific capabilities, operational workflows, and safety guardrails utilized by **Open Cloud Agents**. 

Skills empower autonomous agents with deep procedural knowledge, tool configurations, real-world incident exploration runbooks, and automated verification scripts across Cloud Service Providers (CSPs), Programming Languages, DevOps, Security, Data Science, and Continual Learning.

---

## Skills Taxonomy & Catalog Overview

```text
skills/
├── csp/                        # Cloud Service Providers (The Remix Standard)
│   ├── aws/                    # AWS Well-Architected, Core & Specialized Skills, MCP Plugins
│   ├── azure/                  # Microsoft Azure (193 curated service skills)
│   └── gcp/                    # Google Cloud Platform & GCP Well-Architected Suite
├── programming/                # Language-specific idiomatic patterns & testing
│   ├── dart/                   # Dart 3 & Flutter (FFI native assets, CLI apps, test suites)
│   ├── python/                 # Python 3.11+ (FastAPI REST patterns, pytest async suites)
│   ├── javascript/             # TypeScript & Node.js (Strict discriminated unions, branded types)
│   ├── go/                     # Golang (Structured concurrency, errgroup worker pools)
│   └── java/                   # Java 21+ & Spring Boot (Clean architecture, HikariCP resilience)
├── devops/                     # Infrastructure, Delivery & SRE
│   ├── iac/                    # Terraform / OpenTofu modules & state destruction protection
│   ├── kubernetes/             # Pod triage (CoreDNS throttling outage) & Helm chart scaffold
│   ├── docker/                 # Container hardening & multi-stage minimal runtime builds
│   ├── ci-cd/                  # GitHub Actions OIDC federation & ArgoCD GitOps promotion
│   └── observability/          # OpenTelemetry tracing & PromQL Golden Signals alerting
├── security/                   # Enterprise Governance, SIEM/XDR & Runtime Threat Defense
│   ├── cis-complete-audit/     # 4-layer CIS benchmark auditor (Cloud, K8s, Host, Docker)
│   ├── falco/                  # eBPF runtime threat detection & Falco Talon active response
│   ├── sysdig/                 # CNAPP container drift control & forensic capture trace replay
│   ├── wazuh/                  # Enterprise SIEM/XDR, real-time FIM whodata & active response
│   ├── sentinel/               # Cloud SIEM/SOAR, KQL threat hunting & Logic Apps playbooks
│   ├── cloud-armor-crs-rule-upgrader/ # Cloud Armor OWASP CRS 4.22 migration & preview tuning
│   ├── owasp-llm-security/     # OWASP Top 10 for LLMs prompt injection & output validation
│   ├── compliance/             # CIS benchmarks, SOC 2 evidence & AI governance (ISO 42001/EU AI Act)
│   ├── iam-least-privilege/    # IAM policy synthesizer & Workload Identity federation
│   └── secret-management/      # Git secret leak emergency runbook & KMS envelope encryption
├── data-science/               # Data & Machine Learning Operations
│   ├── mlops/                  # Low-latency model serving with ONNX Runtime & Triton
│   └── data-analysis/          # Analytical SQL & cloud data warehouse optimization
└── continual-learning/         # Self-Knowledge Enhancement Engine
    ├── knowledge-enhancement-loop/       # Live transcript mining & skill auto-patching
    └── incident-postmortem-to-guardrail/ # Converts SRE findings to DevSecOps pre-merge rules
```

---

## 🌐 Global Skill Architecture Design Reference

| Project Architecture Layer | Technical Focus Area | Primary Global Constraints to Track |
|---|---|---|
| **Data Engine** | Data Residency & Privacy | GDPR, CCPA, PIPL, Cross-border transfer rules |
| **Infrastructure Layer** | Technical Controls & IAM | ISO 27001, SOC 2, NIST CSF 2.0, CIS Benchmarks |
| **Financial/Payment Engine** | Transaction Handling | PCI-DSS, DORA, GLBA, SWIFT CSP, APRA |
| **Vendor Matrix** | Supply Chain Security | TPRM, SBOM tracking, Vendor SOC 2 validations |
| **Incident Response Engine** | Breach Notification Timelines | 72-hour counters, statutory templates by jurisdiction |
| **Model/ML Layer** | Algorithmic Integrity | EU AI Act, ISO 42001, NIST AI RMF |

### AI Compliance Integration Matrix

| Framework / Law | Compliance Nature | Core Enforcement Mechanism | Key Metric Your Agent Must Track |
|---|---|---|---|
| **EU AI Act** | Statutory Law | Conformity certifications & massive revenue-based fines | Risk classification tier (High vs. Low) & logging persistence |
| **ISO/IEC 42001** | Voluntary Certification | Independent third-party CPA/ISO audits | Existence of an active Artificial Intelligence Management System (AIMS) |
| **NIST AI RMF** | Operational Blueprint | Enterprise risk management alignment | Continuous measuring of model bias, validity, and explainability |
| **OWASP Top 10 LLM** | Technical Vulnerability | Code scanning, WAF configuration, and edge sanitization | Implementation of prompt sandboxing and LLM output validation |

---

## Anatomy of an Enterprise Skill

Every skill in Open Cloud Agents is a self-contained package adhering to a 3-tier architecture:

```text
<skill-name>/
├── SKILL.md                 # 1. Autonomous instructions, real-life incidents, guardrails
├── references/              # 2. Architecture specs, decision trees, cheat sheets
└── scripts/                 # 3. Executable verification, linting, and recovery tools
```

| Layer | File / Directory | Purpose |
|---|---|---|
| **Instructions** | `SKILL.md` | YAML frontmatter (`name`, `description`) + real-life incident postmortems, live exploration commands, and non-destructive guardrails. |
| **References** | `references/` | Deep documentation: dangerous attribute matrices, OIDC trust specs, PromQL cheat sheets, and RFC envelopes. |
| **Automation** | `scripts/` | Executable Python and Bash scripts (`chmod +x`) with strict exit codes for automated CI/CD verification and incident remediation. |

---

## Core Skills Index

### 1. DevOps & Infrastructure ([`devops/`](./devops/README.md))

| Skill | Highlights | References | Automation Scripts |
|---|---|---|---|
| **[`iac-state-protection`](./devops/iac/iac-state-protection/SKILL.md)** | Prevents `forces replacement` on stateful cloud resources (RDS, Storage, Cosmos DB). | [`dangerous-attributes-matrix.md`](./devops/iac/iac-state-protection/references/dangerous-attributes-matrix.md) | [`verify_state_safety.py`](./devops/iac/iac-state-protection/scripts/verify_state_safety.py) |
| **[`terraform-opentofu-modules`](./devops/iac/terraform-opentofu-modules/SKILL.md)** | Enterprise reusable HCL module layouts and variable validation. | [`hcl-style-guide.md`](./devops/iac/terraform-opentofu-modules/references/hcl-style-guide.md) | [`lint_modules.sh`](./devops/iac/terraform-opentofu-modules/scripts/lint_modules.sh) |
| **[`k8s-pod-troubleshooting`](./devops/kubernetes/k8s-pod-troubleshooting/SKILL.md)** | Diagnoses CrashLoopBackOff, OOMKilled, and CoreDNS throttling outages. | [`k8s-pod-diagnostic-decision-tree.md`](./devops/kubernetes/k8s-pod-troubleshooting/references/k8s-pod-diagnostic-decision-tree.md) | [`pod_diagnose.sh`](./devops/kubernetes/k8s-pod-troubleshooting/scripts/pod_diagnose.sh) |
| **[`helm-chart-scaffold`](./devops/kubernetes/helm-chart-scaffold/SKILL.md)** | Scaffolds hardened charts with securityContext, schemas, and linting. | [`chart-best-practices.md`](./devops/kubernetes/helm-chart-scaffold/references/chart-best-practices.md) | [`validate_chart.sh`](./devops/kubernetes/helm-chart-scaffold/scripts/validate_chart.sh) |
| **[`dockerfile-hardening`](./devops/docker/dockerfile-hardening/SKILL.md)** | Multi-stage builds, non-root users, distroless runtimes, and Trivy CVE scans. | [`container-security-cheat-sheet.md`](./devops/docker/dockerfile-hardening/references/container-security-cheat-sheet.md) | [`audit_dockerfile.py`](./devops/docker/dockerfile-hardening/scripts/audit_dockerfile.py) |
| **[`github-actions-hardening`](./devops/ci-cd/github-actions-hardening/SKILL.md)** | OIDC cloud identity federation, least-privilege tokens, and SHA pinning. | [`oidc-trust-policy-specs.md`](./devops/ci-cd/github-actions-hardening/references/oidc-trust-policy-specs.md) | [`audit_workflows.py`](./devops/ci-cd/github-actions-hardening/scripts/audit_workflows.py) |
| **[`gitops-argocd-promotion`](./devops/ci-cd/gitops-argocd-promotion/SKILL.md)** | Progressive multi-environment promotion (`dev` ➔ `uat` ➔ `prod`) and sync waves. | [`argocd-sync-waves.md`](./devops/ci-cd/gitops-argocd-promotion/references/argocd-sync-waves.md) | [`promote_environment.sh`](./devops/ci-cd/gitops-argocd-promotion/scripts/promote_environment.sh) |
| **[`promql-golden-signals`](./devops/observability/promql-golden-signals/SKILL.md)** | Queries for Latency, Traffic, Errors, Saturation, and multi-window burn rates. | [`golden-signals-reference.md`](./devops/observability/promql-golden-signals/references/golden-signals-reference.md) | [`evaluate_slo_burn.py`](./devops/observability/promql-golden-signals/scripts/evaluate_slo_burn.py) |
| **[`opentelemetry-instrumentation`](./devops/observability/opentelemetry-instrumentation/SKILL.md)** | W3C distributed trace propagation and OTLP exporter setup. | [`semantic-conventions-cheatsheet.md`](./devops/observability/opentelemetry-instrumentation/references/semantic-conventions-cheatsheet.md) | [`verify_otel_endpoint.py`](./devops/observability/opentelemetry-instrumentation/scripts/verify_otel_endpoint.py) |

---

### 2. Security & Governance ([`security/`](./security/README.md))

| Skill | Highlights | References | Automation Scripts |
|---|---|---|---|
| **[`cis-benchmark-audit`](./security/compliance/cis-benchmark-audit/SKILL.md)** | Audits cloud environments against CIS Foundation benchmarks. | [`cis-control-mappings.md`](./security/compliance/cis-benchmark-audit/references/cis-control-mappings.md) | [`audit_cis_foundations.sh`](./security/compliance/cis-benchmark-audit/scripts/audit_cis_foundations.sh) |
| **[`soc2-evidence-collector`](./security/compliance/soc2-evidence-collector/SKILL.md)** | Automates gathering of technical evidence for CC6.1-CC8.1 audit criteria. | [`soc2-type2-evidence-matrix.md`](./security/compliance/soc2-evidence-collector/references/soc2-type2-evidence-matrix.md) | [`collect_soc2_evidence.py`](./security/compliance/soc2-evidence-collector/scripts/collect_soc2_evidence.py) |
| **[`iam-policy-synthesizer`](./security/iam-least-privilege/iam-policy-synthesizer/SKILL.md)** | Transforms wildcard `*:*` permissions into scoped ARNs with HTTPS condition keys. | [`iam-condition-keys-cheatsheet.md`](./security/iam-least-privilege/iam-policy-synthesizer/references/iam-condition-keys-cheatsheet.md) | [`synthesize_least_privilege.py`](./security/iam-least-privilege/iam-policy-synthesizer/scripts/synthesize_least_privilege.py) |
| **[`workload-identity-federation`](./security/iam-least-privilege/workload-identity-federation/SKILL.md)** | Eliminates static cloud keys via OIDC and Kubernetes IRSA tokens. | [`federation-architecture-specs.md`](./security/iam-least-privilege/workload-identity-federation/references/federation-architecture-specs.md) | [`validate_oidc_token.sh`](./security/iam-least-privilege/workload-identity-federation/scripts/validate_oidc_token.sh) |
| **[`git-secret-leak-remediation`](./security/secret-management/git-secret-leak-remediation/SKILL.md)** | Emergency response runbook: revoke ➔ rotate ➔ scrub with `git-filter-repo`. | [`secret-revocation-endpoints.md`](./security/secret-management/git-secret-leak-remediation/references/secret-revocation-endpoints.md) | [`emergency_secret_scrub.sh`](./security/secret-management/git-secret-leak-remediation/scripts/emergency_secret_scrub.sh) |
| **[`kms-envelope-encryption`](./security/secret-management/kms-envelope-encryption/SKILL.md)** | High-performance client-side payload encryption with KMS CMKs and DEKs. | [`envelope-encryption-spec.md`](./security/secret-management/kms-envelope-encryption/references/envelope-encryption-spec.md) | [`envelope_encrypt.py`](./security/secret-management/kms-envelope-encryption/scripts/envelope_encrypt.py) |

---

### 3. Programming Languages ([`programming/`](./programming/README.md))

| Language | Key Skills | References | Automation Scripts |
|---|---|---|---|
| **Dart / Flutter** | 11 production skills (unit testing, FFI native assets, CLI apps, pattern matching) | Integrated in [`dart/`](./programming/dart/README.md) | Built-in test runners & hot reload |
| **Python** | [`fastapi-rest-patterns`](./programming/python/fastapi-rest-patterns/SKILL.md) & [`pytest-test-suite`](./programming/python/pytest-test-suite/SKILL.md) | [`fastapi-production-spec.md`](./programming/python/fastapi-rest-patterns/references/fastapi-production-spec.md) | [`benchmark_api.py`](./programming/python/fastapi-rest-patterns/scripts/benchmark_api.py) & [`run_coverage_gate.sh`](./programming/python/pytest-test-suite/scripts/run_coverage_gate.sh) |
| **JavaScript / TS** | [`typescript-strict-patterns`](./programming/javascript/typescript-strict-patterns/SKILL.md) | [`ts-strict-cheatsheet.md`](./programming/javascript/typescript-strict-patterns/references/ts-strict-cheatsheet.md) | [`typecheck_project.sh`](./programming/javascript/typescript-strict-patterns/scripts/typecheck_project.sh) |
| **Go** | [`go-concurrency-patterns`](./programming/go/go-concurrency-patterns/SKILL.md) | [`go-concurrency-cheatsheet.md`](./programming/go/go-concurrency-patterns/references/go-concurrency-cheatsheet.md) | [`race_detector_runner.sh`](./programming/go/go-concurrency-patterns/scripts/race_detector_runner.sh) |
| **Java** | [`spring-boot-architecture`](./programming/java/spring-boot-architecture/SKILL.md) | [`hikaricp-tuning-cheatsheet.md`](./programming/java/spring-boot-architecture/references/hikaricp-tuning-cheatsheet.md) | [`analyze_thread_dump.py`](./programming/java/spring-boot-architecture/scripts/analyze_thread_dump.py) |

---

### 4. Continual Learning & Data Science

| Domain | Skill | References | Automation Scripts |
|---|---|---|---|
| **Continual Learning** | [`knowledge-enhancement-loop`](./continual-learning/knowledge-enhancement-loop/SKILL.md) | [`knowledge-patch-schema.md`](./continual-learning/knowledge-enhancement-loop/references/knowledge-patch-schema.md) | [`transcript_knowledge_miner.py`](./continual-learning/knowledge-enhancement-loop/scripts/transcript_knowledge_miner.py) |
| **Continual Learning** | [`incident-postmortem-to-guardrail`](./continual-learning/incident-postmortem-to-guardrail/SKILL.md) | [`pir-to-policy-mapping.md`](./continual-learning/incident-postmortem-to-guardrail/references/pir-to-policy-mapping.md) | [`generate_rego_guardrail.py`](./continual-learning/incident-postmortem-to-guardrail/scripts/generate_rego_guardrail.py) |
| **FinOps & Cost Optimization** | [`cloud-waste-reaper`](./finops/cloud-waste-reaper/SKILL.md) | [`waste-matrix.md`](./finops/cloud-waste-reaper/references/waste-matrix.md) | [`reap_cloud_waste.sh`](./finops/cloud-waste-reaper/scripts/reap_cloud_waste.sh) |
| **Data Science / MLOps** | [`model-serving-fastapi-triton`](./data-science/mlops/model-serving-fastapi-triton/SKILL.md) | [`onnx-triton-deployment-spec.md`](./data-science/mlops/model-serving-fastapi-triton/references/onnx-triton-deployment-spec.md) | [`benchmark_inference.py`](./data-science/mlops/model-serving-fastapi-triton/scripts/benchmark_inference.py) |
| **Data Science / Analytics** | [`sql-warehouse-optimization`](./data-science/data-analysis/sql-warehouse-optimization/SKILL.md) | [`bigquery-snowflake-tuning-guide.md`](./data-science/data-analysis/sql-warehouse-optimization/references/bigquery-snowflake-tuning-guide.md) | [`profile_sql_query.py`](./data-science/data-analysis/sql-warehouse-optimization/scripts/profile_sql_query.py) |

---

## Cloud Service Providers ([`csp/`](./csp/README.md))

The CSP skills represent our curated **Remix Standard** across:
* **[`skills/csp/aws/`](./csp/aws/README.md):** Amazon Bedrock, IAM, CDK, CloudFormation, Aurora, and DevSecOps MCP plugins.
* **[`skills/csp/azure/`](./csp/azure/README.md):** 193 production-ready skills for Azure App Service, AKS, Cosmos DB, Entra ID, and VNets.
* **[`skills/csp/gcp/`](./csp/gcp/README.md):** 34 production-ready skills for GKE, Cloud Run, BigQuery, AlloyDB, and the Google Cloud Well-Architected Framework.

---

## Authoring New Skills

All community contributions must follow the 3-tier structure (`SKILL.md`, `references/`, `scripts/`).

### Frontmatter Template
```markdown
---
name: my-skill-name
description: A concise 1-2 sentence description explaining the purpose of the skill and when agents should trigger it.
---

# Title

## Purpose & Scope
When and why an autonomous agent should activate this skill.

## Real-Life Incident / Live Exploration Protocol
Battle-tested production scenarios and exact terminal exploration commands.

## Step-by-Step Procedural Workflow
Checklist and sequential instructions for the agent.

## Non-Destructive Guardrails & Safety
Explicit boundaries preventing unauthorized data destruction or security drift.

## Continuous Self-Knowledge Enhancement Loop
How the agent captures novel edge cases and updates repository knowledge.
```
