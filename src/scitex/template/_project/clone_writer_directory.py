#!/usr/bin/env python3
# Timestamp: "2025-10-30 08:47:48 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/template/clone_writer_directory.py
# ----------------------------------------
from __future__ import annotations

import os

__FILE__ = "./src/scitex/template/clone_writer_directory.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Create a new paper directory from the scitex-writer template.
"""

import sys
from typing import Optional

from ._clone_project import clone_project

TEMPLATE_REPO_URL = "https://github.com/ywatanabe1989/scitex-writer.git"


def clone_writer_directory(
    project_dir: str,
    git_strategy: Optional[str] = "child",
    branch: Optional[str] = "main",
    tag: Optional[str] = None,
    **kwargs,
) -> bool:
    """
    Create a new paper directory from the scitex-writer template repository.

    Parameters
    ----------
    project_dir : str
        Path to project directory (will be created). Can be a simple name like "my_paper"
        or a full path like "./papers/my_paper"
    git_strategy : str, optional
        Git initialization strategy ('child', 'parent', None). Default is 'child'.
    branch : str, optional
        Specific branch of the template repository to clone. Default is 'main'.
        Mutually exclusive with tag parameter.
    tag : str, optional
        Specific tag/release of the template repository to clone. If None, uses the branch.
        Mutually exclusive with branch parameter.

    Returns
    -------
    bool
        True if successful, False otherwise

    Example
    -------
    >>> from scitex.template import clone_writer_directory
    >>> clone_writer_directory("my_paper")  # Uses main branch
    >>> clone_writer_directory("./papers/my_paper")
    >>> clone_writer_directory("my_paper", branch="develop")
    >>> clone_writer_directory("my_paper", tag="v2.0.0")
    """
    return clone_project(
        project_dir,
        TEMPLATE_REPO_URL,
        "scitex-writer",
        git_strategy,
        branch,
        tag,
    )


def main(args: list = None) -> None:
    """
    Command-line interface for clone_writer_directory.

    Parameters
    ----------
    args : list, optional
        Command-line arguments. If None, uses sys.argv[1:]
    """
    if args is None:
        args = sys.argv[1:]

    if len(args) < 1:
        print("Usage: python -m scitex clone_writer_directory <project-dir>")
        print("")
        print("Arguments:")
        print("  project-dir   Path to project directory (will be created)")
        print(
            "                Can be a simple name like 'my_paper' or a full path like './papers/my_paper'"
        )
        print("")
        print("Example:")
        print("  python -m scitex clone_writer_directory my_paper")
        print("  python -m scitex clone_writer_directory ./papers/my_paper")
        sys.exit(1)

    project_dir = args[0]

    success = clone_writer_directory(project_dir)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

# EOF
