#!/usr/bin/env python3
"""
audit_workflows.py - Security Auditor for GitHub Actions Workflows

Scans .github/workflows/*.yml for common security vulnerabilities:
- Unpinned third-party actions (using mutable @v1, @v2, @main instead of commit SHA)
- Dangerous pull_request_target triggers
- Missing top-level permissions block (defaults to write-all)
- Script injection via untrusted context interpolation (${{ github.event.issue.title }})
"""

import sys
import glob
import re

UNPINNED_ACTION_REGEX = re.compile(r'uses:\s*[\'"]?([a-zA-Z0-9_\-]+/[a-zA-Z0-9_\-]+)@(v\d+|main|master)[\'"]?')
UNTRUSTED_INJECTION_REGEX = re.compile(r'\$\{\{\s*github\.event\.(issue|pull_request)\.(title|body)\s*\}\}')

def audit_workflow(filepath: str) -> list:
    issues = []
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.splitlines()

    # Check for missing top-level permissions block
    if not re.search(r'(?m)^permissions:', content):
        issues.append("Missing top-level 'permissions:' block. Defaults to broad write access on older GitHub Enterprise setups.")

    # Check for pull_request_target
    if "pull_request_target" in content:
        issues.append("Uses 'pull_request_target'. If checking out PR code, repository secrets may be exfiltrated by fork PRs.")

    for idx, line in enumerate(lines, start=1):
        if UNPINNED_ACTION_REGEX.search(line):
            match = UNPINNED_ACTION_REGEX.search(line).group(0)
            issues.append(f"Line {idx}: Unpinned action detected ('{match}'). Recommend pinning to full 40-character commit SHA.")

        if UNTRUSTED_INJECTION_REGEX.search(line):
            issues.append(f"Line {idx}: Dangerous context interpolation in run block. Susceptible to command injection.")

    return issues

def main():
    workflows = glob.glob(".github/workflows/*.y*ml")
    if not workflows:
        print("No GitHub Actions workflows found in .github/workflows/")
        sys.exit(0)

    total_issues = 0
    for wf in workflows:
        issues = audit_workflow(wf)
        if issues:
            print(f"\n[FAIL] Workflow: {wf}")
            for issue in issues:
                print(f"  • {issue}")
            total_issues += len(issues)
        else:
            print(f"[PASS] Workflow: {wf} (Hardened)")

    sys.exit(1 if total_issues > 0 else 0)

if __name__ == "__main__":
    main()

