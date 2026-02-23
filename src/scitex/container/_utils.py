#!/usr/bin/env python3
"""Shared utilities for container management."""

from __future__ import annotations

import shutil
from pathlib import Path


def detect_container_cmd() -> str:
    """Detect apptainer or singularity command.

    Returns
    -------
    str
        The container command name ('apptainer' or 'singularity').

    Raises
    ------
    FileNotFoundError
        If neither command is found.
    """
    for cmd in ("apptainer", "singularity"):
        if shutil.which(cmd):
            return cmd
    raise FileNotFoundError(
        "Neither apptainer nor singularity is installed. "
        "Install with: sudo apt-get install apptainer"
    )


def find_containers_dir() -> Path:
    """Find the containers directory.

    Search order:
    1. ./containers/ (current working directory)
    2. Package-relative containers/ (scitex-python source tree)
    3. ~/.scitex/containers/ (user-managed)

    Returns
    -------
    Path
        Path to the containers directory.

    Raises
    ------
    FileNotFoundError
        If no containers directory is found.
    """
    # 1. Current working directory
    cwd_containers = Path.cwd() / "containers"
    if cwd_containers.is_dir() and list(cwd_containers.glob("*.def")):
        return cwd_containers

    # 2. Package-relative (scitex-python/containers/)
    pkg_root = Path(__file__).resolve().parents[3]  # src/scitex/container -> root
    pkg_containers = pkg_root / "containers"
    if pkg_containers.is_dir() and list(pkg_containers.glob("*.def")):
        return pkg_containers

    # 3. User-managed
    user_containers = Path.home() / ".scitex" / "containers"
    if user_containers.is_dir() and list(user_containers.glob("*.def")):
        return user_containers

    raise FileNotFoundError(
        "No containers directory found. Searched:\n"
        f"  - {cwd_containers}\n"
        f"  - {pkg_containers}\n"
        f"  - {user_containers}"
    )


# EOF
