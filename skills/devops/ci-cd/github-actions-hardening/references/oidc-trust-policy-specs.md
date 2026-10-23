# OIDC Cloud Federation Trust Policy Specifications

## AWS IAM Role Trust Policy for GitHub Actions
Allows GitHub Actions runners from specific repositories to assume an IAM role without long-lived access keys:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::<ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:<ORG_OR_USER>/<REPO>:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

## Azure Federated Identity Credential
In Microsoft Entra ID (Azure AD), configure a Federated Credential on the target App Registration / Managed Identity:
- **Issuer:** `https://token.actions.githubusercontent.com`
- **Subject Identifier:** `repo:<ORG_OR_USER>/<REPO>:environment:production`
- **Audience:** `api://AzureADTokenExchange`

## GCP Workload Identity Pool Provider
- **Provider URL:** `https://token.actions.githubusercontent.com`
- **Attribute Mapping:**
  - `google.subject` = `assertion.sub`
  - `attribute.repository` = `assertion.repository`
  - `attribute.actor` = `assertion.actor`

