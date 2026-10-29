# Sysdig In-Line Image Scanning & Kubernetes Admission Control

This guide covers shift-left vulnerability management, in-line CLI scanning, and Kubernetes admission controller gatekeeping using Sysdig Secure.

---

## 1. Shift-Left In-Line CLI Scanner (`sysdig-cli-scanner`)

The `sysdig-cli-scanner` performs container image analysis locally within CI runners (GitHub Actions, GitLab CI, Jenkins) without sending container image layers to external cloud endpoints. Only image metadata and package manifests are transmitted.

### CI/CD Runner Invocation

```bash
# Set credentials via environment variables
export SECURE_API_TOKEN="<SYSDIG_API_TOKEN>"

# Run in-line scan with exit code on failure
sysdig-cli-scanner \
  --apiurl "https://app.sysdigcloud.com" \
  --policy "Production-Strict-Gate" \
  --detailed-json report.json \
  internal-registry.io/apps/order-service:sha-8f921ab
```

---

## 2. Gate Evaluation Criteria

A production admission gate evaluates multiple risk dimensions:

| Dimension | Rule | Action |
|---|---|---|
| **CISA KEV** | Active entry in CISA Known Exploited Vulnerabilities catalog | `STOP` (Immediate Build Failure) |
| **Exploit Prediction (EPSS)** | EPSS score $> 0.35$ with CVSS $\ge 7.0$ | `STOP` |
| **Fix Availability** | Vulnerability has an official vendor security patch available | `STOP` if Severity $\ge$ High |
| **Plaintext Credentials** | Embedded RSA private keys, AWS access keys, or JWT tokens detected | `STOP` |
| **User Context** | Default user is `root` (UID 0) or missing explicit `USER` directive | `WARN` or `STOP` |
| **OS Package Hygiene** | Unused compilers (`gcc`, `make`, `g++`) present in runtime image | `WARN` |

---

## 3. Kubernetes Admission Controller Integration

Deploy the Sysdig Validating Admission Webhook to block unverified or failing images before pods are scheduled by Kubernetes:

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: sysdig-admission-controller
webhooks:
  - name: image-scanning.sysdig.com
    clientConfig:
      service:
        name: sysdig-admission-service
        namespace: sysdig
        path: /validate
      caBundle: "<BASE64_CA_BUNDLE>"
    rules:
      - operations: ["CREATE", "UPDATE"]
        apiGroups: [""]
        apiVersions: ["v1"]
        resources: ["pods"]
    admissionReviewVersions: ["v1"]
    sideEffects: None
    timeoutSeconds: 5
    failurePolicy: Fail
    namespaceSelector:
      matchExpressions:
        - key: kubernetes.io/metadata.name
          operator: NotIn
          values: ["kube-system", "sysdig"]
```
