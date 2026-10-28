# ISO/IEC 42001:2023 Artificial Intelligence Management System (AIMS) Matrix

ISO/IEC 42001 is the international standard specifying requirements and guidance for establishing, implementing, maintaining, and continually improving an Artificial Intelligence Management System (AIMS). It provides a structured governance framework for managing AI-related risks, ethical concerns, data provenance, and continuous accountability.

---

## 1. High-Level Management System Structure (Clauses 4–10)

| Clause | Name | Objective | Cloud / GitOps Implementation |
|---|---|---|---|
| **Clause 4** | Context of the Organization | Identify internal/external stakeholders, legal requirements, and AIMS boundaries. | Documented in `docs/compliance/aims-scope.md`; maps Vertex AI, SageMaker, and Bedrock tenants. |
| **Clause 5** | Leadership & Commitment | Executive responsibility, AI Ethics Board oversight, and AI Policy endorsement. | Signed AI Policy published in repo root; AI governance review committee integrated in pull requests. |
| **Clause 6** | Planning & Risk Assessment | Systematic identification of AI risks (bias, safety, hallucination, data poisoning). | Continuous AI Risk Registry maintained in GitOps manifests; threat modeling in PR gatekeepers. |
| **Clause 7** | Support & Resources | Competence, awareness, communication, and documented information control. | Automated artifact versioning, training records, and cryptographically verified pipelines. |
| **Clause 8** | Operation | AI system design, life cycle management, and third-party risk controls. | Pre-deployment model evaluation gates, dataset lineage checks, and CI/CD verification harnesses. |
| **Clause 9** | Performance Evaluation | Monitoring, measurement, internal audits, and management review of AI KPIs. | Automated metric streaming (latency, drift, toxicity, override drops) to SIEM / CloudWatch. |
| **Clause 10** | Improvement | Nonconformity management, blameless root-cause analysis, and continual learning. | Continuous integration into SRE incident response postmortems and `AGENTS.md` learned facts. |

---

## 2. Annex A & B Control Implementation Matrix

Annex B provides detailed guidance for controls organized across 38 specific control areas. The primary controls critical for Cloud Architecture and DevSecOps include:

### Domain B.2: AI Policy & Objectives
- **B.2.1 AI Policy:** An approved policy defining organizational principles for responsible AI development, human-centric design, and risk tolerance thresholds.
- **B.2.2 Alignment with Business Objectives:** Mapping model utility to enterprise governance, data protection regulations (GDPR/CCPA), and zero-trust security.

### Domain B.4: AI Impact Assessment
- **B.4.1 Assessing AI System Impacts:** Pre-deployment algorithmic impact assessment (AIA) evaluating potential harm to individuals, protected groups, privacy, and systemic reliability.
- **B.4.2 Continuous Assessment:** Re-evaluating impact whenever model weights, prompt templates, or underlying training corpora undergo major version bumps.

### Domain B.5: AI System Life Cycle
- **B.5.2 System Requirements:** Specification of accuracy, robustness, fairness, explainability, and cybersecurity requirements before engineering starts.
- **B.5.5 System Verification & Validation:** Formal benchmarking using automated evaluation harnesses (e.g. ROUGE, BLEU, Toxicity benchmarks, prompt injection adversarial suites).
- **B.5.7 Deployment Controls:** Blue/green canary rollouts with automated kill-switches and edge WAF inspection layers.

### Domain B.6: Data for AI Systems
- **B.6.1 Data Acquisition & Quality:** Data quality metrics (completeness, accuracy, representativeness) validated before training ingestion.
- **B.6.2 Data Provenance & Lineage (CRITICAL - Control B.9.2):**
  - All training corpora must possess immutable SHA-256 hashes.
  - S3 / GCS buckets must enforce versioning, KMS SSE, and object-lock retention policies.
  - Ingestion manifests must track data origin, license metadata, scraping timestamps, and preprocessing steps.

### Domain B.7: Information for Interested Parties & Transparency
- **B.7.1 System Documentation:** Model Cards detailing model architecture, parameter count, intended use, limitations, benchmark metrics, and out-of-scope tasks.
- **B.7.2 Transparency & Explainability:** Providing end-users with notifications that they are interacting with an AI system; clear attribution of synthetic outputs.

### Domain B.8: Human Oversight & Operational Use
- **B.8.2 Human-in-the-Loop (HITL):** High-stakes operational actions (financial transfers, privilege escalations, database deletions) cannot be executed autonomously without human confirmation.
- **B.8.4 Operational Monitoring:** Real-time tracking of concept drift, data drift, anomalous token consumption, and edge filtering hits.

### Domain B.9: Third-Party & Supply Chain Risk
- **B.9.1 Third-Party Model Providers:** Risk vetting for foundation model APIs (OpenAI, Anthropic, Google Cloud Vertex AI, AWS Bedrock) regarding data retention and model weight provenance.
- **B.9.2 Data Lineage in Supply Chains:** Enforcing signed SBOMs and cryptographic lineage on fine-tuning weights and RAG vector embeddings.

### Domain B.10: Continuous Monitoring & Incident Response
- **B.10.1 Logging & Audit Trails:** Immutable inference logs capturing prompt hashes, response hashes, model version, temperature, and latency.
- **B.10.2 AI Incident Response:** Automated isolation of compromised models upon detection of prompt injection, data exfiltration, or malicious weight perturbation.

---

## 3. Auditor-Ready Evidence Collection Checklist

| ISO 42001 Control | Required Audit Artifact | Target Cloud / Repository Location | Verification Method |
|---|---|---|---|
| **B.4.1** | AI Impact Assessment Document | `docs/compliance/impact-assessment.md` | PR manual sign-off by Ethics Board |
| **B.5.5** | Automated Evaluation Test Report | `tests/evaluations/report.json` | CI test suite exit code 0 |
| **B.6.2 / B.9.2** | Cryptographic Dataset Manifest | `pipelines/train_v2.json` | `python3 verify_ai_lineage.py --manifest ...` |
| **B.7.1** | Standardized Model Card | `models/<model-id>/MODEL_CARD.md` | Automated Markdown schema check |
| **B.8.2** | Human-in-the-Loop Sign-off Gate | GitHub PR review / Cloud Deploy Approval | Audit log of human user approval |
| **B.10.1** | Immutable Inference Logging | Cloud Storage / BigQuery write-once table | KMS key policy & bucket lock inspection |
