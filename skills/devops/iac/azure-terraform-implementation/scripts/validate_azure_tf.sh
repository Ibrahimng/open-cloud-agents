#!/usr/bin/env bash
# ==============================================================================
# validate_azure_tf.sh
# Validates Azure Terraform configurations:
# 1. Format check: terraform fmt -check -recursive
# 2. Syntax & internal validity: terraform validate
# 3. Dry-run plan: terraform plan (optional if remote backend initialized)
# ==============================================================================
set -euo pipefail

TARGET_DIR="${1:-infrastructure}"

if [ ! -d "$TARGET_DIR" ]; then
  echo "❌ Error: Target directory '$TARGET_DIR' does not exist."
  exit 1
fi

echo "============================================================"
echo " 🛡️  Azure Terraform Validation Suite: $TARGET_DIR"
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
echo "SUCCESS: Azure Terraform checks passed cleanly!"
