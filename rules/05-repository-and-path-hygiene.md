---
name: Repository & Path Hygiene Standard
severity: CI_BLOCKING
scope: ALL_AGENTS
---

# Rule 05: Repository & Path Hygiene Standard

## Principle
Open Cloud Agents is an open-source, collaborative project designed to run portably across any developer's local machine, cloud workstation, or CI/CD container. All paths, documentation links, and references must be strictly relative and clean.

---

## Inviolable Path Hygiene Rules

### 1. Zero Absolute Local Workstation Paths
- Under no circumstances may an agent or contributor commit paths containing `/Users/<username>/` (macOS) or `/home/<username>/` (Linux).
- All file references must be relative to the repository root or current file location.
- Example:
  - ❌ `file:///Users/<username>/projects/...`
  - ✅ `../skills/devops/kubernetes/k8s-pod-troubleshooting/SKILL.md`

### 2. Relative Markdown Links
- Every link to another document, agent persona, skill, or script must use standard relative Markdown links (e.g. `[Link Text](../path/to/target.md)`).
- Broken links will fail the automated CI pipeline (`scripts/ci/validate_repo.py`).

### 3. File Permissions
- All shell helper scripts (`*.sh`) and executable Python CLI tools in `scripts/` must retain execution bits (`chmod +x`).

### 4. Git Ignore Discipline
- The `ai_brain/` directory, editor state, virtual environments (`.venv`), and temporary scratch logs must remain permanently ignored via `.gitignore`.
