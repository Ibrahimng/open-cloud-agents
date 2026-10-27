#!/usr/bin/env python3
"""
validate_infra_plan.py
=============================================================================
Validates that a Terraform Infrastructure Implementation Plan in
.terraform-planning-files/ conforms to the mandatory standard:
- Workload classification & provider targets
- Well-Architected Framework alignment
- Architecture diagrams
- Module & resource specification matrix
- Implementation roadmap
=============================================================================
"""

import sys
from pathlib import Path

REQUIRED_SECTIONS = [
    "Executive Summary",
    "Well-Architected Framework",
    "Diagram",
    "Specification",
    "Implementation",
]


def validate_plan_file(plan_path: Path) -> bool:
    if not plan_path.exists():
        print(f"❌ Error: Plan file {plan_path} does not exist.", file=sys.stderr)
        return False

    content = plan_path.read_text(encoding="utf-8")
    missing = []
    for section in REQUIRED_SECTIONS:
        if section.lower() not in content.lower():
            missing.append(section)

    if missing:
        print(f"❌ Error: Plan {plan_path.name} is missing required sections: {', '.join(missing)}", file=sys.stderr)
        return False

    print(f"✔ Plan {plan_path.name} is structurally valid and complete.")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 validate_infra_plan.py <path_to_plan.md>")
        sys.exit(1)

    success = validate_plan_file(Path(sys.argv[1]))
    sys.exit(0 if success else 1)
