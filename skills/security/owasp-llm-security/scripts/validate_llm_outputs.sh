#!/usr/bin/env bash
# ==============================================================================
# LLM Output Validator & Sanitization Gatekeeper (OWASP LLM02)
# ==============================================================================
# Validates raw model responses against downstream SQL injection, OS command
# injection, XSS payloads, and malformed JSON syntax before execution.
# ==============================================================================
set -euo pipefail

INPUT_TEXT=""
INPUT_FILE=""
CHECK_SQL=0
CHECK_CMD=0
CHECK_XSS=0
CHECK_JSON=0
RUN_SAMPLE=0

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  --input, -i TEXT       Raw LLM output string to validate"
    echo "  --file, -f PATH        File containing LLM output"
    echo "  --check-sql            Check for raw SQL commands & injection patterns"
    echo "  --check-cmd            Check for dangerous OS shell commands"
    echo "  --check-xss            Check for HTML/XSS script execution tags"
    echo "  --check-json           Verify valid JSON structure"
    echo "  --all                  Enable all security checks"
    echo "  --sample               Execute built-in test suite"
    echo "  --help, -h             Show this help message"
    exit 1
}

# Parse CLI arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --input|-i)
            INPUT_TEXT="$2"
            shift 2
            ;;
        --file|-f)
            INPUT_FILE="$2"
            shift 2
            ;;
        --check-sql)
            CHECK_SQL=1
            shift
            ;;
        --check-cmd)
            CHECK_CMD=1
            shift
            ;;
        --check-xss)
            CHECK_XSS=1
            shift
            ;;
        --check-json)
            CHECK_JSON=1
            shift
            ;;
        --all)
            CHECK_SQL=1
            CHECK_CMD=1
            CHECK_XSS=1
            CHECK_JSON=1
            shift
            ;;
        --sample)
            RUN_SAMPLE=1
            shift
            ;;
        --help|-h)
            usage
            ;;
        *)
            echo "Unknown argument: $1" >&2
            usage
            ;;
    esac
done

# If no specific check enabled, default to all
if [[ $CHECK_SQL -eq 0 && $CHECK_CMD -eq 0 && $CHECK_XSS -eq 0 && $CHECK_JSON -eq 0 && $RUN_SAMPLE -eq 0 ]]; then
    CHECK_SQL=1
    CHECK_CMD=1
    CHECK_XSS=1
fi

validate_content() {
    local content="$1"
    local violations=()

    # 1. Check SQL injection / raw query patterns
    if [[ $CHECK_SQL -eq 1 ]]; then
        if echo "$content" | grep -E -i '\b(DROP|TRUNCATE|ALTER)\s+(TABLE|DATABASE|SCHEMA)\b' >/dev/null 2>&1; then
            violations+=("CRITICAL: Destructive SQL statement detected (DROP/TRUNCATE/ALTER).")
        fi
        if echo "$content" | grep -E -i '(;|--|\/\*|\*\/|\bOR\s+1\s*=\s*1\b|\bUNION\s+(ALL\s+)?SELECT\b)' >/dev/null 2>&1; then
            violations+=("HIGH: SQL injection or multi-statement delimiter detected.")
        fi
    fi

    # 2. Check OS command injection patterns
    if [[ $CHECK_CMD -eq 1 ]]; then
        if echo "$content" | grep -E '(\brm\s+-rf\b|\bmkfs\b|\bdd\s+if=|\bcurl\b.*\|\s*(bash|sh)|\bwget\b.*\|\s*(bash|sh)|\b(nc|netcat)\s+-e\b)' >/dev/null 2>&1; then
            violations+=("CRITICAL: Dangerous shell command sequence detected (rm -rf, piped curl, reverse shell).")
        fi
        if echo "$content" | grep -E '(`[^`]+`|\$\([^\)]+\)|;\s*(rm|cat|chmod|chown|wget|curl)\b)' >/dev/null 2>&1; then
            violations+=("HIGH: Shell command substitution or chained execution detected.")
        fi
    fi

    # 3. Check XSS patterns
    if [[ $CHECK_XSS -eq 1 ]]; then
        if echo "$content" | grep -E -i '<\s*script\b|javascript\s*:|<\s*iframe\b|onerror\s*=|onload\s*=' >/dev/null 2>&1; then
            violations+=("HIGH: Stored XSS or HTML script tag detected in output.")
        fi
    fi

    # 4. Check JSON validity if requested
    if [[ $CHECK_JSON -eq 1 ]]; then
        if ! python3 -c "import json, sys; json.loads(sys.stdin.read())" <<< "$content" >/dev/null 2>&1; then
            violations+=("MEDIUM: Malformed JSON output; fails strict parsing.")
        fi
    fi

    if [[ ${#violations[@]} -gt 0 ]]; then
        echo -e "\033[91m[FAIL]\033[0m Output validation failed with ${#violations[@]} violation(s):"
        for v in "${violations[@]}"; do
            echo "   ✖ $v"
        done
        return 1
    else
        echo -e "\033[92m[PASS]\033[0m Output passed all enabled syntactic and safety gates."
        return 0
    fi
}

if [[ $RUN_SAMPLE -eq 1 ]]; then
    echo "========================================================================"
    echo " 🧪 Executing OWASP LLM02 Output Validation Test Suite"
    echo "========================================================================"
    CHECK_SQL=1
    CHECK_CMD=1
    CHECK_XSS=1

    echo -n "Test 1: Safe benign text response... "
    validate_content "The cluster status is healthy with 5 active nodes." >/dev/null && echo "✔ PASS" || { echo "✖ FAIL"; exit 1; }

    echo -n "Test 2: Raw SQL injection attempt... "
    validate_content "SELECT * FROM users WHERE id = 1; DROP TABLE users; --" >/dev/null && { echo "✖ FAILED TO DETECT"; exit 1; } || echo "✔ BLOCKED"

    echo -n "Test 3: Destructive shell command... "
    validate_content "To clean up disk space, run: rm -rf /var/log/*" >/dev/null && { echo "✖ FAILED TO DETECT"; exit 1; } || echo "✔ BLOCKED"

    echo -n "Test 4: Stored XSS payload... "
    validate_content "<script>alert('pwned')</script>" >/dev/null && { echo "✖ FAILED TO DETECT"; exit 1; } || echo "✔ BLOCKED"

    echo "------------------------------------------------------------------------"
    echo "Verdict: ✅ All output validation test cases passed successfully."
    exit 0
fi

# Load content from argument or file
TARGET_CONTENT=""
if [[ -n "$INPUT_TEXT" ]]; then
    TARGET_CONTENT="$INPUT_TEXT"
elif [[ -n "$INPUT_FILE" ]]; then
    if [[ ! -f "$INPUT_FILE" ]]; then
        echo "Error: Target file '$INPUT_FILE' not found." >&2
        exit 1
    fi
    TARGET_CONTENT=$(cat "$INPUT_FILE")
else
    echo "Error: No input provided. Use --input, --file, or --sample." >&2
    usage
fi

validate_content "$TARGET_CONTENT"
