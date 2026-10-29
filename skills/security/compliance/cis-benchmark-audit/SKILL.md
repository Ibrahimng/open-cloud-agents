---
name: cis-benchmark-audit
description: Audit cloud infrastructure configurations across AWS, Azure, and GCP against CIS (Center for Internet Security) Foundation Benchmarks to uncover security posture drifts.
---

# CIS Cloud Benchmark Security Audit

## Critical Benchmark Checks Across Clouds

### AWS CIS Foundations Benchmark

- **IAM (Section 1):**
    - Ensure MFA is enabled for all IAM users with console access.
    - Ensure no root account access keys exist.
    - Ensure credentials unused for 90 days are disabled.
- **Storage & Logging (Section 2 & 3):**
    - Ensure CloudTrail is enabled across all regions and encrypted with KMS.
    - Ensure S3 bucket public access block is applied at the account and bucket level.
- **Networking (Section 4 & 5):**
    - Ensure no security group allows unrestricted ingress (`0.0.0.0/0`) on port 22 (SSH) or 3389 (RDP).
    - Ensure default VPCs have all default security group ingress/egress rules removed.

### Azure CIS Foundations Benchmark

- **Identity & Access Management:**
    - Ensure Security Defaults or Conditional Access MFA is enabled for all administrative accounts.
    - Ensure external guest user invitations are restricted to approved administrators.
- **Storage & Database:**
    - Ensure Storage Account public blob access is disallowed (`allowBlobPublicAccess: false`).
    - Enforce TLS 1.2+ minimum version on storage accounts and databases.
- **Networking & Logging:**
    - Ensure Network Security Groups (NSGs) disallow unrestricted inbound access on port 22 and 3389.
    - Ensure Microsoft Defender for Cloud is enabled across subscription resources.

### GCP CIS Foundations Benchmark

- **Identity & Access Management:**
    - Ensure corporate login credentials are used instead of personal accounts.
    - Ensure service account keys are not created for User-Managed Service Accounts (prefer Workload Identity).
    - Ensure default compute service accounts do not hold Editor or Owner roles.
- **Storage & Database:**
    - Ensure Cloud Storage buckets are not anonymously or publicly accessible (`allUsers`).
    - Ensure Cloud Storage uniform bucket-level access is enabled.
- **Networking & Logging:**
    - Ensure Cloud Audit Logging is configured for all services.
    - Ensure default VPC network is deleted and firewall rules restrict unrestricted port 22 access.

### Audit Command Examples

```bash
# Automated multi-cloud sanity audit script
bash skills/security/compliance/cis-benchmark-audit/scripts/audit_cis_foundations.sh

# AWS: Check for unencrypted S3 buckets
aws s3api list-buckets --query 'Buckets[*].Name' --output text | tr '\t' '\n' | while read -r bucket; do
  aws s3api get-bucket-encryption --bucket "$bucket" 2>&1 | grep -q "ServerSideEncryptionConfiguration" || echo "UNENCRYPTED: $bucket"
done

# AWS: Verify CloudTrail multi-region logging
aws cloudtrail describe-trails --query 'trailList[*].[Name,IsMultiRegionTrail,KmsKeyId]' --output table

# GCP: Check organization constraint for uniform bucket access
gcloud storage buckets list --format="value(name)" | while read -r bucket; do
  gcloud storage buckets describe "gs://$bucket" --format="value(uniform_bucket_level_access)"
done

# Azure: Audit Storage Account public access setting
az storage account list --query '[*].[name,allowBlobPublicAccess]' --output table
```

---

## 📚 References & Tools

- [cis-control-mappings.md](references/cis-control-mappings.md): Multi-cloud CIS control crosswalk across AWS, Azure, and GCP.
- `scripts/audit_cis_foundations.sh`: Automated baseline audit script for CIS Foundation security controls.

