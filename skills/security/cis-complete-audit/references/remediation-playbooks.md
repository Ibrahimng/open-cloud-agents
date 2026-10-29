# CIS Remediation Playbooks & Automation Recipes

This document provides ready-to-deploy Infrastructure-as-Code (Terraform), Ansible, and CLI remediation recipes for high-risk CIS benchmark violations.

---

## 1. Cloud Foundations Remediation (Terraform)

### 1.1 AWS S3 Account-Level Public Access Block (AWS 2.1.1)

```hcl
resource "aws_s3_account_public_access_block" "global" {
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```

### 1.2 AWS Multi-Region CloudTrail with KMS (AWS 3.1 & 3.2)

```hcl
resource "aws_kms_key" "cloudtrail_key" {
  description             = "KMS Key for multi-region CloudTrail audit logging"
  deletion_window_in_days = 30
  enable_key_rotation     = true
}

resource "aws_cloudtrail" "main_audit" {
  name                          = "enterprise-compliance-trail"
  s3_bucket_name                = aws_s3_bucket.trail_bucket.id
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true
  kms_key_id                    = aws_kms_key.cloudtrail_key.arn
}
```

### 1.3 GCP Cloud Storage Uniform Bucket-Level Access (GCP 3.2)

```hcl
resource "google_storage_bucket" "secure_bucket" {
  name                        = "enterprise-compliance-storage"
  location                    = "US"
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  encryption {
    default_kms_key_name = google_kms_crypto_key.storage_key.id
  }
}
```

---

## 2. Kubernetes Remediation (Manifests & Helm)

### 2.1 Restrict Application Namespace with Pod Security Standards

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: hardened-app
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: v1.28
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/audit: restricted
```

### 2.2 Pod Security Context Template

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: secure-microservice
  namespace: hardened-app
spec:
  replicas: 3
  template:
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 10001
        runAsGroup: 10001
        fsGroup: 10001
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: app
          image: internal-registry.io/app:v2.4
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
          volumeMounts:
            - mountPath: /tmp
              name: ephemeral-tmp
      volumes:
        - name: ephemeral-tmp
          emptyDir: {}
```

---

## 3. Host System Remediation (Shell & Ansible)

### 3.1 Lock Down SSH Daemon

```bash
sudo sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sudo sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/^#*X11Forwarding.*/X11Forwarding no/' /etc/ssh/sshd_config
sudo sed -i 's/^#*MaxAuthTries.*/MaxAuthTries 4/' /etc/ssh/sshd_config
sudo sshd -t && sudo systemctl reload sshd
```

### 3.2 Apply Kernel Network Hardening

```bash
cat << 'EOF' | sudo tee /etc/sysctl.d/99-cis-remediation.conf
net.ipv4.ip_forward = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1
net.ipv4.tcp_syncookies = 1
kernel.randomize_va_space = 2
EOF

sudo sysctl -p /etc/sysctl.d/99-cis-remediation.conf
```
