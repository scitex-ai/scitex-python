#!/usr/bin/env python3
# Timestamp: "2026-02-17 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/template/_project/_directory_structure.py
"""Standard directory structure for SciTeX research projects."""

from pathlib import Path
from typing import Dict, List, Union

from scitex.logging import getLogger

logger = getLogger(__name__)

__all__ = ["PROJECT_STRUCTURE", "build_directory_tree"]

# Standard directory layout for scientific research projects.
PROJECT_STRUCTURE: Dict[str, Union[Dict, List]] = {
    "config": [],
    "data": [],
    "scripts": [],
    "docs": [],
    "results": [],
    "temp": [],
}


def build_directory_tree(
    project_dir: str,
    structure: Dict = None,
) -> None:
    """Create the standard project directory tree.

    Parameters
    ----------
    project_dir : str
        Project root directory (must already exist).
    structure : dict, optional
        Directory tree specification. Defaults to ``PROJECT_STRUCTURE``.

    Raises
    ------
    RuntimeError
        If a directory cannot be created.
    """
    if structure is None:
        structure = PROJECT_STRUCTURE

    root = Path(project_dir)

    for main_dir, sub_structure in structure.items():
        main_path = root / main_dir
        main_path.mkdir(parents=True, exist_ok=True)

        if isinstance(sub_structure, dict):
            for sub_dir, sub_sub_dirs in sub_structure.items():
                sub_path = main_path / sub_dir
                sub_path.mkdir(parents=True, exist_ok=True)
                for sub_sub_dir in sub_sub_dirs:
                    (sub_path / sub_sub_dir).mkdir(parents=True, exist_ok=True)
        elif isinstance(sub_structure, list):
            for sub_dir in sub_structure:
                (main_path / sub_dir).mkdir(parents=True, exist_ok=True)


# EOF
