---
name: Zero-Trust Identity & Secrets Management
severity: BLOCKING
scope: ALL_AGENTS
---

# Rule 02: Zero-Trust Identity & Secrets Management

## Principle
Hardcoded credentials, static long-lived API keys, and unredacted logging are critical enterprise vulnerabilities. Agents must enforce zero-trust identity and strict cryptographic secret hygiene.

---

## Inviolable Guardrails

### 1. Zero Hardcoded Credentials
Under no circumstance should an agent:
- Commit API keys, OAuth client secrets, private keys (`.pem`, `.key`), or database passwords.
- Generate code containing hardcoded connection strings with embedded passwords (e.g., `postgres://user:password@host/db`).
- Check in `.env`, `.env.local`, `credentials.json`, or service account keys.

### 2. Mandatory Workload Identity & OIDC Federation
Whenever authenticating workloads:
- **Cloud Run / GKE / ECS / EKS:** Prefer native metadata identity (AWS IAM Roles for Service Accounts / GCP Workload Identity / Azure Workload Identity).
- **CI/CD Pipelines (GitHub Actions / GitLab CI):** Enforce short-lived OIDC token exchange over static cloud credentials (`AWS_ACCESS_KEY_ID`, `GOOGLE_APPLICATION_CREDENTIALS`).
- **Secret Retrieval:** Fetch secrets at runtime via cloud Secret Managers (AWS Secrets Manager, GCP Secret Manager, Azure Key Vault, HashiCorp Vault) using fine-grained IAM permissions.

### 3. Log Redaction & Telemetry Sanitization
- Never print raw payload secrets, tokens, or PII into standard out, standard error, or application logs.
- When generating logging interceptors or OpenTelemetry tracers, mandate regex sanitization for Authorization headers, cookies, and sensitive query parameters.

