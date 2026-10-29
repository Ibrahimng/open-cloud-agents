# Real-Time Prevention & Automated Response with Falco Talon

This guide details the integration of **Falco Talon** with Falco to deliver automated, real-time threat neutralization across Kubernetes nodes.

---

## 1. Falco Talon Architecture

While Falco acts as a sensor detecting malicious syscall patterns, **Falco Talon** listens to the alert stream and executes predefined responses directly through the Kubernetes API, CNI plugins (Cilium/Calico), or node-level agents.

```
 [ Linux Kernel ] ---> [ Falco Engine ] ---> [ Falco Talon ]
                                                     │
               ┌─────────────────────────────────────┴─────────────────────────────────────┐
               ▼                                     ▼                                     ▼
      [ Terminate Pod ]                   [ Network Quarantine ]                  [ Process Kill ]
  (Zero-downtime eviction)            (Calico/Cilium egress isolate)            (SIGKILL container PID)
```

---

## 2. Talon Action Configuration (`rules.yaml`)

### 2.1 Action Definitions

```yaml
# 1. Action: Terminate Compromised Pod
- action: Terminate Pod Instantly
  actionner: kubernetes:terminate
  parameters:
    grace_period_seconds: 0

# 2. Action: Inject Network Quarantine Policy
- action: Quarantine Pod Network
  actionner: kubernetes:networkpolicy
  parameters:
    type: egress-deny-all

# 3. Action: Execute Custom Mitigation Script
- action: Trigger PagerDuty Incident
  actionner: webhook:http
  parameters:
    url: "https://events.pagerduty.com/v2/enqueue"
    method: "POST"
```

### 2.2 Matching Rules to Actions

```yaml
- rule: Isolate and Evict on Cryptomining
  match:
    rules:
      - "Cryptomining Pool Connection Attempt"
      - "Container Namespace Escape Attempt"
    output_fields:
      - "k8s.pod.name"
      - "k8s.ns.name"
  actions:
    - action: Quarantine Pod Network
    - action: Terminate Pod Instantly
    - action: Trigger PagerDuty Incident

- rule: Kill Interactive Shell in Production
  match:
    rules:
      - "Terminal Shell Spawned in Container"
    output_fields:
      - "k8s.pod.name"
      - "k8s.ns.name"
    filter: "k8s.ns.name == 'production'"
  actions:
    - action: Terminate Pod Instantly
```

---

## 3. Network Quarantine via Calico / Cilium

When a network quarantine action is triggered, Falco Talon generates a targeted `NetworkPolicy` isolating the specific pod pod selector:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: falco-quarantine-pod-xyz
  namespace: production
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/instance: compromised-pod-xyz
  policyTypes:
    - Ingress
    - Egress
  # Empty ingress and egress blocks sever all external and lateral network connectivity
  ingress: []
  egress: []
```

---

## 4. Safety Guardrails & Circuit Breakers

To prevent accidental denial-of-service in case of misconfigured rules or broad alerts, Talon supports rate-limiting and blast radius boundaries:

```yaml
global:
  rate_limit:
    max_actions_per_minute: 5
    action_cooldown_seconds: 30
  exempt_namespaces:
    - kube-system
    - falco
    - ingress-nginx
    - monitoring
```
