#!/usr/bin/env bash
set -euo pipefail

# promote_environment.sh - Automated GitOps environment image tag promotion

if [ "$#" -lt 3 ]; then
  echo "Usage: $0 <overlays-dir> <target-env: dev|uat|prod> <new-image-tag>"
  echo "Example: $0 gitops/overlays prod sha-a1b2c3d"
  exit 1
fi

OVERLAYS_DIR="$1"
TARGET_ENV="$2"
NEW_TAG="$3"
KUSTOMIZE_FILE="$OVERLAYS_DIR/$TARGET_ENV/kustomization.yaml"

if [ ! -f "$KUSTOMIZE_FILE" ]; then
  echo "Error: Kustomization file not found at: $KUSTOMIZE_FILE"
  exit 1
fi

echo "Promoting '$TARGET_ENV' to new tag: $NEW_TAG..."

# Update newTag in kustomization.yaml using kustomize or sed
if command -v kustomize >/dev/null 2>&1; then
  (cd "$OVERLAYS_DIR/$TARGET_ENV" && kustomize edit set image "app=*:$NEW_TAG")
else
  # Portable in-place replacement
  sed -i.bak -E "s/(newTag:\s*).*/\1$NEW_TAG/" "$KUSTOMIZE_FILE" && rm -f "$KUSTOMIZE_FILE.bak"
fi

echo "[PASS] Successfully updated $KUSTOMIZE_FILE to tag $NEW_TAG."
echo "Review git diff and commit with: git commit -m 'chore(gitops): promote $TARGET_ENV to $NEW_TAG'"
