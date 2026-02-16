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
from typing import Optional

from ._clone_project import clone_project

TEMPLATE_REPO_URL = "https://github.com/ywatanabe1989/scitex-writer.git"


def clone_research_minimal(
    project_dir: str,
    git_strategy: Optional[str] = "child",
    branch: Optional[str] = None,
    tag: Optional[str] = None,
) -> bool:
    """
    Create a new minimal research project from scitex-writer (single source of truth).

    This template contains the essential project structure:
    - writer/ - Full LaTeX manuscript writing with compilation scripts
    - scripts/ - Compilation and automation scripts

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
    return clone_project(
        project_dir,
        TEMPLATE_REPO_URL,
        "scitex-writer",
        git_strategy,
        branch=branch,
        tag=tag,
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
