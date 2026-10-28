# Security, Governance & Threat Defense Skills

Curated agent skills for enterprise security posture management, regulatory compliance, cloud workload protection, and real-time threat detection & autonomous prevention.

## Subdomains & Enterprise Defense Skills
- [`compliance/`](./compliance/): CIS Benchmarks, SOC 2 Type II, ISO 27001, ISO 42001, EU AI Act, and NIST frameworks.
  - [`compliance/ai-governance-audit/`](./compliance/ai-governance-audit/): Artificial Intelligence Management System (ISO/IEC 42001:2023), EU AI Act (Regulation EU 2024/1689), data provenance (B.9.2), automated logging verification, and edge WAF injection defenses.
- [`owasp-llm-security/`](./owasp-llm-security/): Application security, prompt injection defense (LLM01), insecure output validation (LLM02), prompt sandboxing, and edge WAF filtering for LLM gateways and agent workflows.
- [`cis-complete-audit/`](./cis-complete-audit/): Comprehensive 4-layer Center for Internet Security (CIS) compliance auditing, scoring, automated drift detection, and remediation across Cloud Foundations (AWS, Azure, GCP), Kubernetes, Linux Hosts, and Docker Containers.
- [`falco/`](./falco/): CNCF graduated eBPF kernel runtime security, syscall behavioral monitoring, declarative rule authoring, and real-time threat prevention via Falco Talon and container isolation.
- [`sysdig/`](./sysdig/): Cloud Native Application Protection Platform (CNAPP), Sysdig Secure & OSS syscall tracing, container runtime drift control, image vulnerability gatekeeping, and automated incident capture forensics.
- [`wazuh/`](./wazuh/): Enterprise open-source SIEM and XDR, real-time File Integrity Monitoring (FIM / `syscheck`), Security Configuration Assessment (SCA), log decoders, and autonomous Active Response threat containment.
- [`sentinel/`](./sentinel/): Cloud-native SIEM and SOAR engineering for Microsoft Sentinel: multi-cloud log ingestion, advanced KQL threat hunting, analytical rule authoring, automated SOAR incident response playbooks, and UEBA entity analytics.
- [`iam-least-privilege/`](./iam-least-privilege/): Zero-trust identity architecture, service account hardening, and SCPs/Permission Boundaries.
- [`secret-management/`](./secret-management/): KMS envelope encryption, HashiCorp Vault, cloud secrets rotation, and SOPS.
- [`cloud-armor-crs-rule-upgrader/`](./cloud-armor-crs-rule-upgrader/): Automated Google Cloud Armor OWASP CRS 3.0/3.3 to CRS 4.22 policy migration, sensitivity tuning, and preview-mode cutover.

---

## Core Structural Reference Matrix

This table details the exact files within the workspace where reference standards are parsed to drive active agent decisions:

| Active Skill Folder | Reference Documentation File | Primary Script Consumer | Automated Security Function |
|---|---|---|---|
| [`compliance/ai-governance-audit/`](./compliance/ai-governance-audit/SKILL.md) | [`iso-42001-aims-matrix.md`](./compliance/ai-governance-audit/references/iso-42001-aims-matrix.md) | [`verify_ai_lineage.py`](./compliance/ai-governance-audit/scripts/verify_ai_lineage.py) | Validates data manifest formats against compliance metrics |
| [`owasp-llm-security/`](./owasp-llm-security/SKILL.md) | [`llm-vulnerability-vectors.md`](./owasp-llm-security/references/llm-vulnerability-vectors.md) | [`scan_prompt_injection.py`](./owasp-llm-security/scripts/scan_prompt_injection.py) | Updates regex pattern profiles with known injection signatures |
| [`owasp-llm-security/`](./owasp-llm-security/SKILL.md) | [`llm-vulnerability-vectors.md`](./owasp-llm-security/references/llm-vulnerability-vectors.md) | [`validate_llm_outputs.sh`](./owasp-llm-security/scripts/validate_llm_outputs.sh) | Sets grep verification blocks for malicious output strings |
| [`cloud-armor-crs-rule-upgrader/`](./cloud-armor-crs-rule-upgrader/SKILL.md) | [`crs-422-sensitivity-matrix.md`](./cloud-armor-crs-rule-upgrader/references/crs-422-sensitivity-matrix.md) | [`upgrade_policy.py`](./cloud-armor-crs-rule-upgrader/scripts/upgrade_policy.py) | Upgrades Cloud Armor policies to OWASP ModSecurity CRS 4.22 |
| [`compliance/soc2-evidence-collector/`](./compliance/soc2-evidence-collector/SKILL.md) | [`soc2-trust-criteria-matrix.md`](./compliance/soc2-evidence-collector/references/soc2-trust-criteria-matrix.md) | [`collect_soc2_evidence.py`](./compliance/soc2-evidence-collector/scripts/collect_soc2_evidence.py) | Collects automated multi-cloud AICPA SOC 2 Type II audit evidence |
