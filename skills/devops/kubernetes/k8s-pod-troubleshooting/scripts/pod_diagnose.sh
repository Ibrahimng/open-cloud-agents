#!/usr/bin/env bash
set -euo pipefail

# pod_diagnose.sh - Automated diagnostic collector for unhealthy Kubernetes pods

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <namespace> <pod-name>"
  exit 1
fi

NAMESPACE="$1"
POD_NAME="$2"

echo "========================================================"
echo "Kubernetes Diagnostic Triage for: $NAMESPACE / $POD_NAME"
echo "========================================================"

echo "[1/4] Status & Resource Details:"
kubectl get pod "$POD_NAME" -n "$NAMESPACE" -o wide

echo ""
echo "[2/4] Recent Events & Termination Status:"
kubectl describe pod "$POD_NAME" -n "$NAMESPACE" | grep -E "(State:|Reason:|Exit Code:|Last State:|Events:)" -A 10

echo ""
echo "[3/4] Tail of Previous Container Instance Logs (Crash Context):"
kubectl logs "$POD_NAME" -n "$NAMESPACE" --previous --tail=40 2>&1 || echo "[NOTE] No previous container termination logs available."

echo ""
echo "[4/4] Tail of Current Container Logs:"
kubectl logs "$POD_NAME" -n "$NAMESPACE" --tail=30 2>&1 || true

echo ""
echo "[5/5] Production Guardrail Evaluation (The 10 Non-Negotiables):"
POD_JSON=$(kubectl get pod "$POD_NAME" -n "$NAMESPACE" -o json 2>/dev/null || true)

if [ -n "$POD_JSON" ]; then
  # Check QoS Class
  QOS=$(echo "$POD_JSON" | grep -m1 '"qosClass":' | tr -d '", ' | cut -d: -f2 || echo "Unknown")
  echo "  • QoS Class: $QOS"

  # Check Probes
  if echo "$POD_JSON" | grep -q '"livenessProbe"'; then
    echo "  • LivenessProbe: Configured"
  else
    echo "  • LivenessProbe: [WARN] Missing (Risk of undetected deadlock/zombie pod)"
  fi

  if echo "$POD_JSON" | grep -q '"readinessProbe"'; then
    echo "  • ReadinessProbe: Configured"
  else
    echo "  • ReadinessProbe: [WARN] Missing (Risk of 502/503 during startup/deployments)"
  fi

  # Check Resource Limits
  if echo "$POD_JSON" | grep -q '"limits"'; then
    echo "  • Resource Limits: Configured"
  else
    echo "  • Resource Limits: [FAIL] Missing (Risk of OOM eviction/node starvation)"
  fi

  # Check Security Context
  if echo "$POD_JSON" | grep -q '"runAsNonRoot": true'; then
    echo "  • SecurityContext (runAsNonRoot): Enforced"
  else
    echo "  • SecurityContext: [WARN] runAsNonRoot not explicitly true"
  fi
fi

echo "========================================================"
echo "Diagnostic collection complete."

