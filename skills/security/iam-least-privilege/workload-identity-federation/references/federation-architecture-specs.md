# Workload Identity Federation Architecture Specifications

```text
[GitHub Actions Runner]                     [AWS Security Token Service (STS)]
         │                                                    │
         ├────── 1. Request JWT Token (id-token: write) ──────┤
         │       (Includes repo, actor, environment claims)   │
         │                                                    │
         ├────── 2. AssumeRoleWithWebIdentity(JWT) ───────────►
         │                                                    │
         │       3. Verifies OIDC Thumbprint via Issuer URL   │
         │       (token.actions.githubusercontent.com)        │
         │                                                    │
         ◄────── 4. Returns Temporary Credentials (1 Hour) ───┤
```

## JWT Claim Verification Table

| Claim | Typical Value | Purpose |
|---|---|---|
| `iss` | `https://token.actions.githubusercontent.com` | Identity of the token issuer |
| `aud` | `sts.amazonaws.com` (or Azure Client ID) | Target audience |
| `sub` | `repo:<org>/<repo>:ref:refs/heads/main` | Subject repository and branch filter |
| `job_workflow_ref` | `org/repo/.github/workflows/deploy.yml@refs/heads/main` | Workflow execution provenance |
