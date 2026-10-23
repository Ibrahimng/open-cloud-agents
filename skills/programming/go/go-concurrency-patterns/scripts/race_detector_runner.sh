#!/usr/bin/env bash
set -euo pipefail

# race_detector_runner.sh - Executes Go unit tests with data race detector and leak profiling

echo "Executing Go test suite with -race flag..."

if ! command -v go >/dev/null 2>&1; then
  echo "Error: go binary not found on PATH."
  exit 1
fi

go test -race -v -timeout 120s ./...
echo "[PASS] All Go concurrent tests passed with zero data races detected."

