#!/usr/bin/env python3
"""
benchmark_api.py - HTTP Latency & Health Check Benchmark for REST APIs

Measures response turnaround, connection establishment time, and HTTP status codes.
"""

import sys
import time
import argparse
import urllib.request

def ping_endpoint(url: str, count: int = 10) -> int:
    print(f"Pinging {url} ({count} requests)...")
    durations = []

    for i in range(count):
        t0 = time.time()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "OpenCloudAgents-Probe/1.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                _ = resp.read()
                elapsed_ms = (time.time() - t0) * 1000.0
                durations.append(elapsed_ms)
        except Exception as e:
            print(f"  Request {i+1}: FAILED ({e})")
            return 1

    avg_ms = sum(durations) / len(durations)
    print("=" * 50)
    print(f"Average Latency: {avg_ms:.2f} ms")
    print(f"Min Latency:     {min(durations):.2f} ms")
    print(f"Max Latency:     {max(durations):.2f} ms")
    print("=" * 50)
    return 0

def main():
    parser = argparse.ArgumentParser(description="Test API latency.")
    parser.add_argument("url", nargs="?", default="http://localhost:8000/healthz", help="Endpoint to test")
    parser.add_argument("--count", type=int, default=10, help="Number of requests")
    args = parser.parse_args()

    sys.exit(ping_endpoint(args.url, args.count))

if __name__ == "__main__":
    main()
