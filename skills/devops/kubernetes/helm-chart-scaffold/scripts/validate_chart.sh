#!/usr/bin/env bash
set -euo pipefail

# validate_chart.sh - Automated linting, template rendering, and schema validation for Helm charts

CHART_DIR="${1:-.}"
echo "Validating Helm Chart in: $CHART_DIR"

if ! command -v helm >/dev/null 2>&1; then
  echo "Error: helm binary not found on PATH."
  exit 1
fi

echo "[1/3] Running helm lint..."
helm lint "$CHART_DIR"

echo "[2/3] Rendering templates with strict dry-run..."
helm template validate-test "$CHART_DIR" --dry-run --debug > /dev/null

echo "[3/3] Checking for values.schema.json..."
if [ -f "$CHART_DIR/values.schema.json" ]; then
  echo "[PASS] values.schema.json detected."
else
  echo "[WARN] No values.schema.json found in chart root. Adding a schema is recommended."
fi

echo "[PASS] Helm chart validation completed successfully."

