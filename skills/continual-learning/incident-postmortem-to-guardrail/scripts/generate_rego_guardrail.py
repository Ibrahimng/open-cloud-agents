#!/usr/bin/env python3
"""
generate_rego_guardrail.py - Scaffolds an OPA Rego Guardrail from an Incident Brief

Takes an incident ID and violation description, and outputs a valid Open Policy Agent (OPA)
Kubernetes admission or Terraform static policy.
"""

import sys
import argparse

REGO_TEMPLATE = """package postmortem.guardrails

# Guardrail generated from Incident: {incident_id}
# Rationale: {rationale}

default allow = false

deny[msg] {{
    # Target resource condition
    input.kind == "{resource_kind}"
    {condition_check}
    msg := sprintf("[BLOCK] Incident {incident_id} recurrence: %v", ["{rationale}"])
}}
"""

def main():
    parser = argparse.ArgumentParser(description="Generate OPA Rego guardrail from incident.")
    parser.add_argument("--incident-id", required=True, help="Incident tracking ID (e.g. INC-4091)")
    parser.add_argument("--kind", default="Deployment", help="Resource kind (e.g. Deployment, aws_s3_bucket)")
    parser.add_argument("--rationale", required=True, help="Failure mechanism and why it must be blocked")
    args = parser.parse_args()

    rego = REGO_TEMPLATE.format(
        incident_id=args.incident_id,
        resource_kind=args.kind,
        rationale=args.rationale,
        condition_check="not input.spec.template.spec.securityContext.runAsNonRoot"
    )
    print(rego)

if __name__ == "__main__":
    main()
