# Kubernetes in Production: The 10 DevSecOps Non-Negotiables

This reference details the 10 production guardrails derived from battle-tested DevSecOps playbooks, incident postmortems, and cloud-native standards (CIS Kubernetes Benchmark v1.9, NIST SP 800-190, Pod Security Standards). Every production deployment scaffolded via Helm or raw manifests must adhere to these non-negotiable patterns.

---

## 🏛️ Master Guardrails Matrix

| # | Guardrail Domain | Production Vulnerability / Symptom | DevSecOps Remediation | Non-Negotiable Production Rule |
|---|---|---|---|---|
| **1** | **Liveness & Readiness Probes** | Pod reports `Running` but drops incoming traffic during boot or fails silently in a deadlock. | Configure separate `startupProbe`, `livenessProbe` (`/healthz`), and `readinessProbe` (`/ready`). | *Never ship a deployment without both probes. Ever.* |
| **2** | **Resource Requests & Limits** | Memory leaks crash entire worker nodes or noisy neighbors starve co-located microservices. | Set CPU/Memory `requests` for scheduling and `limits` for hard boundary enforcement. | *No container goes to prod without defined resource limits.* |
| **3** | **Horizontal Pod Autoscaler (HPA)** | Traffic surges overwhelm static replica counts, causing cascading 502/504 errors. | Deploy `HorizontalPodAutoscaler` (v2) with CPU, memory, and custom metrics (KEDA). | *Autoscale what matters. Always.* |
| **4** | **Network Policies** | Flat network permits compromised frontend pods to scan and query internal databases directly. | Enforce default-deny ingress/egress with explicit pod/namespace whitelisting. | *No public east-west traffic. Ever.* |
| **5** | **Pod Disruption Budgets (PDB)** | Node maintenance, AMI rollouts, or cluster upgrades drain nodes and kill all active pods simultaneously. | Configure `PodDisruptionBudget` with `minAvailable: 2` or `maxUnavailable: 25%`. | *If uptime matters, use PDBs.* |
| **6** | **Security Contexts & Pod Policies** | Root container escape exploit compromises the host kernel and node filesystem. | Enforce `runAsNonRoot: true`, `allowPrivilegeEscalation: false`, and `readOnlyRootFilesystem`. | *Treat every pod like it's exposed to the internet.* |
| **7** | **Logging & Monitoring** | Microservices fail silently with zero telemetry, leaving on-call engineers blind. | Centralize structured logs (Loki/Fluent Bit), collect 4 Golden Signals, and trace with OTel. | *Observability isn't optional. It's your lifeline.* |
| **8** | **Image Provenance & Scanning** | Pulling unvetted public container images executes malicious cryptominers or CVE exploits. | Enforce cryptographic signature verification (Cosign) and CI build vulnerability scanning. | *Trust no image you didn't build or scan yourself.* |
| **9** | **Secrets Management** | Production credentials and API keys stored in plaintext or base64 ConfigMaps/Secrets. | Integrate External Secrets Operator (ESO) / Vault CSI driver and enable KMS on etcd. | *Secrets belong in secret stores. Not in YAML files.* |
| **10** | **Rolling Updates & Rollbacks** | Broken deployments drop in-flight user requests and lack automated rollback triggers. | Use `RollingUpdate` with `maxUnavailable: 0`, a `preStop` hook, and automated rollback plans. | *Every rollout must have a rollback plan.* |

---

## 🔍 Detailed 10 Non-Negotiables Breakdown

### 1. Liveness & Readiness Probes

#### The Problem
> *"We shipped to production and... the pods were running, but nothing worked."*

When a container starts, its process is immediately created (`Running 1/1`), but internal framework initialization (JVM startup, cache pre-warming, database connection pool establishment) may take tens of seconds. Without probes, `kube-proxy` immediately routes user traffic to the unready pod, producing massive HTTP 502/503 errors. Conversely, if a running pod deadlocks, Kubernetes assumes it is healthy unless a liveness check fails.

#### Real Implementation
```yaml
startupProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 10
  failureThreshold: 30

livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 15
  periodSeconds: 10
  timeoutSeconds: 3
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 2
  failureThreshold: 2
```

#### Golden Rules
- **Your app might run but still not be ready:** Always decouple the liveness check (is the process deadlocked?) from the readiness check (is the process ready to accept requests?).
- **Without readiness probes, Kubernetes thinks your pod is fine:** Traffic starts hitting during initialization.
- **Without liveness probes, zombie pods stay alive silently failing:** Deadlocks never get automatically restarted.
- **The Liveness Cascading Trap:** NEVER check external dependencies (databases, Redis, downstream APIs) in `livenessProbe`. If your database experiences a 10-second failover, checking it in liveness will cause Kubernetes to kill and restart every pod across your entire fleet at once, creating a catastrophic reboot storm. Check external dependencies ONLY in `readinessProbe`.

#### Production Rule
> **Never ship a deployment without both probes. Ever.**

---

### 2. Resource Requests & Limits

#### The Problem
> *"It worked on my cluster - until it ate all the memory."*

