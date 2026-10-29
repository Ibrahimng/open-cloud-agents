---
name: cis-complete-audit
description: Comprehensive multi-layer Center for Internet Security (CIS) benchmark auditing, scoring, automated drift detection, and remediation across Cloud Foundations (AWS, Azure, GCP), Kubernetes (Control Plane & Workers), Linux OS Hosts, and Docker Containers.
---

# CIS Complete Multi-Layer Benchmark Audit & Hardening

Comprehensive, end-to-end Center for Internet Security (CIS) compliance auditing, drift detection, and automated remediation engine. This runbook operationalizes CIS benchmarks across all four layers of modern enterprise infrastructure: **Cloud Foundations**, **Kubernetes Clusters**, **Linux OS Hosts**, and **Container Runtimes**.

---

## 🏛️ 4-Tier CIS Benchmark Architecture

```
                       ┌──────────────────────────────────────────────┐
                       │           CIS Complete Audit Suite           │
                       └──────────────────────┬───────────────────────┘
                                              │
         ┌──────────────────┬─────────────────┴────────────────┬──────────────────┐
         ▼                  ▼                                  ▼                  ▼
┌─────────────────┐ ┌─────────────────┐              ┌─────────────────┐ ┌─────────────────┐
│ Cloud Foundation│ │Kubernetes (K8s) │              │ Linux OS Host   │ │Docker Container │
│ AWS / GCP / Az  │ │CP & Worker Nodes│              │ Ubuntu / RHEL   │ │Daemon & Runtime │
├─────────────────┤ ├─────────────────┤              ├─────────────────┤ ├─────────────────┤
│• IAM & Access   │ │• API Server     │              │• Filesystem Mnt │ │• Daemon Config  │
│• Storage Encrypt│ │• etcd & Auth    │              │• PAM & Passwords│ │• Non-root User  │
│• Audit Logging  │ │• Kubelet Flags  │              │• auditd Logging │ │• Read-only Root │
│• Net & Ingress  │ │• Pod Sec Stds   │              │• sysctl & Net   │ │• Content Trust  │
└─────────────────┘ └─────────────────┘              └─────────────────┘ └─────────────────┘
```

### Profile Levels
- **Level 1 (Pragmatic / Essential):** Foundational security baseline controls that can be applied with minimal risk of breaking application functionality or performance.
- **Level 2 (Defense-in-Depth / High-Security):** Stricter controls intended for environments requiring defense-in-depth where security takes precedence over operational flexibility.

---

## 🚀 Operational Workflow

### Step 1: Pre-Audit Environment Discovery
Identify targets, cloud provider accounts, cluster kubeconfigs, or host access:

```bash
# Verify cloud identities and permissions
aws sts get-caller-identity
gcloud auth list
az account show

# Verify Kubernetes cluster connection
kubectl cluster-info
kubectl get nodes -o wide

# Check host OS release and container engine
uname -a
docker info 2>/dev/null || podman info
```

### Step 2: Automated Multi-Target Compliance Audit
Execute the standalone, unified CIS audit scanner across targets:

```bash
# Run complete audit across all layers with JSON and Markdown reports
python3 skills/security/cis-complete-audit/scripts/audit_cis_compliance.py \
  --target all \
  --profile level1 \
  --format markdown \
  --output cis-audit-report.md

# Target specific subsystem (e.g. Kubernetes cluster Level 2)
python3 skills/security/cis-complete-audit/scripts/audit_cis_compliance.py \
  --target k8s \
  --profile level2 \
  --format console
```

### Step 3: Drift Detection & Real-Time Posture Tracking

Continuously evaluate configuration drift against CIS golden baselines:

- **Cloud IAM Drift:** Detect unrotated access keys (> 90 days), root account usage, missing MFA.
- **Kubernetes Drift:** Detect pods launched without `securityContext.runAsNonRoot: true` or with `privileged: true`.
- **Host Drift:** Detect modified `/etc/shadow` or `/etc/pam.d/`, world-writable files, unlogged sudo commands.
- **Docker Drift:** Detect containers running with `--privileged` or binding to `0.0.0.0:22`.

---

## 🔍 Core CIS Checks by Subsystem

### 1. Cloud Foundations (AWS, Azure, GCP)
See detailed checklist and commands in [cloud-foundations-matrix.md](references/cloud-foundations-matrix.md).

- **Identity & Access Management:**
    - MFA enforced for all console users and break-glass admins.
    - Zero active root account access keys or GCP default compute service accounts with Editor/Owner roles.
    - Unused credentials (> 90 days) automatically disabled.
- **Storage & Encryption:**
    - Public Access Blocks enabled on all object buckets (S3 / GCS / Azure Blob).
    - KMS Customer Managed Keys (CMK) envelope encryption with automatic 365-day rotation.
