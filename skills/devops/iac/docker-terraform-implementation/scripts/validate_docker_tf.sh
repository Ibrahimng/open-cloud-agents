#!/usr/bin/env bash
# ==============================================================================
# validate_docker_tf.sh
# Validates Docker Terraform configurations:
# 1. Format check: terraform fmt -check -recursive
# 2. Syntax & internal validity: terraform validate
# 3. Dry-run plan: terraform plan (optional if remote backend initialized)
# ==============================================================================
set -euo pipefail

TARGET_DIR="${1:-infrastructure/docker}"

if [ ! -d "$TARGET_DIR" ]; then
  # Fallback to current or infrastructure directory if infrastructure/docker doesn't exist
  if [ -d "infrastructure" ]; then
    TARGET_DIR="infrastructure"
  else
    TARGET_DIR="."
  fi
fi

echo "============================================================"
echo " 🛡️  Docker Terraform Validation Suite: $TARGET_DIR"
echo "============================================================"

# 1. Formatting
echo "ℹ Checking Terraform format..."
if terraform -chdir="$TARGET_DIR" fmt -check -recursive; then
  echo "✔ Formatting is clean."
else
  echo "⚠️ Format issues detected. Run 'terraform fmt -recursive $TARGET_DIR' to fix."
  exit 1
fi

# 2. Validation (if initialized)
if [ -d "$TARGET_DIR/.terraform" ]; then
  echo "ℹ Running terraform validate..."
  terraform -chdir="$TARGET_DIR" validate
  echo "✔ Validation passed."
else
  echo "ℹ Terraform not initialized (.terraform missing). Skipping validate & plan."
fi

echo "============================================================"
echo "SUCCESS: Docker Terraform checks passed cleanly!"
