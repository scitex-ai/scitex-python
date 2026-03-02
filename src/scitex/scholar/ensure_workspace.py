#!/usr/bin/env python3
# Timestamp: 2026-02-17
# File: src/scitex/scholar/ensure.py

"""Ensure scholar workspace exists within a project."""

from pathlib import Path
from typing import Union

from scitex.logging import getLogger

logger = getLogger(__name__)

SCHOLAR_SUBDIRS = ["bib_files", "library", "prompts"]


def ensure_workspace(project_dir: Union[str, Path]) -> Path:
    """Ensure scholar workspace exists at {project_dir}/scitex/scholar/.

    Creates the directory scaffold with subdirectories for bibliography
    files, library storage, and prompt templates.

    Parameters
    ----------
    project_dir : str or Path
        Root project directory. Scholar workspace will be at
        ``{project_dir}/scitex/scholar/``.

    Returns
    -------
    pathlib.Path
        Path to the scholar workspace directory.
    """
    scholar_path = Path(project_dir) / "scitex" / "scholar"
    if scholar_path.exists() and any(scholar_path.iterdir()):
        return scholar_path

    for subdir in SCHOLAR_SUBDIRS:
        (scholar_path / subdir).mkdir(parents=True, exist_ok=True)

    logger.info(f"Created scholar workspace at {scholar_path}")
    return scholar_path


__all__ = ["ensure_workspace", "SCHOLAR_SUBDIRS"]

# EOF
