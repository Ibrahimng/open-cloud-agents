---
name: model-designer
description: Use this skill to create advance models for Automations.
environments:
  - local
  - remote
  - any
---

# Advance Model Designer Automation (Interactive)

## Purpose
This skill defines standards for building software and AI systems with strong engineering discipline and strict cybersecurity controls. It applies to coding, AI, machine learning, generative AI, and agentic systems.

## Scope
This policy applies to:
- Application code, scripts, APIs, services, and infrastructure-as-code.
- Data pipelines, ML training workflows, model serving, and evaluation.
- Generative AI features such as prompting, retrieval, summarization, and content generation.
- Agentic systems that plan, call tools, access data, take actions, or operate with partial autonomy.
- Human and automated contributors, including developers, reviewers, operators, and AI assistants.

## Core Engineering Standards
- Write clear, modular, testable code with small functions and explicit interfaces.
- Prefer secure defaults over convenience.
- Use version control for all changes; no direct edits in production.
- Require peer review for all non-trivial changes.
- Enforce linting, formatting, dependency checks, unit tests, and static analysis in CI.
- Document architecture decisions, assumptions, risks, and rollback steps.
- Keep secrets out of source code, logs, prompts, notebooks, and tickets.
- Minimize complexity; remove dead code and unused dependencies.

## Coding Policy
### Required
- Validate all inputs at trust boundaries.
- Use parameterized queries and safe ORM patterns.
- Encode outputs for their destination context, including HTML, SQL, shell, and URLs.
- Handle errors safely; fail closed when security controls are uncertain.
- Use typed interfaces where practical.
- Add tests for security-sensitive logic and edge cases.
- Apply least privilege to service accounts, tokens, and runtime permissions.

### Prohibited
- Hardcoded secrets, API keys, tokens, credentials, or private certificates.
- Dynamic code execution from untrusted input.
- Unsafe deserialization of untrusted data.
- Blind shell execution with user-controlled arguments.
- Disabling TLS verification in any environment except isolated local debugging with explicit approval.
- Copying production data into local, test, or third-party environments without authorization and sanitization.

## AI and ML Policy
### Data Governance
- Use only approved datasets with defined ownership, lawful basis, and retention rules.
- Classify data before use: public, internal, confidential, restricted.
- Minimize personal data and sensitive attributes; prefer anonymization or pseudonymization.
- Track dataset lineage, consent constraints, transformations, and access history.

### Model Development
- Define objective, success metrics, failure modes, and misuse cases before training.
- Version datasets, features, prompts, models, and evaluation results.
- Evaluate accuracy, robustness, drift, bias, privacy exposure, and security risks before release.
- Do not deploy models without documented fallback behavior and rollback criteria.
- Require human review for high-impact decisions affecting finance, employment, health, safety, identity, or legal status.

### Model Operations
- Monitor for drift, prompt abuse, abnormal tool usage, exfiltration signals, and unsafe outputs.
- Log security-relevant events without storing secrets or unnecessary personal data.
- Restrict model access by role, environment, and approved use case.
- Revoke or rotate credentials immediately after suspected compromise.

## Generative AI Policy
### Prompt and Context Safety
- Treat prompts, system instructions, memory, retrieved documents, and tool outputs as security-relevant inputs.
- Sanitize retrieved and user-supplied content before passing it to downstream tools or execution environments.
- Prevent prompt injection by isolating instructions from untrusted content and explicitly defining tool-use rules.
- Do not expose hidden prompts, internal policies, credentials, private documents, or security controls in outputs.

### Output Safety
- Validate generated code, queries, commands, and configuration before execution or merge.
- Require deterministic checks for high-risk actions such as file deletion, privilege changes, payments, or external publishing.
- Label AI-generated content where policy or regulation requires it.
- Block generation of malware, credential theft, exploit payloads, unauthorized surveillance, or harmful evasion techniques.

## Agentic Systems Policy
### Authorization
- Agents must operate with explicit scopes, bounded objectives, time limits, and tool allowlists.
- Every tool call must be attributable to an authenticated identity and a logged decision context.
- Agents may only access the minimum data and capabilities required for the task.

### Execution Controls
- Require confirmation gates for destructive, irreversible, regulated, or externally visible actions.
- Enforce rate limits, budget limits, network restrictions, and recursion limits.
- Sandbox code execution, file handling, browsing, and model-to-tool actions.
- Deny self-modification, policy modification, or privilege escalation unless explicitly approved through a separate secure workflow.

### Human Oversight
- Human approval is mandatory for production changes, secrets access, customer-impacting actions, and policy exceptions.
- Operators must be able to interrupt, audit, and shut down any agent session.
- Incidents involving autonomous behavior require post-incident review and updated controls.

