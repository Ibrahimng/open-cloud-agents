---
name: iam-policy-synthesizer
description: Transform overly broad wildcard IAM permissions (*:*) into precise, resource-scoped, least-privilege IAM policies with condition keys.
---

# IAM Least-Privilege Policy Synthesis

## The Anti-Pattern: Wildcards
```json
// PROHIBITED IN PRODUCTION
{
  "Effect": "Allow",
  "Action": "*",
  "Resource": "*"
}
```

## The Synthesized Standard: Action & Resource Scoping
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadOrdersStorageOnly",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::company-prod-orders",
        "arn:aws:s3:::company-prod-orders/*"
      ],
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "true"
        }
      }
    }
  ]
}
```

## Policy Synthesis Procedure
1. **Analyze CloudTrail Events:** Identify actual actions invoked by the identity over a 30-day window using Athena / CloudTrail Lake.
2. **Remove Write/Delete Privileges:** Isolate read operations (`Get*`, `List*`, `Describe*`) from mutation operations (`Put*`, `Create*`, `Delete*`).
3. **Bind to Specific ARNs:** Replace `Resource: "*"` with exact resource ARNs.
4. **Attach Security Conditions:** Enforce `aws:SecureTransport: true` (HTTPS only) and IP / VPC endpoint restriction condition keys.

