# CIS Cloud Foundations Benchmark Reference Matrix (AWS, Azure, GCP)

This document maps essential Center for Internet Security (CIS) controls across AWS, Azure, and Google Cloud Platform (GCP) with corresponding audit CLI commands and evaluation criteria.

---

## 1. Amazon Web Services (AWS CIS Foundations Benchmark v3.0)

| Benchmark ID | Control Title | Profile | Audit CLI Command | Expected Finding |
|---|---|---|---|---|
| **AWS 1.1** | Avoid use of the 'root' account | Level 1 | `aws iam get-account-summary --query 'SummaryMap.AccountAccessKeysPresent'` | `0` (Zero root access keys) |
| **AWS 1.2** | Ensure multi-factor authentication (MFA) is enabled for all IAM users with a console password | Level 1 | `aws iam get-credential-report` (base64 decode and parse CSV for `password_enabled=true` and `mfa_active=false`) | Zero users without MFA |
| **AWS 1.3** | Ensure credentials unused for 90 days or greater are disabled | Level 1 | `aws iam generate-credential-report` followed by checking `password_last_used` and `access_key_1_last_used_date` | No active keys > 90 days |
| **AWS 2.1.1** | Ensure S3 Bucket Public Access Block is enabled at account level | Level 1 | `aws s3control get-public-access-block --account-id <ACCOUNT_ID>` | `BlockPublicAcls: true`, `IgnorePublicAcls: true`, `BlockPublicPolicy: true`, `RestrictPublicBuckets: true` |
| **AWS 2.1.2** | Ensure S3 bucket encryption is enabled | Level 1 | `aws s3api get-bucket-encryption --bucket <NAME>` | `ServerSideEncryptionConfiguration` exists with KMS/AES256 |
| **AWS 3.1** | Ensure CloudTrail is enabled across all regions | Level 1 | `aws cloudtrail describe-trails --query 'trailList[*].[Name,IsMultiRegionTrail,IncludeGlobalServiceEvents]'` | At least one multi-region trail with global events enabled |
| **AWS 3.2** | Ensure CloudTrail log file validation is enabled | Level 2 | `aws cloudtrail describe-trails --query 'trailList[*].[Name,LogFileValidationEnabled]'` | `true` |
| **AWS 4.1** | Ensure no Security Groups allow unrestricted ingress (`0.0.0.0/0`) on port 22 (SSH) | Level 1 | `aws ec2 describe-security-groups --filters Name=ip-permission.from-port,Values=22 Name=ip-permission.to-port,Values=22 Name=ip-permission.cidr,Values=0.0.0.0/0` | Empty result |
| **AWS 4.2** | Ensure no Security Groups allow unrestricted ingress (`0.0.0.0/0`) on port 3389 (RDP) | Level 1 | `aws ec2 describe-security-groups --filters Name=ip-permission.from-port,Values=3389 Name=ip-permission.to-port,Values=3389 Name=ip-permission.cidr,Values=0.0.0.0/0` | Empty result |
| **AWS 4.3** | Ensure the default security group of every VPC restricts all traffic | Level 2 | `aws ec2 describe-security-groups --filters Name=group-name,Values=default --query 'SecurityGroups[*].[GroupId,IpPermissions,IpPermissionsEgress]'` | Empty `IpPermissions` and `IpPermissionsEgress` |

---

## 2. Google Cloud Platform (GCP CIS Foundations Benchmark v3.0)

