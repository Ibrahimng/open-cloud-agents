---
name: github-actions-hardening
description: Author secure, least-privilege GitHub Actions workflows utilizing OIDC cloud federation (no long-lived keys), SHA-pinned third-party actions, and secret-masking guardrails.
---

# GitHub Actions Workflow Hardening

## Key Security Directives
1. **Zero Long-Lived Cloud Credentials**:
   - Ban storing `AWS_ACCESS_KEY_ID` or GCP service account JSON keys in GitHub Secrets.
   - Use OpenID Connect (OIDC) identity federation (`aws-actions/configure-aws-credentials`, `google-github-actions/auth`).
2. **Explicit Least-Privilege Permissions**:
   - Always declare a top-level `permissions` block in every workflow.
   - Restrict write access strictly to jobs that require it.
3. **SHA-256 Pin Third-Party Actions**:
   - Pin third-party actions to immutable commit SHAs rather than mutable tags (e.g. `actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2`).

## Hardened Workflow Boilerplate (AWS OIDC Deployment)

```yaml
name: Deploy Production Service

on:
  push:
    branches: [main]

permissions:
  id-token: write   # Required for requesting the OIDC JWT token
  contents: read    # Read-only repository access

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: false

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Checkout Code
        uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2

      - name: Authenticate to AWS via OIDC
        uses: aws-actions/configure-aws-credentials@e3ddf14a3dc1e892a2987e1b7894c518000ea4bb # v4.0.2
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-actions-deploy-role
          aws-region: us-east-1

      - name: Verify Identity
        run: aws sts get-caller-identity
```

## Security Linting
Validate workflows prior to committing using `actionlint`:
```bash
actionlint -color
```
