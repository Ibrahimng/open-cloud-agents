---
name: k8s-pod-troubleshooting
description: Systematically diagnose and remediate failing Kubernetes workloads exhibiting CrashLoopBackOff, OOMKilled, ImagePullBackOff, Pending scheduling, and failed readiness/liveness probes.
---

# Kubernetes Pod Failure Triage & Root Cause Analysis

## Purpose & Scope
This skill outlines the standard diagnostic workflow for triaging unhealthy pods in Kubernetes clusters across Amazon EKS, Azure AKS, and Google Cloud GKE.

## Diagnostic Flowchart

```text
[Pod Unhealthy]
  ├── Status: ImagePullBackOff / ErrImagePull
  │     └── Verify image registry secret, tag existence, network access.
  ├── Status: CrashLoopBackOff
  │     └── Exit Code 137? -> OOMKilled (Increase memory limits).
  │     └── Exit Code 1 / 2? -> Application crash (Check stdout logs).
  ├── Status: Pending
  │     └── Insufficient CPU/Memory on nodes, unmet nodeAffinity/tolerations, PVC binding issue.
  └── Status: Running (0/1 Ready)
        └── Health check failing: inspect readinessProbe endpoint & response timeout.
```

## Step-by-Step Triage Commands

### 1. Identify the Unhealthy Resource
```bash
kubectl get pods -n <namespace> -o wide --sort-by='.status.startTime'
```

### 2. Inspect Failure Events & Conditions
```bash
kubectl describe pod <pod-name> -n <namespace>
```
Look for:
- `Last State: Terminated` with `Reason: OOMKilled` (Exit Code 137).
- `Events:` section at bottom for probe failures, scheduling rejections, or volume attach errors.

### 3. Stream Application Logs
```bash
# Check current logs
kubectl logs <pod-name> -n <namespace> --tail=100

# Check previous terminated instance (critical for CrashLoopBackOff)
kubectl logs <pod-name> -n <namespace> --previous --tail=100
```

### 4. Interactive Debugging & Network Connectivity
If the container crashes immediately or is unreachable:
```bash
# Ephemeral debug container attach
kubectl debug -it <pod-name> -n <namespace> --image=curlimages/curl --target=<container-name>
```

## Guardrails
- Never execute destructive namespace deletions or force pod teardowns (`--grace-period=0 --force`) without confirming state persistence.
- Do not blindly increase resource limits without checking for memory leaks via heap dumps or telemetry.