- **Logging & Monitoring:**
    - Multi-region CloudTrail / GCP Cloud Audit Logs / Azure Activity Log enabled and immutable.
    - Metric filters and alerts configured for unauthorized API calls, IAM policy changes, and security group alterations.
- **Networking:**
    - Security Groups prohibiting unrestricted ingress (`0.0.0.0/0` and `::/0`) on ports 22 (SSH), 3389 (RDP), 3306 (MySQL), 5432 (Postgres), 6379 (Redis).
    - Default VPC security groups configured with zero ingress and egress rules.

### 2. Kubernetes CIS Benchmark (v1.9)
See detailed checklist and parameters in [kubernetes-cis-guide.md](references/kubernetes-cis-guide.md).

- **Control Plane Hardening (`kube-apiserver`):**
    - `--anonymous-auth=false`
    - `--authorization-mode=Node,RBAC`
    - `--enable-admission-plugins=NodeRestriction,PodSecurity`
    - `--audit-log-path` and `--audit-log-maxage=30`
- **etcd Security:**
    - `--cert-file`, `--key-file`, `--client-cert-auth=true`
    - Encrypted at rest via `EncryptionConfiguration` with KMS envelope provider.
- **Worker Node & Kubelet Hardening:**
    - `--anonymous-auth=false`
    - `--authorization-mode=Webhook`
    - `--read-only-port=0`
    - `--protect-kernel-defaults=true`
- **Workload Security (Pod Security Standards):**
    - Admission enforcement of `restricted` or `baseline` PSS profile on all application namespaces.

### 3. Linux OS Host Benchmark (Ubuntu / RHEL)
See detailed configuration parameters in [linux-host-hardening-matrix.md](references/linux-host-hardening-matrix.md).

- **Filesystem Configuration:**
    - `/tmp`, `/var/tmp`, `/dev/shm` mounted with `nodev,nosuid,noexec`.
    - Sticky bit set on all world-writable directories.
- **Access Control & PAM:**
    - Password expiration: `PASS_MAX_DAYS 90`, `PASS_MIN_DAYS 7`, `PASS_MIN_LEN 14`.
    - Failed login lockouts via `pam_faillock` (account locked after 5 failed attempts).
    - SSH Daemon: `PermitRootLogin no`, `PasswordAuthentication no`, `MaxAuthTries 4`, `X11Forwarding no`.
- **System Auditing (`auditd`):**
    - Immutable audit daemon rules tracking changes to system time, user/group databases, network configs, and file deletions.
- **Kernel Network Parameters (`sysctl`):**
    - `net.ipv4.ip_forward = 0` (non-routing hosts).
    - `net.ipv4.conf.all.send_redirects = 0`
    - `net.ipv4.conf.all.accept_redirects = 0`
    - `net.ipv4.conf.all.rp_filter = 1` (reverse path filtering).

### 4. Docker Container Runtime Benchmark
See container daemon parameters in [docker-container-cis-matrix.md](references/docker-container-cis-matrix.md).

- **Daemon Hardening (`/etc/docker/daemon.json`):**
    - `"icc": false` (inter-container communication restricted).
    - `"userns-remap": "default"` (user namespace remapping enabled).
    - `"live-restore": true`
    - `"no-new-privileges": true`
- **Container Execution:**
    - Containers must not run as user `root` (UID 0).
    - Read-only root filesystem (`--read-only`) with tmpfs mounts for ephemeral paths.
    - Resource limits (`--memory`, `--cpus`) enforced to prevent host starvation.

---

## 🛠️ Automated Remediation & Safe Rollback

Always evaluate remediation impacts in dry-run mode before enforcing state changes:

```bash
# Run host and container remediation helper in dry-run mode
bash skills/security/cis-complete-audit/scripts/cis_remediation_helper.sh --dry-run

# Apply verified remediations
bash skills/security/cis-complete-audit/scripts/cis_remediation_helper.sh --apply
```

Detailed remediation snippets for Terraform, Ansible, and Shell are in [remediation-playbooks.md](references/remediation-playbooks.md).

---

## 📚 References & Tools

- [cloud-foundations-matrix.md](references/cloud-foundations-matrix.md): AWS, Azure, GCP CIS Benchmark rules, audit commands, and scoring.
- [kubernetes-cis-guide.md](references/kubernetes-cis-guide.md): Kubernetes CIS control plane, kubelet, and PSS audit specifications.
- [linux-host-hardening-matrix.md](references/linux-host-hardening-matrix.md): Linux host filesystem, PAM, auditd, and kernel sysctl hardening.
- [docker-container-cis-matrix.md](references/docker-container-cis-matrix.md): Docker daemon security configuration and container runtime boundaries.
- [remediation-playbooks.md](references/remediation-playbooks.md): Executable remediation recipes and rollback steps.
- `scripts/audit_cis_compliance.py`: Standalone, multi-target CIS compliance auditor and report generator.
- `scripts/cis_remediation_helper.sh`: Automated host and docker security remediation script.
