---
name: wazuh
description: Enterprise open-source SIEM and XDR (Extended Detection & Response), File Integrity Monitoring (FIM), Security Configuration Assessment (SCA), log analysis decoders, and automated Active Response threat neutralization.
---

# Wazuh Enterprise SIEM, XDR & Active Response Defense

Wazuh is the leading open-source Security Information and Event Management (SIEM) and Extended Detection and Response (XDR) platform. It provides unified threat detection across cloud, virtual, container, and on-premises endpoints through real-time log analysis, **File Integrity Monitoring (FIM)**, automated **Security Configuration Assessment (SCA / CIS)**, and autonomous **Active Response** containment.

---

## 🏛️ Wazuh XDR Architecture & Pipeline

```
 ┌────────────────────────────────────────────────────────────────────────┐
 │                      Wazuh Agents (Endpoints)                          │
 │  Linux / Windows / macOS / K8s Nodes / Cloud Compute (EC2, GCE, Azure)  │
 ├───────────────────────────────────┬────────────────────────────────────┤
 │• Real-time Log Collector (syslog) │• File Integrity Monitoring (FIM)   │
 │• SCA / CIS Compliance Scanner     │• Rootcheck / Anomaly Detection     │
 │• Command / Syscall Inspector      │• Active Response Execution Engine  │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │ Encrypted TLS / Port 1514
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                    Wazuh Server / Manager Cluster                      │
 │      Analysis Engine: Decoders ➔ Rules Engine ➔ Active Response        │
 └─────────────────┬───────────────────────────────────┬──────────────────┘
                   │ Alert Stream                      │ Automated Trigger
                   ▼                                   ▼
 ┌───────────────────────────────────┐ ┌──────────────────────────────────┐
 │     Wazuh Indexer & Dashboard     │ │     Autonomous Active Response   │
 │   (OpenSearch Analytics & Visual) │ │   (Real-Time Threat Prevention)  │
 ├───────────────────────────────────┤ ├──────────────────────────────────┤
 │• MITRE ATT&CK Matrix Navigation   │ │• Dynamic IP Drop (iptables/nft)  │
 │• Regulatory Compliance (SOC 2, CIS│ │• Kill Rogue Process (SIGKILL)    │
 │• Threat Intelligence & CVE Feeds  │ │• Disable Compromised User Account│
 └───────────────────────────────────┘ └──────────────────────────────────┘
```

---

## 🚀 Operational Workflow

### Step 1: Agent Deployment & Registration
Deploy the lightweight Wazuh agent across cloud VMs or Kubernetes nodes:

```bash
# Ubuntu / Debian
curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | gpg --no-default-keyring --keyring gnupg-ring:/usr/share/keyrings/wazuh.gpg --import && chmod 644 /usr/share/keyrings/wazuh.gpg
echo "deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main" | tee -a /etc/apt/sources.list.d/wazuh.list
apt-get update && WAZUH_MANAGER='wazuh-manager.internal' apt-get install -y wazuh-agent

# Start and verify agent daemon
systemctl daemon-reload
systemctl enable wazuh-agent
systemctl start wazuh-agent
systemctl status wazuh-agent
```

See [wazuh-architecture-and-deployment.md](references/wazuh-architecture-and-deployment.md).

---

### Step 2: Configure File Integrity Monitoring (FIM / `syscheck`)
Configure real-time cryptographic file integrity auditing with **whodata** attribution via `auditd`:

```xml
<!-- In /var/ossec/etc/ossec.conf -->
<syscheck>
  <disabled>no</disabled>
  <frequency>43200</frequency>
  <scan_on_start>yes</scan_on_start>

  <!-- Real-time whodata monitoring on sensitive directories -->
  <directories check_all="yes" whodata="yes" realtime="yes">/etc,/usr/bin,/usr/sbin,/bin,/sbin</directories>
  <directories check_all="yes" whodata="yes">/root/.ssh,/home/*/.ssh</directories>

  <!-- Exclude high-churn temporary directories -->
  <ignore>/etc/mtab</ignore>
  <ignore>/etc/hosts.deny</ignore>
  <ignore type="sregex">^/var/log</ignore>
</syscheck>
```

See [fim-and-auditd-deep-dive.md](references/fim-and-auditd-deep-dive.md).

---

### Step 3: Test Decoders & Custom Detection Rules
Validate log parsing and custom rule triggering using the standalone rule tester:

```bash
python3 skills/security/wazuh/scripts/wazuh_rule_tester.py \
  --rules skills/security/wazuh/references/custom-decoders-and-rules.md \
  --log "Failed password for invalid user admin from 198.51.100.42 port 54321 ssh2"
```

---

### Step 4: Real-Time Threat Prevention via Active Response
Configure automated active defense actions in `ossec.conf` to neutralize attacks upon detection:

```xml
<!-- 1. Define Prevention Command -->
<command>
  <name>firewall-drop</name>
  <executable>firewall-drop</executable>
  <timeout_allowed>yes</timeout_allowed>
</command>

<!-- 2. Bind Active Response to Threat Rule -->
<active-response>
  <command>firewall-drop</command>
  <location>local</location>
  <!-- Trigger when SSH brute force or web exploit fires (Level >= 10) -->
  <level>10</level>
  <!-- Drop offending IP for 15 minutes, then automatically release -->
  <timeout>900</timeout>
</active-response>
```

Verify active response execution and rollback behavior:
```bash
python3 skills/security/wazuh/scripts/wazuh_active_response_simulator.py --test-ip 198.51.100.42 --timeout 5
```

See [active-response-playbooks.md](references/active-response-playbooks.md).

---

## 📚 References & Tools

- [wazuh-architecture-and-deployment.md](references/wazuh-architecture-and-deployment.md): Cluster architecture, multi-tier deployment, and TLS mutual auth.
- [fim-and-auditd-deep-dive.md](references/fim-and-auditd-deep-dive.md): Real-time FIM, whodata auditing, and integrity baseline configuration.
- [active-response-playbooks.md](references/active-response-playbooks.md): Autonomous prevention commands, firewall dropping, and host isolation.
- [custom-decoders-and-rules.md](references/custom-decoders-and-rules.md): XML decoders, parent/child rules, alert levels, and MITRE mapping.
- `scripts/wazuh_rule_tester.py`: Standalone decoder and rule evaluation testing tool.
- `scripts/wazuh_active_response_simulator.py`: Safe active response execution and rollback verification harness.
