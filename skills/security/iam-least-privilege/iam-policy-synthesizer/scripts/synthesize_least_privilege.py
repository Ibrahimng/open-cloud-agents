#!/usr/bin/env python3
"""
synthesize_least_privilege.py - Synthesize Least-Privilege IAM Policies

Takes a raw list of observed CloudTrail API actions and target resource ARNs,
and generates a tightly-scoped, production-ready IAM policy with HTTPS condition keys.
"""

import sys
import json
import argparse

def generate_policy(actions: list, resource_arns: list, enforce_tls: bool = True) -> dict:
    statement = {
        "Sid": "ScopedLeastPrivilegeAccess",
        "Effect": "Allow",
        "Action": sorted(list(set(actions))),
        "Resource": sorted(list(set(resource_arns))) if resource_arns else ["*"]
    }

    if enforce_tls:
        statement["Condition"] = {
            "Bool": {
                "aws:SecureTransport": "true"
            }
        }

    return {
        "Version": "2012-10-17",
        "Statement": [statement]
    }

def main():
    parser = argparse.ArgumentParser(description="Generate least-privilege IAM policy.")
    parser.add_argument("--actions", required=True, help="Comma-separated API actions (e.g. s3:GetObject,s3:ListBucket)")
    parser.add_argument("--resources", required=False, default="*", help="Comma-separated resource ARNs (e.g. arn:aws:s3:::my-bucket/*)")
    args = parser.parse_args()

    action_list = [a.strip() for a in args.actions.split(",") if a.strip()]
    resource_list = [r.strip() for r in args.resources.split(",") if r.strip()]

    policy = generate_policy(action_list, resource_list)
    print(json.dumps(policy, indent=2))

if __name__ == "__main__":
    main()
