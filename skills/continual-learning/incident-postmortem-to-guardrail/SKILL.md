---
name: incident-postmortem-to-guardrail
description: Translates runtime incident postmortems (PIRs) and SRE root cause findings into automated, pre-merge DevSecOps linting rules and IaC policy-as-code guardrails.
---

# Incident Postmortem to Preventative Guardrail Pipeline

## Purpose & Scope
This skill closes the feedback loop between production incidents and code reviews. Whenever an outage or degradation is triaged, this protocol automatically generates a preventative guardrail to block identical failure modes before code merges.

---

## The Translation Pipeline

```text
SRE Postmortem (PIR)
  └── Root Cause: "Service crashed because Kubernetes liveness probe timeout (1s) was shorter than downstream database timeout (5s)."
        │
        ▼ (Translation Skill)
Policy-as-Code Guardrail
  └── Check: In Helm / Kubernetes manifests, verify that `livenessProbe.timeoutSeconds` is greater than or equal to downstream client timeouts.
        │
        ▼ (Target Ingestion)
`devsecops-reviewer` & `devsecops-engineer`
```

---

## Step-by-Step Translation Protocol

### 1. Ingest SRE Incident Artifact
Extract three critical fields from the blameless postmortem:
- **Failure Trigger:** What specific configuration or code caused the failure?
- **Blast Radius:** What environments and services were impacted?
- **Root Cause Mechanism:** Why did the safety system fail to prevent it?

### 2. Determine the Optimal Enforcement Layer
Choose the earliest possible detection stage in the SDLC:
1. **Pre-commit / Editor:** Tree-sitter or linter regex.
2. **Pre-merge CI:** Conftest (Rego), Checkov custom policy, or GitHub Actions validation step.
3. **Runtime Admission:** Kyverno or OPA Gatekeeper constraint template.

### 3. Generate Preventative Policy (Example: Rego / OPA)

```rego
package kubernetes.admission

# Prevent liveness probe timeouts shorter than 3 seconds
deny[msg] {
    input.request.kind.kind == "Deployment"
    container := input.request.object.spec.template.spec.containers[_]
    probe := container.livenessProbe
    probe.timeoutSeconds < 3
    msg := sprintf("Container '%v' has liveness probe timeout < 3s, which caused Incident INC-4091. Must be >= 3s.", [container.name])
}
```

### 4. Register in Agent Suite
Add the guardrail description to [`agents/7-agent-master-suite/devsecops-reviewer.md`](file:///Users/ijimoh/openIDE/agents/7-agent-master-suite/devsecops-reviewer.md) under the active audit checklist.
