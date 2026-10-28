#!/usr/bin/env python3
"""
Falco Runtime Alert & Syscall Simulator.
Safely exercises system calls matching standard Falco detection rules
to verify that eBPF probes, user-space filters, and alerting pipelines are operating.

Usage:
    python3 simulate_falco_alerts.py --test-all
    python3 simulate_falco_alerts.py --test-shell
    python3 simulate_falco_alerts.py --dry-run
"""

import argparse
import json
import os
import socket
import subprocess
import sys
import tempfile
import time

def simulate_shell_spawn(dry_run: bool = False) -> dict:
    rule_name = "Terminal Shell Spawned in Container"
    cmd = ["/bin/sh", "-c", "echo 'Falco alert simulation: shell spawned'"]
    if dry_run:
        return {"rule": rule_name, "status": "DRY_RUN", "cmd": " ".join(cmd)}

    t0 = time.time()
    res = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "rule": rule_name,
        "status": "TRIGGERED",
        "syscall": "execve",
        "cmd": " ".join(cmd),
        "exit_code": res.returncode,
        "elapsed_ms": round((time.time() - t0) * 1000, 2)
    }

def simulate_sensitive_file_read(dry_run: bool = False) -> dict:
    rule_name = "Sensitive File Read Access"
    # Create safe mock file in temp directory
    with tempfile.NamedTemporaryFile(prefix="mock_shadow_", delete=False) as tf:
        mock_path = tf.name
        tf.write(b"root:!:19000:0:99999:7:::\n")

    if dry_run:
        os.remove(mock_path)
        return {"rule": rule_name, "status": "DRY_RUN", "file": mock_path}

    try:
        t0 = time.time()
        with open(mock_path, "r") as f:
            _ = f.read()
        return {
            "rule": rule_name,
            "status": "TRIGGERED",
            "syscall": "openat",
            "file": mock_path,
            "elapsed_ms": round((time.time() - t0) * 1000, 2)
        }
    finally:
        if os.path.exists(mock_path):
            os.remove(mock_path)

def simulate_loopback_connection(dry_run: bool = False) -> dict:
    rule_name = "Suspicious Outbound Network Connection"
    if dry_run:
        return {"rule": rule_name, "status": "DRY_RUN", "dest": "127.0.0.1:4444"}

    t0 = time.time()
    # Test connection to closed port on loopback (generates connect syscall)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    try:
        s.connect(("127.0.0.1", 4444))
    except Exception:
        pass
    finally:
        s.close()

    return {
        "rule": rule_name,
        "status": "TRIGGERED",
        "syscall": "connect",
        "dest": "127.0.0.1:4444",
        "elapsed_ms": round((time.time() - t0) * 1000, 2)
    }

def main():
    parser = argparse.ArgumentParser(description="Falco Runtime Alert & Syscall Simulator")
    parser.add_argument("--test-all", action="store_true", help="Execute all safe detection simulation tests")
    parser.add_argument("--test-shell", action="store_true", help="Simulate shell execution (execve)")
    parser.add_argument("--test-file", action="store_true", help="Simulate sensitive file open (openat)")
    parser.add_argument("--test-network", action="store_true", help="Simulate network socket connection (connect)")
    parser.add_argument("--dry-run", action="store_true", help="Print expected simulation actions without executing")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()

    # Default to test-all if no specific test specified
    if not (args.test_shell or args.test_file or args.test_network):
        args.test_all = True

    results = []

    if args.test_all or args.test_shell:
        results.append(simulate_shell_spawn(args.dry_run))

    if args.test_all or args.test_file:
        results.append(simulate_sensitive_file_read(args.dry_run))

    if args.test_all or args.test_network:
        results.append(simulate_loopback_connection(args.dry_run))

    if args.json:
        print(json.dumps({"simulations": results}, indent=2))
    else:
        print("============================================================")
        print(" 🦅 Falco Runtime Syscall Simulator")
        print("============================================================")
        print(f"Mode: {'DRY_RUN' if args.dry_run else 'ACTIVE_SIMULATION'}")
        print("------------------------------------------------------------")
        for r in results:
            status = r.get("status")
            rule = r.get("rule")
            syscall = r.get("syscall", "N/A")
            elapsed = r.get("elapsed_ms", 0.0)
            print(f"[{status}] Rule: '{rule}' | Syscall: {syscall} ({elapsed}ms)")
        print("============================================================")
        print("Simulation complete. Check Falco logs (`journalctl -u falco` or kubectl logs)")

if __name__ == "__main__":
    main()
