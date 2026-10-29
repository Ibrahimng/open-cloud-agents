# Helm Chart Production Best Practices & Checklist

This checklist operationalizes the [10 DevSecOps Production Non-Negotiables](k8s-production-non-negotiables.md) across all scaffolded Helm charts and Kubernetes manifests.

---

## Production Helm Chart 10 Non-Negotiables Checklist

- [ ] **Chart.yaml SemVer:** `version` tracks chart release (SemVer 2.0), while `appVersion` matches the immutable container image tag (never `:latest`).
- [ ] **1. Health Probes:** Explicit `livenessProbe` (`/healthz`) and `readinessProbe` (`/ready`) with tuned `initialDelaySeconds` and `failureThreshold`. Never check external dependencies in liveness!
- [ ] **2. Resource Requests & Limits:** Both `requests` and `limits` defined for CPU and memory. Prefer matching memory requests and limits for Guaranteed QoS.
- [ ] **3. Horizontal Pod Autoscaler:** `hpa.yaml` enabled with CPU, memory, or KEDA event-driven scaling targets and a 300s scale-down stabilization window.
- [ ] **4. Zero-Trust NetworkPolicy:** Default-deny ingress/egress policy with explicit whitelist rules restricting inter-microservice communication.
- [ ] **5. Pod Disruption Budget:** `pdb.yaml` included specifying `minAvailable: 2` or `maxUnavailable: 25%` to prevent outages during node draining.
- [ ] **6. Restricted SecurityContext:**
    - `runAsNonRoot: true` with unprivileged UID (`runAsUser: 10001`).
    - `allowPrivilegeEscalation: false`.
    - `readOnlyRootFilesystem: true` with `emptyDir` mount for `/tmp`.
    - `capabilities.drop: ["ALL"]`.
    - `seccompProfile.type: RuntimeDefault`.
- [ ] **7. Observability Integration:** Pod annotations for Prometheus metrics scraping (`prometheus.io/scrape: "true"`, `prometheus.io/port: "8080"`), structured JSON logging to stdout, and OTel trace propagation.
- [ ] **8. Image Provenance:** Images hosted in private enterprise registries, scanned via Trivy in CI, and cryptographically signed with Sigstore/Cosign.
- [ ] **9. External Secrets Management:** Zero plaintext secrets in Helm `values.yaml`. Workloads pull credentials dynamically via External Secrets Operator (`kind: ExternalSecret`) or Vault CSI driver.
- [ ] **10. Zero-Downtime Rollout Strategy:** `RollingUpdate` with `maxUnavailable: 0` and `maxSurge: 25%`, paired with a container `preStop` hook (`sleep 10`) for clean connection draining.
- [ ] **High Availability Pod Anti-Affinity:** Soft anti-affinity (`preferredDuringSchedulingIgnoredDuringExecution`) across topology zones to prevent co-locating all replicas on a single worker node.
- [ ] **JSON Schema Validation:** `values.schema.json` present to strictly enforce parameter types, ranges, and mandatory keys on `values.yaml`.

---

## 📚 References

- [k8s-production-non-negotiables.md](k8s-production-non-negotiables.md): Detailed DevSecOps Non-Negotiables runbook.
- [k8s-pod-diagnostic-decision-tree.md](../../k8s-pod-troubleshooting/references/k8s-pod-diagnostic-decision-tree.md): Diagnostic decision tree for pod crashes and OOM events.

