# Microsoft Sentinel Incident Triage, UEBA & Investigation Graph

This reference guides security analysts through the triage lifecycle, User and Entity Behavior Analytics (UEBA), and entity mapping in Microsoft Sentinel.

---

## 1. Entity Mapping Architecture

Sentinel requires KQL queries to project columns mapped to well-defined entity types so the correlation engine can construct the unified **Investigation Graph**.

| Entity Type | Required Fields | Example Mapping in KQL |
|---|---|---|
| **Account** | `Name`, `UPN`, `AadUserId` | `extend AccountCustomEntity = UserPrincipalName` |
| **Host** | `HostName`, `DnsDomain`, `AzureResourceId` | `extend HostCustomEntity = Computer` |
| **IP** | `Address` | `extend IPCustomEntity = IPAddress` |
| **URL** | `Url` | `extend URLCustomEntity = RequestUrl` |
| **FileHash** | `Algorithm`, `Value` | `extend FileHashCustomEntity = SHA256` |

---

## 2. User and Entity Behavior Analytics (UEBA)

UEBA builds baseline behavioral profiles for accounts, hosts, and IP addresses across 30 days of telemetry.

### Built-in UEBA Tables
- **`IdentityInfo`:** Synchronized directory metadata from Microsoft Entra ID (manager, department, job title, risk level).
- **`UserPeerAnalytics`:** Groups peers based on organizational structure to detect anomalous actions relative to teammates.
- **`Anomalies`:** Machine-learning generated anomaly events (e.g. abnormal volume of data downloaded, first-time access to application).

### Querying UEBA Anomalies
```kusto
Anomalies
| where TimeGenerated > ago(24h)
| where AnomalyScore > 70
| extend User = tostring(parse_json(ExtendedProperties).UserPrincipalName)
| project TimeGenerated, AnomalyType, AnomalyScore, User, Description
```

---

## 3. Incident Severity & Classification

When closing an incident, record root-cause classification for continuous learning and metric reporting:

| Classification | Meaning | Follow-Up Action |
|---|---|---|
| **True Positive - Suspicious Activity** | Legitimate threat or policy breach confirmed. | Trigger containment playbook, update threat intelligence indicators, conduct post-incident review. |
| **False Positive - Inaccurate Data** | Alert fired due to parsing failure or corrupt log source. | Update data connector transform or log parser. |
| **False Positive - Incorrect Rule Logic** | Query logic too broad, matching benign business activities. | Tune analytics rule thresholds, add whitelist exceptions. |
| **Benign Positive - Expected Activity** | Action was unauthorized in theory but approved in practice (e.g. penetration testing, maintenance window). | Suppress rule for the specific actor or time window. |
