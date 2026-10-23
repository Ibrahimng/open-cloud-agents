#!/usr/bin/env python3
"""
evaluate_slo_burn.py - Multi-Window Multi-Burn-Rate SLO Alert Calculator

Calculates consumption of a 30-day error budget based on Google SRE Workbook standards:
- 1-hour window with 14.4x burn rate = 2% of budget consumed in 1 hour (Critical alert / Page)
- 6-hour window with 6.0x burn rate = 5% of budget consumed in 6 hours (Ticket / Warning)
"""

import sys
import argparse

def calculate_burn_rate(target_slo: float, error_rate: float) -> dict:
    # Error budget allowed = 1.0 - target_slo
    # E.g. for 99.9% SLO, allowed error fraction = 0.001
    allowed_error_fraction = (100.0 - target_slo) / 100.0
    actual_error_fraction = error_rate / 100.0

    burn_rate = actual_error_fraction / allowed_error_fraction

    # Time to complete 100% budget exhaustion at current rate
    # 30 days = 720 hours
    hours_to_exhaustion = 720.0 / burn_rate if burn_rate > 0 else float("inf")

    severity = "HEALTHY"
    if burn_rate >= 14.4:
        severity = "P1_PAGE (14.4x burn - 2% budget consumed per hour)"
    elif burn_rate >= 6.0:
        severity = "P2_WARNING (6.0x burn - 5% budget consumed in 6 hours)"
    elif burn_rate >= 1.0:
        severity = "BUDGET_DEPLETION_NOTICE (>1.0x burn)"

    return {
        "target_slo": f"{target_slo}%",
        "error_rate": f"{error_rate}%",
        "burn_rate": f"{burn_rate:.2f}x",
        "hours_to_total_exhaustion": f"{hours_to_exhaustion:.1f} hours" if hours_to_exhaustion != float("inf") else "Infinite",
        "severity": severity
    }

def main():
    parser = argparse.ArgumentParser(description="Calculate multi-window SLO burn rate.")
    parser.add_argument("--slo", type=float, default=99.9, help="Target availability SLO percentage (e.g. 99.9)")
    parser.add_argument("--error-rate", type=float, required=True, help="Observed 5xx error rate percentage (e.g. 1.5)")
    args = parser.parse_args()

    result = calculate_burn_rate(args.slo, args.error_rate)
    print("SLO Burn Rate Evaluation Results:")
    print("=" * 60)
    for k, v in result.items():
        print(f"  {k:28}: {v}")
    print("=" * 60)

    if "P1" in result["severity"]:
        sys.exit(2)
    elif "P2" in result["severity"]:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()

