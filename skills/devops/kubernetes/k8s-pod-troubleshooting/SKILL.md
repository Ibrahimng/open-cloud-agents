---
name: k8s-pod-troubleshooting
description: Systematically diagnose and remediate production Kubernetes workload degradations, silent socket exhaustion, DNS throttling, and probe failures based on real-world outage postmortems.
---

# Kubernetes Pod Failure Triage & Root Cause Analysis

## Purpose & Scope
This skill outlines the live diagnostic exploration workflow for triaging unhealthy or degrading pods in Kubernetes clusters across Amazon EKS, Azure AKS, and Google Cloud GKE.

---

## Real-Life Production Incident Case: CoreDNS Throttling & Cascading 502 Outage

### Background & What Happened
During a morning traffic surge (35,000 requests/sec), an enterprise checkout API began throwing HTTP 502 errors to end users. Pods were reported as `Running 1/1`, CPU usage was under 40%, and memory was within quota. Standard health checks showed green. 
However, response times spiked from 25ms to 8,000ms.

### Real-Time Live Exploration Sequence
The SRE agent executed the following live diagnostic steps:

#### 1. Inspect Node-Level Conntrack Saturation
```bash
# Check if host node conntrack tables are dropping SYN packets
kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.addresses[0].address}{"\n"}{end}'
# Query kernel metrics on node
kubectl debug node/<node-name> -it --image=busybox -- chroot /host sysctl net.netfilter.nf_conntrack_count net.netfilter.nf_conntrack_max
```

#### 2. Attach Ephemeral Container for Network Diagnostic
Standard container lacked tools; the agent attached an ephemeral container into the target pod's network namespace:
```bash
kubectl debug -it <pod-name> -n prod --image=nicolaka/netshoot --target=<container-name>
```

#### 3. Real-Time DNS Query Latency & Drop Analysis
Inside the ephemeral container:
```bash
# Measure DNS lookup turnaround
dig @10.96.0.10 auth-service.prod.svc.cluster.local +stats | grep "Query time"

# Inspect socket backlog and TCP connection states
ss -s
ss -tna | grep -c TIME-WAIT
ss -tna | grep -c CLOSE-WAIT
```
**The Discovery:** CoreDNS pods were throttling single-threaded UDP lookups, causing 5-second DNS timeouts on downstream microservice calls.

---

## Production Remediation Protocol

1. **Deploy NodeLocal DNSCache DaemonSet:**
   Eliminates CoreDNS saturation by intercepting DNS queries locally on each worker node over TCP.
2. **Apply Pod `dnsConfig` ndots Optimization:**
   Change `ndots: 5` to `ndots: 2` in pod spec to prevent unneeded multi-suffix domain walkings:
   ```yaml
   spec:
     dnsConfig:
       options:
         - name: ndots
           value: "2"
         - name: single-request-reopen
   ```
3. **Tune Keepalive Connection Pooling:**
   Configure HTTP client connection pooling in the application to reuse established TCP sockets rather than opening a new socket per incoming request.

---

## 🚨 The 10 Non-Negotiables Incident Triage Flow

When a pod is reported in `CrashLoopBackOff`, `Pending`, or `Running` with elevated 5xx error rates, evaluate against the [10 DevSecOps Production Non-Negotiables](references/k8s-production-troubleshooting-cheatsheet.md):

1. **Probe Misconfigurations:**
    - Is `readinessProbe` failing or unconfigured, causing traffic to hit booting pods?
    - Is `livenessProbe` checking an external database, causing cascading pod termination storms?
2. **Resource Starvation & QoS:**
    - Was the container terminated with Exit Code `137` (`OOMKilled`)? Run `kubectl describe pod` to verify `Last State: Terminated Reason: OOMKilled`.
    - Is CFS quota throttling CPU threads? Verify if `resources.limits.cpu` is set unrealistically tight.
3. **Autoscaling Stalls:**
    - Did a traffic spike overwhelm fixed replicas? Verify `kubectl get hpa` and check whether `metrics-server` is reporting metrics.
4. **NetworkPolicy Lateral Blocks:**
    - Are egress or cross-namespace ingress packets being dropped by CNI network policies?
5. **PDB Node Eviction Locks:**
    - Is `kubectl drain` hanging during node pool maintenance? Verify `kubectl get pdb -A` to confirm `DisruptionsAllowed > 0`.
6. **Connection Draining Drops:**
    - Are 502 errors occurring strictly during deployments? Verify if the container lacks a `preStop: sleep 10` lifecycle hook.

---

## Continuous Self-Knowledge Enhancement Loop

Whenever an agent identifies a subtle networking or runtime edge case:

1. **Isolate Root Cause Trigger:** (e.g. CoreDNS UDP packet drops at > 10,000 QPS, or liveness cascading DB failover).
2. **Auto-Generate a Preventative Check:** Propose a guardrail in [`skills/devops/kubernetes/helm-chart-scaffold/SKILL.md`](../helm-chart-scaffold/SKILL.md) to enforce declarative policy controls.
3. **Record in Knowledge Base:** Update `AGENTS.md` under `## Learned Kubernetes Networking Facts` or `## Learned Kubernetes Production Reliability & Security Facts`.

---

## 📚 References & Tools

- [k8s-production-troubleshooting-cheatsheet.md](references/k8s-production-troubleshooting-cheatsheet.md): Direct mapping of the 10 Non-Negotiables to failure symptoms and commands.
- [k8s-pod-diagnostic-decision-tree.md](references/k8s-pod-diagnostic-decision-tree.md): Diagnostic decision tree and Linux signal exit codes (137, 139, 143, 1, 2).
- [k8s-production-non-negotiables.md](../helm-chart-scaffold/references/k8s-production-non-negotiables.md): The 10 DevSecOps Production Non-Negotiables standard.
- `scripts/pod_diagnose.sh`: Automated multi-step pod diagnostic and guardrail compliance inspector.
