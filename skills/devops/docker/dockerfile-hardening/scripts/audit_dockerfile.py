#!/usr/bin/env python3
"""
audit_dockerfile.py - Static Security Linter for Dockerfiles

Audits a Dockerfile for common container security anti-patterns:
- Running as root user
- Missing explicit tags (using ':latest')
- Leaked credentials or tokens in ENV/ARG
- Missing multi-stage architecture
"""

import sys
import re
import argparse

DANGEROUS_SECRETS_PATTERN = re.compile(
    r'(?i)(api[_-]?key|secret|password|token|aws[_-]?access)\s*[=:]\s*[\'"][^\'"]+[\'"]'
)

def audit_dockerfile(filepath: str) -> int:
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    issues = []
    has_user_instruction = False
    from_stages = 0

    for idx, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        # Count build stages
        if re.match(r'(?i)^FROM\s+', line):
            from_stages += 1
            if ":latest" in line or (":" not in line.split()[1] and "@" not in line.split()[1]):
                issues.append(f"Line {idx}: Unpinned base image tag detected ('{line}'). Use an explicit version or digest.")

        # Check for USER instruction
        if re.match(r'(?i)^USER\s+', line):
            has_user_instruction = True
            if re.match(r'(?i)^USER\s+(root|0)\b', line):
                issues.append(f"Line {idx}: Explicit root user declared: '{line}'.")

        # Check for leaked secrets
        if DANGEROUS_SECRETS_PATTERN.search(line):
            issues.append(f"Line {idx}: Potential hardcoded secret found: '{line}'.")

        # Check for curl/wget piped to sh
        if re.search(r'(curl|wget).+\|\s*(sh|bash)', line):
            issues.append(f"Line {idx}: Insecure pipe-to-shell command detected: '{line}'.")

    if from_stages == 1:
        issues.append("Single-stage Dockerfile detected. Recommend adopting multi-stage build to minimize runtime attack surface.")

    if not has_user_instruction:
        issues.append("No 'USER' instruction found. Container will default to running as root.")

    print(f"Auditing Dockerfile: {filepath}")
    print("=" * 60)
    if not issues:
        print("[PASS] Zero security anti-patterns detected.")
        return 0

    print(f"[FAIL] Found {len(issues)} security issue(s):")
    for issue in issues:
        print(f"  • {issue}")
    return 1

def main():
    parser = argparse.ArgumentParser(description="Audit a Dockerfile for security compliance.")
    parser.add_argument("dockerfile", nargs="?", default="Dockerfile", help="Path to Dockerfile (default: Dockerfile)")
    args = parser.parse_args()

    sys.exit(audit_dockerfile(args.dockerfile))

if __name__ == "__main__":
    main()
