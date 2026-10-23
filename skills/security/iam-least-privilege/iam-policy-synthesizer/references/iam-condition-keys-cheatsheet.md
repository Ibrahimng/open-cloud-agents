# IAM Condition Keys Security Cheat Sheet

## Essential Security Condition Keys (AWS)

### 1. Enforce TLS 1.2+ Transport
Prevents unencrypted HTTP access to any service (S3, SQS, SNS):
```json
"Condition": {
  "Bool": {
    "aws:SecureTransport": "true"
  }
}
```

### 2. Restrict to Specific VPC Endpoints
Guarantees requests originate strictly from private company VPC endpoints:
```json
"Condition": {
  "StringEquals": {
    "aws:sourceVpce": "vpce-0123456789abcdef0"
  }
}
```

### 3. Restrict by Resource Tags
Limits identity to modifying only resources matching specific project tags:
```json
"Condition": {
  "StringEquals": {
    "aws:ResourceTag/Environment": "production"
  }
}
```

### 4. MFA Required for Mutation
```json
"Condition": {
  "BoolIfExists": {
    "aws:MultiFactorAuthPresent": "true"
  }
}
```