Kubernetes worker nodes share CPU cores and RAM. Without boundaries, a memory leak in one container triggers the Linux kernel Out-Of-Memory (OOM) killer to terminate arbitrary pods across the node.

#### Real Implementation
```yaml
resources:
  requests:
    cpu: "250m"
    memory: "512Mi"
  limits:
    cpu: "500m"
    memory: "1Gi"
```

#### Golden Rules
- **Requests are promises; Limits are hard stops:** `kube-scheduler` uses `requests` to place pods on nodes that have guaranteed capacity. `limits` are enforced by Linux cgroups.
- **Always set both; No exceptions:** Missing requests leads to overcommitting nodes; missing limits leads to node starvation.
- **Use performance profiling, not guesswork:** Measure 7-day p95 and p99 CPU/Memory usage under load via Prometheus to size requests accurately.
- **QoS Class Discipline:**
    - Setting `requests.memory == limits.memory` grants **Guaranteed QoS**, protecting the pod from being killed first during node memory pressure.
    - Setting `requests.memory < limits.memory` grants **Burstable QoS**.
- **CPU Throttling Warning:** Memory is non-compressible (`OOMKilled` Exit Code 137). CPU is compressible (throttled by CFS quota). If CPU limits are set too aggressively, the Linux kernel throttles execution threads within 100ms CFS quota periods, introducing latency spikes without CPU exhaustion.

#### Production Rule
> **No container goes to prod without defined resource limits.**

---

### 3. Horizontal Pod Autoscaler (HPA)

#### The Problem
> *"Traffic spiked. The app crashed. Monitoring said it was fine."*

Traffic is inherently variable. Relying on manual replica scaling or fixed cluster sizes guarantees either resource waste during troughs or service outages during peaks.

#### Real Implementation
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: checkout-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: checkout-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 75
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
```

#### Golden Rules
- **Enable `metrics-server`:** HPA cannot operate without active metrics aggregation from kubelet.
- **Autoscale on what correlates with load:** Use CPU/Memory for computational APIs. Use Custom/External metrics via KEDA (Kafka consumer lag, SQS queue depth, active HTTP concurrency) for message-driven workers.
- **Stabilize scale-down:** Configure `behavior.scaleDown.stabilizationWindowSeconds: 300` to prevent flapping (rapid scaling up and down) during brief traffic oscillations.

#### Production Rule
> **Autoscale what matters. Always.**

---

### 4. Network Policies

#### The Problem
> *"A frontend in one namespace talked to a database in another — unencrypted."*

By default, Kubernetes implements an open flat network: any pod in any namespace can communicate with any other pod across the cluster. If a single public-facing pod is compromised, the attacker has unrestricted lateral traversal.

#### Real Implementation

```yaml
# 1. Default-Deny All Ingress and Egress
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
---
# 2. Explicit Ingress Whitelist for Backend
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
  namespace: production
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app.kubernetes.io/name: frontend
    ports:
    - protocol: TCP
      port: 8080
```

#### Golden Rules
- **Default deny, then explicitly allow:** Start each production namespace with a default-deny policy.
- **Define policies per namespace or microservice tier:** Isolate ingress and egress per communication boundary.
- **Verify CNI Plugin Support:** NetworkPolicy objects are ignored unless the cluster CNI supports policy enforcement (Cilium, Calico, AWS VPC CNI with network policy, Azure CNI with Cilium, GKE Datapath v2).

#### Production Rule
> **No public or unrestricted east-west traffic. Ever.**

---

### 5. Pod Disruption Budgets (PDB)

#### The Problem
> *"Our upgrade caused a complete service outage — even with three replicas."*

Cluster upgrades, node maintenance, and autoscaler scale-downs trigger `kubectl drain`. Without a PDB, the Kubernetes eviction API can evict all replicas of your microservice simultaneously, causing complete downtime.

#### Real Implementation
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: checkout-service-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app.kubernetes.io/name: checkout-service
```

#### Golden Rules
- **Use with StatefulSets and Deployments:** Any multi-replica service serving user traffic requires a PDB.
- **Ensure PDB aligns with HPA and replica count:**
    - If `replicas: 1` and `minAvailable: 1`, node draining will hang indefinitely because the eviction API cannot satisfy the disruption budget.
    - Prefer `maxUnavailable: 1` or `maxUnavailable: 25%` on multi-replica deployments.

#### Production Rule
> **If uptime matters, use PDBs.**

---

### 6. Security Contexts & Pod Policies

#### The Problem
> *"The container was running as root. A CVE exploited it."*

Containers running as root (UID 0) share the host kernel. An unprivileged container escape or directory traversal vulnerability can grant root host access or compromise cloud metadata services.

#### Real Implementation
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 10001
  runAsGroup: 10001
  fsGroup: 10001
  seccompProfile:
    type: RuntimeDefault
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop:
      - ALL
