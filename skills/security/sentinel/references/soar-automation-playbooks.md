# Microsoft Sentinel SOAR Automation Playbooks (Azure Logic Apps)

This guide details the design, triggers, and deployment of Security Orchestration, Automation, and Response (SOAR) playbooks using Azure Logic Apps.

---

## 1. SOAR Trigger Models

Sentinel playbooks run as Azure Logic Apps (Standard or Consumption) using the Microsoft Sentinel Connector:

1. **Incident Trigger (`When a Microsoft Sentinel Incident is created or updated`):**
   Fires once per incident; provides access to all aggregated alerts, entities, and comments.
2. **Alert Trigger (`When a Microsoft Sentinel Alert is triggered`):**
   Fires on each individual alert rule execution.
3. **Entity Trigger (`When an entity is selected in incident`):**
   Manual analyst trigger executed directly from the investigation pane.

---

## 2. Production Playbook Recipes

### 2.1 Identity Containment: Revoke Entra ID User Sessions
When a high-severity alert fires involving a user account (e.g. credential theft, impossible travel):

```json
{
  "definition": {
    "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
    "actions": {
      "Get_Accounts": {
        "type": "ApiConnection",
        "inputs": {
          "host": {
            "connection": {
              "name": "@parameters('$connections')['azuresentinel']['connectionId']"
            }
          },
          "method": "post",
          "path": "/Incidents/subscriptions/@{triggerBody()?['workspaceInfo']?['subscriptionId']}/resourceGroups/@{triggerBody()?['workspaceInfo']?['resourceGroupName']}/workspaces/@{triggerBody()?['workspaceInfo']?['workspaceName']}/incidents/@{triggerBody()?['object']?['properties']?['incidentNumber']}/entities"
        }
      },
      "For_each_account": {
        "type": "Foreach",
        "foreach": "@body('Get_Accounts')?['Entities']",
        "actions": {
          "Revoke_Sessions": {
            "type": "ApiConnection",
            "inputs": {
              "host": {
                "connection": {
                  "name": "@parameters('$connections')['azuread']['connectionId']"
                }
              },
              "method": "post",
              "path": "/users/@{items('For_each_account')?['Name']}/revokeSignInSessions"
            }
          }
        }
      },
      "Add_Comment_to_Incident": {
        "type": "ApiConnection",
        "inputs": {
          "host": {
            "connection": {
              "name": "@parameters('$connections')['azuresentinel']['connectionId']"
            }
          },
          "method": "post",
          "path": "/Incidents/comments",
          "body": {
            "message": "Automated SOAR Action: Active OAuth sessions revoked for compromised account."
          }
        }
      }
    }
  }
}
```

### 2.2 Endpoint Quarantine: Isolate Host via Defender for Endpoint
Calls the Microsoft Defender for Endpoint REST API:

```http
POST https://api.securitycenter.microsoft.com/api/machines/{MachineId}/isolate
Content-Type: application/json
Authorization: Bearer <TOKEN>

{
  "Comment": "Automated isolation by Microsoft Sentinel incident #1042 - Ransomware activity detected",
  "IsolationType": "Full"
}
```

### 2.3 Perimeter Defense: Add IP to Azure Firewall Drop Group
Appends malicious source IP addresses to an Azure Firewall IP Group:

```bash
az network ip-group update \
  --name "ipg-malicious-quarantine" \
  --resource-group "rg-network-prod" \
  --add ipAddresses "198.51.100.42"
```

---

## 3. Human-in-the-Loop Approval via Teams Adaptive Card

Avoid accidental automated disruptions by inserting an interactive approval card before taking high-impact isolation actions:

```json
{
  "type": "AdaptiveCard",
  "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
  "version": "1.3",
  "body": [
    {
      "type": "TextBlock",
      "text": "🚨 Microsoft Sentinel High-Severity Alert",
      "weight": "Bolder",
      "size": "Medium"
    },
    {
      "type": "FactSet",
      "facts": [
        { "title": "Incident ID:", "value": "@{triggerBody()?['object']?['properties']?['incidentNumber']}" },
        { "title": "Title:", "value": "@{triggerBody()?['object']?['properties']?['title']}" },
        { "title": "Affected User:", "value": "@{items('For_each_account')?['Name']}" }
      ]
    }
  ],
  "actions": [
    { "type": "Action.Submit", "title": "Approve User Session Revoke", "data": { "decision": "Approve" } },
    { "type": "Action.Submit", "title": "Dismiss & Mark False Positive", "data": { "decision": "Dismiss" } }
  ]
}
```

