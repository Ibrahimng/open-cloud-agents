---
name: Surgical Scope Discipline & Non-Interference
severity: STRICT
scope: ALL_AGENTS
---

# Rule 03: Surgical Scope Discipline & Non-Interference

## Principle
AI agents frequently cause regressions when attempting unsolicited "cleanups", mass refactorings, or whole-repository formatting sweeps. Agents must maintain strict surgical discipline, modifying only what is necessary to accomplish the user's explicit objective.

---

## Prohibited Behaviors

### 1. Zero Unsolicited Refactoring
- Do not refactor existing working code, rename classes, change method signatures, or reorganize folder hierarchies unless explicitly requested by the user.
- Preserve existing comments, docstrings, licensing headers, and architectural conventions.

### 2. Zero Global Formatting Sweeps
- Do not run repository-wide linters or formatters (e.g. running `prettier` or `black` across files untouched by the current task).
- Large diffs hide regressions and complicate peer reviews. Limit changes strictly to the relevant lines.

### 3. Minimal Dependency Changes
- Do not introduce new third-party libraries or external dependencies unless the user's task fundamentally requires it.
- Never bump dependency versions across the entire package manifest (`package.json`, `pom.xml`, `requirements.txt`, `go.mod`) without explicit permission.

---

## The DevSecOps Engineer Rule
When applying a fix or implementing a feature:
1. Target only the minimum required file(s).
2. Validate that the targeted changes pass automated local tests.
3. Generate clean, atomic git commits using Conventional Commits format (`feat:`, `fix:`, `refactor:`, `docs:`).
