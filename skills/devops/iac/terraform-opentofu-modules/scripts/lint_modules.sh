#!/usr/bin/env bash
set -euo pipefail

# lint_modules.sh - Static analysis and formatting validation for Terraform / OpenTofu modules

TARGET_DIR="${1:-.}"
echo "Running static analysis on: $TARGET_DIR"

# 1. Format check
if command -v tofu >/dev/null 2>&1; then
  echo "Checking OpenTofu formatting..."
  tofu fmt -check -recursive "$TARGET_DIR"
elif command -v terraform >/dev/null 2>&1; then
  echo "Checking Terraform formatting..."
  terraform fmt -check -recursive "$TARGET_DIR"
else
  echo "[SKIP] Neither tofu nor terraform binary found on PATH."
fi

# 2. Check for hardcoded AWS access keys or secrets in .tf files
echo "Scanning for hardcoded credentials..."
if grep -rnE "(AKIA[0-9A-Z]{16}|aws_secret_access_key|password\s*=\s*\"[^\$])" "$TARGET_DIR" --include="*.tf" | grep -v 'variable ' | grep -v 'description'; then
  echo "[FAIL] Potential hardcoded credential detected in HCL files!"
  exit 1
else
  echo "[PASS] Zero hardcoded secrets detected in .tf files."
fi

echo "[PASS] Module linting completed successfully."

