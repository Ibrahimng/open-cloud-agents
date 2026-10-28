# Microsoft Sentinel KQL Threat Hunting Library

This library contains production Kusto Query Language (KQL) detections mapped to MITRE ATT&CK tactics for cloud identity, infrastructure, and multi-cloud telemetry.

---

## 1. Initial Access & Credential Abuse (T1078 / T1110)

### 1.1 High-Volume Password Spray Across Multiple Accounts (T1110.003)
Detects a single external IP attempting to authenticate against multiple distinct user accounts with failed credentials:

```kusto
SigninLogs
| where TimeGenerated > ago(1h)
| where ResultType in (50126, 50053) // Invalid password or locked account
| summarize 
    FailedAccountsCount = dcount(UserPrincipalName), 
    FailedAttempts = count(), 
    TargetAccounts = make_set(UserPrincipalName, 20) 
    by IPAddress, AppDisplayName, Location
| where FailedAccountsCount >= 5 and FailedAttempts >= 15
| extend IPCustomEntity = IPAddress
| project IPAddress, FailedAccountsCount, FailedAttempts, TargetAccounts, AppDisplayName, Location, IPCustomEntity
```

### 1.2 Impossible Travel / Anomalous Sign-In Locations (T1078)
Identifies accounts signing in successfully from geographically distant locations within a physically impossible timeframe:

```kusto
let timeWindow = 6h;
SigninLogs
| where TimeGenerated > ago(timeWindow)
| where ResultType == 0 // Successful sign-in
| extend Latitude = toreal(parse_json(LocationDetails).geoCoordinates.latitude)
| extend Longitude = toreal(parse_json(LocationDetails).geoCoordinates.longitude)
| where isnotnull(Latitude) and isnotnull(Longitude)
| project TimeGenerated, UserPrincipalName, IPAddress, Location, Latitude, Longitude
| order by UserPrincipalName, TimeGenerated asc
| serialize
| extend PrevLocation = prev(Location), PrevTime = prev(TimeGenerated), PrevIP = prev(IPAddress)
| extend PrevLat = prev(Latitude), PrevLon = prev(Longitude), PrevUser = prev(UserPrincipalName)
| where UserPrincipalName == PrevUser and Location != PrevLocation
| extend TimeDiffMinutes = datetime_diff('minute', TimeGenerated, PrevTime)
| where TimeDiffMinutes between (1 .. 120)
| extend AccountCustomEntity = UserPrincipalName
| extend IPCustomEntity = IPAddress
| project UserPrincipalName, TimeGenerated, Location, IPAddress, PrevTime, PrevLocation, PrevIP, TimeDiffMinutes, AccountCustomEntity, IPCustomEntity
```

---

## 2. Privilege Escalation & Persistence (T1098 / T1078.004)

### 2.1 Global Administrator or Privileged Role Assignment (T1098)
Detects when a user or service principal is added to high-privilege directory roles in Microsoft Entra ID:

```kusto
AuditLogs
| where TimeGenerated > ago(2h)
| where OperationName has "Add member to role"
| where TargetResources[0].modifiedProperties[1].newValue has "Global Administrator" 
     or TargetResources[0].modifiedProperties[1].newValue has "Privileged Role Administrator"
     or TargetResources[0].modifiedProperties[1].newValue has "Security Administrator"
| extend Actor = tostring(InitiatedBy.user.userPrincipalName)
| extend TargetUser = tostring(TargetResources[0].userPrincipalName)
| extend AssignedRole = tostring(TargetResources[0].modifiedProperties[1].newValue)
| extend AccountCustomEntity = TargetUser
| project TimeGenerated, Actor, TargetUser, AssignedRole, AccountCustomEntity
```

### 2.2 New Service Principal Credential Added by Non-Admin (T1098.001)
Detects addition of secrets or certificates to existing applications or service principals (backdoor creation):

```kusto
AuditLogs
| where TimeGenerated > ago(2h)
| where OperationName in ("Update application – Certificates and secrets management", "Add service principal credentials")
| extend Initiator = tostring(InitiatedBy.user.userPrincipalName)
| extend AppName = tostring(TargetResources[0].displayName)
| extend AppId = tostring(TargetResources[0].id)
| extend AccountCustomEntity = Initiator
| project TimeGenerated, Initiator, AppName, AppId, OperationName, Result, AccountCustomEntity
```

---

## 3. Defense Evasion & Impact (T1562 / T1552)

### 3.1 Azure Network Security Group Rule Modified to Allow 0.0.0.0/0 (T1562.001)
Detects administrative modifications opening ingress ports to the public internet:

```kusto
AzureActivity
| where TimeGenerated > ago(2h)
| where OperationNameValue has "Microsoft.Network/networkSecurityGroups/securityRules/write"
| where ActivityStatusValue == "Success"
| extend RuleConfig = parse_json(Properties)
| extend SourceRange = tostring(RuleConfig.requestbody)
| where SourceRange contains "0.0.0.0" or SourceRange contains "*"
| extend Caller = Caller
| extend Resource = Resource
| extend AccountCustomEntity = Caller
| project TimeGenerated, Caller, Resource, OperationNameValue, ActivityStatusValue, AccountCustomEntity
```

### 3.2 Mass Secret Extraction from Azure Key Vault (T1552.004)
Detects abnormal volume of `SecretGet` operations on an Azure Key Vault:

```kusto
AzureDiagnostics
| where TimeGenerated > ago(1h)
| where ResourceProvider == "MICROSOFT.KEYVAULT"
| where OperationName == "SecretGet" and ResultType == "Success"
| summarize SecretGetCount = count(), AccessedSecrets = make_set(id_s, 20) by CallerIPAddress, identity_claim_upn_s, Resource
| where SecretGetCount >= 10
| extend AccountCustomEntity = identity_claim_upn_s
| extend IPCustomEntity = CallerIPAddress
| project Resource, identity_claim_upn_s, CallerIPAddress, SecretGetCount, AccessedSecrets, AccountCustomEntity, IPCustomEntity
```
