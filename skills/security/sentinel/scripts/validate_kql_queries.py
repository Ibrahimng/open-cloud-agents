#!/usr/bin/env python3
"""
Microsoft Sentinel Kusto Query Language (KQL) Validator & Performance Linter.
Validates syntax, time boundary constraints, balanced delimiters,
and entity mapping conventions across Sentinel analytics queries.

Usage:
    python3 validate_kql_queries.py --query-file references/kql-threat-hunting-library.md
    python3 validate_kql_queries.py --raw-kql "SigninLogs | where TimeGenerated > ago(1h) | project UserPrincipalName"
"""

import argparse
import re
import sys
from typing import List, Dict, Any, Tuple

COMMON_SENTINEL_TABLES = {
    "signinlogs", "auditlogs", "azureactivity", "azurediagnostics",
    "securityalert", "securityincident", "commonsecuritylog", "syslog",
    "deviceprocesssevents", "devicefileevents", "devicenetworkevents",
    "anomalies", "identityinfo", "officeactivity", "awscloudtrail",
    "googlecloudaudit"
}

VALID_KQL_OPERATORS = {
    "where", "project", "extend", "summarize", "join", "union",
    "order by", "sort by", "top", "take", "limit", "distinct",
    "mv-expand", "make-series", "serialize", "evaluate", "parse",
    "parse-where", "count"
}

def extract_kql_blocks(file_path: str) -> List[Tuple[str, str]]:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = []
    # If markdown file, extract fenced kusto / kql blocks
    if file_path.endswith(".md"):
        matches = re.finditer(r"(?:###\s+(.*?)\n)?```(?:kusto|kql)\n(.*?)```", content, re.DOTALL)
        for m in matches:
            title = m.group(1).strip() if m.group(1) else "Unnamed Query"
            code = m.group(2).strip()
            blocks.append((title, code))
    else:
        blocks.append(("Single Query", content.strip()))

    return blocks

def check_balanced_delimiters(code: str) -> bool:
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    in_single_quote = False
    in_double_quote = False

    for char in code:
        if char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
        elif char == "'" and not in_double_quote:
            in_single_quote = not in_single_quote

        if in_single_quote or in_double_quote:
            continue

        if char in "([{":
            stack.append(char)
        elif char in ")]}":
            if not stack or stack[-1] != pairs[char]:
                return False
            stack.pop()

    return len(stack) == 0

def lint_kql_query(name: str, query: str) -> Tuple[List[str], List[str]]:
    errors = []
    warnings = []

    lines = [l.strip() for l in query.splitlines() if l.strip() and not l.strip().startswith("//")]
    if not lines:
        errors.append(f"{name}: Empty query")
        return errors, warnings

    # 1. Delimiter balance check
    if not check_balanced_delimiters(query):
        errors.append(f"{name}: Unbalanced parentheses, brackets, or quotes")

    # 2. Base table check
    first_token = lines[0].split()[0].lower()
    if first_token == "let" or first_token.startswith("let "):
        # Query starts with let statement, find root table
        root_table = None
        for line in lines:
            if not line.startswith("let ") and not line.startswith("//") and not line.startswith("let\t"):
                root_table = line.split()[0].lower()
                break
        first_token = root_table or "unknown"

    first_token_clean = re.sub(r"[^a-z0-9_]", "", first_token)
    if first_token_clean not in COMMON_SENTINEL_TABLES and not first_token_clean.startswith("custom"):
        warnings.append(f"{name}: Table '{first_token_clean}' is not in the recognized Sentinel common schema list")

    # 3. Mandatory TimeGenerated filter check
    time_filter_found = False
    for line in lines:
        if "timegenerated" in line.lower() and ("ago(" in line.lower() or "between" in line.lower() or ">=" in line or "timewindow" in line.lower()):
            time_filter_found = True
            break
    if not time_filter_found:
        warnings.append(f"{name}: Missing explicit 'TimeGenerated > ago(...)' filter (risk of costly full-table scan)")

    # 4. Entity projection check for Sentinel incidents
    has_entity_mapping = False
    for line in lines:
        if any(e in line for e in ["AccountCustomEntity", "HostCustomEntity", "IPCustomEntity", "URLCustomEntity", "FileHashCustomEntity"]):
            has_entity_mapping = True
            break
    if not has_entity_mapping:
        warnings.append(f"{name}: No Sentinel entity mapping detected (recommend projecting AccountCustomEntity, IPCustomEntity, or HostCustomEntity)")

    return errors, warnings

def main():
    parser = argparse.ArgumentParser(description="Microsoft Sentinel KQL Validator & Linter")
    parser.add_argument("--query-file", help="Path to markdown or KQL file containing queries")
    parser.add_argument("--raw-kql", help="Raw KQL query string to evaluate")

    args = parser.parse_args()

    queries = []
    if args.query_file:
        queries = extract_kql_blocks(args.query_file)
    elif args.raw_kql:
        queries = [("Raw Input Query", args.raw_kql)]
    else:
        print("Please provide --query-file <path> or --raw-kql '<query>'")
        sys.exit(1)

    print("============================================================")
    print(" 🔎 Microsoft Sentinel KQL Validator & Linter")
    print("============================================================")
    print(f"Total queries evaluated: {len(queries)}\n")

    total_errors = 0
    total_warnings = 0

    for name, code in queries:
        errors, warnings = lint_kql_query(name, code)
        status = "✔ PASS" if not errors and not warnings else ("⚠️ WARN" if not errors else "❌ FAIL")
        print(f"[{status}] {name}")
        for err in errors:
            print(f"    ❌ Error: {err}")
            total_errors += 1
        for warn in warnings:
            print(f"    ⚠️  Warning: {warn}")
            total_warnings += 1

    print("============================================================")
    if total_errors > 0:
        print(f"Failed with {total_errors} error(s) and {total_warnings} warning(s).")
        sys.exit(1)
    else:
        print(f"All {len(queries)} KQL queries validated cleanly ({total_warnings} warning(s)).")
        sys.exit(0)

if __name__ == "__main__":
    main()

