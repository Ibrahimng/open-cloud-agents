---
name: knowledge-enhancement-loop
description: Enables AI agents to autonomously reflect on tool execution transcripts, capture novel cloud behaviors and runtime edge cases, and update knowledge repositories (AGENTS.md and SKILL.md) for continuous self-improvement.
---

# Autonomous Knowledge Harvesting & Self-Improvement Protocol

## Purpose & Scope
This skill provides agents with a structured, non-destructive protocol to learn from every production task, failed attempt, or novel cloud provider behavior. It ensures the agent ensemble compounds in intelligence over time.

---

## When to Trigger the Self-Improvement Loop
The agent must initiate self-reflection when any of the following triggers occur:
1. **Tool Execution Recovery:** A tool call failed with an unexpected error (e.g. cloud provider API quota, undocumented deprecation, region restriction), and the agent successfully discovered a workaround.
2. **Post-Incident Resolution:** An active outage or pipeline failure was mitigated by the SRE or DevSecOps Engineer.
3. **Novel Environment Fact:** The agent discovers workspace-specific topology details (e.g. custom VPC peering CIDRs, specific KMS key aliases, internal proxy requirements).

---

## The 4-Step Self-Enhancement Workflow

```text
[Execution Transcript] 
         │
         ▼
 1. TRIAGE & EXTRACT (Isolate signal from noise)
         │
         ▼
 2. VALIDATE FACT (Confirm not hallucinated or one-off fluke)
         │
         ▼
 3. LOCALIZED IN-PLACE PATCH (Update target SKILL.md or AGENTS.md)
         │
         ▼
 4. VERIFY REGRESSION RESISTANCE (Ensure no existing rules were broken)
```

### Step 1: Extract the Knowledge Delta
Parse the session transcript for the delta:
- **What was assumed:** (e.g., "Assumed Azure CLI supports `--query` filtering on this preview command.")
- **What actually happened:** (e.g., "The command failed with exit code 2: JMESPath query unsupported on preview endpoint.")
- **What succeeded:** (e.g., "Piped raw JSON to `jq` locally.")

### Step 2: Formulate the Knowledge Record
Format the learning into a single, high-density bullet:
```text
- [Date: YYYY-MM-DD] [Scope: azure/preview-api] Never use --query on preview resource commands; pipe raw JSON to jq to avoid exit code 2.
```

### Step 3: Apply In-Place Knowledge Patching
- If the learning is a **workspace-specific convention**, append to the project's root `AGENTS.md` under `## Learned Workspace Facts`.
- If the learning is a **general cloud engineering rule**, propose a patch directly to the corresponding `SKILL.md` under `## Known Edge Cases & Traps`.

### Step 4: Guardrails Against Knowledge Poisoning
- **Never delete or overwrite existing safety rules.**
- **No speculative knowledge:** Only record facts substantiated by observed command output or verifiable HTTP responses.
- **Deduplicate:** Check if an identical or broader rule already exists before appending.

---

## Real-Life Example: Auto-Updating an AWS Skill
During a Terraform apply, AWS returned `InvalidParameterValue: RDS storage type io2 requires iops allocation between 1000 and 256000`.
The agent autonomously caught this, corrected the IOPS parameter, and appended the rule to `skills/devops/iac/terraform-opentofu-modules/SKILL.md`:
```markdown
### Learned Cloud Quota (AWS RDS io2)
- AWS RDS `io2` storage volumes strictly enforce minimum 1,000 IOPS and maximum 256,000 IOPS. Always include an HCL validation block ensuring `var.iops >= 1000 && var.iops <= 256000`.
```
