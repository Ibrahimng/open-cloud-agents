# Cloud-Native Threat Library: Production Falco Rules

This library contains battle-tested, production-ready Falco rules covering critical MITRE ATT&CK techniques in containerized and Kubernetes environments.

---

## 1. Execution & Lateral Movement (T1059 / T1210)

```yaml
- list: interactive_shells
  items: [bash, sh, zsh, ksh, csh, ash, dash]

- macro: spawned_process
  condition: (evt.type in (execve, execveat) and evt.dir = <)

- macro: in_container
  condition: (container.id != host and container.name != "")

- rule: Terminal Shell Spawned in Container
  desc: Detects interactive shell execution inside a production container
  condition: >
    spawned_process and
    in_container and
    proc.name in (interactive_shells) and
    not proc.pname in (containerd-shim, docker-runc)
  output: >
    Interactive shell spawned inside container (pod=%k8s.pod.name ns=%k8s.ns.name
    container=%container.name user=%user.name command=%proc.cmdline parent=%proc.pname)
  priority: WARNING
  tags: [mitre_execution, T1059, container]

- rule: Outbound Network Connection from Ephemeral Process
  desc: Detects unknown processes initiating outbound network connections
  condition: >
    evt.type in (connect) and
    evt.dir = < and
    in_container and
    (fd.net != "127.0.0.1" and fd.net != "10.0.0.0/8" and fd.net != "172.16.0.0/12") and
    proc.name in (interactive_shells, python3, perl, ruby, php, nc, ncat, netcat)
  output: >
    Suspicious outbound connection initiated by shell or interpreter (pod=%k8s.pod.name
    dest=%fd.dip:%fd.dport proc=%proc.name cmd=%proc.cmdline)
  priority: CRITICAL
  tags: [mitre_command_and_control, T1071, network]
```

---

## 2. Privilege Escalation & Container Breakout (T1068 / T1611)

```yaml
- macro: open_write
  condition: (evt.type in (open, openat, openat2) and evt.is_open_write = true)

- rule: Container Namespace Escape Attempt
  desc: Detects process calling setns or unshare to enter host namespaces
  condition: >
    evt.type in (setns, unshare) and
    in_container
  output: >
    Container breakout / namespace modification attempt detected (pod=%k8s.pod.name
    container=%container.name proc=%proc.name user=%user.name)
  priority: EMERGENCY
  tags: [mitre_privilege_escalation, T1611, breakout]

- rule: Execution of SUID or Privileged Binary
  desc: Detects execution of SUID binaries inside container
  condition: >
    spawned_process and
    in_container and
    proc.is_exe_suid = true
  output: >
    SUID binary execution detected inside container (pod=%k8s.pod.name
    proc=%proc.name file=%fd.name user=%user.name)
  priority: ERROR
  tags: [mitre_privilege_escalation, T1068, suid]
```

---

## 3. Credential Theft & Discovery (T1552 / T1613)

```yaml
- list: k8s_token_files
  items:
    - /var/run/secrets/kubernetes.io/serviceaccount/token
    - /var/run/secrets/kubernetes.io/serviceaccount/ca.crt

- list: trusted_k8s_clients
  items: [kube-proxy, flannel, calico-node, cilium-agent]

- rule: Unauthorized K8s Service Account Token Access
  desc: Detects reading of the default service account token by untrusted processes
  condition: >
    (evt.type in (open, openat) and evt.is_open_read = true) and
    in_container and
    fd.name in (k8s_token_files) and
    not proc.name in (trusted_k8s_clients)
  output: >
    Kubernetes Service Account token accessed (pod=%k8s.pod.name ns=%k8s.ns.name
    proc=%proc.name cmd=%proc.cmdline user=%user.name file=%fd.name)
  priority: WARNING
  tags: [mitre_credential_access, T1552, kubernetes]

- rule: Sensitive Host Directory Read Inside Container
  desc: Detects access to host filesystems mounted into containers
  condition: >
    (evt.type in (open, openat) and evt.is_open_read = true) and
    in_container and
    (fd.name startswith "/etc/shadow" or fd.name startswith "/etc/sudoers" or fd.name startswith "/root/.ssh")
  output: >
    Sensitive host credential accessed inside container (file=%fd.name
    pod=%k8s.pod.name container=%container.name proc=%proc.name)
  priority: CRITICAL
  tags: [mitre_credential_access, T1552, filesystem]
```

---

## 4. Cryptomining & Defense Evasion (T1496 / T1070)

```yaml
- list: miner_domains_and_ips
  items: [pool.supportxmr.com, xmr.nanopool.org, monerohash.com]

- list: miner_ports
  items: [3333, 4444, 5555, 7777, 9999, 14433, 14444]

- rule: Cryptomining Pool Connection Attempt
  desc: Detects network traffic matching known mining pools or Stratum mining ports
  condition: >
    evt.type in (connect) and
    in_container and
    (fd.dport in (miner_ports) or fd.sip in (miner_domains_and_ips) or fd.dip in (miner_domains_and_ips))
  output: >
    Cryptomining connection detected from container (pod=%k8s.pod.name
    dest=%fd.dip:%fd.dport proc=%proc.name cmdline=%proc.cmdline)
  priority: CRITICAL
  tags: [mitre_impact, T1496, cryptomining]

- rule: Clear Bash History or System Audit Logs
  desc: Detects truncation or deletion of shell history or audit logs
  condition: >
    (evt.type in (unlink, unlinkat, truncate, ftruncate) or open_write) and
    (fd.name endswith ".bash_history" or fd.name startswith "/var/log/audit" or fd.name startswith "/var/log/messages")
  output: >
    Evasion attempt: log or history file modified/deleted (file=%fd.name
    proc=%proc.name user=%user.name)
  priority: WARNING
  tags: [mitre_defense_evasion, T1070, anti_forensics]
```
