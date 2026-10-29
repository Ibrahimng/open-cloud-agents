# Microsoft Sentinel Architecture & Data Connector Engineering

This guide details workspace architecture, data ingestion models, cost optimization, and multi-cloud data connectors for Microsoft Sentinel.

---

## 1. Log Analytics Workspace (LAW) Topology

Microsoft Sentinel operates on top of an Azure Log Analytics Workspace.

```
       [ Microsoft 365 & Entra ID ] ────(Service-to-Service Connector)───┐
                                                                          │
       [ Azure VMs / Linux / Windows ] ──(Azure Monitor Agent / DCR)─────┼──> [ Log Analytics Workspace ]
                                                                          │        (Sentinel Core)
       [ AWS CloudTrail / S3 Logs ] ────(S3 SQS Poll / AssumeRole)───────┤
                                                                          │
       [ On-Prem Firewall / Syslog ] ───(CEF Forwarder on Linux VM)──────┘
```

### Ingestion Tiers
- **Analytics Logs (Default):** Full KQL query capability, 90-day to 730-day interactive retention, evaluated by analytics rules and ML models.
- **Basic Logs:** Low-cost ingestion for high-volume verbose logs (e.g., NetFlow, raw firewall traffic). Supports basic debugging queries with reduced query timeout (30 seconds).
- **Archive Logs:** Long-term compliance retention (up to 7 years) at cold storage prices.

---

## 2. Ingestion Connectors

### 2.1 Microsoft Entra ID & Microsoft 365 (Zero-Ingestion Cost)

Certain foundational security logs incur zero ingestion cost into Sentinel:

- `SigninLogs` (Entra ID Interactive & Non-Interactive)
- `AuditLogs` (Entra ID Directory Auditing)
- `OfficeActivity` (Exchange, SharePoint, OneDrive, Teams audit logs)
- `SecurityAlert` (Alerts from Defender for Cloud, Defender for Endpoint, Defender for Identity)

### 2.2 Multi-Cloud Ingestion: AWS CloudTrail via SQS
Connects AWS CloudTrail directly using an AWS S3 bucket, SQS queue, and an Azure Sentinel service principal with `sts:AssumeRole`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::197857026523:root"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "<WORKSPACE_ID>"
        }
      }
    }
  ]
}
```

### 2.3 Common Event Format (CEF) / Syslog via Azure Monitor Agent (AMA)
Deploy a dedicated Linux VM forwarder running `rsyslog` and the Azure Monitor Agent with a Data Collection Rule (DCR):

```bash
# Verify forwarder ingestion
tail -f /var/log/syslog | grep "CEF:"
```

---

## 3. Ingestion Cost Optimization Techniques

1. **Prune Unused Columns with DCR Ingestion Transforms:**
   Filter out noisy events before writing to the workspace:
   ```kusto
   source
   | where EventLevel != "Verbose"
   | where not(ProcessName endswith "background_sync.exe")
   ```
2. **Commitment Tiers:**
   Switch from Pay-As-You-Go (\$2.30/GB) to Commitment Tiers (100 GB/day to 5,000 GB/day) to save up to 50% on predictable enterprise ingestion.
3. **Data Retention Policies:**
   Configure table-level retention to keep high-value security tables (`SigninLogs`, `AuditLogs`) for 365 days, while truncating verbose network telemetry after 30 days.

