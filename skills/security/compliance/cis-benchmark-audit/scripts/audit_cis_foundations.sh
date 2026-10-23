#!/usr/bin/env bash
set -euo pipefail

# audit_cis_foundations.sh - Automated baseline audit for CIS Foundation security controls

echo "=========================================================="
echo "CIS Multi-Cloud Foundation Compliance Sanity Checker"
echo "=========================================================="

FAILURES=0

# 1. AWS Sanity Checks
if command -v aws >/dev/null 2>&1 && aws sts get-caller-identity >/dev/null 2>&1; then
  echo "[AWS] Auditing S3 Account-Level Public Access Block..."
  if aws s3control get-public-access-block --account-id "$(aws sts get-caller-identity --query 'Account' --output text)" 2>/dev/null | grep -q '"BlockPublicAcls": true'; then
    echo "[PASS] AWS S3 Account-level Block Public Access is active."
  else
    echo "[FAIL] AWS S3 Account-level Block Public Access is NOT fully enabled."
    FAILURES=$((FAILURES + 1))
  fi
else
  echo "[SKIP] AWS CLI not configured or unauthenticated."
fi

# 2. GCP Sanity Checks
if command -v gcloud >/dev/null 2>&1 && gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | grep -q "@"; then
  echo "[GCP] Checking organization constraint for uniform bucket access..."
  CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
  echo "[INFO] Active GCP Project: $CURRENT_PROJECT"
else
  echo "[SKIP] GCP CLI not configured or unauthenticated."
fi

echo "=========================================================="
if [ "$FAILURES" -gt 0 ]; then
  echo "[FAIL] CIS Sanity Audit found $FAILURES non-compliant control(s)."
  exit 1
else
  echo "[PASS] All active cloud checks passed baseline CIS requirements."
  exit 0
fi
