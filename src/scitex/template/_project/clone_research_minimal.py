#!/usr/bin/env python3
# File: /home/ywatanabe/proj/scitex-code/src/scitex/template/clone_research_minimal.py
# ----------------------------------------
from __future__ import annotations

import os

__FILE__ = "./src/scitex/template/clone_research_minimal.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Create a new minimal research project from the scitex-writer template.

Single source of truth: https://github.com/ywatanabe1989/scitex-writer.git

Contains:
- writer/ - LaTeX manuscript writing and compilation
- scripts/ - Compilation and automation scripts
"""

import sys
from typing import List, Optional

from ._clone_project import clone_project

TEMPLATE_REPO_URL = "https://github.com/ywatanabe1989/scitex-writer.git"

# Directories/files to keep for the minimal template
MINIMAL_INCLUDE_DIRS = [
    "00_shared",
    "01_manuscript",
    "02_supplementary",
    "03_revision",
    "scripts",
    "compile.sh",
    "Makefile",
    "config",
]


def clone_research_minimal(
    project_dir: str,
    git_strategy: Optional[str] = "child",
    branch: Optional[str] = None,
    tag: Optional[str] = None,
    include_dirs: Optional[List[str]] = None,
) -> bool:
    """
    Create a new minimal research project from scitex-writer (single source of truth).

    Clones scitex-writer and keeps only essential directories for manuscript writing.

    Parameters
    ----------
    project_dir : str
        Path to project directory (will be created). Can be a simple name like "my_project"
        or a full path like "./projects/my_project"
    git_strategy : str, optional
        Git initialization strategy ('child', 'parent', None). Default is 'child'.
    branch : str, optional
        Specific branch of the template repository to clone.
    tag : str, optional
        Specific tag/release of the template repository to clone.
    include_dirs : list of str, optional
        Top-level items to keep. Defaults to MINIMAL_INCLUDE_DIRS.

    Returns
    -------
    bool
        True if successful, False otherwise

    Example
    -------
    >>> from scitex.template import clone_research_minimal
    >>> clone_research_minimal("my_research_project")
    >>> clone_research_minimal("./projects/my_project")
    """
    if include_dirs is None:
        include_dirs = MINIMAL_INCLUDE_DIRS
    return clone_project(
        project_dir,
        TEMPLATE_REPO_URL,
        "scitex-writer",
        git_strategy,
        branch=branch,
        tag=tag,
        include_dirs=include_dirs,
    )


def main(args: list = None) -> None:
    """
    Command-line interface for clone_research_minimal.

    Parameters
    ----------
    args : list, optional
        Command-line arguments. If None, uses sys.argv[1:]
    """
    if args is None:
        args = sys.argv[1:]

    if len(args) < 1:
        print("Usage: python -m scitex clone_research_minimal <project-dir>")
        print("")
        print("Arguments:")
        print("  project-dir   Path to project directory (will be created)")
        print("                Can be a simple name like 'my_project' or a full path")
        print("")
        print("Example:")
        print("  python -m scitex clone_research_minimal my_research_project")
        sys.exit(1)

    project_dir = args[0]

    success = clone_research_minimal(project_dir)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

# EOF
