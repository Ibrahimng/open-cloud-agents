# Helm Chart Production Best Practices & Checklist

## Production Helm Chart Checklist
- [ ] **Chart.yaml SemVer:** `version` tracks chart version (SemVer), `appVersion` tracks container image tag.
- [ ] **SecurityContext Enforced:**
  - `runAsNonRoot: true`
  - `allowPrivilegeEscalation: false`
  - `readOnlyRootFilesystem: true`
  - `capabilities.drop: ["ALL"]`
- [ ] **Probes Configured:** Explicit `livenessProbe` and `readinessProbe` with appropriate `timeoutSeconds` (>= 3s) and `periodSeconds`.
- [ ] **Resource Limits:** Both `requests` and `limits` defined for CPU and memory.
- [ ] **Pod Anti-Affinity:** Soft anti-affinity (`preferredDuringSchedulingIgnoredDuringExecution`) across topology zones to prevent co-locating replicas on a single worker node.
- [ ] **values.schema.json Present:** Strictly enforces types for all `values.yaml` inputs.
