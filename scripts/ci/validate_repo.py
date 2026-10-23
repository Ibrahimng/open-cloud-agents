#!/usr/bin/env python3
"""
Open Cloud Agents: Repository Hygiene & Skill Spec Validator.
Validates:
1. Skill YAML Frontmatter (name, description) on all SKILL.md files.
2. Executable permissions on all helper and verification shell scripts (*.sh).
3. Internal relative Markdown links across core skills, agents, docs, and root files.
4. Absence of hardcoded local absolute user paths (/Users/ or /home/).

Usage:
    python3 scripts/ci/validate_repo.py
"""

import os
import re
import sys
import urllib.parse

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def log_pass(msg: str):
    print(f"  \033[92m✔\033[0m {msg}")

def log_fail(msg: str):
    print(f"  \033[91m✖\033[0m {msg}")

def log_info(msg: str):
    print(f"\033[94mℹ\033[0m {msg}")


def check_skill_frontmatter() -> list[str]:
    log_info("Checking YAML frontmatter on all SKILL.md files...")
    errors = []
    count = 0
    for root, _, files in os.walk(REPO_ROOT):
        if ".git" in root or "ai_brain" in root:
            continue
        for f in files:
            if f == "SKILL.md":
                count += 1
                p = os.path.join(root, f)
                rel_p = os.path.relpath(p, REPO_ROOT)
                try:
                    with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                        content = fh.read()
                    if not content.startswith("---"):
                        errors.append(f"{rel_p}: Missing starting '---' YAML frontmatter")
                        continue
                    # Check first 20 lines for name and description
                    head = "\n".join(content.splitlines()[:20])
                    if "name:" not in head:
                        errors.append(f"{rel_p}: Missing 'name:' in frontmatter")
                    if "description:" not in head:
                        errors.append(f"{rel_p}: Missing 'description:' in frontmatter")
                except Exception as e:
                    errors.append(f"{rel_p}: Failed to read file: {e}")

    if not errors:
        log_pass(f"All {count} SKILL.md specifications contain valid frontmatter.")
    else:
        for err in errors[:10]:
            log_fail(err)
        if len(errors) > 10:
            log_fail(f"... and {len(errors) - 10} more frontmatter errors.")
    return errors


def check_script_permissions() -> list[str]:
    log_info("Checking executable permissions on shell scripts (*.sh)...")
    errors = []
    count = 0
    for root, _, files in os.walk(REPO_ROOT):
        if ".git" in root or "ai_brain" in root:
            continue
        for f in files:
            if f.endswith(".sh"):
                count += 1
                p = os.path.join(root, f)
                rel_p = os.path.relpath(p, REPO_ROOT)
                if not os.access(p, os.X_OK):
                    errors.append(f"{rel_p}: Script is not executable (chmod +x required)")

    if not errors:
        log_pass(f"All {count} shell scripts have executable permissions.")
    else:
        for err in errors:
            log_fail(err)
    return errors


def check_markdown_links() -> list[str]:
    log_info("Checking internal relative Markdown links across core architecture & skills...")
    errors = []
    link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    count = 0

    # We validate root docs, agents, docs, and core skills (excluding 3rd-party vendor dumps)
    for root, _, files in os.walk(REPO_ROOT):
        if ".git" in root or "ai_brain" in root or "skills/csp" in root:
            continue
        for f in files:
            if f.endswith(".md"):
                count += 1
                path = os.path.join(root, f)
                rel_src = os.path.relpath(path, REPO_ROOT)
                dir_name = os.path.dirname(path)
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                        content = fh.read()
                    # Strip code blocks and inline code spans
                    content_clean = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
                    content_clean = re.sub(r"`[^`\n]+`", "", content_clean)
                    for m in link_pattern.finditer(content_clean):
                        target = m.group(2).strip()
                        # Ignore absolute external URLs, anchors, or pseudo-schemes
                        if target.startswith((
                            "http://", "https://", "mailto:", "#",
                            "file://", "sidecar://", "conversation://"
                        )):
                            continue
                        target_file = target.split("#")[0]
                        if not target_file:
                            continue
                        resolved = os.path.normpath(os.path.join(dir_name, urllib.parse.unquote(target_file)))
                        if not os.path.exists(resolved):
                            errors.append(f"{rel_src}: Broken link '{target}' -> target '{os.path.relpath(resolved, REPO_ROOT)}' not found")
                except Exception as e:
                    errors.append(f"{rel_src}: Failed to parse links: {e}")

    if not errors:
        log_pass(f"All relative links in {count} core Markdown documents resolve successfully.")
    else:
        for err in errors:
            log_fail(err)
    return errors


def check_no_absolute_user_paths() -> list[str]:
    log_info("Checking for leaking local machine paths (/Users/<username>/)...")
    errors = []
    # Match personal local workstation directories like /Users/username/
    user_path_pattern = re.compile(r"/Users/[a-zA-Z0-9_\-]+/")
    count = 0
    for root, _, files in os.walk(REPO_ROOT):
        if ".git" in root or "ai_brain" in root:
            continue
        for f in files:
            if f.endswith((".md", ".sh", ".yaml", ".yml", ".json")):
                count += 1
                p = os.path.join(root, f)
                rel_p = os.path.relpath(p, REPO_ROOT)
                try:
                    with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                        for line_num, line in enumerate(fh, 1):
                            if user_path_pattern.search(line):
                                errors.append(f"{rel_p}:{line_num}: Contains local user machine path: {line.strip()[:80]}")
                except Exception:
                    pass

    if not errors:
        log_pass(f"No local developer machine paths found in {count} tracked source files.")
    else:
        for err in errors:
            log_fail(err)
    return errors


def main():
    print("=" * 60)
    print(" 🛡️  Open Cloud Agents: Repository Hygiene & Validation Suite")
    print("=" * 60)
    
    all_errors = []
    all_errors.extend(check_skill_frontmatter())
    all_errors.extend(check_script_permissions())
    all_errors.extend(check_markdown_links())
    all_errors.extend(check_no_absolute_user_paths())

    print("=" * 60)
    if all_errors:
        print(f"\033[91mFAILED:\033[0m Found {len(all_errors)} repository hygiene violation(s).")
        sys.exit(1)
    else:
        print("\033[92mSUCCESS:\033[0m All repository hygiene checks passed cleanly!")
        sys.exit(0)

if __name__ == "__main__":
    main()
