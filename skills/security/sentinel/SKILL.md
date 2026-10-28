---
name: sentinel
description: Cloud-native SIEM and SOAR engineering for Microsoft Sentinel: multi-cloud log ingestion, advanced KQL threat hunting, analytical rule authoring, automated SOAR incident response playbooks, and UEBA entity analytics.
---

# Microsoft Sentinel Cloud-Native SIEM, KQL Threat Hunting & SOAR Defense

Microsoft Sentinel is the cloud-native Security Information and Event Management (SIEM) and Security Orchestration, Automation, and Response (SOAR) solution built on Azure Log Analytics. It provides intelligent security analytics across the entire enterprise, correlating multi-cloud telemetry (Azure, AWS, GCP, on-prem), executing advanced Kusto Query Language (KQL) threat detections, and autonomously mitigating attacks through Logic Apps playbooks.

---

## 🏛️ Sentinel Detection, Analytics & SOAR Continuum

```
 ┌────────────────────────────────────────────────────────────────────────┐
 │                      Multi-Cloud Data Connectors                       │
 │  Azure / Entra ID / M365 / AWS CloudTrail / GCP Audit / CEF & Syslog   │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │ Data Collection Rules (DCR) / AMA
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                 Azure Log Analytics Workspace (LAW)                    │
 │               Scalable Telemetry Store & Hot/Cold Tiering              │
 └─────────────────┬───────────────────────────────────┬──────────────────┘
                   │ KQL Analytics Rules               │ ML Fusion & UEBA
                   ▼                                   ▼
 ┌───────────────────────────────────┐ ┌──────────────────────────────────┐
 │         Incident Triage           │ │   Automated SOAR Logic Apps      │
 │       & Investigation Graph       │ │  (Real-Time Threat Containment)  │
 ├───────────────────────────────────┤ ├──────────────────────────────────┤
 │• Entity Mapping (Host, IP, User)  │ │• Revoke Entra ID User Sessions   │
 │• Timeline & MITRE ATT&CK Crosswalk│ │• Isolate Endpoint via Defender   │
 │• True/False Positive Classification│ │• Block Malicious IP on Firewall │
 └───────────────────────────────────┘ └──────────────────────────────────┘
```

---

## 🚀 Operational Workflow

### Step 1: Ingestion & Workspace Architecture
Ensure Log Analytics Workspace (LAW) and Azure Monitor Agent (AMA) are properly configured:

```bash
# Verify Log Analytics workspace status via Azure CLI
az monitor log-analytics workspace show \
  --resource-group "rg-sentinel-prod" \
  --workspace-name "law-sentinel-prod" \
  --query "[name,retentionInDays,provisioningState,sku.name]"

# List active Sentinel data connectors
az sentinel data-connector list \
  --resource-group "rg-sentinel-prod" \
  --workspace-name "law-sentinel-prod" \
  --output table
```

See [sentinel-architecture-and-data-connectors.md](references/sentinel-architecture-and-data-connectors.md).

---

### Step 2: Advanced KQL Threat Hunting
Hunt for adversary techniques across authentication logs (`SigninLogs`), audit trails (`AuditLogs`), and cloud control planes:

```kusto
// Example: Detect Impossible Travel Sign-Ins (T1078)
SigninLogs
| where TimeGenerated > ago(24h)
| where ResultType == 0 // Successful sign-in
| project TimeGenerated, UserPrincipalName, IPAddress, Location, AppDisplayName
| evaluate basket()
```

Validate query syntax and performance best practices using the standalone linter:
```bash
python3 skills/security/sentinel/scripts/validate_kql_queries.py \
  --query-file skills/security/sentinel/references/kql-threat-hunting-library.md
```

See the complete query catalog in [kql-threat-hunting-library.md](references/kql-threat-hunting-library.md).

---

### Step 3: Scheduled Analytics Rules & Entity Mapping
Translate threat hunt queries into persistent scheduled analytics rules that generate actionable incidents:

- **Query Frequency:** e.g., Every 5 minutes (`PT5M`).
- **Query Period:** Lookback window e.g., Last 15 minutes (`PT15M`).
- **Trigger Threshold:** Generate incident if `count > 0` or anomalous threshold exceeded.
- **Entity Mappings:** Map KQL output columns to standardized Sentinel entities (`Account`, `Host`, `IP`, `URL`, `FileHash`).

Generate declarative analytics rule ARM templates:
```bash
python3 skills/security/sentinel/scripts/sentinel_playbook_generator.py \
  --rule-name "Detect-GlobalAdmin-RoleAssignment" \
  --severity High \
  --query-type scheduled \
  --output admin-assignment-rule.json
```

See [incident-triage-and-entity-analytics.md](references/incident-triage-and-entity-analytics.md).

---

### Step 4: Autonomous SOAR Playbook Execution
Trigger automated containment actions in real-time via Azure Logic Apps playbooks:

1. **Identity Containment:** Revoke all active OAuth refresh tokens and force password reset for compromised Entra ID accounts.
2. **Endpoint Quarantine:** Isolate compromised virtual machines or managed endpoints via Defender for Endpoint API.
3. **Perimeter Defense:** Push malicious source IPs to Azure Firewall IP Groups or Network Security Groups (NSGs).
4. **Analyst Escalation:** Post interactive Adaptive Cards to Microsoft Teams or Slack channels for one-click human confirmation.

See deployment patterns in [soar-automation-playbooks.md](references/soar-automation-playbooks.md).

---

## 📚 References & Tools

- [kql-threat-hunting-library.md](references/kql-threat-hunting-library.md): Advanced KQL queries mapped to MITRE ATT&CK cloud tactics.
- [sentinel-architecture-and-data-connectors.md](references/sentinel-architecture-and-data-connectors.md): Workspace design, AMA configuration, and multi-cloud ingestion.
- [soar-automation-playbooks.md](references/soar-automation-playbooks.md): Logic Apps SOAR workflows, incident triggers, and containment actions.
- [incident-triage-and-entity-analytics.md](references/incident-triage-and-entity-analytics.md): Entity mappings, UEBA profiling, investigation graphs, and closing workflows.
- `scripts/validate_kql_queries.py`: Syntactic validator and performance linter for KQL queries.
- `scripts/sentinel_playbook_generator.py`: Declarative ARM/Bicep template generator for Sentinel analytics rules and SOAR bindings.

