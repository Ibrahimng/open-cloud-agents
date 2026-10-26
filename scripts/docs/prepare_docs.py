#!/usr/bin/env python3
# ==============================================================================
# Open Cloud Agents: Documentation Preparation Script for MkDocs / GitHub Pages
#
# Stages all in-repo Markdown documents (Single Source of Truth) into a unified
# build_docs/ directory for MkDocs static site generation.
# ==============================================================================

import os
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BUILD_DOCS = REPO_ROOT / "build_docs"


def log(msg: str):
    print(f"ℹ [Docs Builder] {msg}")


def prepare_docs():
    log(f"Staging docs into: {BUILD_DOCS}")

    if BUILD_DOCS.exists():
        shutil.rmtree(BUILD_DOCS)
    BUILD_DOCS.mkdir(parents=True, exist_ok=True)

    # 1. Homepage: Copy README.md as index.md
    readme_src = REPO_ROOT / "README.md"
    if readme_src.exists():
        shutil.copy2(readme_src, BUILD_DOCS / "index.md")
        log("Staged README.md -> index.md (Homepage)")

    # 2. Core Root Documents
    core_files = [
        "AGENTS.md",
        "CHANGELOG.md",
        "CONTRIBUTING.md",
        "CONTRIBUTORS.md",
        "LICENSE",
    ]
    for filename in core_files:
        src = REPO_ROOT / filename
        if src.exists():
            shutil.copy2(src, BUILD_DOCS / filename)
            log(f"Staged {filename}")

    # 3. Core Architecture Trees
    core_trees = ["agents", "rules", "skills"]
    for tree in core_trees:
        src = REPO_ROOT / tree
        dest = BUILD_DOCS / tree
        if src.exists():
            shutil.copytree(src, dest, ignore=shutil.ignore_patterns(".git*", "__pycache__", "*.pyc"))
            log(f"Staged {tree}/ directory")

    # 4. Existing docs/ directory content
    docs_dir = REPO_ROOT / "docs"
    if docs_dir.exists():
        for item in docs_dir.iterdir():
            if item.name.startswith("."):
                continue
            dest_item = BUILD_DOCS / item.name
            if item.is_dir():
                shutil.copytree(item, dest_item)
            else:
                shutil.copy2(item, dest_item)
        log("Staged docs/ architectural specs and assets")

        # Also support docs/images/ alias path for relative markdown links
        docs_alias = BUILD_DOCS / "docs"
        docs_alias.mkdir(parents=True, exist_ok=True)
        images_src = docs_dir / "images"
        if images_src.exists():
            shutil.copytree(images_src, docs_alias / "images", dirs_exist_ok=True)

    log("Documentation preparation completed successfully!")


if __name__ == "__main__":
    prepare_docs()
