---
name: sysdig
description: Cloud Native Application Protection Platform (CNAPP), Sysdig Secure & OSS system call tracing, container runtime drift control, image vulnerability gatekeeping, and automated incident capture forensics.
---

# Sysdig Runtime Defense, Drift Control & Deep Forensics

Sysdig provides comprehensive Cloud Native Application Protection Platform (CNAPP) capabilities, combining deep kernel system call visibility via Sysdig OSS with enterprise runtime security, container **Drift Control**, CI/CD image vulnerability admission gatekeeping, and forensic incident captures.

---

## 🏛️ Sysdig Architecture & Protection Continuum

```
                               ┌────────────────────────────────────────────────────────┐
                               │       Sysdig Cloud-Native Defense Continuum            │
                               └──────────────────────────┬─────────────────────────────┘
                                                          │
         ┌─────────────────────────────────┬──────────────┴────────────────┬────────────────────────────────┐
         ▼                                 ▼                               ▼                                ▼
┌──────────────────┐             ┌───────────────────┐           ┌──────────────────┐             ┌──────────────────┐
│   Build / CI/CD  │             │  Deploy / Admit   │           │ Runtime Defense  │             │ Incident Capture │
├──────────────────┤             ├───────────────────┤           ├──────────────────┤             ├──────────────────┤
│• sysdig-cli-scan │             │• Admission Webhook│           │• Drift Control   │             │• Auto .scap dump │
│• Block OS & Vuln │             │• Block Unscanned  │           │• In-memory block │             │• Chisels & Spies │
│• CISA KEV / EPSS │             │• Enforce Non-Root │           │• Kill Container  │             │• Forensic Replay │
└──────────────────┘             └───────────────────┘           └──────────────────┘             └──────────────────┘
```

---

## 🚀 Operational Workflow

### Step 1: Real-Time Runtime Drift Control
Drift Control guarantees container immutability by detecting and preventing unauthorized binaries from executing inside running containers:

1. **Drift Identification:** A process attempts to execute a binary that was not part of the original immutable container image (e.g. downloaded via `curl`, `wget`, or written via `/tmp`).
2. **Immediate Prevention:** Sysdig agent intercepts the `execve` system call before the instruction executes and sends `SIGKILL` or suspends the container.

```bash
# Generate a hardened runtime drift control policy
python3 skills/security/sysdig/scripts/sysdig_policy_generator.py \
  --policy-name "prod-drift-prevention" \
  --action kill \
  --block-drift \
  --output drift-policy.json
```

See [drift-control-and-prevention.md](references/drift-control-and-prevention.md) for enforcement configurations.

---

### Step 2: In-Line Image Scanning & Admission Gatekeeping
Prevent vulnerable images or embedded credentials from reaching production Kubernetes clusters:

```bash
# Execute local in-line scan with sysdig-cli-scanner
sysdig-cli-scanner \
  --apiurl "https://app.sysdigcloud.com" \
  --console-log \
  --policy "Enterprise-Production-Gate" \
  my-registry.io/service:v1.4.0
```

Gate enforcement policies evaluate:
- **CISA Known Exploited Vulnerabilities (KEV):** Reject any image with actively exploited CVEs.
- **EPSS Score:** Reject images with EPSS score $> 0.35$ and CVSS $\ge 7.0$.
- **Plaintext Secrets:** Reject images containing embedded private keys, AWS tokens, or `.env` files.
- **Root User:** Reject images specifying `USER root` or UID 0.

See [image-scanning-admission-controller.md](references/image-scanning-admission-controller.md).

---

### Step 3: Deep Forensics with Sysdig OSS & Chisels
When a high-severity alert fires, Sysdig triggers an automated system call capture (`.scap`), recording all events 10 seconds before and 30 seconds after the trigger:

```bash
# Live inspection of active containers
sysdig -c topcontainers_cpu

# Spy on interactive user sessions inside containers
sysdig -c spy_users

# Inspect HTTP requests across all pods in real-time
sysdig -s 2000 -A -c echo_fds "fd.port=80 or fd.port=8080"

# Parse and analyze capture file for forensic anomalies
python3 skills/security/sysdig/scripts/parse_sysdig_capture.py \
  --input incident-trace.log \
  --analyze anomalies
```

See full chisel and filter commands in [sysdig-oss-chisel-cheatsheet.md](references/sysdig-oss-chisel-cheatsheet.md).

---

### Step 4: Multi-Cloud Threat Detection (Cloud Connector)
Sysdig Cloud Connector ingests control plane telemetry across AWS CloudTrail, GCP Audit Logs, and Azure Activity Logs:
- Detects cloud IAM credential exfiltration and privilege escalation.
- Identifies modifications to VPC security groups, Route 53 DNS, or S3 bucket ACLs.
- Detects console logins from non-MFA sessions or unrecognized IP ranges.

See [cloud-threat-detection-matrix.md](references/cloud-threat-detection-matrix.md).

---

## 📚 References & Tools

- [sysdig-oss-chisel-cheatsheet.md](references/sysdig-oss-chisel-cheatsheet.md): Sysdig CLI commands, filter syntax, and chisel utilities.
- [drift-control-and-prevention.md](references/drift-control-and-prevention.md): Runtime drift control architecture, execution prevention, and immutability.
- [image-scanning-admission-controller.md](references/image-scanning-admission-controller.md): CI/CD in-line scanning, vulnerability gates, and K8s admission control.
- [cloud-threat-detection-matrix.md](references/cloud-threat-detection-matrix.md): Multi-cloud control plane rules for AWS, GCP, and Azure.
- `scripts/sysdig_policy_generator.py`: Generates Sysdig Secure runtime and drift prevention policies.
- `scripts/parse_sysdig_capture.py`: Standalone forensic analyzer for Sysdig capture traces.
