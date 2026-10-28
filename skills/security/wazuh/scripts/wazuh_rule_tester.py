#!/usr/bin/env python3
"""
Wazuh Log & Rule Evaluation Tester.
Simulates wazuh-logtest locally using standard Python libraries,
evaluating log strings against decoders, rule matching logic, and active response thresholds.

Usage:
    python3 wazuh_rule_tester.py --log "Failed password for invalid user admin from 198.51.100.42 port 54321 ssh2"
    python3 wazuh_rule_tester.py --sample-demo
"""

import argparse
import json
import re
import sys
from typing import Dict, Any, Optional

BUILTIN_RULES = [
    {
        "id": "5710",
        "level": 5,
        "decoder": "sshd",
        "regex": r"Failed password for (\S+) from (\d+\.\d+\.\d+\.\d+)",
        "fields": ["user", "srcip"],
        "description": "sshd: Attempt to login using non-existent or invalid user",
        "mitre": ["T1110"]
    },
    {
        "id": "5712",
        "level": 10,
        "decoder": "sshd",
        "regex": r"Failed password for .* from (\d+\.\d+\.\d+\.\d+)",
        "fields": ["srcip"],
        "description": "sshd: Brute force attack detected (multiple authentication failures)",
        "mitre": ["T1110", "T1110.001"]
    },
    {
        "id": "5402",
        "level": 3,
        "decoder": "sudo",
        "regex": r"sudo:\s+(\S+) : TTY=\S+ ; PWD=\S+ ; USER=(\S+) ; COMMAND=(.*)",
        "fields": ["user", "target_user", "command"],
        "description": "Successful sudo command execution",
        "mitre": ["T1078"]
    },
    {
        "id": "100101",
        "level": 11,
        "decoder": "custom-app",
        "regex": r"user:\s*(\S+)\s+src_ip:\s*(\d+\.\d+\.\d+\.\d+)\s+action:\s*token_generate_unauthorized",
        "fields": ["user", "srcip"],
        "description": "Unauthorized API token minted for user",
        "mitre": ["T1078", "T1098"]
    },
    {
        "id": "550",
        "level": 12,
        "decoder": "syscheck",
        "regex": r"Integrity checksum changed for:\s*'([^']+)'",
        "fields": ["file"],
        "description": "Integrity checksum altered on critical system file",
        "mitre": ["T1565", "T1070"]
    }
]

def decode_and_evaluate(log_line: str) -> Dict[str, Any]:
    matched_rule = None
    extracted_fields = {}
    matched_decoder = "generic"

    for r in BUILTIN_RULES:
        m = re.search(r["regex"], log_line)
        if m:
            matched_rule = r
            matched_decoder = r["decoder"]
            for idx, field_name in enumerate(r["fields"]):
                if idx < len(m.groups()):
                    extracted_fields[field_name] = m.group(idx + 1)
            break

    if not matched_rule:
        return {
            "status": "UNMATCHED",
            "log": log_line,
            "decoder": "unknown",
            "fields": {},
            "rule": None
        }

    active_response = matched_rule["level"] >= 10
    return {
        "status": "MATCHED",
        "log": log_line,
        "decoder": matched_decoder,
        "fields": extracted_fields,
        "rule": {
            "id": matched_rule["id"],
            "level": matched_rule["level"],
            "description": matched_rule["description"],
            "mitre": matched_rule["mitre"]
        },
        "active_response_triggered": active_response,
        "recommended_action": "firewall-drop" if active_response and "srcip" in extracted_fields else ("host-deny" if active_response else "none")
    }

def main():
    parser = argparse.ArgumentParser(description="Wazuh Log & Rule Evaluation Tester")
    parser.add_argument("--log", help="Raw log string to evaluate")
    parser.add_argument("--sample-demo", action="store_true", help="Run demonstration logs across SSH, Sudo, and FIM")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")

    args = parser.parse_args()

    logs_to_test = []
    if args.sample_demo:
        logs_to_test = [
            "Oct 28 10:14:22 host sshd[1234]: Failed password for invalid user admin from 198.51.100.42 port 54321 ssh2",
            "Oct 28 10:15:00 host sudo:   developer : TTY=pts/1 ; PWD=/home/developer ; USER=root ; COMMAND=/bin/cat /etc/shadow",
            "Integrity checksum changed for: '/etc/shadow'",
            "[AppSecurityEvent] user: bob src_ip: 203.0.113.88 action: token_generate_unauthorized"
        ]
    elif args.log:
        logs_to_test = [args.log]
    else:
        print("Please specify --log '<string>' or --sample-demo")
        sys.exit(1)

    print("============================================================")
    print(" 🐺 Wazuh Log & Rule Evaluation Test Harness")
    print("============================================================")

    for idx, l in enumerate(logs_to_test, 1):
        res = decode_and_evaluate(l)
        print(f"\n[Test #{idx}] Evaluating Log:")
        print(f"  Raw: {res['log']}")
        print(f"  **Phase 1: Completed decoding.")
        print(f"       decoder: '{res['decoder']}'")
        for k, v in res["fields"].items():
            print(f"       {k}: '{v}'")

        print(f"  **Phase 2: Completed rule inspection.")
        if res["rule"]:
            r = res["rule"]
            print(f"       Rule id: '{r['id']}'")
            print(f"       Level:   '{r['level']}'")
            print(f"       Desc:    '{r['description']}'")
            print(f"       MITRE:   {r['mitre']}")
            print(f"  **Phase 3: Active Response.")
            print(f"       Triggered: {'🚨 YES' if res['active_response_triggered'] else '⚪ NO'}")
            if res['active_response_triggered']:
                print(f"       Action:    '{res['recommended_action']}'")
        else:
            print("       No specific rule matched (Level 0 / Ignored).")

    print("\n============================================================")
    print("Evaluation complete.")

if __name__ == "__main__":
    main()
