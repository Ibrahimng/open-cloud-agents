#!/usr/bin/env bash
set -euo pipefail

# emergency_secret_scrub.sh - Emergency Git Reflog & History Cleaner using git-filter-repo

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <secret-string-to-redact>"
  echo "CAUTION: This will rewrite git commit SHAs across all branches."
  exit 1
fi

SECRET_TO_SCRUB="$1"

echo "=========================================================="
echo "EMERGENCY GIT SECRET HISTORY SCRUBBER"
echo "=========================================================="
echo "Searching for commits containing the secret..."

if ! command -v git-filter-repo >/dev/null 2>&1; then
  echo "Error: git-filter-repo is required. Install with: pip install git-filter-repo"
  exit 1
fi

TMP_FILE=$(mktemp)
echo "${SECRET_TO_SCRUB}==>[REDACTED_BY_SECURITY]" > "$TMP_FILE"

echo "Executing git-filter-repo replacement..."
git-filter-repo --replace-text "$TMP_FILE" --force

rm -f "$TMP_FILE"
echo "[PASS] Secret string successfully scrubbed from all commits and trees."
echo "To push scrubbed history: git push origin --force --all && git push origin --force --tags"
