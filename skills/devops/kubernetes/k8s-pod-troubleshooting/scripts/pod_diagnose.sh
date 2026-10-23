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

echo "========================================================"
echo "Diagnostic collection complete."

