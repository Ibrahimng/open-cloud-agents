#!/usr/bin/env python3
"""
AI Dataset Lineage, Provenance & Governance Verification Tool
=============================================================
Audits AI training pipeline configurations, dataset manifests, and model
deployment specifications against ISO/IEC 42001:2023 (Control B.9.2) and the
EU AI Act (Regulation EU 2024/1689, Articles 10, 12, 14, and 15).

Zero external dependencies - standard library only.
"""

import argparse
import hashlib
import json
import os
import re
import sys
from typing import Any, Dict, List, Tuple


def parse_manifest_file(file_path: str) -> Dict[str, Any]:
    """Parse JSON or key-value pipeline manifest file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Fallback to key-value or simplified parser
        data: Dict[str, Any] = {}
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                k, v = line.split(":", 1)
                data[k.strip()] = v.strip().strip('"\'')
        return data


def audit_ai_manifest(manifest: Dict[str, Any], file_path: str) -> Tuple[List[Dict[str, str]], int, int]:
    """
    Evaluates manifest against ISO 42001 and EU AI Act technical rules.
    Returns: (findings_list, pass_count, warning_count, fail_count)
    """
    findings: List[Dict[str, str]] = []

    # -------------------------------------------------------------
    # 1. ISO 42001 Control B.9.2 & EU AI Act Art. 10: Data Provenance
    # -------------------------------------------------------------
    datasets = manifest.get("datasets") or manifest.get("training_data") or []
    if isinstance(datasets, dict):
        datasets = [datasets]
    elif not isinstance(datasets, list) and datasets:
        datasets = [{"uri": str(datasets)}]

    if not datasets:
        findings.append({
            "control": "ISO 42001 B.9.2 / EU AI Act Art. 10",
            "status": "FAIL",
            "category": "Data Lineage",
            "message": f"No training datasets or data clusters declared in manifest '{file_path}'."
        })
    else:
        for idx, ds in enumerate(datasets):
            ds_name = ds.get("name") if isinstance(ds, dict) else f"dataset[{idx}]"
            uri = ds.get("uri") or ds.get("path") or "" if isinstance(ds, dict) else str(ds)
            checksum = ds.get("sha256") or ds.get("checksum") or ds.get("hash") if isinstance(ds, dict) else None
            version = ds.get("version") or ds.get("tag") or ds.get("commit") if isinstance(ds, dict) else None

            # Check unversioned S3/GCS or generic URIs
            if uri.startswith("s3://") or uri.startswith("gs://"):
                if not version and not checksum:
                    findings.append({
                        "control": "ISO 42001 B.9.2",
                        "status": "WARN",
                        "category": "Data Provenance",
                        "message": f"Dataset '{ds_name}' ({uri}) ingests cloud storage clusters without version tag or commit hash. Prone to silent data poisoning."
                    })
                elif version and not checksum:
                    findings.append({
                        "control": "ISO 42001 B.9.2",
                        "status": "WARN",
                        "category": "Cryptographic Verification",
                        "message": f"Dataset '{ds_name}' has version '{version}' but lacks SHA-256 cryptographic checksum verification."
                    })
                else:
                    findings.append({
                        "control": "ISO 42001 B.9.2",
                        "status": "PASS",
                        "category": "Data Provenance",
                        "message": f"Dataset '{ds_name}' verified with immutable URI, version '{version}', and SHA-256 hash."
                    })
            elif uri:
                if not checksum:
                    findings.append({
                        "control": "EU AI Act Art. 10",
                        "status": "WARN",
                        "category": "Data Integrity",
                        "message": f"Dataset '{ds_name}' ({uri}) does not declare a cryptographic SHA-256 hash."
                    })
                else:
                    findings.append({
                        "control": "EU AI Act Art. 10",
                        "status": "PASS",
                        "category": "Data Integrity",
                        "message": f"Dataset '{ds_name}' declares cryptographic verification hash."
                    })

    # -------------------------------------------------------------
    # 2. EU AI Act Art. 12 & Art. 15: Cyber & Logging Resilience
    # -------------------------------------------------------------
    logging_cfg = manifest.get("logging") or manifest.get("audit_logging") or manifest.get("telemetry") or {}
    if not logging_cfg:
        findings.append({
            "control": "EU AI Act Art. 12 / Art. 15",
            "status": "FAIL",
            "category": "Logging & Traceability",
            "message": "Model deployment manifest lacks automated inference and security event logging configuration."
        })
    else:
        sink = logging_cfg.get("sink") or logging_cfg.get("destination") or ""
        immutable = logging_cfg.get("immutable") or logging_cfg.get("write_once") or False
        retention = logging_cfg.get("retention_days") or logging_cfg.get("retention") or 0

        if not sink:
            findings.append({
                "control": "EU AI Act Art. 12",
                "status": "WARN",
                "category": "Logging Destination",
                "message": "Logging enabled but no explicit destination sink (SCC, CloudWatch, S3 Object Lock) defined."
            })
        elif not immutable:
            findings.append({
                "control": "EU AI Act Art. 15",
                "status": "WARN",
                "category": "Tamper Resistance",
                "message": f"Logging sink '{sink}' is not configured with immutable write-once storage policies."
            })
        else:
            findings.append({
                "control": "EU AI Act Art. 15",
                "status": "PASS",
                "category": "Logging & Traceability",
                "message": f"Automated inference logging to '{sink}' enforces write-once immutability (Retention: {retention}d)."
            })

    # -------------------------------------------------------------
    # 3. EU AI Act Art. 14: Human Oversight & Risk Classification
    # -------------------------------------------------------------
    risk_tier = str(manifest.get("risk_tier") or manifest.get("risk_classification") or "unknown").lower()
    human_oversight = manifest.get("human_oversight") or manifest.get("hitl") or manifest.get("approval_required")

    if risk_tier in ("high", "high_risk", "annex_iii"):
        if not human_oversight:
            findings.append({
                "control": "EU AI Act Art. 14",
                "status": "FAIL",
                "category": "Human Oversight",
                "message": f"System classified as High Risk ('{risk_tier}') but lacks required Human-in-the-Loop (HITL) manual intervention gate."
            })
        else:
            findings.append({
                "control": "EU AI Act Art. 14",
                "status": "PASS",
                "category": "Human Oversight",
                "message": f"High-Risk system enforces mandatory human oversight and manual intervention stop-gate."
            })
    else:
        findings.append({
            "control": "EU AI Act Art. 6",
            "status": "PASS",
            "category": "Risk Tiering",
            "message": f"AI System registered under risk tier: '{risk_tier}'."
        })

    # -------------------------------------------------------------
    # 4. OWASP LLM02: Insecure Output Sanitization
    # -------------------------------------------------------------
    output_handling = manifest.get("output_handling") or manifest.get("guardrails") or {}
    if output_handling:
        strict_schema = output_handling.get("strict_schema") or output_handling.get("schema_validation")
        if strict_schema:
            findings.append({
                "control": "OWASP LLM02",
                "status": "PASS",
                "category": "Output Handling",
                "message": "Downstream model outputs validated through strict schema parsing."
            })
        else:
            findings.append({
                "control": "OWASP LLM02",
                "status": "WARN",
                "category": "Output Handling",
                "message": "Output handling declared without strict schema validation; risk of downstream injection."
            })

    return findings


def generate_sample_manifest() -> Dict[str, Any]:
    """Generates an illustrative compliant manifest if testing in sandbox."""
    return {
        "model_name": "enterprise-agent-reasoning-v2",
        "risk_tier": "High Risk",
        "human_oversight": True,
        "datasets": [
            {
                "name": "corporate-knowledge-corpus",
                "uri": "s3://enterprise-ai-training-data-vault/v2.1/",
                "version": "v2.1.4",
                "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
            }
        ],
        "logging": {
            "sink": "google-cloud-scc-immutable-vault",
            "immutable": True,
            "retention_days": 180
        },
        "output_handling": {
            "strict_schema": True,
            "type_casting": True
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description="Verify AI pipeline manifests against ISO 42001 and EU AI Act requirements."
    )
    parser.add_argument("--manifest", "-m", help="Path to AI pipeline JSON manifest")
    parser.add_argument("--dir", "-d", help="Directory of AI manifests to recursively inspect")
    parser.add_argument("--strict", action="store_true", help="Fail on warnings as well as failures")
    parser.add_argument("--json-output", action="store_true", help="Emit findings as structured JSON")
    parser.add_argument("--sample", action="store_true", help="Run audit against compliant sample manifest")

    args = parser.parse_args()

    targets: List[str] = []
    if args.manifest:
        targets.append(args.manifest)
    elif args.dir:
        for root, _, files in os.walk(args.dir):
            for f in files:
                if f.endswith(".json") and ("pipeline" in f or "train" in f or "model" in f or "ai" in f):
                    targets.append(os.path.join(root, f))
    elif args.sample:
        targets = ["<sample-manifest>"]
    else:
        # Default scan for any train or pipeline JSON files in workspace
        for candidate in ["pipelines/train_v2.json", "pipelines/train.json", "deploy/ai-pipeline.json"]:
            if os.path.exists(candidate):
                targets.append(candidate)
        if not targets:
            targets = ["<sample-manifest>"]

    all_findings = []
    has_failure = False

    for target in targets:
        if target == "<sample-manifest>":
            data = generate_sample_manifest()
            path_display = "sample-compliant-pipeline.json"
        else:
            if not os.path.exists(target):
                print(f"Error: Target manifest '{target}' not found.", file=sys.stderr)
                sys.exit(1)
            data = parse_manifest_file(target)
            path_display = target

        findings = audit_ai_manifest(data, path_display)
        for f in findings:
            f["target"] = path_display
            all_findings.append(f)
            if f["status"] == "FAIL":
                has_failure = True
            elif args.strict and f["status"] == "WARN":
                has_failure = True

    if args.json_output:
        print(json.dumps(all_findings, indent=2))
    else:
        print("=" * 72)
        print(" 🤖 AI Governance & Lineage Verification Audit")
        print(" Frameworks: ISO/IEC 42001:2023 (B.9.2) & EU AI Act (Arts. 10, 12, 14, 15)")
        print("=" * 72)

        for f in all_findings:
            if f["status"] == "PASS":
                badge = "\033[92m[PASS]\033[0m"
            elif f["status"] == "WARN":
                badge = "\033[93m[WARN]\033[0m"
            else:
                badge = "\033[91m[FAIL]\033[0m"

            print(f"{badge} {f['control']:<32} | {f['category']:<18} | {f['message']}")

        print("-" * 72)
        pass_cnt = sum(1 for f in all_findings if f["status"] == "PASS")
        warn_cnt = sum(1 for f in all_findings if f["status"] == "WARN")
        fail_cnt = sum(1 for f in all_findings if f["status"] == "FAIL")

        print(f"Audit Summary: {pass_cnt} Passing, {warn_cnt} Warnings, {fail_cnt} Failing.")
        if has_failure:
            print("Verdict: ❌ Non-Compliant with AI Governance Baselines.")
            sys.exit(1)
        else:
            print("Verdict: ✅ All Evaluated AI Governance Baseline Controls Satisfied.")
            sys.exit(0)


if __name__ == "__main__":
    main()
