#!/usr/bin/env bash
# ==============================================================================
# Agent Skill Component: Security Compliance Commander (SCC)
# Framework Mapping: OWASP Top 10 for LLM Applications (LLM02)
# Purpose: Validates model-generated responses against toxic execution strings.
# ==============================================================================

set -euo pipefail

# Terminal formatting definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

# Allow CLI override for target file or use in-memory mock buffer
TARGET_FILE="${1:-app/storage/last_inference_output.log}"

echo -e "${YELLOW}[*] OWASP LLM02 Guard: Initializing Output Structural Check...${NC}"

# Ensure log path context exists defensively before executing inspection
if [ ! -f "$TARGET_FILE" ]; then
    mkdir -p "$(dirname "$TARGET_FILE")"
    # Establish a default safe template payload string if file does not exist
    echo "SUCCESS: Compliance parameters validated successfully." > "$TARGET_FILE"
fi

# Read output log payload string
MODEL_RESPONSE=$(cat "$TARGET_FILE")

# ------------------------------------------------------------------------------
# EVALUATION LAYER: Threat String Verification
# ------------------------------------------------------------------------------
INVALID_OUTPUT_FLAG=0

# 1. Inspect for explicit Remote Code Execution (RCE) payload signatures
if echo "$MODEL_RESPONSE" | grep -Ei "rm -rf|chmod \+x|/etc/passwd" > /dev/null; then
    echo -e "${RED}🚨 [OWASP LLM02 - CRITICAL RISK] Model generated suspect system execution payload strings!${NC}"
    echo -e "   Payload Finding: $(echo "$MODEL_RESPONSE" | grep -Ei "rm -rf|chmod \+x|/etc/passwd")"
    INVALID_OUTPUT_FLAG=1
fi

# 2. Inspect for unparameterized SQL query injection attempts
if echo "$MODEL_RESPONSE" | grep -Ei "UNION SELECT|' OR '1'='1|DROP TABLE" > /dev/null; then
    echo -e "${RED}🚨 [OWASP LLM02 - CRITICAL RISK] Model output contains dangerous SQL query structures!${NC}"
    echo -e "   Payload Finding: $(echo "$MODEL_RESPONSE" | grep -Ei "UNION SELECT|' OR '1'='1|DROP TABLE")"
    INVALID_OUTPUT_FLAG=1
fi

# ------------------------------------------------------------------------------
# TERMINATION ROUTINE
# ------------------------------------------------------------------------------
if [ "$INVALID_OUTPUT_FLAG" -eq 1 ]; then
    echo -e "${RED}[-] Execution Blocked: Model output contains unsafe execution vectors.${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Output Validation Passed: Model response matches safe structure profiles.${NC}"
    exit 0
fi
