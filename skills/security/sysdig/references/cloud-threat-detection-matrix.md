# Sysdig Cloud Threat Detection & Cloud Connector Matrix

Sysdig Cloud Connector integrates directly with cloud audit trails (AWS CloudTrail, GCP Cloud Audit Logs, Azure Activity Logs) to detect identity abuse and control plane misconfigurations.

---

## 1. Cloud Connector Architecture

```
 ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
 │ AWS CloudTrail  │       │ GCP Audit Logs  │       │ Azure Event Hub │
 └────────┬────────┘       └────────┬────────┘       └────────┬────────┘
          │ EventBridge             │ Cloud Pub/Sub           │ Event Grid
          ▼                         ▼                         ▼
 ┌─────────────────────────────────────────────────────────────────────┐
 │                     Sysdig Cloud Connector                          │
 │         Streams events against Falco-compatible YAML rules          │
 └──────────────────────────────────┬──────────────────────────────────┘
                                    ▼
         Alerting & Automated Response (Slack, PagerDuty, SIEM)
```

---

## 2. Threat Detection Rules Matrix

| Provider | Threat Scenario | Detection Logic | Severity |
|---|---|---|---|
| **AWS** | Root Account Login | `eventName = "ConsoleLogin" and userIdentity.type = "Root"` | `CRITICAL` |
| **AWS** | Unattached KMS Key Scheduled for Deletion | `eventName = "ScheduleKeyDeletion"` | `HIGH` |
| **AWS** | Security Group Ingress Opened to World | `eventName = "AuthorizeSecurityGroupIngress" and requestParameters.ipPermissions.items[].ipRanges.items[].cidrIp = "0.0.0.0/0"` | `CRITICAL` |
| **AWS** | Disabling CloudTrail Logging | `eventName in ("StopLogging", "DeleteTrail")` | `EMERGENCY` |
| **GCP** | Service Account Key Exported | `protoPayload.methodName = "google.iam.admin.v1.CreateServiceAccountKey"` | `HIGH` |
| **GCP** | Cloud Storage Bucket IAM Public Grant | `protoPayload.methodName = "storage.setIamPermissions" and protoPayload.serviceData.policyDelta.bindingDeltas[].member in ("allUsers", "allAuthenticatedUsers")` | `CRITICAL` |
| **GCP** | Firewall Rule Permitting Inbound SSH | `protoPayload.methodName = "compute.firewalls.insert" and protoPayload.request.allowed[].ports:22` | `CRITICAL` |
| **Azure** | Global Admin Role Assignment | `operationName = "Microsoft.Authorization/roleAssignments/write" and properties.requestbody contains "Global Administrator"` | `CRITICAL` |
| **Azure** | Network Security Group Inbound Allow Any | `operationName = "Microsoft.Network/networkSecurityGroups/securityRules/write" and properties.requestbody contains "0.0.0.0"` | `HIGH` |
