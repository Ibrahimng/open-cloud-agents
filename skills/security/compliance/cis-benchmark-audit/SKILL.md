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

### Audit Command Examples

```bash
# Check for unencrypted S3 buckets
aws s3api list-buckets --query 'Buckets[*].Name' --output text | tr '\t' '\n' | while read -r bucket; do
  aws s3api get-bucket-encryption --bucket "$bucket" 2>&1 | grep -q "ServerSideEncryptionConfiguration" || echo "UNENCRYPTED: $bucket"
done

# Verify CloudTrail multi-region logging
aws cloudtrail describe-trails --query 'trailList[*].[Name,IsMultiRegionTrail,KmsKeyId]' --output table
```

