#!/usr/bin/env bash
set -euo pipefail

# run_coverage_gate.sh - Enforces minimum test coverage gate in CI/CD

MIN_COVERAGE="${1:-85}"
echo "Running pytest test suite with minimum coverage gate: ${MIN_COVERAGE}%"

if ! command -v pytest >/dev/null 2>&1; then
  echo "Error: pytest binary not found on PATH."
  exit 1
fi

pytest --cov=src --cov-report=term-missing --cov-fail-under="$MIN_COVERAGE"
echo "[PASS] Test suite and coverage gate passed successfully."

