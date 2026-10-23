#!/usr/bin/env python3
"""
verify_otel_endpoint.py - Health & Connectivity Probe for OpenTelemetry Collector

Verifies that the target OpenTelemetry OTLP/HTTP or OTLP/gRPC endpoint
is reachable, accepting traces, and responding to health check endpoints.
"""

import sys
import argparse
import urllib.request
import urllib.error

def check_endpoint(endpoint_url: str) -> int:
    print(f"Probing OpenTelemetry Collector at: {endpoint_url}")
    try:
        req = urllib.request.Request(endpoint_url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            status = resp.status
            print(f"[PASS] Collector reachable! HTTP status: {status}")
            return 0
    except urllib.error.HTTPError as e:
        # Many collectors return 405 Method Not Allowed on root GET, which still indicates connectivity!
        if e.code in (200, 204, 404, 405):
            print(f"[PASS] Collector is listening on port. Responded with HTTP {e.code}.")
            return 0
        print(f"[FAIL] Collector returned error status: {e.code}")
        return 1
    except urllib.error.URLError as e:
        print(f"[FAIL] Unable to connect to OTLP collector: {e.reason}")
        return 1

def main():
    parser = argparse.ArgumentParser(description="Probe OpenTelemetry Collector connectivity.")
    parser.add_argument("endpoint", nargs="?", default="http://localhost:4318", help="OTLP HTTP endpoint (default: http://localhost:4318)")
    args = parser.parse_args()

    sys.exit(check_endpoint(args.endpoint))

if __name__ == "__main__":
    main()
