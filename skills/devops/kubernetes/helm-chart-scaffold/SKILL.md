---
name: helm-chart-scaffold
description: Scaffold, package, and lint enterprise-grade Helm charts following semantic versioning, schema validation, and configurable ingress/HPA defaults.
---

# Enterprise Helm Chart Architecture

## Purpose & Scope
This skill provides templates and validation workflows for packaging cloud-native applications as reusable Helm charts with strict schema validation.

## Standard Chart Layout
```text
my-app/
├── Chart.yaml             # Metadata, chart version (SemVer), appVersion
├── values.yaml            # Default production-safe configuration parameters
├── values.schema.json     # JSON Schema enforcing type safety on values.yaml
├── templates/
│   ├── _helpers.tpl       # Reusable template definitions (labels, selectors)
│   ├── deployment.yaml    # Pod specification with securityContext & probes
│   ├── service.yaml       # ClusterIP / headless networking
│   ├── serviceaccount.yaml# Workload Identity bound ServiceAccount
│   ├── hpa.yaml           # HorizontalPodAutoscaler definition
│   └── ingress.yaml       # Ingress controller routing (TLS, annotations)
└── tests/
    └── test-connection.yaml
```

## Production Defaults for `deployment.yaml`
1. **Explicit Security Context**:
   ```yaml
   securityContext:
     runAsNonRoot: true
     runAsUser: 10001
     readOnlyRootFilesystem: true
     allowPrivilegeEscalation: false
     capabilities:
       drop: ["ALL"]
   ```
2. **Probes Required**: Always configure `livenessProbe` and `readinessProbe` with appropriate `initialDelaySeconds` and `periodSeconds`.
3. **Resource Requests & Limits**: Mandatory CPU and Memory allocations.

## Validation Workflow
- [ ] 1. Validate template syntax and lint chart:
  ```bash
  helm lint my-app/
  ```
- [ ] 2. Render templates locally with strict dry-run:
  ```bash
  helm template test-release my-app/ --debug --dry-run
  ```
- [ ] 3. Validate against Kubernetes OpenAPI schemas using `kubeconform`:
  ```bash
  helm template test-release my-app/ | kubeconform -strict -summary
  ```
