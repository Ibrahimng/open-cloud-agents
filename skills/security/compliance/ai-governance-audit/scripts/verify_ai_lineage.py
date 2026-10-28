#!/usr/bin/env python3
"""
Agent Skill Component: Security Compliance Commander (SCC)
Framework Mapping: ISO/IEC 42001:2023 Control B.9.2 & EU AI Act Art 15
Purpose: Validates data provenance, lineage declarations, and dataset integrity hashes.
"""

import argparse
import hashlib
import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple


def calculate_file_sha256(filepath: str) -> Optional[str]:
    """Generates SHA-256 checksum for dataset validation verification."""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except (FileNotFoundError, IsADirectoryError, PermissionError):
        return None


def audit_pipeline_lineage(manifest_path: str, strict: bool = False, json_output: bool = False) -> bool:
    """Inspects ML pipeline declarations for rigorous tracking metrics."""
    if not json_output:
        print(f"[*] Initializing Lineage & Data Provenance Audit on: {manifest_path}")

    if not os.path.exists(manifest_path):
        print(f"[-] Audit Target Failure: Manifest file {manifest_path} does not exist.", file=sys.stderr)
        sys.exit(1)

    with open(manifest_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print("[-] Audit Critical Failure: Manifest is not valid JSON.", file=sys.stderr)
            sys.exit(1)

    # Core ISO 42001 Evaluation Structural Checks
    findings: List[Dict[str, str]] = []
    compliance_status = "Compliant"

    # 1. Check for explicit data tracking fields (ISO 42001 B.9.2 / EU AI Act Art 10)
    if "dataset_provenance" not in data and "datasets" not in data:
        findings.append({
            "control": "ISO 42001 B.9.2 / EU AI Act",
            "status": "NON-COMPLIANT",
            "finding": "Missing top-level 'dataset_provenance' declarations metadata block."
        })
        compliance_status = "Non-Compliant"
    else:
        # Check single dataset_provenance block or multi-dataset list
        prov_blocks = []
        if "dataset_provenance" in data:
            prov_blocks.append(data.get("dataset_provenance", {}))
        if "datasets" in data and isinstance(data["datasets"], list):
            for ds in data["datasets"]:
                if isinstance(ds, dict) and ds not in prov_blocks:
                    prov_blocks.append(ds)

        for prov in prov_blocks:
            ds_name = prov.get("name", "unnamed-dataset")
            expected_hash = prov.get("expected_sha256") or prov.get("sha256") or prov.get("checksum")
            version = prov.get("version") or prov.get("tag") or prov.get("commit")
            uri = prov.get("uri") or prov.get("path") or ""

            # 2. Check for Hash Integrity Enforcement
            if not expected_hash:
                findings.append({
                    "control": "ISO 42001 B.9.2",
                    "status": "WARNING",
                    "finding": f"Dataset '{ds_name}' 'expected_sha256' hash omitted. Vulnerable to data poisoning drift."
                })
                if compliance_status != "Non-Compliant":
                    compliance_status = "Warning"
            else:
                findings.append({
                    "control": "ISO 42001 B.9.2",
                    "status": "PASS",
                    "finding": f"Dataset '{ds_name}' hash verification enforced (SHA-256: {expected_hash[:16]}...)."
                })

            # 3. Check for Versioning Control tracking
            if not version:
                findings.append({
                    "control": "ISO 42001 B.9.2",
                    "status": "WARNING",
                    "finding": f"Dataset '{ds_name}' has no static version identifier explicitly tied to training sources."
                })
                if compliance_status != "Non-Compliant":
                    compliance_status = "Warning"
            else:
                findings.append({
                    "control": "ISO 42001 B.9.2",
                    "status": "PASS",
                    "finding": f"Dataset '{ds_name}' lineage anchored to immutable version: '{version}'."
                })

            # 4. Artifact Hash Verification if local file target exists
            if uri and os.path.exists(uri) and os.path.isfile(uri):
                actual_hash = calculate_file_sha256(uri)
                if expected_hash and actual_hash:
                    if actual_hash.lower() == expected_hash.lower():
                        findings.append({
                            "control": "ISO 42001 B.9.2",
                            "status": "PASS",
                            "finding": f"Cryptographic integrity confirmed: local file '{uri}' matches declared SHA-256."
                        })
                    else:
                        findings.append({
                            "control": "ISO 42001 B.9.2",
                            "status": "NON-COMPLIANT",
                            "finding": f"Integrity Failure: local file '{uri}' SHA-256 mismatch ({actual_hash} != {expected_hash})."
                        })
                        compliance_status = "Non-Compliant"

    # 5. Check for Immutable Logging & Cyber Resilience (EU AI Act Art 12 & Art 15)
    logging_cfg = data.get("logging") or data.get("audit_logging") or {}
    if not logging_cfg:
        findings.append({
            "control": "EU AI Act Art. 12 / Art. 15",
            "status": "WARNING",
            "finding": "Model pipeline lacks automated inference and security event logging configuration."
        })
        if compliance_status != "Non-Compliant":
            compliance_status = "Warning"
    else:
        sink = logging_cfg.get("sink") or logging_cfg.get("destination", "configured")
        immutable = logging_cfg.get("immutable") or logging_cfg.get("write_once", False)
        if immutable:
            findings.append({
                "control": "EU AI Act Art. 15",
                "status": "PASS",
                "finding": f"Inference and anomalous input logging routed to write-once sink '{sink}'."
            })
        else:
            findings.append({
                "control": "EU AI Act Art. 15",
                "status": "WARNING",
                "finding": f"Logging sink '{sink}' does not enforce write-once immutability policies."
            })
            if compliance_status != "Non-Compliant":
                compliance_status = "Warning"

    # 6. Check for Human Oversight & Risk Tiering (EU AI Act Art. 14)
    risk_tier = str(data.get("risk_tier", "standard")).lower()
    human_oversight = data.get("human_oversight", False)
    if "high" in risk_tier:
        if human_oversight:
            findings.append({
                "control": "EU AI Act Art. 14",
                "status": "PASS",
                "finding": "High-Risk system enforces mandatory human-in-the-loop intervention stop-gate."
            })
        else:
            findings.append({
                "control": "EU AI Act Art. 14",
                "status": "NON-COMPLIANT",
                "finding": "High-Risk system lacks required Human-in-the-Loop (HITL) manual intervention gate."
            })
            compliance_status = "Non-Compliant"

    # Output Auditor Scorecard
    if json_output:
        result = {
            "manifest": manifest_path,
            "overall_status": compliance_status,
            "is_compliant": compliance_status == "Compliant",
            "findings": findings
        }
        print(json.dumps(result, indent=2))
    else:
        print("\n=== SCC AI LINEAGE AUDIT MATRIX ===")
        print(f"Overall Status: {compliance_status}")
        for item in findings:
            if item["status"] == "PASS":
                badge = "\033[92m[PASS]\033[0m"
            elif item["status"] == "WARNING":
                badge = "\033[93m[WARNING]\033[0m"
            else:
                badge = "\033[91m[NON-COMPLIANT]\033[0m"
            print(f"{badge} Control {item['control']}: {item['finding']}")

    if strict and compliance_status != "Compliant":
        return False
    return compliance_status != "Non-Compliant"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Verify AI pipeline manifests against ISO 42001 and EU AI Act requirements."
    )
    parser.add_argument("manifest_pos", nargs="?", default=None, help="Target manifest path")
    parser.add_argument("--manifest", "-m", help="Path to AI pipeline JSON manifest")
    parser.add_argument("--strict", action="store_true", help="Fail if any warnings are detected")
    parser.add_argument("--json", action="store_true", help="Output findings as JSON")
    parser.add_argument("--sample", action="store_true", help="Run against default sample manifest")

    args = parser.parse_args()

    # Determine target manifest path
    target = args.manifest or args.manifest_pos
    if not target:
        default_candidate = "pipelines/train_v2.json"
        if os.path.exists(default_candidate):
            target = default_candidate
        else:
            print(f"[*] No target specified and '{default_candidate}' not found. Please provide manifest path.", file=sys.stderr)
            parser.print_help()
            sys.exit(1)

    is_compliant = audit_pipeline_lineage(target, strict=args.strict, json_output=args.json)
    sys.exit(0 if is_compliant else 1)
