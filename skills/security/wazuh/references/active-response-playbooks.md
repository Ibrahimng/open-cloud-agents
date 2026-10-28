# Wazuh Active Response Playbooks & Threat Containment

Active Response enables Wazuh to automatically execute containment scripts on endpoints upon matching high-severity threat detection rules.

---

## 1. Built-In Active Response Commands

Wazuh bundles production-tested binary scripts in `/var/ossec/active-response/bin/`:

| Command Name | Executable | Description | Operating Systems |
|---|---|---|---|
| **firewall-drop** | `firewall-drop` | Appends offending IP to `iptables`, `nftables`, or Windows Firewall drop chain. | Linux, Windows |
| **host-deny** | `host-deny` | Appends offending IP to `/etc/hosts.deny` (TCP wrappers). | Linux, Unix |
| **disable-account** | `disable-account` | Disables or locks a user account (`usermod -L` or `net user /active:no`). | Linux, Windows |
| **restart-wazuh** | `restart-wazuh` | Restarts the Wazuh agent daemon. | All |
| **route-null** | `route-null` | Routes offending IP address traffic to the null interface (`ip route add blackhole`). | Linux |

---

## 2. Configuration Playbook (`ossec.conf`)

### 2.1 Block Ingress on SSH Brute-Force (Level $\ge 10$)
```xml
<command>
  <name>firewall-drop</name>
  <executable>firewall-drop</executable>
  <timeout_allowed>yes</timeout_allowed>
</command>

<active-response>
  <command>firewall-drop</command>
  <location>local</location>
  <!-- Rule 5712: SSHD brute force attempt -->
  <rules_id>5712, 5710, 5716</rules_id>
  <!-- Block for 30 minutes, then automatically release -->
  <timeout>1800</timeout>
</active-response>
```

### 2.2 Neutralize Container Host on Malware or Reverse Shell
```xml
<command>
  <name>isolate-endpoint</name>
  <executable>custom-isolate-host.sh</executable>
  <timeout_allowed>no</timeout_allowed>
</command>

<active-response>
  <command>isolate-endpoint</command>
  <location>local</location>
  <rules_id>100201, 100202</rules_id>
</active-response>
```

---

## 3. Custom Active Response Script Architecture

Custom active response handlers read alert JSON through standard input (`stdin`) and return an execution status code:

```bash
#!/usr/bin/env bash
# /var/ossec/active-response/bin/custom-isolate-host.sh

read -r INPUT_JSON
ACTION=$(echo "$INPUT_JSON" | jq -r '.command')
SRC_IP=$(echo "$INPUT_JSON" | jq -r '.parameters.alert.data.srcip')

if [[ "$ACTION" == "add" ]]; then
  echo "$(date) - Blocking IP: $SRC_IP" >> /var/ossec/logs/active-responses.log
  iptables -I INPUT -s "$SRC_IP" -j DROP
elif [[ "$ACTION" == "delete" ]]; then
  echo "$(date) - Unblocking IP: $SRC_IP" >> /var/ossec/logs/active-responses.log
  iptables -D INPUT -s "$SRC_IP" -j DROP || true
fi
exit 0
```
