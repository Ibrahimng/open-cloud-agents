---
name: git-secret-leak-remediation
description: Detect leaked API keys, tokens, or credentials in Git history and execute immediate revocation, rotation, and CloudTrail blast-radius forensics based on real-world incident runbooks.
---

# Git Secret Leak Triage & Remediation Runbook

## Purpose & Scope
This skill provides an emergency response protocol for compromised cloud credentials, tokens, or private certificates pushed to source control or logged in CI/CD artifacts.

---

## Real-Life Incident Case: Compromised IAM Key via Public Fork PR

### Background & What Happened
A developer submitted a pull request from a public fork. The GitHub Actions CI workflow utilized `pull_request_target` instead of `pull_request`, exposing repository secrets to untrusted code. 
An attacker injected a curl command into the test runner to exfiltrate an AWS administrator access key (`AKIA...`) to an external webhook. Within 7 minutes, automated adversary scanners began enumerating S3 buckets and launching GPU EC2 instances for crypto-mining.

---

## Real-Time Emergency Triage Protocol (Order of Operations)

### Phase 1: Instant Neutralization (First 60 Seconds)
Do NOT spend time investigating or rewriting Git history first. **Deactivate the key immediately**:
```bash
# Deactivate key via AWS CLI immediately
aws iam update-access-key --access-key-id <LEAKED_KEY_ID> --status Inactive --user-name <USER_NAME>

# Attach an explicit DENY-ALL inline policy to the user identity to sever any active STS sessions
aws iam put-user-policy --user-name <USER_NAME> --policy-name EmergencyDenyAll --policy-document '{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Deny",
    "Action": "*",
    "Resource": "*"
  }]
}'
```

### Phase 2: Live CloudTrail Blast-Radius Forensics
Identify what actions the attacker performed between exfiltration and deactivation:
```bash
# Query CloudTrail for all API calls initiated by the compromised Access Key ID
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=AccessKeyId,AttributeValue=<LEAKED_KEY_ID> \
  --start-time $(date -u -v-2H +%Y-%m-%dT%H:%M:%SZ) \
  --query 'Events[*].[EventTime,EventName,SourceIPAddress,ReadOnly]' \
  --output table
```
Inspect especially for:
- `CreateUser`, `CreateAccessKey` (Backdoor persistence)
- `RunInstances` (Crypto-mining or compute hijacking)
- `PutBucketPolicy`, `ModifyVpcPeeringConnection` (Perimeter breach)

### Phase 3: Scrub Secret from Git Reflogs & Tree
Once the key is deactivated and forensic logs are collected:
```bash
# Scrub exact key string from all commits and branches
pip install git-filter-repo
git filter-repo --replace-text <(echo '<LEAKED_KEY_SECRET>==>REVOKED_AND_ROTATED')

# Force push scrubbed history
git push origin --force --all
git push origin --force --tags
```

---

## Continuous Self-Knowledge Enhancement Loop

When the security incident is contained:
1. **Analyze Vulnerability Vector:** (e.g. `pull_request_target` event in GitHub Actions).
2. **Auto-Generate Preventative Policy:** Add a check in [`skills/devops/ci-cd/github-actions-hardening/SKILL.md`](../../devops/ci-cd/github-actions-hardening/SKILL.md) banning `pull_request_target` with secrets.
3. **Update Pre-Merge Auditor Rules:** Update [`agents/7-agent-master-suite/devsecops-reviewer.md`](../../../agents/7-agent-master-suite/devsecops-reviewer.md) to flag any workflow change introducing secret access in fork PRs.
