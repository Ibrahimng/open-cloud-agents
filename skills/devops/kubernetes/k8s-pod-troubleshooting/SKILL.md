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

## Continuous Self-Knowledge Enhancement Loop

Whenever an agent identifies a subtle networking or runtime edge case:
1. **Isolate Root Cause Trigger:** (e.g. CoreDNS UDP packet drops at > 10,000 QPS).
2. **Auto-Generate a Preventative Check:** Propose a rule in [`skills/devops/kubernetes/helm-chart-scaffold/SKILL.md`](../helm-chart-scaffold/SKILL.md) to mandate `dnsConfig.options` on high-throughput deployments.
3. **Record in Knowledge Base:** Update `AGENTS.md` under `## Learned Kubernetes Networking Facts` so the SRE Incident Commander checks DNS latency immediately whenever 502/504 errors appear with low CPU usage.
