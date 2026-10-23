---
name: workload-identity-federation
description: Eliminate static cloud credentials and API keys by configuring Workload Identity Federation across GitHub Actions, Kubernetes pods (IRSA/GKE Workload Identity), and cloud providers.
---

# Workload Identity Federation Architecture

## Why Static Keys Must Be Eliminated
- Long-lived keys (`AKIA...`) leak into git repos, developer laptops, and CI logs.
- They lack automated rotation and bypass short-lived session token boundaries.
- **Federated OIDC:** Issues cryptographically verified, short-lived (15–60 min) STS tokens directly to workloads based on verifiable claims (repository name, environment, branch).

## GitHub Actions to AWS IAM Trust Policy
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:Ibrahimng/open-cloud-agents:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

## Kubernetes IRSA (IAM Roles for Service Accounts)
Annotate your Kubernetes ServiceAccount with the IAM role ARN:
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: order-processor-sa
  namespace: prod
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/order-processor-pod-role
```
The AWS SDK automatically retrieves temporary credentials via the mounted projected service account token.

