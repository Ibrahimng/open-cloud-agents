# EU AI Act (Regulation EU 2024/1689) Technical Conformity Guide

The European Union Artificial Intelligence Act (EU AI Act) is the world's first comprehensive horizontal legal framework for artificial intelligence. It establishes harmonized rules for the development, placing on the market, putting into service, and use of AI systems in the Union, backed by severe administrative fines (up to €35,000,000 or 7% of total worldwide annual turnover).

---

## 1. 4-Tier Risk Categorization Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Tier 1: Unacceptable Risk (Prohibited - Art. 5)             │
│  Social scoring, cognitive manipulation, untargeted scrape  │
└──────────────────────────────┬──────────────────────────────┘
                               │ Prohibited completely
┌──────────────────────────────▼──────────────────────────────┐
│  Tier 2: High Risk (Annex I & Annex III - Arts. 6-15)        │
│  Critical infra, employment, credit scoring, biometrics     │
└──────────────────────────────┬──────────────────────────────┘
                               │ Mandatory Conformity & CE Mark
┌──────────────────────────────▼──────────────────────────────┐
│  Tier 3: Specific Transparency Risk (Art. 50)               │
│  Chatbots, deepfakes, emotion recognition, synthetic content│
└──────────────────────────────┬──────────────────────────────┘
                               │ Clear disclosure & watermarking
┌──────────────────────────────▼──────────────────────────────┐
│  Tier 4: Minimal / Low Risk (General Purpose AI / Tools)    │
│  Spam filters, coding assistants, video games               │
└─────────────────────────────────────────────────────────────┘
                                 Voluntary codes of conduct
```

### Prohibited AI Practices (Article 5)
1. **Subliminal or manipulative techniques** distorting behavior to cause significant harm.
2. **Exploitation of vulnerabilities** (age, disability, socio-economic situation).
3. **Biometric categorization** deducing race, political opinions, trade union membership, religious beliefs, or sexual orientation.
4. **Social scoring** leading to detrimental or unfavorable treatment across unrelated contexts.
5. **Untargeted scraping of facial images** from the internet or CCTV footage to build facial recognition databases.

---

## 2. Mandatory Technical Requirements for High-Risk Systems (Articles 8–15)

High-Risk AI systems (deployments in critical infrastructure, access to education, recruitment/HR, creditworthiness, law enforcement, border control) must satisfy strict requirements before entering service:

| Article | Statutory Mandate | Engineering & Technical Implementation |
|---|---|---|
| **Article 9** | **Risk Management System** | Continuous identification, estimation, and mitigation of risks throughout the AI system lifecycle. Documented in IaC risk policies and PR review matrices. |
| **Article 10** | **Data & Data Governance** | Training, validation, and testing datasets must be subject to data governance: lineage tracking, representation bias assessment, and cryptographic SHA-256 integrity verification. |
| **Article 11** | **Technical Documentation** | Detailed documentation per Annex IV (system architecture, design choices, algorithmic parameters, training methodology) maintained under Git version control. |
| **Article 12** | **Record-Keeping & Automated Logging** | AI systems must automatically log events over their operational lifetime. High-Risk logs must capture inference timestamps, input/output hashes, monitoring metrics, and operator interventions, retained for minimum statutory periods (e.g., 6 months). |
| **Article 13** | **Transparency & User Guidance** | Deployers must receive clear technical instructions: capabilities, known limitations, input specifications, and performance metrics. |
| **Article 14** | **Human Oversight** | Systems must enable human operators to understand outputs, remain aware of automation bias, and intervene via an emergency manual stop / override switch. |
| **Article 15** | **Accuracy, Robustness & Cybersecurity** | Systems must remain resilient against errors, adversarial prompt injection (OWASP LLM01), data poisoning, and model evasion. Must maintain automated write-once logging to Google Cloud SCC / AWS Security Hub. |

---

## 3. General-Purpose AI (GPAI) Models (Articles 51–56)

Providers of general-purpose AI models (including foundation LLMs) must:
1. Maintain comprehensive technical documentation, including training and testing processes.
2. Make information available to downstream providers who integrate the model into AI systems.
3. Establish a copyright compliance policy respecting EU copyright law.
4. Publish a sufficiently detailed summary about the content used for training the model.
5. **Systemic Risk Classification (Art. 51):** Models trained with cumulative compute > $10^{25}$ FLOPs are subject to additional obligations: adversarial testing, model evaluation, and reporting serious incidents to the EU AI Office.

---

## 4. Technical Conformity Assessment Checklist

```bash
# Automated verification workflow for CI/CD gates
1. Check dataset lineage and cryptographic verification:
   python3 skills/security/compliance/ai-governance-audit/scripts/verify_ai_lineage.py --manifest pipelines/train_v2.json --strict

2. Verify prompt injection edge defenses:
   python3 skills/security/owasp-llm-security/scripts/scan_prompt_injection.py --input "$PROMPT_PAYLOAD"

3. Verify output validation and escaping:
   bash skills/security/owasp-llm-security/scripts/validate_llm_outputs.sh --input "$MODEL_RESPONSE" --check-sql --check-cmd

4. Ensure immutable write-once logging is enabled:
   Verify deploy/gcp-vertex-infra.tf contains object lock / Cloud Storage retention_policy blocks.
```
