#!/usr/bin/env python3
"""
Open Cloud Agents: Universal CLI (ocagents).

Production CLI for syncing, listing, validating, and running Open Cloud Agents
specialist personas and skills across GitHub Copilot, Cursor, Claude Code, and Gemini.

Usage:
    ocagents list
    ocagents -a ls
    ocagents sync --all --format github --target /path/to/repo --sync-skills
    ocagents -A -format github --target /path/to/repo
    ocagents validate
    ocagents run --task "Architect multi-region payment DR"
    ocagents info
"""

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

__version__ = "1.3.0"

CANONICAL_REPO_URL = "https://github.com/Ibrahimng/open-cloud-agents.git"
AVAILABLE_FORMATS = ["github", "claude", "cursor", "gemini", "raw"]


def resolve_asset_root() -> Path:
    """Dynamically resolves the root directory containing agents/ and skills/."""
    # 1. Check explicit environment override
    env_root = os.environ.get("OCAGENTS_HOME")
    if env_root and Path(env_root).exists() and (Path(env_root) / "agents").exists():
        return Path(env_root).resolve()

    # 2. Check if running inside the cloned git repository
    file_dir = Path(__file__).resolve().parent
    repo_candidate = file_dir.parent.parent
    if (repo_candidate / "agents" / "7-agent-master-suite").exists():
        return repo_candidate

    # 3. Check standard user installation directory (~/.open-cloud-agents)
    user_home_candidate = Path.home() / ".open-cloud-agents"
    if (user_home_candidate / "agents" / "7-agent-master-suite").exists():
        return user_home_candidate

    # Fallback to current working directory
    return Path.cwd().resolve()


def get_agents_dir(asset_root: Path) -> Path:
    return asset_root / "agents" / "7-agent-master-suite"


def get_skills_dir(asset_root: Path) -> Path:
    return asset_root / "skills"


def log_pass(msg: str):
    print(f"  \033[92m✔\033[0m {msg}")


def log_fail(msg: str):
    print(f"  \033[91m✖\033[0m {msg}")


def log_info(msg: str):
    print(f"\033[94mℹ\033[0m {msg}")


