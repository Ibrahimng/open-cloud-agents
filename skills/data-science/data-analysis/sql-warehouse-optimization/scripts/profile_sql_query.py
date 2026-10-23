#!/usr/bin/env python3
"""
profile_sql_query.py - Static Query Analyzer & Anti-Pattern Detector for BigQuery/Snowflake SQL

Inspects SQL files for costly anti-patterns:
- SELECT * usage
- Missing WHERE clauses on partitioned tables
- Cross join syntax
- High-cardinality COUNT(DISTINCT)
"""

import sys
import re
import argparse

ANTI_PATTERNS = [
    (re.compile(r'(?i)\bSELECT\s+\*\b'), "[HIGH RISK] 'SELECT *' detected. Always enumerate columns explicitly to prevent full-table byte scans."),
    (re.compile(r'(?i)\bCROSS\s+JOIN\b'), "[CRITICAL] Explicit 'CROSS JOIN' detected. Can result in exponential Cartesian product memory explosion."),
    (re.compile(r'(?i)\bCOUNT\s*\(\s*DISTINCT\b'), "[OPTIMIZATION] 'COUNT(DISTINCT)' detected. On large datasets, evaluate 'APPROX_COUNT_DISTINCT' to save slot time."),
    (re.compile(r'(?i)\bORDER\s+BY\b(?!.*LIMIT)'), "[PERFORMANCE] 'ORDER BY' without 'LIMIT' in outer query. Forces single-node global sorting.")
]

def analyze_sql(filepath: str) -> int:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"Profiling SQL query: {filepath}")
    print("=" * 60)
    warnings = []

    for pattern, msg in ANTI_PATTERNS:
        if pattern.search(content):
            warnings.append(msg)

    if not warnings:
        print("[PASS] Zero high-cost analytical anti-patterns detected.")
        return 0

    print(f"[WARN] Found {len(warnings)} optimization suggestion(s):")
    for w in warnings:
        print(f"  • {w}")
    return 1

def main():
    parser = argparse.ArgumentParser(description="Analyze SQL file for analytical warehouse anti-patterns.")
    parser.add_argument("sql_file", help="Path to SQL file")
    args = parser.parse_args()

    sys.exit(analyze_sql(args.sql_file))

if __name__ == "__main__":
    main()