```

#### Golden Rules
- **Drop root wherever possible:** Set `runAsNonRoot: true` and specify a high unprivileged UID (`runAsUser: 10001`).
- **Enforce Pod Security Standards (PSS):** Apply the `restricted` profile on all production namespaces.
- **Strip capabilities:** Always specify `capabilities.drop: ["ALL"]`. Mount temporary writable volumes via `emptyDir` at `/tmp` if the application requires temporary file generation.

#### Production Rule
> **Treat every pod like it's exposed to the internet.**

---

### 7. Logging & Monitoring (Observability)

#### The Problem
> *"The app failed silently. We had no logs."*

Ephemeral pods discard logs upon termination. Without external telemetry, reproducing production crashes or diagnosing intermittent timeouts is impossible.

#### Real Implementation Architecture
```text
  Application Pods (stdout/stderr JSON)
             │
             ▼
  DaemonSet Log Collector (Fluent Bit / Vector)
             │
             ▼
  Centralized Storage (Grafana Loki / OpenSearch / CloudWatch)
             ▲
             │ Metrics & Traces
  Prometheus + OpenTelemetry Collector ➔ Grafana Dashboards + Alertmanager
```

#### Golden Rules
- **Centralize logs:** Never rely on `kubectl logs` for incident investigations. Route logs to Loki, ELK, or Cloud Logging.
- **Track the Four Golden Signals:** Latency, Traffic, Errors, Saturation.
- **Alert on SLO/SLI Burn Rates:** Alert on sustained error rate burn against your SLO rather than instantaneous CPU threshold spikes.
- **Distributed Tracing:** Propagate W3C TraceContext headers through OpenTelemetry to pinpoint latency bottlenecks across microservices.

#### Production Rule
> **Observability isn't optional. It's your lifeline.**

---

### 8. Image Provenance & Vulnerability Scanning

#### The Problem
> *"We pulled an image from a public registry. It had a crypto miner."*

Public or unvetted container images frequently contain critical CVEs, outdated base libraries, or malicious supply-chain payloads.

#### Golden Rules
- **Use signed images:** Cryptographically sign container images using Sigstore/Cosign or Notary during the CI build stage.
- **Scan every build:** Block CI pipelines if Trivy, Grype, or Clair detects High/Critical vulnerabilities with active exploits (CISA KEV, EPSS > 0.35).
- **Private Registries with Immutable Tags:** Host images in private enterprise registries (Harbor, AWS ECR, Azure ACR, Google Artifact Registry). Never deploy images tagged `:latest`.

#### Production Rule
> **Trust no image you didn't build or scan yourself.**

---

### 9. Secrets Management

#### The Problem
> *"Our S3 credentials were in plaintext inside a ConfigMap."*

Native Kubernetes Secrets (`kind: Secret`) are simply base64-encoded strings stored in `etcd`. Anyone with read RBAC or cluster backup access can decode them instantly.

#### Real Implementation (External Secrets Operator)
```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: database-credentials
spec:
  refreshInterval: "1h"
  secretStoreRef:
    name: aws-secrets-manager
    kind: ClusterSecretStore
  target:
    name: app-db-secret
    creationPolicy: Owner
  data:
  - secretKey: password
    remoteRef:
      key: prod/rds/postgres
      property: password
```

#### Golden Rules
- **Use external secret stores:** Integrate HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, or Google Secret Manager via External Secrets Operator (ESO) or Secrets Store CSI Driver.
- **Enable etcd KMS envelope encryption:** Encrypt the `etcd` database at rest using customer-managed encryption keys (CMEK).
- **Rotate secrets regularly:** Automate secret rotation and avoid baking credentials into container images or Git repositories.

#### Production Rule
> **Secrets belong in secret stores. Not in YAML files.**

---

### 10. Rolling Updates & Deployment Strategies

#### The Problem
> *"We deployed a new version. It broke everything. No rollback was in place."*

Instantaneous pod replacement drops active user connections, saturates database connections, and creates downtime if the new release crashes on startup.

#### Real Implementation
```yaml
spec:
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

#### Golden Rules
- **Zero-Downtime Rolling Updates:** Set `maxUnavailable: 0` and `maxSurge: 25%` (or `maxSurge: 1`) to ensure existing capacity is never degraded during upgrades.
- **The `preStop` Sleep Invariant:** Kubernetes sends `SIGTERM` to the pod at the exact same millisecond that `kube-proxy` begins updating node iptables/IPVS rules. Adding a `preStop` hook (`sleep 10`) ensures the pod continues handling in-flight requests while routing tables propagate across the cluster.
- **Progressive Delivery:** For mission-critical workloads, adopt Canary or Blue-Green rollouts with Argo Rollouts or Flagger, automatically reverting if Prometheus error rates spike.

#### Production Rule
> **Every rollout must have a rollback plan.**

---

## 📚 References & Standards Cross-Reference

- [chart-best-practices.md](chart-best-practices.md): Helm chart production checklists and validation commands.
- [k8s-pod-diagnostic-decision-tree.md](../../k8s-pod-troubleshooting/references/k8s-pod-diagnostic-decision-tree.md): Diagnostic triage decision tree for pod crashes.
- [kubernetes-cis-guide.md](../../../../security/cis-complete-audit/references/kubernetes-cis-guide.md): CIS Kubernetes Benchmark v1.9 specification.
