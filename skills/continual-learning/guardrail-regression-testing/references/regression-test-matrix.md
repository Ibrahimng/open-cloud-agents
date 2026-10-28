# Guardrail Regression Test Matrix

Authoritative regression inventory testing pre-merge audit guardrails in `scripts/ci/audit_pr_diff.py` and `AGENTS.md`.

---

## 1. Active Guardrail Test Cases

| Test Case ID | Target Guardrail | Synthetic Input Construct | Expected Result | Target File Scope |
|:---|:---|:---|:---:|:---|
| **TC-GUARD-01** | IaC Force Replacement | `+ lifecycle { forces replacement = true }` | 🚨 **FLAGGED** | `*.tf`, `*.hcl` |
| **TC-GUARD-02** | Bucket Force Destroy | `+ force_destroy = true` | 🚨 **FLAGGED** | `*.tf`, `*.hcl` |
| **TC-GUARD-03** | Open Ingress Rule | `+ cidr_blocks = ["0.0.0.0/0"]` | 🚨 **FLAGGED** | `*.tf`, `*.hcl` |
| **TC-GUARD-04** | Overly Permissive Chmod | `+ chmod 777 /tmp/script.sh` | 🚨 **FLAGGED** | `*.sh` |
| **TC-GUARD-05** | Markdown Checklist Exemption | `+ - [ ] Avoid 0.0.0.0/0 ingress` | ✅ **CLEAN** | `*.md` |
| **TC-GUARD-06** | Commented Pattern Exemption | `+ # Note: Avoid force_destroy = true` | ✅ **CLEAN** | `*.tf`, `*.py`, `*.sh` |
| **TC-GUARD-07** | Hardened Ingress Rule | `+ cidr_blocks = ["10.0.0.0/16"]` | ✅ **CLEAN** | `*.tf`, `*.hcl` |

---

## 2. Maintenance Protocol
When adding a new check to `scripts/ci/audit_pr_diff.py`:
1. Register both the negative and positive test assertions in `verify_guardrail_regressions.py`.
2. Add the test row to this matrix.
3. Ensure the test suite passes before committing changes.

