---
name: guardrail-regression-testing
metadata:
  category: Continual-Learning
  version: "1.0.0"
description: >-
  Automated testing suite and verification runbook for preventative guardrails, ensuring newly added policy-as-code rules, linter patterns, and DevSecOps checks reliably catch historical failure modes without generating false positives on compliant code.
---

# Guardrail Regression Testing & Quality Verification

## Purpose & Scope
Whenever an autonomous agent creates a new guardrail via [`incident-postmortem-to-guardrail`](../incident-postmortem-to-guardrail/SKILL.md) or records a learned rule in `AGENTS.md` via [`knowledge-enhancement-loop`](../knowledge-enhancement-loop/SKILL.md), this skill validates that the guardrail:
1. **Catches the Bug (Zero False Negatives):** Reliably flags and blocks synthetic code recreating the historical failure mode.
2. **Permits Compliant Code (Zero False Positives):** Does not flag documentation, comments, markdown checklists, or hardened code patterns.

---

## The Guardrail Verification Cycle

```text
[New Guardrail / Linter Proposed]
               │
               ▼
  1. Synthetic Vulnerability Test (Ensure detection triggers)
               │
               ▼
  2. Compliant Workload Test (Ensure zero false-positive flags)
               │
               ▼
  3. Edge-Case Boundary Test (Comments, docs, whitespace)
               │
               ▼
[Certified: Registered in DevSecOps Reviewer & CI]
```

---

## Operational Workflow

### Step 1: Formulate the Regression Test Pair
For every new rule, construct a paired test case:
- **Negative Test (Expected FAIL / FLAG):** Contains the exact dangerous HCL/script/manifest construct.
- **Positive Test (Expected PASS / CLEAN):** Contains the compliant, hardened equivalent or a commented reference.

### Step 2: Execute the Automated Test Runner
Run the regression verification script:
```bash
python3 skills/continual-learning/guardrail-regression-testing/scripts/verify_guardrail_regressions.py
```

### Step 3: Inspect Test Results
The suite executes test assertions against `scripts/ci/audit_pr_diff.py`:
- Checks for `force_destroy = true` detection
- Checks for `forces replacement` trap detection
- Checks for `0.0.0.0/0` ingress detection
- Checks for `chmod 777` detection
- Verifies markdown files and code comments are ignored

---

## References & Tools
- [regression-test-matrix.md](references/regression-test-matrix.md): Comprehensive inventory of active guardrail test cases and expected verdicts.
- `scripts/verify_guardrail_regressions.py`: Executable regression test runner.

