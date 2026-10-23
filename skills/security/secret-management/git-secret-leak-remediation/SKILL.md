---
name: git-secret-leak-remediation
description: Detect leaked API keys, tokens, or credentials in Git history and execute immediate revocation, rotation, and commit history rewriting using git-filter-repo.
---

# Git Secret Leak Triage & Remediation Runbook

## Immediate Priority Rule: Revoke First, Rewrite Second
> [!CAUTION]
> If a secret (AWS key, Stripe token, database password) has been pushed to a remote Git repository, **assume it is compromised immediately**. Rewriting Git history alone does NOT secure the system. You must **revoke/rotate the credential in the cloud provider before touching Git**.

## Step-by-Step Incident Workflow

### Step 1: Revoke & Rotate
1. Deactivate or delete the compromised credential in the target provider.
2. Issue a replacement credential and update secret management stores (Vault, AWS Secrets Manager, GitHub Secrets).
3. Check access logs (CloudTrail, audit logs) for unauthorized API calls using the leaked key ID.

### Step 2: Remove Secret from Git History with `git-filter-repo`
Do NOT use `git reset` or delete-commit PRs; the secret remains in Git reflogs.
```bash
# 1. Install git-filter-repo if missing
pip install git-filter-repo

# 2. Scrub specific string across all commits and tags
git filter-repo --replace-text <(echo 'compromised_secret_value==>REDACTED_SECRET')

# 3. Force push cleaned history to remote
git push origin --force --all
git push origin --force --tags
```

### Step 3: Prevent Future Leaks with Pre-commit Hooks
Add Gitleaks pre-commit scanning to block secrets before commit creation:
```bash
brew install gitleaks
gitleaks detect --source . -v
```
