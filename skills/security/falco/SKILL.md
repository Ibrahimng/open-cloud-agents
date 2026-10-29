---
name: falco
description: Real-time cloud-native runtime threat detection, behavioral monitoring, eBPF kernel syscall inspection, Falco rule development, and automated active prevention via Falco Talon and container isolation.
---

# Falco Cloud-Native Runtime Security & Threat Prevention

Falco is the CNCF graduated standard for cloud-native runtime security and behavioral monitoring. Operating at the Linux kernel boundary using modern eBPF probes, Falco intercepts system calls in real time to detect unauthorized process executions, privilege escalations, sensitive file access, and anomalous network connections across containers and Kubernetes clusters.

---

## 🏛️ Real-Time Detection & Prevention Architecture

```
 ┌────────────────────────────────────────────────────────────────────────┐
 │                      Linux Kernel / eBPF Probe                         │
 │           Intercepts: execve, openat, connect, setns, ptrace           │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │ Ring Buffer (Kernel-to-Userspace)
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                         Falco Userspace Engine                         │
 │     Evaluates System Calls against Declarative Rules & Macros           │
 └─────────────────┬───────────────────────────────────┬──────────────────┘
                   │ gRPC / UNIX Socket                │ JSON Output
                   ▼                                   ▼
 ┌───────────────────────────────────┐ ┌──────────────────────────────────┐
 │      Falco Talon Response Engine  │ │          FalcoSidekick           │
 │      (Active Real-Time Prevention)│ │       (Alert Fan-Out & SIEM)     │
 ├───────────────────────────────────┤ ├──────────────────────────────────┤
 │• Kill compromised process         │ │• Wazuh SIEM / OpenSearch         │
 │• Evict / terminate pod            │ │• Slack / PagerDuty / Opsgenie    │
 │• Inject quarantine NetworkPolicy  │ │• AWS SQS / GCP PubSub / Azure EH │
 └───────────────────────────────────┘ └──────────────────────────────────┘
```

---

## 🚀 Operational Workflow

### Step 1: Deploy Falco with Modern eBPF

Deploy Falco across Kubernetes nodes using Helm with the non-intrusive modern eBPF driver:

```bash
# Add Falco Helm repository
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm repo update

# Deploy Falco DaemonSet with modern-bpf driver and FalcoSidekick
helm upgrade --install falco falcosecurity/falco \
  --namespace falco --create-namespace \
  --set driver.kind=modern_bpf \
  --set falcosidekick.enabled=true \
  --set falcosidekick.webui.enabled=true \
  --set falco.grpc.enabled=true \
  --set falco.grpc_output.enabled=true
```

### Step 2: Validate Custom Rules

Before deploying or modifying rules in production, run the syntax validator:

```bash
python3 skills/security/falco/scripts/validate_falco_rules.py \
  --rules skills/security/falco/references/cloud-native-threat-library.md
```

### Step 3: Test Runtime Detection Safely

Simulate benign security triggers to verify that the detection pipeline, alerts, and response hooks fire correctly:

```bash
python3 skills/security/falco/scripts/simulate_falco_alerts.py --test-all
```

---

## 📜 Falco Rule Syntax Fundamentals

Falco rules use a declarative YAML structure consisting of three primary building blocks:

1. **Lists (`list`):** Named collections of processes, directories, or ports.
2. **Macros (`macro`):** Reusable boolean filtering conditions.
3. **Rules (`rule`):** Alert specifications triggered when incoming syscall events match conditions.

### Rule Template

```yaml
- list: shell_binaries
  items: [bash, sh, zsh, ksh, csh]

- macro: container_running
  condition: (container.id != host and container.name != "")

- rule: Terminal Shell Spawned in Container
  desc: Detects interactive shell execution inside a running container
  condition: >
    spawned_process and
    container_running and
    proc.name in (shell_binaries)
  output: >
    Unauthorized shell spawned in container (user=%user.name container_id=%container.id
    pod=%k8s.pod.name ns=%k8s.ns.name command=%proc.cmdline parent=%proc.pname)
  priority: WARNING
  tags: [mitre_execution, T1059, container, runtime]
```

See the full syntax reference in [falco-rules-architecture.md](references/falco-rules-architecture.md).

---

## 🛡️ Real-Time Detection & Active Prevention Patterns

### High-Priority MITRE ATT&CK Threat Rules

Detailed production rules are in [cloud-native-threat-library.md](references/cloud-native-threat-library.md):

- **T1059 (Command Execution):** Terminal shell or script execution inside production pods.
- **T1068 (Privilege Escalation):** SUID binary execution or container namespace escape attempt (`setns`).
- **T1552 (Credential Theft):** Reading service account tokens (`/var/run/secrets/kubernetes.io/serviceaccount/token`) by non-whitelisted processes.
- **T1496 (Resource Hijacking):** Outbound network connections to known cryptomining pools or Stratum protocol ports.
- **T1070 (Indicator Removal):** Deleting system logs (`/var/log/*`) or clearing bash history (`.bash_history`).

### Active Automated Prevention with Falco Talon

Falco alone emits detection telemetry. **Falco Talon** acts as the enforcement response engine to execute automated containment actions within milliseconds:

```yaml
- action: Terminate Compromised Pod
  actionner: kubernetes:terminate
  parameters:
    grace_period_seconds: 0

- action: Quarantine Network via Calico/Cilium
  actionner: kubernetes:networkpolicy
  parameters:
    type: egress-deny-all

- rule: Kill Container on Reverse Shell
  match:
    rules:
      - "Reverse Shell Detected"
      - "Terminal Shell Spawned in Container"
  actions:
    - action: Quarantine Network via Calico/Cilium
    - action: Terminate Compromised Pod
```

See automated prevention playbooks in [active-response-falco-talon.md](references/active-response-falco-talon.md).

---

## ⚙️ False Positive Tuning & Performance Optimization

In high-throughput microservice clusters, eliminate alert fatigue without creating blind spots:

1. **Use `falco_rules.local.yaml`:** Never modify default upstream rule files. Append overrides in the local configuration.
2. **Leverage Structured Exceptions:** Use Falco `exceptions` blocks rather than loosely appending `and not proc.name = ...`.
3. **Profile Node Dropped Events:** Monitor `falco.outputs` counter metrics (`drop_rate`) and adjust ring buffer size (`buffer_dim_mb: 16`).

See complete tuning methodologies in [tuning-and-false-positives.md](references/tuning-and-false-positives.md).

---

## 📚 References & Tools

- [falco-rules-architecture.md](references/falco-rules-architecture.md): Rule syntax, conditions, operators, and syscall field reference.
- [cloud-native-threat-library.md](references/cloud-native-threat-library.md): Production rule library for MITRE ATT&CK container threats.
- [active-response-falco-talon.md](references/active-response-falco-talon.md): Automated prevention playbooks, pod termination, and network quarantine.
- [tuning-and-false-positives.md](references/tuning-and-false-positives.md): Custom rule exceptions, noise reduction, and eBPF buffer optimization.
- `scripts/validate_falco_rules.py`: Syntactic linter and validator for custom Falco rule files.
- `scripts/simulate_falco_alerts.py`: Safe syscall event simulator to verify detection pipelines.
