#!/usr/bin/env python3
# Timestamp: "2025-10-29 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/template/_clone_project.py
# ----------------------------------------
from __future__ import annotations

import os

__FILE__ = "./src/scitex/template/_clone_project.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Orchestration for creating projects from template repositories.

This module provides high-level orchestration only, delegating to:
- _copy: Directory operations
- _rename: Package renaming
- _customize: Reference updates
- _git_strategy: Git handling
"""

import shutil
import tempfile
from pathlib import Path
from typing import List, Optional

import scitex.git
from scitex.logging import getLogger

from .._utils._copy import copy_template
from .._utils._customize import update_references
from .._utils._git_strategy import apply_git_strategy, remove_template_git
from .._utils._logging_helpers import log_final, log_group
from .._utils._rename import rename_package_directories
from ._scholar_writer_integration import setup_scholar_writer_integration

logger = getLogger(__name__)

# Items always preserved during include_dirs filtering
_ALWAYS_KEEP = {".gitignore", ".git", "LICENSE", "README.md"}


def _filter_to_include_dirs(target_path: Path, include_dirs: List[str]) -> None:
    """Remove top-level items not in include_dirs.

    Dotfiles (.gitignore, .git) and LICENSE/README.md are always preserved.
    """
    keep = set(include_dirs) | _ALWAYS_KEEP
    for item in list(target_path.iterdir()):
        if item.name in keep or item.name.startswith("."):
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()
        logger.debug(f"Removed excluded item: {item.name}")


def clone_project(
    project_dir: str,
    template_url: str,
    template_name: str,
    git_strategy: Optional[str] = "child",
    branch: Optional[str] = None,
    tag: Optional[str] = None,
    use_cache: bool = True,
    include_dirs: Optional[List[str]] = None,
) -> bool:
    """
    Create a project from a template repository.

    This function orchestrates the entire project creation process:
    1. Validates target directory
    2. Clones template to temporary location
    3. Copies template to target location
    4. Filters to include_dirs if specified
    5. Customizes package names and references
    6. Applies git strategy

    Parameters
    ----------
    project_dir : str
        Path to project directory (will be created). Can be a simple name like "my_paper"
        or a full path like "./papers/my_paper"
    template_url : str
        Git repository URL of the template
    template_name : str
        Name of the template (for logging purposes)
    git_strategy : str, optional
        Git initialization strategy:
        - 'child': Create isolated git in project directory (default)
        - 'parent': Use parent git repository
        - 'origin': Preserve template's original git history
        - None: No git initialization
    branch : str, optional
        Specific branch of the template repository to clone. If None, clones the default branch.
        Mutually exclusive with tag parameter.
    tag : str, optional
        Specific tag/release of the template repository to clone. If None, clones the default branch.
        Mutually exclusive with branch parameter.
    use_cache : bool, optional
        Use cached template from ~/.scitex/templates/ if available. Default True.
        Set to False to force fresh git clone.
    include_dirs : list of str, optional
        If set, only keep these top-level items after cloning. Dotfiles
        (.gitignore, .git) and LICENSE/README.md are always preserved.

    Returns
    -------
    bool
        True if successful, False otherwise
    """
    try:
        # Parse project_dir into name and parent directory
        project_path = Path(project_dir)
        project_name = project_path.name
        target_dir_path = (
            project_path.parent if project_path.parent != Path(".") else Path.cwd()
        )
        target_path = target_dir_path / project_name

        # Check if target directory already exists
        if target_path.exists():
            if scitex.git.is_cloned_from(target_path, template_url):
                log_final(f"Project already exists at {target_path}")
                return True
            logger.error(f"Directory already exists: {target_path}")
            logger.error(f"Cannot clone from {template_url}")
            logger.error(
                "Please choose a different project name or remove the existing directory"
            )
            return False

        # Setup project structure
        with log_group("Setting up project structure", "📦") as ctx:
            target_dir_path.mkdir(parents=True, exist_ok=True)
            ctx.step(f"Target directory: {target_dir_path}")

            # Determine cache location
            from scitex.config import get_scitex_dir

            cache_dir = get_scitex_dir() / "templates"
            cache_name = template_name.replace("/", "_").replace(":", "_")
            cache_path = cache_dir / cache_name

            # Resolve remote ref for cache validation
            ref = tag or branch  # None means default branch (HEAD)
            cache_valid = False

            if use_cache and cache_path.exists():
                # Validate cache against remote by comparing commit hashes
                cache_hash = scitex.git.get_head_hash(cache_path)
                remote_hash = scitex.git.ls_remote(template_url, ref=ref)

                if cache_hash and remote_hash and cache_hash == remote_hash:
                    cache_valid = True
                    ctx.step(f"Cache valid ({cache_hash[:8]}): {cache_path}")
                else:
                    ctx.step(
                        f"Cache stale (local={cache_hash[:8] if cache_hash else '?'}"
                        f" remote={remote_hash[:8] if remote_hash else '?'})"
                    )
                    shutil.rmtree(cache_path)

            if cache_valid:
                # Copy from validated cache
                copy_template(cache_path, target_path, quiet=True)
                ctx.step("Copied from cache")
            else:
                # Clone fresh from git
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir) / "template"

                    ref_info = ""
                    if branch:
                        ref_info = f" (branch: {branch})"
                    elif tag:
                        ref_info = f" (tag: {tag})"

                    # Clone the template repository
                    ctx.substep(f"Cloning from {template_url}{ref_info}...")
                    if not scitex.git.clone_repo(
                        template_url, temp_path, branch=branch, tag=tag, verbose=False
                    ):
                        ctx.step(f"Failed to clone to {target_path}", success=False)
                        return False
                    ctx.step("Cloned template")

                    # Cache the template if caching enabled (before removing .git)
                    if use_cache:
                        cache_dir.mkdir(parents=True, exist_ok=True)
                        if cache_path.exists():
                            shutil.rmtree(cache_path)
                        shutil.copytree(temp_path, cache_path, symlinks=True)
                        new_hash = scitex.git.get_head_hash(cache_path)
                        ctx.substep(
                            f"Cached ({new_hash[:8] if new_hash else '?'})"
                            f" to {cache_path}"
                        )

                    # Handle git directory based on strategy
                    if git_strategy != "origin":
                        remove_template_git(temp_path)

                    # Copy template to target location
                    copy_template(temp_path, target_path, quiet=True)
                    ctx.step("Copied template files")

        # Filter to include_dirs if specified
        if include_dirs:
            _filter_to_include_dirs(target_path, include_dirs)
            logger.info(f"Filtered template to: {include_dirs}")

        # Customize template for project
        with log_group("Customizing template", "🔧") as ctx:
            rename_package_directories(target_path, project_name)
            updated_count = update_references(target_path, project_name)
            if updated_count > 0:
                ctx.step(f"Updated {updated_count} references to {project_name}")
            else:
                ctx.step("No references to update")

        # Setup scholar-writer integration (symlinks for bibliography sharing)
        with log_group("Setting up scholar integration", "📚") as ctx:
            result = setup_scholar_writer_integration(target_path)
            if result["success"] and result["layout"]:
                ctx.step(f"Layout detected: {result['layout']}")
                if result["symlink_created"]:
                    ctx.step("Created symlink for bibliography sharing")
                else:
                    ctx.step("Symlink already exists")
            else:
                ctx.step("Scholar integration skipped")

        # Apply git strategy
        apply_git_strategy(target_path, git_strategy, template_name)

        # Success summary
        log_final(f"Successfully created project at {target_path}")
        logger.info("")
        logger.info("Next steps:")
        logger.info(f"  cd {target_path}")
        if git_strategy == "child":
            logger.info("  # Edit your manuscript in 01_manuscript/contents/")
            logger.info("  scitex writer compile manuscript")

        return True

    except Exception as e:
        logger.error(f"Failed to create project: {str(e)}")
        return False


__all__ = ["clone_project", "_filter_to_include_dirs"]

# EOF