## Cybersecurity Policy
### Identity and Access
- Enforce SSO, MFA, strong session management, and least privilege.
- Use short-lived credentials wherever possible.
- Review access regularly and remove stale accounts immediately.
- Separate duties for development, deployment, approval, and audit.

### Secrets Management
- Store secrets only in approved secret managers.
- Rotate secrets on schedule and after any suspected exposure.
- Never log secrets or include them in prompts, screenshots, exports, or crash dumps.
- Use separate secrets per environment and service.

### Secure Development Lifecycle
- Maintain threat models for critical systems and update them when architecture changes.
- Run SAST, DAST, dependency scanning, container scanning, and IaC scanning in CI/CD.
- Patch critical vulnerabilities on an emergency timeline.
- Block releases with unresolved critical security findings unless formally accepted by authorized risk owners.

### Infrastructure and Network
- Segment environments and isolate production from development and experimentation.
- Use default-deny network policies and explicit egress controls.
- Encrypt data in transit and at rest using approved algorithms and managed keys.
- Keep audit logs tamper-resistant and time-synchronized.

### Application Security
- Protect against OWASP Top 10 classes, including injection, broken access control, SSRF, insecure deserialization, and security misconfiguration.
- Apply CSRF, CORS, CSP, and secure cookie controls where applicable.
- Rate-limit authentication and sensitive endpoints.
- Verify uploads by type, size, malware scanning, and storage isolation.

### AI-Specific Security
- Defend against prompt injection, data poisoning, model theft, training data extraction, jailbreaks, and indirect prompt attacks.
- Restrict retrieval sources and verify external content before grounding model outputs.
- Separate public inference from internal administration paths.
- Test agents and LLM applications against adversarial inputs before release.

## Logging, Monitoring, and Incident Response
- Log authentication events, privilege changes, tool invocations, policy decisions, model routing, and security exceptions.
- Alert on anomalous access, excessive failures, unusual exports, policy bypass attempts, and agent loop behavior.
- Maintain incident runbooks for credential leaks, data exfiltration, model abuse, supply-chain compromise, and unsafe autonomous actions.
- Preserve forensic evidence and notify stakeholders according to severity and legal obligations.

## Third-Party and Supply Chain Controls
- Approve external libraries, models, datasets, plugins, and SaaS providers before use.
- Pin dependency versions and verify provenance where possible.
- Review licenses, security posture, data handling, and subprocessor exposure.
- Disable unused packages, extensions, integrations, and model tools.

## Privacy and Compliance
- Follow applicable privacy, security, and sector regulations.
- Collect the minimum data required and define retention and deletion rules.
- Support subject rights and auditability where legally required.
- Complete security and privacy review before introducing new high-risk processing.

## Review and Governance
- Review this skill at least quarterly and after major incidents or architectural changes.
- Exceptions must be documented, time-bound, risk-assessed, and approved by security leadership.
- Non-compliance may block deployment, revoke access, or trigger incident handling.

## Enforcement Checklist
- No secrets in code, prompts, logs, or tickets.
- No unreviewed production changes.
- No unscoped autonomous agents.
- No model or agent deployment without evaluation, monitoring, and rollback.
- No access beyond least privilege.
- No exceptions without written approval.

## Common Patterns

### Pattern: Input to Model to Action
Use this pattern when an automation receives structured or unstructured input, transforms it into a validated model decision, and then triggers a bounded action.

- Ingest data through validated interfaces only.
- Normalize and classify the input before model use.
- Run policy checks before any tool call or external action.
- Produce a typed result with confidence, rationale, and next-step status.
- Require approval for destructive, regulated, or customer-visible actions.

### Pattern: Retrieval-Augmented Automation
Use this pattern when the model needs current documents, internal procedures, or domain knowledge.

- Restrict retrieval to approved sources.
- Sanitize retrieved content before injecting it into prompts.
- Separate untrusted document content from system instructions.
- Attach provenance metadata to outputs.
- Reject actions when supporting evidence is missing or conflicting.

### Pattern: Human-in-the-Loop Escalation
Use this pattern for high-risk workflows, ambiguous model outcomes, or exception handling.

- Define confidence thresholds for automatic escalation.
- Present a concise summary, evidence, and proposed action to the reviewer.
- Log reviewer identity, decision, and timestamp.
- Resume automation only within the approved scope.

### Pattern: Multi-Step Agent Workflow
Use this pattern when an agent must plan, evaluate, call tools, and adapt.

