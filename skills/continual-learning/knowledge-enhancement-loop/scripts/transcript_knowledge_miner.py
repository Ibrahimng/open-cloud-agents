#!/usr/bin/env python3
"""
transcript_knowledge_miner.py - Transcript Log Learning Miner

Scans session transcript JSONL files or execution logs to isolate:
- Recovered tool failures (non-zero exits followed by successful alternative)
- Deprecation warnings from cloud CLI tools
- Outputs candidate knowledge patch entries formatted according to knowledge-patch-schema.md
"""

import sys
import json
import re

ERROR_KEYWORDS = ["error", "fatal", "denied", "deprecated", "unsupported", "forces replacement"]

def mine_text(text: str) -> list:
    candidates = []
    lines = text.splitlines()
    for line in lines:
        lower = line.lower()
        if any(kw in lower for kw in ERROR_KEYWORDS) and len(line.strip()) > 20:
            candidates.append(line.strip())
    return candidates

def main():
    if sys.stdin.isatty():
        print("Usage: cat session.log | python3 transcript_knowledge_miner.py")
        sys.exit(0)

    raw_input = sys.stdin.read()
    candidates = mine_text(raw_input)

    print(f"Transcript Mining Complete: {len(candidates)} candidate signal(s) isolated.")
    print("=" * 70)
    for idx, c in enumerate(candidates[:10], start=1):
        print(f"{idx}. {c}")
    print("=" * 70)
    print("Select verified entries and append to AGENTS.md or target SKILL.md.")

if __name__ == "__main__":
    main()

