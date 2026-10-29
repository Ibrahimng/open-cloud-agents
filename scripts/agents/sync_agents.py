#!/usr/bin/env python3
"""
Open Cloud Agents: Universal Multi-Workspace Agent & Skill Synchronizer.

Syncs Open Cloud Agents (such as DevSecOps Reviewer) and their linked specialist
skills into external repositories and preferred IDE workspaces:
  - GitHub Copilot CLI & Workspaces (.github/agents/*)
  - Claude Code & Anthropic Workbench (.claude/agents/*, .claude/skills/*)
  - Cursor Rules & Agent Directory (.cursor/rules/*.mdc, .cursor/agents/*)
  - Google Antigravity & Gemini Workspaces (.gemini/agents/*)

Usage:
    # Sync DevSecOps Reviewer to GitHub Copilot agents with linked skills
    python3 scripts/agents/sync_agents.py --agent devsecops-reviewer --format github --target /path/to/repo --sync-skills

    # Sync all 7 agents to Cursor Rules (.cursor/rules/*.mdc)
    python3 scripts/agents/sync_agents.py --all --format cursor --target /path/to/repo

    # Sync to Claude Code with symlinks for local dev
    python3 scripts/agents/sync_agents.py --agent devsecops-reviewer --format claude --target . --symlink --sync-skills

    # List all available master suite agents and their declared skills
    python3 scripts/agents/sync_agents.py --list
"""

import argparse
import os
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
AGENTS_DIR = REPO_ROOT / "agents" / "7-agent-master-suite"
SKILLS_DIR = REPO_ROOT / "skills"

CANONICAL_DOCS_BASE = "https://ibrahimng.github.io/open-cloud-agents"

AVAILABLE_FORMATS = ["github", "claude", "cursor", "gemini", "raw"]


def log_pass(msg: str):
    print(f"  \033[92m✔\033[0m {msg}")


def log_fail(msg: str):
    print(f"  \033[91m✖\033[0m {msg}")


def log_info(msg: str):
    print(f"\033[94mℹ\033[0m {msg}")


def parse_agent_frontmatter(file_path: Path) -> tuple[dict, str]:
    """Parse YAML frontmatter and body from agent markdown."""
    content = file_path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return {}, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    fm_raw = parts[1]
    body = parts[2]
    meta = {}
    for line in fm_raw.strip().splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()
            if val.startswith("[") and val.endswith("]"):
                meta[key] = [item.strip() for item in val[1:-1].split(",") if item.strip()]
            else:
                meta[key] = val.strip('"\'')
    return meta, body


def get_available_agents() -> dict[str, Path]:
    """Retrieve map of agent slug to Path."""
    agents = {}
    if not AGENTS_DIR.exists():
        return agents
    for p in AGENTS_DIR.glob("*.md"):
        slug = p.stem
        agents[slug] = p
    return agents


def transform_for_cursor(meta: dict, body: str) -> str:
    """Format markdown file as a Cursor Rule (.mdc)."""
    desc = meta.get("description", "Open Cloud Agents specialist assistant")
    frontmatter = f"""---
description: "{desc}"
globs: "*"
alwaysApply: false
---
"""
    return frontmatter + body


