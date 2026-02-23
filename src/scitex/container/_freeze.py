#!/usr/bin/env python3
"""Extract pinned versions from a built SIF for reproducibility."""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path

from ._utils import detect_container_cmd

logger = logging.getLogger("scitex")


def freeze(
    sif_path: str | Path,
    output_dir: str | Path | None = None,
) -> dict[str, Path]:
    """Extract pinned versions from a built SIF.

    Parameters
    ----------
    sif_path : str or Path
        Path to the .sif file.
    output_dir : str or Path, optional
        Directory for lock files. Defaults to same dir as .sif.

    Returns
    -------
    dict[str, Path]
        Mapping of lock file type to path: {pip, dpkg, node}.

    Raises
    ------
    FileNotFoundError
        If SIF file or container command not found.
    """
    sif_path = Path(sif_path)
    if not sif_path.exists():
        raise FileNotFoundError(f"SIF not found: {sif_path}")

    cmd = detect_container_cmd()
    out_dir = Path(output_dir) if output_dir else sif_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    lock_files = {}

    # pip freeze
    pip_lock = out_dir / "requirements-lock.txt"
    logger.info("Extracting pip freeze...")
    result = subprocess.run(
        [cmd, "exec", str(sif_path), "pip", "freeze"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        pip_lock.write_text(result.stdout)
        lock_files["pip"] = pip_lock

    # dpkg packages
    dpkg_lock = out_dir / "dpkg-lock.txt"
    logger.info("Extracting dpkg packages...")
    result = subprocess.run(
        [cmd, "exec", str(sif_path), "dpkg-query", "-W", "-f=${Package}=${Version}\n"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        dpkg_lock.write_text(result.stdout)
        lock_files["dpkg"] = dpkg_lock

    # npm global packages
    node_lock = out_dir / "node-lock.txt"
    logger.info("Extracting npm packages...")
    result = subprocess.run(
        [cmd, "exec", str(sif_path), "npm", "list", "-g", "--depth=0", "--json"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        node_lock.write_text(result.stdout)
        lock_files["node"] = node_lock

    logger.info("Freeze complete: %d lock files", len(lock_files))
    return lock_files


# EOF
