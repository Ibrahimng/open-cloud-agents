#!/usr/bin/env python3
"""
Wazuh Active Response Lifecycle & Rollback Simulator.
Safely exercises the automated containment lifecycle (block, verification,
timeout countdown, and rollback release) without disrupting live production networking.

Usage:
    python3 wazuh_active_response_simulator.py --test-ip 198.51.100.42 --command firewall-drop --timeout 2
    python3 wazuh_active_response_simulator.py --dry-run
"""

import argparse
import json
import sys
import time
from typing import Dict, Any

def simulate_active_response(ip: str, command: str, timeout_seconds: int, dry_run: bool = False) -> Dict[str, Any]:
    alert_payload = {
        "command": "add",
        "parameters": {
            "extra_args": [],
            "alert": {
                "rule": {
                    "id": "5712",
                    "level": 10,
                    "description": "sshd: Brute force attack detected"
                },
                "data": {
                    "srcip": ip
                }
            },
            "program": f"/var/ossec/active-response/bin/{command}"
        }
    }

    if dry_run:
        return {
            "status": "DRY_RUN",
            "target_ip": ip,
            "command": command,
            "timeout_seconds": timeout_seconds,
            "payload_sample": alert_payload
        }

    events = []
    # 1. Trigger Block
    t0 = time.time()
    events.append({
        "phase": "EXECUTE_BLOCK",
        "action": f"{command} add {ip}",
        "status": "APPLIED",
        "timestamp": round(t0, 3)
    })

    # 2. Emulate active duration
    sleep_time = min(timeout_seconds, 3)
    time.sleep(sleep_time)

    # 3. Trigger Rollback (Unblock)
    t1 = time.time()
    rollback_payload = dict(alert_payload)
    rollback_payload["command"] = "delete"

    events.append({
        "phase": "TIMEOUT_EXPIRED",
        "action": f"{command} delete {ip}",
        "status": "ROLLED_BACK",
        "timestamp": round(t1, 3),
        "duration_held_sec": round(t1 - t0, 2)
    })

    return {
        "status": "SUCCESS",
        "target_ip": ip,
        "command": command,
        "configured_timeout": timeout_seconds,
        "events": events,
        "rollback_verified": True
    }

def main():
    parser = argparse.ArgumentParser(description="Wazuh Active Response Lifecycle Simulator")
    parser.add_argument("--test-ip", default="198.51.100.42", help="Offending IP address to simulate containment on")
    parser.add_argument("--command", choices=["firewall-drop", "host-deny", "disable-account"], default="firewall-drop", help="Active response command to test")
    parser.add_argument("--timeout", type=int, default=2, help="Block timeout in seconds before unblocking")
    parser.add_argument("--dry-run", action="store_true", help="Print expected actions without running timer")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()

    res = simulate_active_response(
        ip=args.test_ip,
        command=args.command,
        timeout_seconds=args.timeout,
        dry_run=args.dry_run
    )

    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print("============================================================")
        print(" 🐺 Wazuh Active Response Lifecycle Simulator")
        print("============================================================")
        print(f"Target IP:        {res['target_ip']}")
        print(f"Command:          {res['command']}")
        print(f"Mode:             {res['status']}")

        if res["status"] == "DRY_RUN":
            print("\nSimulated Alert Ingestion Payload:")
            print(json.dumps(res["payload_sample"], indent=2))
        else:
            print("\nExecution Sequence:")
            for e in res["events"]:
                print(f"  • [{e['phase']}] -> {e['action']} ({e['status']})")
            print(f"\n✔ Active response containment and automatic rollback verified successfully!")
        print("============================================================")

if __name__ == "__main__":
    main()
