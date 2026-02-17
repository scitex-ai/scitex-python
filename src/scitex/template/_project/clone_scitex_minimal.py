#!/usr/bin/env python3
# Timestamp: 2026-02-17
# File: src/scitex/template/_project/clone_scitex_minimal.py

"""Create a minimal scitex project (writer + scholar).

Composes ensure calls for each module workspace:
- scitex.writer.ensure() -> {project_dir}/scitex/writer/ (full scitex-writer clone)
- scitex.scholar.ensure() -> {project_dir}/scitex/scholar/ (directory scaffold)

Then sets up bibliography sharing between writer and scholar.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from scitex.logging import getLogger

logger = getLogger(__name__)


def clone_scitex_minimal(
    project_dir: str,
    git_strategy: Optional[str] = "child",
    branch: Optional[str] = None,
    tag: Optional[str] = None,
    **kwargs,
) -> bool:
    """Create a minimal scitex project with writer and scholar workspaces.

    Parameters
    ----------
    project_dir : str
        Path to project directory (will be created).
    git_strategy : str, optional
        Git initialization strategy ('child', 'parent', 'origin', None).
    branch : str, optional
        Specific branch of the writer template to clone.
    tag : str, optional
        Specific tag/release of the writer template to clone.
    **kwargs
        Additional keyword arguments forwarded to writer ensure.

    Returns
    -------
    bool
        True if successful, False otherwise.
    """
    try:
        project_path = Path(project_dir)
        project_path.mkdir(parents=True, exist_ok=True)

        # Ensure writer workspace (full scitex-writer clone)
        from scitex.writer import ensure_workspace as ensure_writer

        ensure_writer(
            str(project_path),
            git_strategy=git_strategy,
            branch=branch,
            tag=tag,
            **kwargs,
        )

        # Ensure scholar workspace (directory scaffold)
        from scitex.scholar import ensure_workspace as ensure_scholar

        ensure_scholar(str(project_path))

        # Set up bibliography sharing symlink
        from ._scholar_writer_integration import ensure_integration

        ensure_integration(project_path)

        logger.info(f"Created scitex_minimal project at {project_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to create scitex_minimal project: {e}")
        return False


def main(args: list = None) -> None:
    """Command-line interface for clone_scitex_minimal."""
    if args is None:
        args = sys.argv[1:]

    if len(args) < 1:
        print("Usage: python -m scitex clone_scitex_minimal <project-dir>")
        print("")
        print("Creates a minimal scitex project with writer + scholar.")
        sys.exit(1)

    success = clone_scitex_minimal(args[0])
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

# EOF
