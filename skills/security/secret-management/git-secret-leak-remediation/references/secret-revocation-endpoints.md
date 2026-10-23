# Emergency Credential Revocation Cheat Sheet

## 1. AWS IAM Access Key
```bash
# Immediately deactivate
aws iam update-access-key --access-key-id <ACCESS_KEY_ID> --status Inactive --user-name <USER_NAME>
# Sever active STS sessions
aws iam put-user-policy --user-name <USER_NAME> --policy-name RevokeAllSessions --policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Deny","Action":"*","Resource":"*"}]}'
```

## 2. GitHub Personal Access Token (PAT)
If a GitHub PAT leaks, revoke via GitHub API:
```bash
curl -X DELETE -H "Authorization: Bearer <ADMIN_OR_USER_TOKEN>" \
  https://api.github.com/user/tokens/<TOKEN_ID>
```

## 3. Stripe Secret Keys
Rotate immediately via Stripe Dashboard or CLI:
```bash
stripe keys expire <KEY_ID>
```

## 4. Slack Bot Tokens (`xoxb-...`)
Revoke token via Slack Web API:
```bash
curl -X POST https://slack.com/api/auth.revoke -d "token=<LEAKED_SLACK_TOKEN>"
```

