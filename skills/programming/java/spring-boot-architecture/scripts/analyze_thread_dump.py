#!/usr/bin/env python3
"""
analyze_thread_dump.py - JVM Thread Dump Analyzer for Database Connection Pool Starvation

Scans a thread dump text file to detect thread pool deadlocks, blocked worker states,
and HikariCP / DB pool contention.
"""

import sys
import re
import argparse
from collections import Counter

THREAD_STATE_REGEX = re.compile(r'java\.lang\.Thread\.State:\s*([A-Z_]+)')

def analyze(filepath: str) -> int:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    states = THREAD_STATE_REGEX.findall(content)
    state_counts = Counter(states)

    hikari_blocked = len(re.findall(r'HikariPool.*getConnection', content))
    deadlocks = "Found one Java-level deadlock" in content

    print(f"Analyzing Thread Dump: {filepath}")
    print("=" * 60)
    print("Thread State Summary:")
    for state, count in state_counts.items():
        print(f"  {state:20}: {count}")

    print("-" * 60)
    if deadlocks:
        print("[CRITICAL] Java-level Deadlock detected in thread dump!")
    if hikari_blocked > 0:
        print(f"[ALERT] {hikari_blocked} thread(s) currently BLOCKED waiting for database connections.")
    else:
        print("[PASS] Zero threads blocked on HikariCP connection pool acquisition.")

    return 1 if (deadlocks or hikari_blocked > 5) else 0

def main():
    parser = argparse.ArgumentParser(description="Analyze a JVM thread dump.")
    parser.add_argument("dump_file", help="Path to thread dump txt file")
    args = parser.parse_args()

    sys.exit(analyze(args.dump_file))

if __name__ == "__main__":
    main()
