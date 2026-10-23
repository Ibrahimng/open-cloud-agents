# Knowledge Patch Entry Schema Specification

When an agent extracts a novel rule or edge case from a session transcript, the patch must conform to this schema before insertion into `AGENTS.md` or a target `SKILL.md`:

```text
- [Date: YYYY-MM-DD] [Scope: <domain>/<technology>] [Severity: INFO|WARN|BLOCKER] <Imperative Rule Statement>. Root cause: <Verifiable observed behavior>.
```

## Field Definitions
- **Date:** ISO-8601 date of discovery.
- **Scope:** Provider and tool (e.g. `aws/aurora`, `k8s/coredns`, `fastapi/pydantic`).
- **Severity:**
  - `INFO`: Helpful optimization or performance pattern.
  - `WARN`: Common configuration trap with viable fallback.
  - `BLOCKER`: State-destroying trap, data loss risk, or critical security loophole.
- **Imperative Rule Statement:** Actionable directive starting with a verb (e.g., *Always configure `prevent_destroy = true`* or *Never use `--query` on preview CLI commands*).

## Example Valid Entry
```text
- [Date: 2026-10-23] [Scope: aws/rds-postgres] [Severity: BLOCKER] Never modify parameter group family on live Aurora clusters in-place; triggers immediate cluster recreation and 40+ min outage.
```

