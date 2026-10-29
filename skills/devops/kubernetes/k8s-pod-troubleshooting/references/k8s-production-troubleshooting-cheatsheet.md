# Kubernetes Production Triage Cheat Sheet: The 10 Non-Negotiables

This cheat sheet maps the 10 DevSecOps Non-Negotiables directly to production outage symptoms, diagnostic commands, root causes, and immediate tactical remediations.

---

## ⚡ 10 Non-Negotiables Triage Matrix

| # | Non-Negotiable | Outage Symptom / Alert | Triage Command | Root Cause Indicator | Immediate Remediation |
|---|---|---|---|---|---|
| **1** | **Probes** | 502 Bad Gateway during rollout; Pod is `Running 1/1` but dropping requests. | `kubectl describe pod <NAME> \| grep -A 8 Conditions:` | `ContainersReady: False` or missing `readinessProbe`. | Add `readinessProbe` with proper `initialDelaySeconds`. Never check downstream DB in liveness. |
| **2** | **Resources** | Exit Code `137` (`OOMKilled`); slow API latency; random node evictions. | `kubectl describe pod <NAME> \| grep -E "(OOMKilled\|Exit Code)"` | `Last State: Terminated Reason: OOMKilled`. | Increase `resources.limits.memory` or match `requests == limits` for Guaranteed QoS. |
| **3** | **Autoscaling** | High CPU saturation (> 90%); request queuing; pod count remains static. | `kubectl get hpa; kubectl describe hpa <NAME>` | `unable to get metric` or `Target: <unknown>`. | Verify `metrics-server` health; fix HPA metric resource target. |
| **4** | **NetworkPolicy** | Connection timeout (`ETIMEDOUT`) between microservices; cross-namespace block. | `kubectl get networkpolicy -n <NS>; kubectl get pods -l app=<APP>` | Ingress rule missing source `podSelector` or `namespaceSelector`. | Add explicit allow rule for calling service pod label and port. |
| **5** | **PDB** | Node drain hangs indefinitely; `kubectl drain` fails; voluntary eviction blocked. | `kubectl get pdb -n <NS>; kubectl describe pdb <NAME>` | `DisruptionsAllowed: 0` with `minAvailable == replicas`. | Set `maxUnavailable: 1` or `maxUnavailable: 25%` and increase replica count $\ge 2$. |
| **6** | **SecurityContext** | Pod fails admission with `PodSecurityViolation`; `CrashLoopBackOff` on file write. | `kubectl get events -n <NS> --field-selector reason=FailedCreate` | `violates PodSecurity "restricted": runAsNonRoot != true`. | Add non-root UID (`runAsUser: 10001`) and mount `emptyDir` at `/tmp` for scratch writes. |
| **7** | **Observability** | Pod crashed with no logs; silent error rate spikes without alerting. | `kubectl logs <NAME> --previous --tail=50` | Empty logs; missing structured JSON formatting; collector drop. | Route logs to DaemonSet collector (Fluent Bit / Vector) and verify OTel pipeline. |
| **8** | **Image Security** | `ImagePullBackOff` or `ErrImagePull`; admission webhook rejects unsigned image. | `kubectl describe pod <NAME> \| grep -A 5 Events:` | `cosign: signature verification failed` or registry auth error. | Verify image signature with Cosign and configure valid `imagePullSecrets`. |
| **9** | **Secrets** | Pod crashes with missing env vars; database authentication failure (`401`). | `kubectl get externalsecret -n <NS>; kubectl describe es <NAME>` | `SecretSynced: False` or SecretStore auth failure. | Verify SecretStore IAM / IRSA permissions and refresh token. |
| **10** | **Rollouts** | 502 errors during deployment; in-flight requests dropped upon container termination. | `kubectl rollout history deployment/<NAME>; kubectl describe deploy/<NAME>` | Missing `preStop: sleep 10` hook or `maxUnavailable > 0`. | Add `preStop` hook to container lifecycle; run `kubectl rollout undo deployment/<NAME>`. |

---

## 🛠️ Step-by-Step Diagnostic Recipes

### 1. Diagnosing Probe Failures & Traffic Dropping

```bash
# Check probe definitions and recent probe event failures
kubectl describe pod <POD_NAME> -n <NAMESPACE> | grep -E "(Liveness|Readiness|Startup|Unhealthy)"

# Inspect pod IP endpoint registration in the backing Service
kubectl get endpoints <SERVICE_NAME> -n <NAMESPACE>

# Test readiness endpoint directly from inside the cluster
kubectl run probe-test --rm -it --image=curlimages/curl -- curl -Iv http://<POD_IP>:8080/ready
```

### 2. Diagnosing OOMKilled & Resource Throttling

```bash
# Check if container was terminated due to OOM
kubectl get pod <POD_NAME> -n <NAMESPACE> -o jsonpath='{range .status.containerStatuses[*]}{.name}{": "}{.lastState.terminated.reason}{" (exit: "}{.lastState.terminated.exitCode}{")\n"}{end}'

# Check real-time CPU & memory consumption
kubectl top pod <POD_NAME> -n <NAMESPACE> --containers

# Check container cgroup memory limits from inside the node
kubectl exec -it <POD_NAME> -n <NAMESPACE> -- cat /sys/fs/cgroup/memory.max 2>/dev/null || cat /sys/fs/cgroup/memory/memory.limit_in_bytes
```

### 3. Diagnosing NetworkPolicy Blocks

```bash
# Check active NetworkPolicies in the target namespace
kubectl get networkpolicy -n <NAMESPACE> -o wide

# Test TCP socket connectivity using ephemeral netshoot container
kubectl debug -it <POD_NAME> -n <NAMESPACE> --image=nicolaka/netshoot -- nc -zvw3 <TARGET_SERVICE> 8080

# Check Cilium / Calico drop logs (if CNI supports eBPF tracing)
kubectl exec -n kube-system ds/cilium -- cilium monitor --type drop
```

### 4. Diagnosing PDB Eviction Deadlocks

```bash
# Identify which PDB is blocking node drains
kubectl get pdb -A -o wide

# Check disruptive allowance on target service
kubectl describe pdb <PDB_NAME> -n <NAMESPACE>

# Safe drain override (in non-production emergencies only)
kubectl drain <NODE_NAME> --ignore-daemonsets --delete-emptydir-data --force --disable-eviction
```

### 5. Executing Safe Zero-Downtime Rollbacks

```bash
# Check rollout revision history
kubectl rollout history deployment/<DEPLOYMENT_NAME> -n <NAMESPACE>

# Revert to the immediately preceding stable revision
kubectl rollout undo deployment/<DEPLOYMENT_NAME> -n <NAMESPACE>

# Monitor rollback status until completion
kubectl rollout status deployment/<DEPLOYMENT_NAME> -n <NAMESPACE> --timeout=120s
```

---

## 📚 References

- [k8s-pod-diagnostic-decision-tree.md](k8s-pod-diagnostic-decision-tree.md): Diagnostic decision tree and Linux exit code reference.
- [k8s-production-non-negotiables.md](../../helm-chart-scaffold/references/k8s-production-non-negotiables.md): The 10 DevSecOps Production Non-Negotiables.