def sync_single_agent(
    agent_slug: str,
    agent_path: Path,
    target_root: Path,
    fmt: str,
    sync_skills: bool,
    use_symlink: bool,
    dry_run: bool,
) -> bool:
    """Synchronize an agent and optionally its skills into the target workspace."""
    meta, body = parse_agent_frontmatter(agent_path)
    name = meta.get("name", agent_slug)
    log_info(f"Syncing [{name}] to format [{fmt}] in '{target_root}'...")

    # Determine destination paths
    if fmt == "github":
        dest_agent_dir = target_root / ".github" / "agents"
        dest_file = dest_agent_dir / f"{agent_slug}.md"
        skills_target_dir = target_root / ".github" / "skills"
    elif fmt == "claude":
        dest_agent_dir = target_root / ".claude" / "agents"
        dest_file = dest_agent_dir / f"{agent_slug}.md"
        skills_target_dir = target_root / ".claude" / "skills"
    elif fmt == "cursor":
        dest_rules_dir = target_root / ".cursor" / "rules"
        dest_agent_dir = target_root / ".cursor" / "agents"
        dest_file = dest_rules_dir / f"{agent_slug}.mdc"
        dest_agent_file = dest_agent_dir / f"{agent_slug}.md"
        skills_target_dir = target_root / ".cursor" / "skills"
    elif fmt == "gemini":
        dest_agent_dir = target_root / ".gemini" / "agents"
        dest_file = dest_agent_dir / f"{agent_slug}.md"
        skills_target_dir = target_root / ".gemini" / "skills"
    else:  # raw
        dest_agent_dir = target_root / "agents"
        dest_file = dest_agent_dir / f"{agent_slug}.md"
        skills_target_dir = target_root / "skills"

    if dry_run:
        log_pass(f"[DRY-RUN] Would create agent: {dest_file}")
    else:
        dest_agent_dir.mkdir(parents=True, exist_ok=True)
        if fmt == "cursor":
            dest_rules_dir.mkdir(parents=True, exist_ok=True)
            cursor_content = transform_for_cursor(meta, body)
            dest_file.write_text(cursor_content, encoding="utf-8")
            log_pass(f"Wrote Cursor Rule: {dest_file}")
            # Also write raw agent file for Cursor agent mode
            dest_agent_file.write_text(agent_path.read_text(encoding="utf-8"), encoding="utf-8")
            log_pass(f"Wrote Cursor Agent: {dest_agent_file}")
        elif use_symlink:
            if dest_file.exists() or dest_file.is_symlink():
                dest_file.unlink()
            rel_src = os.path.relpath(agent_path, dest_agent_dir)
            dest_file.symlink_to(rel_src)
            log_pass(f"Symlinked: {dest_file} -> {rel_src}")
        else:
            shutil.copy2(agent_path, dest_file)
            log_pass(f"Wrote Agent: {dest_file}")

    # Synchronize linked skills if requested
    declared_skills = meta.get("skills", [])
    if sync_skills and declared_skills:
        log_info(f"Syncing {len(declared_skills)} linked skills for [{agent_slug}]...")
        for skill_rel in declared_skills:
            src_skill_path = SKILLS_DIR / skill_rel
            if not src_skill_path.exists():
                log_fail(f"Declared skill path does not exist: {src_skill_path}")
                continue

            dest_skill_path = skills_target_dir / skill_rel
            if dry_run:
                log_pass(f"[DRY-RUN] Would sync skill: {src_skill_path} -> {dest_skill_path}")
            elif use_symlink:
                dest_skill_path.parent.mkdir(parents=True, exist_ok=True)
                if dest_skill_path.exists() or dest_skill_path.is_symlink():
                    if dest_skill_path.is_dir() and not dest_skill_path.is_symlink():
                        shutil.rmtree(dest_skill_path)
                    else:
                        dest_skill_path.unlink()
                rel_src = os.path.relpath(src_skill_path, dest_skill_path.parent)
                dest_skill_path.symlink_to(rel_src)
                log_pass(f"Symlinked skill: {dest_skill_path} -> {rel_src}")
            else:
                dest_skill_path.parent.mkdir(parents=True, exist_ok=True)
                if dest_skill_path.exists():
                    shutil.rmtree(dest_skill_path)
                shutil.copytree(src_skill_path, dest_skill_path)
                log_pass(f"Copied skill: {src_skill_path.name} -> {dest_skill_path}")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Open Cloud Agents: Multi-Workspace Agent & Skill Synchronizer."
    )
    parser.add_argument(
        "--agent",
        type=str,
        default="devsecops-reviewer",
        help="Specific agent slug (e.g. devsecops-reviewer, security-compliance-commander, all)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Sync all 7 agents in the Master Suite",
    )
    parser.add_argument(
        "--format",
        choices=AVAILABLE_FORMATS,
        default="github",
        help="Target workspace environment format (github, claude, cursor, gemini, raw)",
    )
    parser.add_argument(
        "--target",
        type=str,
        default=".",
        help="Target repository or workspace root directory (default: current directory)",
    )
    parser.add_argument(
        "--sync-skills",
        action="store_true",
        help="Also sync/copy the specialist skills referenced by the target agent(s)",
    )
    parser.add_argument(
        "--symlink",
        action="store_true",
        help="Create symbolic links instead of copying files (ideal for local development)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview synchronization operations without modifying files",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available master suite agents and their declared skills",
    )

    args = parser.parse_args()
    available_agents = get_available_agents()

    if args.list:
        print("\n🏛️  Open Cloud Agents: 7-Agent Master Suite Registry\n" + "=" * 60)
        for slug, p in sorted(available_agents.items()):
            meta, _ = parse_agent_frontmatter(p)
            name = meta.get("name", slug)
            skills = meta.get("skills", [])
            print(f"• \033[1m{slug}\033[0m: {name}")
            if skills:
                print(f"    ↳ Linked Skills ({len(skills)}): {', '.join(skills)}")
            else:
                print("    ↳ Linked Skills: None declared (generalist prompt)")
        print("=" * 60)
        sys.exit(0)

    target_root = Path(args.target).resolve()

    if args.all or args.agent == "all":
        targets = list(available_agents.keys())
    else:
        if args.agent not in available_agents:
            log_fail(f"Agent '{args.agent}' not found. Available: {', '.join(available_agents.keys())}")
            sys.exit(1)
        targets = [args.agent]

    print("\n" + "=" * 65)
    print(" 🔄 Open Cloud Agents: Workspace Synchronizer")
    print("=" * 65)
    log_info(f"Target Directory: {target_root}")
    log_info(f"Target Format:    {args.format}")
    log_info(f"Sync Skills:      {args.sync_skills}")
    log_info(f"Use Symlinks:     {args.symlink}")
    log_info(f"Dry Run:          {args.dry_run}")
    print("-" * 65)

    success_count = 0
    for agent_slug in targets:
        agent_path = available_agents[agent_slug]
        if sync_single_agent(
            agent_slug=agent_slug,
            agent_path=agent_path,
            target_root=target_root,
            fmt=args.format,
            sync_skills=args.sync_skills,
            use_symlink=args.symlink,
            dry_run=args.dry_run,
        ):
            success_count += 1

    print("=" * 65)
    log_pass(f"Successfully synchronized {success_count} agent(s) into '{target_root}'\n")


if __name__ == "__main__":
    main()
