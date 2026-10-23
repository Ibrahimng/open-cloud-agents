---
name: soc2-evidence-collector
description: Automatically gather, format, and document technical audit evidence for SOC 2 Type II trust service criteria (Security, Availability, Confidentiality).
---

# SOC 2 Type II Technical Evidence Collection

## Common Criteria (CC) Mapping

| SOC 2 Criteria | Cloud Control Evidence | Automated Collection Method |
|---|---|---|
| **CC6.1 (Access Controls)** | Multi-factor authentication, SSO enforcement, IAM role separation | IAM user list, IdP sign-in policies |
| **CC6.3 (Least Privilege)** | Automated quarterly access reviews, revoked stale accounts | `aws iam get-account-authorization-details` |
| **CC6.6 / CC6.7 (Data Protection)** | TLS in transit (>= TLS 1.2), KMS encryption at rest | CloudFront/ALB SSL policies, RDS/Storage encryption |
| **CC7.2 (Vulnerability Mgmt)** | Container image scanning, weekly patch verification | Trivy / AWS Inspector scan reports |
| **CC8.1 (Change Management)** | Git branch protection, peer reviews, CI/CD promotion | GitHub API pull request sign-offs |

## Automated Evidence Collection Script (Bash)
```bash
#!/usr/bin/env bash
set -euo pipefail

OUTPUT_DIR="soc2-evidence-$(date +%Y%m%d)"
mkdir -p "$OUTPUT_DIR"

echo "Collecting IAM credential report..."
aws iam generate-credential-report >/dev/null
sleep 3
aws iam get-credential-report --query 'Content' --output text | base64 -d > "$OUTPUT_DIR/iam-credential-report.csv"

echo "Collecting encryption at rest status for RDS..."
aws rds describe-db-instances \
  --query 'DBInstances[*].[DBInstanceIdentifier,StorageEncrypted,KmsKeyId]' \
  --output table > "$OUTPUT_DIR/rds-encryption-status.txt"

echo "Evidence collected in: $OUTPUT_DIR"
```

