#!/usr/bin/env bash
set -euo pipefail

# validate_oidc_token.sh - Base64 decode and inspect unencrypted JWT payload claims

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <jwt-token-string>"
  exit 1
fi

JWT="$1"

# Extract payload (second segment between dots)
PAYLOAD=$(echo "$JWT" | cut -d'.' -f2)

# Add padding if needed
REMAINDER=$(( ${#PAYLOAD} % 4 ))
if [ $REMAINDER -eq 2 ]; then
  PAYLOAD="${PAYLOAD}=="
elif [ $REMAINDER -eq 3 ]; then
  PAYLOAD="${PAYLOAD}="
fi

echo "Decoded OIDC Token Claims:"
echo "=========================================="
echo "$PAYLOAD" | base64 -d 2>/dev/null | jq . || echo "$PAYLOAD" | base64 -D 2>/dev/null | jq .
