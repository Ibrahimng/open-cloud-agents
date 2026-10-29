---
name: helm-chart-scaffold
description: Scaffold, package, and lint enterprise-grade Helm charts following semantic versioning, schema validation, and the 10 DevSecOps production non-negotiables (probes, limits, HPA, PDB, securityContext, network policies).
---

# Enterprise Helm Chart Architecture

## Purpose & Scope

This skill provides templates, production invariants, and validation workflows for packaging cloud-native applications as production-ready Helm charts. All charts generated or validated by this skill must adhere to the [10 DevSecOps Production Non-Negotiables](references/k8s-production-non-negotiables.md).

---

## Standard Chart Layout

```text
my-app/
├── Chart.yaml              # Metadata, chart version (SemVer 2.0), appVersion (no :latest)
├── values.yaml             # Default production-safe configuration parameters
├── values.schema.json      # JSON Schema enforcing strict type safety on values.yaml
├── templates/
│   ├── _helpers.tpl        # Reusable template definitions (labels, selectors)
│   ├── deployment.yaml     # Pod specification with securityContext, probes, lifecycle
│   ├── service.yaml        # ClusterIP / headless networking
│   ├── serviceaccount.yaml # Workload Identity bound ServiceAccount
│   ├── hpa.yaml            # HorizontalPodAutoscaler (v2) definition
│   ├── pdb.yaml            # PodDisruptionBudget (minAvailable / maxUnavailable)
│   ├── networkpolicy.yaml  # Zero-trust NetworkPolicy (default deny + whitelist)
│   ├── externalsecret.yaml # ExternalSecrets synchronization manifest
│   └── ingress.yaml        # Ingress controller routing (TLS, annotations)
└── tests/
    └── test-connection.yaml
```

---

## Production Defaults for `deployment.yaml`

### 1. Restricted Security Context
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 10001
  runAsGroup: 10001
  fsGroup: 10001
  seccompProfile:
    type: RuntimeDefault
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities:
    drop:
      - ALL
```

### 2. Mandatory Health Probes
```yaml
startupProbe:
  httpGet:
    path: /healthz
    port: http
  failureThreshold: 30
  periodSeconds: 10
livenessProbe:
  httpGet:
    path: /healthz
    port: http
  initialDelaySeconds: 15
  periodSeconds: 10
  timeoutSeconds: 3
  failureThreshold: 3
readinessProbe:
  httpGet:
    path: /ready
    port: http
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 2
  failureThreshold: 2
```

### 3. Resource Requests & Limits
```yaml
resources:
  requests:
    cpu: 250m
    memory: 512Mi
  limits:
    cpu: 500m
    memory: 512Mi # Matched memory requests and limits guarantee Guaranteed QoS
```

### 4. Zero-Downtime Rolling Update & PreStop Hook
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 25%
    maxUnavailable: 0
template:
  spec:
    terminationGracePeriodSeconds: 30
    containers:
      - name: app
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 10"]
```

---

## Validation & Guardrail Audit Workflow

- [ ] **1. Validate template syntax and lint chart:**

  ```bash
  helm lint my-app/
  ```

- [ ] **2. Render templates locally with strict dry-run:**

  ```bash
  helm template test-release my-app/ --debug --dry-run
  ```

- [ ] **3. Audit against the 10 DevSecOps Production Non-Negotiables:**

  ```bash
  helm template test-release my-app/ | bash skills/devops/kubernetes/helm-chart-scaffold/scripts/audit_k8s_guardrails.sh -
  ```

- [ ] **4. Validate against Kubernetes OpenAPI schemas using `kubeconform`:**

  ```bash
  helm template test-release my-app/ | kubeconform -strict -summary
  ```

---

## 📚 References & Tools

- [k8s-production-non-negotiables.md](references/k8s-production-non-negotiables.md): Detailed 10 DevSecOps Non-Negotiables runbook and matrix.
- [chart-best-practices.md](references/chart-best-practices.md): Production checklist for values schemas and security profiles.
- `scripts/audit_k8s_guardrails.sh`: Automated static auditor for Kubernetes manifests and Helm templates.
- `scripts/validate_chart.sh`: Complete multi-step Helm chart validation runner.

