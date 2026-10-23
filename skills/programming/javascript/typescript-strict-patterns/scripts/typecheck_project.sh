#!/usr/bin/env bash
set -euo pipefail

# typecheck_project.sh - Strict TypeScript typechecking validation

echo "Executing TypeScript typecheck with --noEmit..."

if ! command -v tsc >/dev/null 2>&1 && ! command -v npx >/dev/null 2>&1; then
  echo "Error: Neither tsc nor npx found on PATH."
  exit 1
fi

if command -v tsc >/dev/null 2>&1; then
  tsc --noEmit --pretty
else
  npx tsc --noEmit --pretty
fi

echo "[PASS] TypeScript compilation check passed with zero type errors."