def parse_agent_frontmatter(file_path: Path) -> tuple[dict, str]:
    """Parse YAML frontmatter and body from agent markdown."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return {}, ""
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


def get_available_agents(agents_dir: Path) -> dict[str, Path]:
    """Retrieve map of agent slug to Path."""
    agents = {}
    if not agents_dir.exists():
        return agents
    for p in agents_dir.glob("*.md"):
        slug = p.stem
        agents[slug] = p
    return agents


def cmd_list(asset_root: Path):
    """List all agents in the Master Suite and their linked skills."""
    agents_dir = get_agents_dir(asset_root)
    agents = get_available_agents(agents_dir)

    print("\n☁️  Open Cloud Agents: 7-Agent Master Suite Registry")
    print("=" * 70)
    if not agents:
        log_fail(f"No agents found in {agents_dir}. Run 'ocagents update' to initialize assets.")
        return 1

    for slug, p in sorted(agents.items()):
        meta, _ = parse_agent_frontmatter(p)
        name = meta.get("name", slug)
        skills = meta.get("skills", [])
        tools = meta.get("tools", [])
        print(f"• \033[1m{slug}\033[0m: {name}")
        print(f"    ↳ Tools: [{', '.join(tools)}]")
        if skills:
            print(f"    ↳ Linked Skills ({len(skills)}): {', '.join(skills)}")
        else:
            print("    ↳ Linked Skills: None declared")
    print("=" * 70)
    print("Tip: Sync agents to your repo with: ocagents sync -A --format github --target .")
    return 0


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
    skills_dir: Path,
) -> bool:
    """Synchronize an agent and optionally its skills into the target workspace."""
    meta, body = parse_agent_frontmatter(agent_path)
    name = meta.get("name", agent_slug)
    log_info(f"Syncing [{name}] to format [{fmt}] in '{target_root}'...")

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

    declared_skills = meta.get("skills", [])
    if sync_skills and declared_skills:
        log_info(f"Syncing {len(declared_skills)} linked skills for [{agent_slug}]...")
        for skill_rel in declared_skills:
            src_skill_path = skills_dir / skill_rel
            if not src_skill_path.exists():
                log_fail(f"Declared skill path does not exist: {src_skill_path}")
                continue

            dest_skill_path = skills_target_dir / skill_rel
            if dry_run:
                log_pass(f"[DRY-RUN] Would sync skill: {src_skill_path.name} -> {dest_skill_path}")
            elif use_symlink:
                dest_skill_path.parent.mkdir(parents=True, exist_ok=True)
                if dest_skill_path.exists() or dest_skill_path.is_symlink():
                    if dest_skill_path.is_dir() and not dest_skill_path.is_symlink():
                        shutil.rmtree(dest_skill_path)
                    else:
                        dest_skill_path.unlink()
                rel_src = os.path.relpath(src_skill_path, dest_skill_path.parent)
                dest_skill_path.symlink_to(rel_src)
                log_pass(f"Symlinked skill: {dest_skill_path.name} -> {rel_src}")
            else:
                dest_skill_path.parent.mkdir(parents=True, exist_ok=True)
                if dest_skill_path.exists():
                    shutil.rmtree(dest_skill_path)
                shutil.copytree(src_skill_path, dest_skill_path)
                log_pass(f"Copied skill: {src_skill_path.name} -> {dest_skill_path}")

    return True


def cmd_sync(args, asset_root: Path):
    """Sync agents and skills to the destination workspace."""
    agents_dir = get_agents_dir(asset_root)
    skills_dir = get_skills_dir(asset_root)
    available_agents = get_available_agents(agents_dir)

    target_root = Path(args.target).resolve()

    if args.all or args.agent == "all":
        targets = list(available_agents.keys())
    else:
        if args.agent not in available_agents:
            log_fail(f"Agent '{args.agent}' not found. Available: {', '.join(available_agents.keys())}")
            return 1
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
            skills_dir=skills_dir,
        ):
            success_count += 1

    print("=" * 65)
    log_pass(f"Successfully synchronized {success_count} agent(s) into '{target_root}'\n")
    return 0


def cmd_validate(asset_root: Path):
    """Runs repository hygiene and agent pipeline validation."""
    log_info("Running Open Cloud Agents contract and spec validation...")
    overall_rc = 0

    pipeline_script = asset_root / "scripts" / "agents" / "agent_pipeline.py"
    if pipeline_script.exists():
        res = subprocess.run([sys.executable, str(pipeline_script), "--validate"])
        if res.returncode != 0:
            overall_rc = res.returncode
    else:
        log_fail(f"Pipeline validation script not found at: {pipeline_script}")
        overall_rc = 1

    ci_script = asset_root / "scripts" / "ci" / "validate_repo.py"
    if ci_script.exists():
        res_ci = subprocess.run([sys.executable, str(ci_script)])
        if res_ci.returncode != 0:
            overall_rc = res_ci.returncode

    return overall_rc


def cmd_run(args, asset_root: Path):
    """Runs the multi-agent pipeline simulation on a task."""
    pipeline_script = asset_root / "scripts" / "agents" / "agent_pipeline.py"
    if pipeline_script.exists():
        cmd = [sys.executable, str(pipeline_script), "--task", args.task]
        res = subprocess.run(cmd)
        return res.returncode
    log_fail(f"Pipeline runner script not found at: {pipeline_script}")
    return 1


def cmd_info(asset_root: Path):
    """Displays CLI and asset environment information."""
    print(f"\n☁️  Open Cloud Agents CLI (ocagents) v{__version__}")
    print("=" * 60)
    print(f"Asset Home:        {asset_root}")
    print(f"Agents Directory:  {get_agents_dir(asset_root)}")
    print(f"Skills Directory:  {get_skills_dir(asset_root)}")
    print(f"Python Runtime:    {sys.executable} ({sys.version.split()[0]})")
    agents = get_available_agents(get_agents_dir(asset_root))
    print(f"Registered Agents: {len(agents)} active")
    print("=" * 60)
    return 0


def cmd_update(asset_root: Path):
    """Updates or installs the canonical agents asset catalog in ~/.open-cloud-agents."""
    target_dir = Path.home() / ".open-cloud-agents"
    print(f"\n☁️  Updating Open Cloud Agents catalog at: {target_dir}")
    if target_dir.exists() and (target_dir / ".git").exists():
        log_info("Fetching latest updates from git repository...")
        res = subprocess.run(["git", "-C", str(target_dir), "pull", "origin", "main"])
        if res.returncode == 0:
            log_pass("Successfully updated Open Cloud Agents catalog.")
            return 0
        log_fail("Git pull failed.")
        return 1
    else:
        log_info(f"Cloning canonical repository from {CANONICAL_REPO_URL}...")
        res = subprocess.run(["git", "clone", "--depth=1", CANONICAL_REPO_URL, str(target_dir)])
        if res.returncode == 0:
            log_pass("Successfully cloned Open Cloud Agents catalog.")
            return 0
        log_fail("Git clone failed.")
        return 1


def normalize_custom_args(argv: list[str]) -> list[str]:
    """Translates user-friendly short flags like -agents, -format, -target into standard flags."""
    normalized = []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("-format", "--format"):
            normalized.append("--format")
        elif arg in ("-target", "--target"):
            normalized.append("--target")
        elif arg == "-agents":
            normalized.append("agents")
        elif arg == "ls":
            normalized.append("list")
        else:
            normalized.append(arg)
        i += 1
    return normalized


def main():
    raw_args = sys.argv[1:]

    # Handle quick top-level invocations matching user request:
    # e.g.: ocagents -agents list, ocagents -a ls, ocagents agents list
    if len(raw_args) >= 1 and raw_args[0] in ("-agents", "agents", "-a") and len(raw_args) >= 2 and raw_args[1] in ("list", "ls"):
        raw_args = ["list"]
    elif len(raw_args) >= 1 and raw_args[0] in ("-a", "ls"):
        if len(raw_args) == 1 and raw_args[0] in ("ls", "list"):
            raw_args = ["list"]

    # Handle shortcut: ocagents -A -format github --target /path
    if len(raw_args) >= 1 and raw_args[0] == "-A":
        raw_args = ["sync", "--all"] + raw_args[1:]

    normalized_args = normalize_custom_args(raw_args)

    parser = argparse.ArgumentParser(
        prog="ocagents",
        description="Open Cloud Agents: Universal CLI for Cloud Architecture & Security Review Agents.",
    )
    parser.add_argument("-v", "--version", action="version", version=f"ocagents v{__version__}")

    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # list
    p_list = subparsers.add_parser("list", aliases=["ls"], help="List all 7 master suite agents and linked skills")

    # sync
    p_sync = subparsers.add_parser("sync", help="Synchronize agents & skills into your workspace")
    p_sync.add_argument("agent", nargs="?", default="devsecops-reviewer", help="Agent slug (or all)")
    p_sync.add_argument("-A", "--all", action="store_true", help="Sync all 7 agents")
    p_sync.add_argument("-a", dest="agent_opt", help="Agent slug alias")
    p_sync.add_argument("-f", "--format", choices=AVAILABLE_FORMATS, default="github", help="Target format")
    p_sync.add_argument("-t", "--target", default=".", help="Target directory")
    p_sync.add_argument("-s", "--sync-skills", action="store_true", help="Also sync declared specialist skills")
    p_sync.add_argument("--symlink", action="store_true", help="Use symlinks instead of copying")
    p_sync.add_argument("--dry-run", action="store_true", help="Dry run without writing files")

    # validate
    subparsers.add_parser("validate", aliases=["check"], help="Validate agent specs, tools, and repo hygiene")

    # run
    p_run = subparsers.add_parser("run", help="Run multi-agent pipeline simulation on an architectural task")
    p_run.add_argument("task", nargs="?", default="Architect multi-region payment DR failover with Aurora Global Database")
    p_run.add_argument("--task", dest="task_opt", help="Task prompt string")

    # info
    subparsers.add_parser("info", help="Show environment, asset path, and CLI version")

    # update
    subparsers.add_parser("update", help="Update the canonical agents catalog in ~/.open-cloud-agents")

    if not normalized_args:
        parser.print_help()
        sys.exit(0)

    parsed = parser.parse_args(normalized_args)
    asset_root = resolve_asset_root()

    if parsed.subcommand in ("list", "ls"):
        sys.exit(cmd_list(asset_root))
    elif parsed.subcommand == "sync":
        if getattr(parsed, "agent_opt", None):
            parsed.agent = parsed.agent_opt
        sys.exit(cmd_sync(parsed, asset_root))
    elif parsed.subcommand in ("validate", "check"):
        sys.exit(cmd_validate(asset_root))
    elif parsed.subcommand == "run":
        if getattr(parsed, "task_opt", None):
            parsed.task = parsed.task_opt
        sys.exit(cmd_run(parsed, asset_root))
    elif parsed.subcommand == "info":
        sys.exit(cmd_info(asset_root))
    elif parsed.subcommand == "update":
        sys.exit(cmd_update(asset_root))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