| Benchmark ID | Control Title | Profile | Audit CLI Command | Expected Finding |
|---|---|---|---|---|
| **GCP 1.1** | Ensure corporate login credentials are used instead of personal accounts | Level 1 | `gcloud projects get-iam-policy <PROJECT_ID> --format=json` (search for `@gmail.com` or `@yahoo.com`) | Zero external personal accounts |
| **GCP 1.3** | Ensure service account keys are not created for User-Managed Service Accounts | Level 1 | `gcloud iam service-accounts list --format="value(email)"` then `gcloud iam service-accounts keys list --iam-account=<EMAIL>` | Only `SYSTEM_MANAGED` keys; zero user-managed private key files |
| **GCP 1.4** | Ensure default service accounts are not granted Editor or Owner roles | Level 1 | `gcloud projects get-iam-policy <PROJECT_ID> --filter="bindings.members:compute@developer.gserviceaccount.com"` | Zero `roles/editor` or `roles/owner` |
| **GCP 2.1** | Ensure Cloud Audit Logging is configured for all services | Level 1 | `gcloud projects get-iam-policy <PROJECT_ID> --format="json(auditConfigs)"` | `auditConfigs` enabled for `allServices` with `ADMIN_READ`, `DATA_WRITE`, `DATA_READ` |
| **GCP 3.1** | Ensure Cloud Storage buckets are not anonymously or publicly accessible | Level 1 | `gcloud storage buckets list --format="value(name)"` then `gcloud storage buckets get-iam-policy gs://<BUCKET>` | Zero `allUsers` or `allAuthenticatedUsers` bindings |
| **GCP 3.2** | Ensure Cloud Storage buckets have uniform bucket-level access enabled | Level 1 | `gcloud storage buckets describe gs://<BUCKET> --format="value(uniform_bucket_level_access)"` | `True` |
| **GCP 3.6** | Ensure Cloud Storage buckets are encrypted with Customer Managed Encryption Keys (CMEK) | Level 2 | `gcloud storage buckets describe gs://<BUCKET> --format="value(encryption.defaultKmsKeyName)"` | Non-empty KMS key URI |
| **GCP 4.1** | Ensure default network does not exist in a project | Level 2 | `gcloud compute networks list --filter="name=default"` | Empty result (default network deleted) |
| **GCP 4.2** | Ensure legacy networks do not exist | Level 1 | `gcloud compute networks list --filter="mode=legacy"` | Empty result |
| **GCP 4.3** | Ensure no firewall rules allow unrestricted ingress (`0.0.0.0/0`) on port 22 | Level 1 | `gcloud compute firewall-rules list --filter="direction=INGRESS AND (allowed[].ports:22 OR allowed[].ports:0-65535) AND sourceRanges:0.0.0.0/0"` | Empty result |

---

## 3. Microsoft Azure (Azure CIS Foundations Benchmark v2.1)

| Benchmark ID | Control Title | Profile | Audit CLI Command | Expected Finding |
|---|---|---|---|---|
| **AZ 1.1** | Ensure Security Defaults is enabled on Microsoft Entra ID | Level 1 | `az rest --method get --url "https://graph.microsoft.com/v1.0/policies/identitySecurityDefaultsEnforcementPolicy"` | `"isEnabled": true` |
| **AZ 1.3** | Ensure MFA is enabled for all users in administrative roles | Level 1 | `az ad user list --query '[*].[userPrincipalName,accountEnabled]'` | Conditional Access MFA active for all admins |
| **AZ 2.1** | Ensure Microsoft Defender for Cloud is enabled across subscription | Level 1 | `az security pricing list --query 'value[*].[name,pricingTier]'` | `pricingTier: Standard` on key resource types |
| **AZ 3.1** | Ensure storage account public access is disallowed | Level 1 | `az storage account list --query '[*].[name,allowBlobPublicAccess]'` | `allowBlobPublicAccess: false` for all accounts |
| **AZ 3.5** | Ensure storage account default network access rule is set to deny | Level 1 | `az storage account list --query '[*].[name,networkRuleSet.defaultAction]'` | `defaultAction: Deny` |
| **AZ 5.1** | Ensure Network Security Groups (NSGs) disallow unrestricted inbound access on port 22 | Level 1 | `az network nsg rule list --nsg-name <NSG> -g <RG> --query "[?access=='Allow' && direction=='Inbound' && destinationPortRange=='22' && (sourceAddressPrefix=='*' || sourceAddressPrefix=='Internet')].name"` | Empty result |
| **AZ 5.2** | Ensure Network Security Groups (NSGs) disallow unrestricted inbound access on port 3389 | Level 1 | `az network nsg rule list --nsg-name <NSG> -g <RG> --query "[?access=='Allow' && direction=='Inbound' && destinationPortRange=='3389' && (sourceAddressPrefix=='*' || sourceAddressPrefix=='Internet')].name"` | Empty result |

---

## 4. Scoring Algorithm

Overall compliance percentage is computed as:

$$\text{Compliance Score (\%)} = \left( \frac{\sum_{i=1}^{N} \text{Passed}_i \times W_i}{\sum_{i=1}^{N} W_i} \right) \times 100$$

Where:
- $W_i = 3.0$ for **Critical Severity** controls (e.g., open root access keys, public S3 buckets, `0.0.0.0/0` SSH ingress).
- $W_i = 2.0$ for **High Severity** controls (e.g., missing multi-region trail, unencrypted volumes).
- $W_i = 1.0$ for **Medium/Low Severity** controls (e.g., log retention thresholds, minor tagging).
