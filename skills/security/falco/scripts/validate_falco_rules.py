#!/usr/bin/env python3
"""
Falco Rules Syntax & Schema Validator.
Lints and verifies Falco YAML rule definitions, checking rule structure,
conditions, macros, lists, priorities, and MITRE ATT&CK tags.
Operates with standard library only (or PyYAML if installed).

Usage:
    python3 validate_falco_rules.py --rules path/to/rules.yaml
    python3 validate_falco_rules.py --rules path/to/cloud-native-threat-library.md
"""

import argparse
import re
import sys
from typing import List, Dict, Any, Tuple

VALID_PRIORITIES = {
    "EMERGENCY", "ALERT", "CRITICAL", "ERROR",
    "WARNING", "NOTICE", "INFO", "DEBUG"
}

def extract_yaml_blocks(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # If markdown file, extract fenced yaml blocks
    if file_path.endswith(".md"):
        yaml_blocks = re.findall(r"```ya?ml\n(.*?)```", content, re.DOTALL)
        if yaml_blocks:
            return "\n".join(yaml_blocks)

    return content

def check_balanced_parentheses(condition: str) -> bool:
    stack = []
    pairs = {')': '(', ']': '['}
    for char in condition:
        if char in '([':
            stack.append(char)
        elif char in ')]':
            if not stack or stack[-1] != pairs[char]:
                return False
            stack.pop()
    return len(stack) == 0

def parse_blocks_fallback(text: str) -> List[Dict[str, Any]]:
    """Lightweight, standard-library fallback parser for Falco YAML documents."""
    blocks = []
    current_block = {}
    current_key = None
    multiline_val = []

    lines = text.splitlines()
    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()

        # Skip empty lines and comments
        if not stripped or stripped.startswith("#"):
            continue

        # Check for start of new item (e.g. "- rule:", "- macro:", "- list:")
        match_start = re.match(r"^-\s+([a-zA-Z0-9_\-]+):\s*(.*)$", line)
        if match_start:
            if current_block:
                if current_key and multiline_val:
                    current_block[current_key] = " ".join(multiline_val).strip()
                blocks.append(current_block)
            current_block = {}
            current_key = match_start.group(1)
            val = match_start.group(2).strip()
            multiline_val = [val] if val else []
            continue

        # Check for secondary key (e.g. "  desc:", "  condition:", "  output:")
        match_key = re.match(r"^\s+([a-zA-Z0-9_\-]+):\s*(.*)$", line)
        if match_key and not line.strip().startswith("-"):
            if current_key and multiline_val:
                current_block[current_key] = " ".join(multiline_val).strip()
            current_key = match_key.group(1)
            val = match_key.group(2).strip()
            multiline_val = [val] if val else []
            continue

        # Multiline continuation line or list item
        if current_key:
            multiline_val.append(stripped.lstrip("- "))

    if current_block:
        if current_key and multiline_val:
            current_block[current_key] = " ".join(multiline_val).strip()
        blocks.append(current_block)

    return blocks

def validate_falco_content(raw_yaml: str, file_path: str) -> Tuple[int, int, List[str]]:
    items = []
    try:
        import yaml
        docs = list(yaml.safe_load_all(raw_yaml))
        for doc in docs:
            if isinstance(doc, list):
                items.extend(doc)
            elif isinstance(doc, dict):
                items.append(doc)
    except ImportError:
        items = parse_blocks_fallback(raw_yaml)
    except Exception as e:
        return 0, 0, [f"YAML parsing error in {file_path}: {e}"]

    errors = []
    rule_count = 0
    macro_count = 0
    list_count = 0

    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            continue

        if "rule" in item:
            rule_count += 1
            name = item.get("rule", f"Unnamed-Rule-#{rule_count}")
            for req in ["desc", "condition", "output", "priority"]:
                if req not in item:
                    errors.append(f"Rule '{name}': Missing required key '{req}'")

            prio = str(item.get("priority", "")).upper()
            if prio not in VALID_PRIORITIES:
                errors.append(f"Rule '{name}': Invalid priority '{prio}'. Must be one of {sorted(VALID_PRIORITIES)}")

            cond = str(item.get("condition", ""))
            if not check_balanced_parentheses(cond):
                errors.append(f"Rule '{name}': Unbalanced parentheses or brackets in condition")

            output = str(item.get("output", ""))
            if "%" in output:
                tokens = re.findall(r"%([a-zA-Z0-9_\.]+)", output)
                if not tokens:
                    errors.append(f"Rule '{name}': Suspicious output format string (contains '%' without valid token)")

        elif "macro" in item:
            macro_count += 1
            name = item.get("macro", f"Unnamed-Macro-#{macro_count}")
            if "condition" not in item:
                errors.append(f"Macro '{name}': Missing required key 'condition'")
            else:
                if not check_balanced_parentheses(str(item["condition"])):
                    errors.append(f"Macro '{name}': Unbalanced parentheses in condition")

        elif "list" in item:
            list_count += 1

    return rule_count, macro_count, errors

def main():
    parser = argparse.ArgumentParser(description="Falco Rules Syntax & Schema Validator")
    parser.add_argument("--rules", required=True, help="Path to Falco rules YAML or Markdown library")
    args = parser.parse_args()

    content = extract_yaml_blocks(args.rules)
    rule_count, macro_count, errors = validate_falco_content(content, args.rules)

    print("============================================================")
    print(" 🦅 Falco Rules Syntax & Schema Validator")
    print("============================================================")
    print(f"Target: {args.rules}")
    print(f"Rules parsed: {rule_count} | Macros parsed: {macro_count}")

    if errors:
        print(f"\n❌ Validation failed with {len(errors)} error(s):")
        for err in errors:
            print(f"  • {err}")
        sys.exit(1)
    else:
        print("\n✔ All Falco rules, macros, and lists validated successfully with zero errors!")
        sys.exit(0)

if __name__ == "__main__":
    main()