- Limit the number of steps, tools, and retries.
- Require explicit state tracking between steps.
- Validate every intermediate result before continuing.
- Stop on policy violations, missing prerequisites, or loop behavior.
- Preserve a full audit trail for every decision and action.

### Pattern: Safe Code Generation
Use this pattern when the model drafts scripts, queries, or infrastructure changes.

- Generate into a sandboxed environment only.
- Run linting, tests, and static analysis before execution.
- Block direct promotion to production.
- Require peer review and security review for sensitive changes.

## CLI Reference
The following reference defines a suggested command structure for implementing this skill in local or remote automation environments.

### Base Command
```bash
model-designer <command> [options]
```

### Commands
- `model-designer init`: Initialize a new automation model project with secure defaults.
- `model-designer validate`: Validate configuration, schema, prompts, and policy alignment.
- `model-designer plan`: Build or refresh the execution plan for an automation workflow.
- `model-designer simulate`: Run the model in dry-run mode without external side effects.
- `model-designer eval`: Execute evaluation suites for quality, safety, and robustness.
- `model-designer deploy`: Package and deploy an approved automation model.
- `model-designer rollback`: Revert to the last approved deployment state.
- `model-designer audit`: Export logs, decisions, and policy checkpoints for review.

### Common Options
- `--config <file>`: Path to the model or automation configuration file.
- `--env <name>`: Target environment such as `local`, `remote`, or `prod`.
- `--dry-run`: Prevent external writes or irreversible actions.
- `--policy <file>`: Load an additional policy definition.
- `--max-steps <n>`: Set an upper bound for agentic execution depth.
- `--approval required`: Force human approval gates for protected actions.
- `--output <path>`: Write reports, plans, or logs to a selected directory.
- `--verbose`: Emit detailed operational logs without exposing secrets.

### Example Commands
```bash
model-designer init --config ./model.yaml --env local
model-designer validate --config ./model.yaml --policy ./security-policy.yaml
model-designer simulate --config ./model.yaml --dry-run --max-steps 8
model-designer eval --config ./model.yaml --output ./reports
model-designer deploy --config ./model.yaml --approval required
model-designer audit --env remote --output ./audit-logs
```

## Best Practices
- Start with the narrowest possible scope, toolset, and permissions.
- Prefer deterministic rules around model decisions when business risk is high.
- Keep prompts, schemas, and policies versioned together.
- Use simulation and replay testing before enabling live actions.
- Define explicit fallback behavior for low confidence, timeouts, and tool failures.
- Separate experimentation from production by account, environment, network, and secrets.
- Measure both usefulness and safety, not just task completion.
- Review logs and incident signals regularly to refine controls.
- Design every automation for graceful shutdown and rollback.
- Treat prompt changes, retrieval changes, and tool changes as production-impacting modifications.

## Troubleshooting
### Validation Fails
Possible causes include invalid schema, missing required fields, unsupported tools, or policy conflicts.

Recommended actions:
- Re-run validation with verbose logging.
- Confirm that configuration keys match the expected schema.
- Check whether approval rules or environment restrictions block the workflow.
- Verify that referenced prompts, models, and policy files exist and are readable.

### Unsafe Output Detected
Possible causes include prompt injection, untrusted retrieval content, weak output constraints, or excessive model autonomy.

Recommended actions:
- Inspect the full input chain, including retrieved documents and tool outputs.
- Tighten output validation and action allowlists.
- Reduce agent step count and require approval gates.
- Add adversarial test cases to the evaluation suite.

### Deployment Blocked
Possible causes include unresolved critical findings, missing approvals, failed evaluation thresholds, or expired credentials.

Recommended actions:
- Review CI/CD security results and policy checks.
- Confirm that the deployment artifact matches the approved version.
- Reissue short-lived credentials through the approved identity flow.
- Verify rollback readiness before retrying deployment.

### Agent Loop or Runaway Execution
Possible causes include missing termination conditions, recursive planning, repeated tool failures, or unclear task goals.

Recommended actions:
- Enforce step, retry, and budget limits.
- Add explicit completion and abort conditions.
- Improve state validation between steps.
- Require human review after repeated failures.

## References
Use these references as implementation anchors for secure software, AI, and automation design.

- OWASP Application Security Verification Standard (ASVS).
- OWASP Top 10.
- NIST Secure Software Development Framework (SSDF).
- NIST AI Risk Management Framework (AI RMF).
- MITRE ATT&CK.
- MITRE ATLAS for adversarial threats to AI systems.
- CIS Critical Security Controls.
- ISO/IEC 27001 and ISO/IEC 27002.
- Organization-specific security standards, privacy policies, and change management procedures.