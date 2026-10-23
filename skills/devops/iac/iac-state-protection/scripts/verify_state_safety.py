#!/usr/bin/env python3
"""
verify_state_safety.py - Automated IaC Plan State Destruction Guardrail

Parses a Terraform / OpenTofu JSON execution plan and blocks CI/CD pipelines
if stateful or critical cloud resources are scheduled for deletion or recreation
('forces replacement').

Usage:
  tofu plan -out=tfplan.binary
  tofu show -json tfplan.binary | python3 verify_state_safety.py [--allow-destruction]
"""

import sys
import json
import argparse

STATEFUL_RESOURCE_TYPES = {
    # AWS
    "aws_db_instance",
    "aws_rds_cluster",
    "aws_s3_bucket",
    "aws_dynamodb_table",
    "aws_kms_key",
    "aws_efs_file_system",
    "aws_elasticache_cluster",
    "aws_elasticache_replication_group",
    # Azure
    "azurerm_cosmosdb_account",
    "azurerm_storage_account",
    "azurerm_mssql_database",
    "azurerm_postgresql_flexible_server",
    "azurerm_key_vault",
    # GCP
    "google_sql_database_instance",
    "google_storage_bucket",
    "google_spanner_instance",
    "google_bigtable_instance",
    "google_kms_crypto_key",
}

def analyze_plan(plan_data: dict, allow_destruction: bool) -> int:
    resource_changes = plan_data.get("resource_changes", [])
    violations = []

    for rc in resource_changes:
        address = rc.get("address", "unknown")
        rtype = rc.get("type", "")
        change = rc.get("change", {})
        actions = change.get("actions", [])

        # Check for destruction actions: 'delete', or replacement: ['delete', 'create'] or ['create', 'delete']
        is_delete = "delete" in actions
        is_replacement = is_delete and "create" in actions

        if is_delete and rtype in STATEFUL_RESOURCE_TYPES:
            action_desc = "FORCED REPLACEMENT (Recreate)" if is_replacement else "DELETION"
            violations.append({
                "address": address,
                "type": rtype,
                "action": action_desc,
                "before": change.get("before", {}),
                "after": change.get("after", {}),
            })

    if not violations:
        print("[PASS] IaC State Safety Check: Zero unauthorized stateful deletions detected.")
        return 0

    print("=" * 80)
    print("CRITICAL DEFECT: UNAUTHORIZED STATE DESTRUCTION DETECTED IN PLAN")
    print("=" * 80)
    for v in violations:
        print(f"• Resource: {v['address']} ({v['type']})")
        print(f"  Action:   {v['action']}")
    print("-" * 80)

    if allow_destruction:
        print("[WARNING] Destruction explicitly permitted via --allow-destruction flag. Proceeding.")
        return 0

    print("[BLOCKED] Pipeline aborted. To prevent data loss, stateful resource destruction is forbidden.")
    print("Refer to references/dangerous-attributes-matrix.md for safe migration patterns.")
    return 1

def main():
    parser = argparse.ArgumentParser(description="Audit Terraform/OpenTofu plan for state destruction.")
    parser.add_argument("--allow-destruction", action="store_true", help="Bypass block if destruction is intentional and authorized.")
    args = parser.parse_args()

    if sys.stdin.isatty():
        print("Error: Expecting JSON plan from stdin. Example: tofu show -json plan.binary | python3 verify_state_safety.py")
        sys.exit(2)

    try:
        plan_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON plan: {e}")
        sys.exit(2)

    sys.exit(analyze_plan(plan_data, args.allow_destruction))

if __name__ == "__main__":
    main()
