#!/usr/bin/env python3
"""
harvest_incident_facts.py
=============================================================================
Continual Learning: Knowledge Base Harvester & Validator
Open Cloud Agents - Master Suite

Validates, extracts, and manages runtime knowledge entries under the
"Continual Learning Memory & Dynamic Knowledge Base" section in AGENTS.md.
Ensures zero duplicate facts, consistent schema formatting, and supports
JSON exports for downstream agent retrieval and RAG indexing.
=============================================================================
"""

import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_AGENTS_MD = Path("AGENTS.md")
FACT_REGEX = re.compile(r"^\s*-\s+\*\*([^*]+)\:\*\*\s+(.+)$")
HEADER_REGEX = re.compile(r"^###\s+Learned\s+(.+)\s+Facts$")


def parse_knowledge_base(agents_md_path: Path) -> tuple[dict[str, list[tuple[str, str]]], list[str]]:
    """
    Parses the Continual Learning section of AGENTS.md into categories and facts.
    Returns (categories_dict, validation_errors).
    """
    if not agents_md_path.exists():
        return {}, [f"Target file not found: {agents_md_path}"]

    with open(agents_md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    categories: dict[str, list[tuple[str, str]]] = {}
    current_category: str | None = None
    in_section = False
    errors: list[str] = []
    seen_titles: set[str] = set()

    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()

        # Section delimiter
        if "Continual Learning Memory & Dynamic Knowledge Base" in stripped:
            in_section = True
            continue

        if not in_section:
            continue

        # Exit on next major H2 section
        if stripped.startswith("## ") and in_section and not "Continual Learning" in stripped:
            break

        # Check Category H3 Headers
        header_match = HEADER_REGEX.match(stripped)
        if header_match:
            current_category = header_match.group(1).strip()
            if current_category not in categories:
                categories[current_category] = []
            continue

        # Check Fact Bullets
        if stripped.startswith("- "):
            fact_match = FACT_REGEX.match(stripped)
            if not fact_match:
                errors.append(f"Line {line_num}: Bullet does not conform to '- **<Topic>:** <Description>' schema: {stripped[:60]}")
                continue

            if current_category is None:
                errors.append(f"Line {line_num}: Fact bullet found before any Category H3 header: {stripped[:60]}")
                continue

            title = fact_match.group(1).strip()
            content = fact_match.group(2).strip()

            if title.lower() in seen_titles:
                errors.append(f"Line {line_num}: Duplicate topic title detected across knowledge base: '{title}'")
            seen_titles.add(title.lower())

            if len(content) < 20:
                errors.append(f"Line {line_num}: Insufficient description for topic '{title}' ({len(content)} chars). Must be actionable.")

            categories[current_category].append((title, content))

    return categories, errors


def add_fact(
    agents_md_path: Path,
    category: str,
    title: str,
    content: str,
    dry_run: bool = False
) -> bool:
    """
    Appends a validated fact to AGENTS.md under the specified category.
    """
    categories, errors = parse_knowledge_base(agents_md_path)
    if errors:
        print("❌ Cannot append to knowledge base: existing validation errors found:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return False

    # Check for duplicate
    all_titles = {t.lower() for facts in categories.values() for t, _ in facts}
    if title.lower() in all_titles:
        print(f"⚠️ Topic '{title}' is already recorded in the knowledge base. Skipping duplicate.", file=sys.stderr)
        return False

    with open(agents_md_path, "r", encoding="utf-8") as f:
        text = f.read()

    new_bullet = f"- **{title}:** {content}\n"
    category_header = f"### Learned {category} Facts"

    if category_header in text:
        # Append under existing category
        idx = text.find(category_header)
        next_h3 = text.find("\n### ", idx + len(category_header))
        next_h2 = text.find("\n## ", idx + len(category_header))

        insert_pos = -1
        if next_h3 != -1 and next_h2 != -1:
            insert_pos = min(next_h3, next_h2)
        elif next_h3 != -1:
            insert_pos = next_h3
        elif next_h2 != -1:
            insert_pos = next_h2
        else:
            insert_pos = len(text)

        updated_text = text[:insert_pos].rstrip() + "\n" + new_bullet + "\n" + text[insert_pos:].lstrip()
    else:
        # Append new category before end of section or at end of file
        end_marker = "## Continual Learning Memory & Dynamic Knowledge Base"
        sec_idx = text.find(end_marker)
        if sec_idx == -1:
            print("❌ Continual Learning section header not found in target file.", file=sys.stderr)
            return False

        next_h2 = text.find("\n## ", sec_idx + len(end_marker))
        new_category_block = f"\n{category_header}\n{new_bullet}\n"

        if next_h2 != -1:
            updated_text = text[:next_h2].rstrip() + "\n" + new_category_block + text[next_h2:]
        else:
            updated_text = text.rstrip() + "\n" + new_category_block

    if dry_run:
        print(f"[DRY-RUN] Would append to {category_header}:\n{new_bullet}")
        return True

    with open(agents_md_path, "w", encoding="utf-8") as f:
        f.write(updated_text)

    print(f"✔ Successfully appended '{title}' to '{category_header}'.")
    return True


def main():
    parser = argparse.ArgumentParser(description="Continual Learning: Knowledge Base Harvester & Validator")
    parser.add_argument("--file", type=Path, default=DEFAULT_AGENTS_MD, help="Path to AGENTS.md")
    parser.add_argument("--validate", action="store_true", help="Validate formatting of all knowledge base entries")
    parser.add_argument("--export-json", type=Path, help="Export parsed knowledge base to a JSON file")
    parser.add_argument("--add", action="store_true", help="Add a new fact to the knowledge base")
    parser.add_argument("--category", type=str, help="Category name (e.g. 'Kubernetes Networking', 'CI/CD & Autonomous Agent Governance')")
    parser.add_argument("--title", type=str, help="Topic title (e.g. 'GitHub Actions Script Injection Defense')")
    parser.add_argument("--fact", type=str, help="Actionable fact description with root-cause and remediation")
    parser.add_argument("--dry-run", action="store_true", help="Simulate addition without writing to disk")

    args = parser.parse_args()

    if args.add:
        if not (args.category and args.title and args.fact):
            print("❌ Adding a fact requires --category, --title, and --fact.", file=sys.stderr)
            sys.exit(1)
        success = add_fact(args.file, args.category, args.title, args.fact, args.dry_run)
        sys.exit(0 if success else 1)

    categories, errors = parse_knowledge_base(args.file)

    if args.export_json:
        out_data = {
            "metadata": {
                "source": str(args.file),
                "total_categories": len(categories),
                "total_facts": sum(len(facts) for facts in categories.values())
            },
            "categories": {
                cat: [{"title": t, "content": c} for t, c in facts]
                for cat, facts in categories.items()
            }
        }
        with open(args.export_json, "w", encoding="utf-8") as f:
            json.dump(out_data, f, indent=2)
        print(f"✔ Exported {out_data['metadata']['total_facts']} facts across {len(categories)} categories to {args.export_json}.")

    if args.validate or not (args.add or args.export_json):
        print("============================================================")
        print(" 🧠 Continual Learning Knowledge Base Audit")
        print("============================================================")
        total_facts = sum(len(facts) for facts in categories.values())
        print(f"ℹ Ingested {total_facts} learned facts across {len(categories)} categories in {args.file}:")
        for cat, facts in categories.items():
            print(f"  • {cat}: {len(facts)} fact(s)")

        if errors:
            print("\n❌ Validation Failures:")
            for err in errors:
                print(f"  ✖ {err}")
            print("============================================================")
            sys.exit(1)
        else:
            print("\n✔ All learned facts strictly adhere to canonical schema!")
            print("============================================================")
            sys.exit(0)


if __name__ == "__main__":
    main()
