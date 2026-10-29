#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# Open Cloud Agents: Kubernetes 10 Non-Negotiables Guardrail Auditor
#
# Audits rendered Kubernetes manifests or Helm templates against the 10 DevSecOps
# production non-negotiables: Probes, Resource Limits, SecurityContext, PDB, etc.
# ==============================================================================

INPUT_TARGET="${1:-}"

if [ -z "$INPUT_TARGET" ]; then
  echo "Usage: $0 <manifest-file-or-dir>"
  echo "   or: helm template <chart> | $0 -"
  exit 1
fi

TEMP_MANIFEST=$(mktemp)
trap 'rm -f "$TEMP_MANIFEST"' EXIT

if [ "$INPUT_TARGET" = "-" ]; then
  cat > "$TEMP_MANIFEST"
elif [ -d "$INPUT_TARGET" ]; then
  find "$INPUT_TARGET" -type f \( -name "*.yaml" -o -name "*.yml" \) -exec cat {} + > "$TEMP_MANIFEST"
elif [ -f "$INPUT_TARGET" ]; then
  cat "$INPUT_TARGET" > "$TEMP_MANIFEST"
else
  echo "Error: Target $INPUT_TARGET not found."
  exit 1
fi

echo "=========================================================="
echo " 🛡️  Kubernetes DevSecOps Production Guardrail Audit"
echo "=========================================================="

FAILURES=0
WARNINGS=0

# 1. Check Liveness & Readiness Probes
echo "[1/10] Auditing Health Probes (Liveness & Readiness)..."
if grep -q "livenessProbe:" "$TEMP_MANIFEST" && grep -q "readinessProbe:" "$TEMP_MANIFEST"; then
  echo "  ✔ [PASS] Both livenessProbe and readinessProbe configured."
else
  echo "  ✖ [FAIL] Missing livenessProbe or readinessProbe in workload specs."
  FAILURES=$((FAILURES + 1))
fi

# 2. Check Resource Requests & Limits
echo "[2/10] Auditing Resource Requests & Limits..."
if grep -q "requests:" "$TEMP_MANIFEST" && grep -q "limits:" "$TEMP_MANIFEST"; then
  echo "  ✔ [PASS] Both resource requests and limits are defined."
else
  echo "  ✖ [FAIL] Missing CPU/Memory requests or limits."
  FAILURES=$((FAILURES + 1))
fi

# 3. Check SecurityContext (runAsNonRoot)
echo "[3/10] Auditing SecurityContext (runAsNonRoot)..."
if grep -q "runAsNonRoot: true" "$TEMP_MANIFEST"; then
  echo "  ✔ [PASS] runAsNonRoot: true is enforced."
else
  echo "  ✖ [FAIL] runAsNonRoot: true not found. Root execution prohibited."
  FAILURES=$((FAILURES + 1))
fi

# 4. Check Privilege Escalation
echo "[4/10] Auditing Privilege Escalation Prevention..."
if grep -q "allowPrivilegeEscalation: false" "$TEMP_MANIFEST"; then
  echo "  ✔ [PASS] allowPrivilegeEscalation: false is enforced."
else
  echo "  ✖ [FAIL] allowPrivilegeEscalation: false not detected."
  FAILURES=$((FAILURES + 1))
fi

# 5. Check Image Tags (Reject :latest)
echo "[5/10] Auditing Container Image Tags..."
if grep -E "image:.*:latest" "$TEMP_MANIFEST" >/dev/null 2>&1; then
  echo "  ✖ [FAIL] Image tagged with ':latest' detected. Immutable version tags required."
  FAILURES=$((FAILURES + 1))
else
  echo "  ✔ [PASS] No ':latest' image tags detected."
fi

# 6. Check Capabilities (Drop ALL)
echo "[6/10] Auditing Linux Capabilities (Drop ALL)..."
if grep -q "drop:" "$TEMP_MANIFEST" && grep -E "(\"ALL\"|'ALL'|ALL)" "$TEMP_MANIFEST" >/dev/null 2>&1; then
  echo "  ✔ [PASS] Linux capabilities dropped (ALL)."
else
  echo "  ⚠ [WARN] capabilities.drop: [ALL] not detected."
  WARNINGS=$((WARNINGS + 1))
fi

# 7. Check for PodDisruptionBudget (PDB)
echo "[7/10] Auditing PodDisruptionBudget (PDB)..."
if grep -q "kind: PodDisruptionBudget" "$TEMP_MANIFEST"; then
  echo "  ✔ [PASS] PodDisruptionBudget manifest found."
else
  echo "  ⚠ [WARN] No PodDisruptionBudget found. Highly recommended for multi-replica services."
  WARNINGS=$((WARNINGS + 1))
fi

# 8. Check for HorizontalPodAutoscaler (HPA)
echo "[8/10] Auditing HorizontalPodAutoscaler (HPA)..."
if grep -q "kind: HorizontalPodAutoscaler" "$TEMP_MANIFEST"; then
  echo "  ✔ [PASS] HorizontalPodAutoscaler manifest found."
else
  echo "  ⚠ [WARN] No HorizontalPodAutoscaler found."
  WARNINGS=$((WARNINGS + 1))
fi

# 9. Check for NetworkPolicy
echo "[9/10] Auditing NetworkPolicy (Zero-Trust)..."
if grep -q "kind: NetworkPolicy" "$TEMP_MANIFEST"; then
  echo "  ✔ [PASS] NetworkPolicy manifest found."
else
  echo "  ⚠ [WARN] No NetworkPolicy found. Default-deny zero trust recommended."
  WARNINGS=$((WARNINGS + 1))
fi

# 10. Check RollingUpdate Strategy & PreStop Hook
echo "[10/10] Auditing Zero-Downtime Deployment Lifecycle..."
if grep -q "RollingUpdate" "$TEMP_MANIFEST" || grep -q "preStop:" "$TEMP_MANIFEST"; then
  echo "  ✔ [PASS] RollingUpdate strategy or preStop lifecycle hook detected."
else
  echo "  ⚠ [WARN] Neither RollingUpdate strategy nor preStop hook found."
  WARNINGS=$((WARNINGS + 1))
fi

echo "=========================================================="
if [ "$FAILURES" -gt 0 ]; then
  echo "❌ AUDIT FAILED: $FAILURES critical non-negotiable violation(s) detected ($WARNINGS warning(s))."
  exit 1
else
  echo "✅ AUDIT PASSED: 0 critical violations ($WARNINGS advisory warning(s))."
  exit 0
fi
