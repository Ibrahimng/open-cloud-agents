#!/usr/bin/env bash
# ==============================================================================
# Agent Skill Component: Security Compliance Commander (SCC)
# Framework Mapping: ISO/IEC 42001 & OWASP Top 10 for LLM Applications
# Purpose: Orchestrates AI Lineage auditing and Static Code Analysis checks.
# ==============================================================================

set -euo pipefail

# Define operational paths matching project workspace tree
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../../../.." && pwd)"

# Verify root detection, fallback to pwd if necessary
if [[ ! -f "${PROJECT_ROOT}/skills/security/compliance/ai-governance-audit/scripts/verify_ai_lineage.py" ]]; then
    PROJECT_ROOT="$(pwd)"
fi

LINEAGE_SCRIPT="${PROJECT_ROOT}/skills/security/compliance/ai-governance-audit/scripts/verify_ai_lineage.py"
OWASP_SCRIPT="${PROJECT_ROOT}/skills/security/owasp-llm-security/scripts/scan_prompt_injection.py"
OUTPUT_SCRIPT="${PROJECT_ROOT}/skills/security/owasp-llm-security/scripts/validate_llm_outputs.sh"

# Terminal formatting definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}====================================================================${NC}"
echo -e "${BLUE}⚡ SCC AGENT RUNTIME: Initializing Automated AI Safety Pipeline ⚡${NC}"
echo -e "${BLUE}====================================================================${NC}"

PIPELINE_FAILED=0

# ------------------------------------------------------------------------------
# PHASE 1: Data Provenance & Lineage Verification (ISO 42001)
# ------------------------------------------------------------------------------
echo -e "\n${BLUE}[PHASE 1] Continuous Auditing: Data Provenance & Lineage Tracking${NC}"
if [[ -f "$LINEAGE_SCRIPT" ]]; then
    # Execute verification script against your pipelines manifest
    if python3 "$LINEAGE_SCRIPT"; then
        echo -e "${GREEN}✅ Phase 1 Success: Data provenance metadata structures verified.${NC}"
    else
        echo -e "${YELLOW}⚠️ Phase 1 Warning: Gaps discovered in ISO 42001 compliance criteria.${NC}"
    fi
else
    echo -e "${RED}❌ Error: Lineage verification module not found at: ${LINEAGE_SCRIPT}${NC}"
    PIPELINE_FAILED=1
fi

# ------------------------------------------------------------------------------
# PHASE 2: Static Code Guardrail Check (OWASP LLM01)
# ------------------------------------------------------------------------------
echo -e "\n${BLUE}[PHASE 2] Static Code Analysis: Prompt Injection Vectors${NC}"
if [[ -f "$OWASP_SCRIPT" ]]; then
    # Execute injection scanner engine
    if python3 "$OWASP_SCRIPT"; then
        echo -e "${GREEN}✅ Phase 2 Success: Zero high-risk prompt string interpolations identified.${NC}"
    else
        echo -e "${RED}❌ Phase 2 Failure: Unsafe dynamic prompt templates found in source files.${NC}"
        PIPELINE_FAILED=1
    fi
else
    echo -e "${RED}❌ Error: OWASP LLM static analyzer not found at: ${OWASP_SCRIPT}${NC}"
    PIPELINE_FAILED=1
fi

# ------------------------------------------------------------------------------
# PHASE 3: Output Integrity Verification (OWASP LLM02)
# ------------------------------------------------------------------------------
echo -e "\n${BLUE}[PHASE 3] Output Integrity Check: Toxic Payload Interception${NC}"
if [[ -f "$OUTPUT_SCRIPT" ]]; then
    if bash "$OUTPUT_SCRIPT"; then
        echo -e "${GREEN}✅ Phase 3 Success: Model output matches safe execution profiles.${NC}"
    else
        echo -e "${RED}❌ Phase 3 Failure: Model output contains unsafe execution vectors.${NC}"
        PIPELINE_FAILED=1
    fi
else
    echo -e "${RED}❌ Error: Output validation module not found at: ${OUTPUT_SCRIPT}${NC}"
    PIPELINE_FAILED=1
fi

# ------------------------------------------------------------------------------
# PIPELINE TERMINATION LOOP
# ------------------------------------------------------------------------------
echo -e "\n${BLUE}====================================================================${NC}"
if [[ "$PIPELINE_FAILED" -eq 0 ]]; then
    echo -e "${GREEN}🎉 STATUS: ALL AI SAFETY AND GOVERNANCE PIPELINE CHECKS PASSED 🎉${NC}"
    echo -e "${BLUE}====================================================================${NC}"
    exit 0
else
    echo -e "${RED}🚨 STATUS: PIPELINE BLOCK - RESOLVE OUTSTANDING AI SECURITY VULNERABILITIES 🚨${NC}"
    echo -e "${BLUE}====================================================================${NC}"
    exit 1
fi

