# Contributing to Open Cloud Agents

Thank you for your interest in contributing to **Open Cloud Agents**! We are building an open, enterprise-grade multi-agent cloud architecture mapped across the AWS, Azure, and Google Cloud Well-Architected Frameworks.

By contributing, you help make cloud architecture, security, GitOps, SRE, and FinOps more reliable and autonomous for engineering teams worldwide.

---

## How You Can Contribute

We welcome contributions in several key areas:

### 1. New Agent Personas
Have an idea for a specialized agent (e.g., `mlops-engineer`, `database-reliability-architect`, `identity-zero-trust-specialist`)?
- Follow the structure used in `agents/7-agent-master-suite/`.
- Ensure each agent includes:
  - Strict scope and mandate
  - Explicit non-goals (what the agent does *not* own)
  - Clear input/output handoffs with upstream and downstream agents
  - Negative trade-off accounting and safety guardrails

### 2. Improving Agent Prompts & Guardrails
- Refining system instructions to eliminate hallucinations.
- Hardening destructive action checks (e.g., state-loss prevention in Terraform/OpenTofu, zero-downtime database migrations).
- Updating tool definitions to support new MCP servers and cloud provider APIs.

### 3. Benchmarks & Real-World Evaluation Cases
- Share prompt evaluations, scenario tests, and test suites that evaluate agent performance across real multi-cloud topologies.

### 4. Bug Reports & Architectural RFCs
- If an agent suggests an outdated pattern, non-optimal cloud tiering, or fails a security standard, open an Issue with context and proposed remediations.

---

## Contribution Process

1. **Fork the Repository** and create your branch from `main`:
   ```bash
   git checkout -b feat/my-new-agent
   ```
2. **Make Your Changes** following our engineering standards (see [`docs/engineering-standards.md`](./docs/engineering-standards.md)).
3. **Run the Local Validation Suite:**
   Before pushing, verify all skill specs, permissions, and markdown links pass:
   ```bash
   python3 scripts/ci/validate_repo.py
   ```
4. **Guardrail Checklist:**
   - [ ] No hardcoded secrets, keys, or credentials (verified by Gitleaks in CI).
   - [ ] All shell scripts have executable bits (`chmod +x scripts/*.sh`).
   - [ ] Skill specs have valid YAML frontmatter (`name:`, `description:`).
   - [ ] Internal markdown links resolve properly without broken relative paths.
   - [ ] Follows conventional commits (`feat:`, `fix:`, `docs:`, `chore:`).
5. **Submit a Pull Request** with a concise description of your changes, the rationale, and any sample outputs or tests.

---

## Community & Conduct

We are committed to providing a friendly, safe, and welcoming environment for all contributors. Please treat others with respect and constructive professionalism.

