#!/usr/bin/env python3
"""Build Apptainer/Singularity SIF from .def file."""

from __future__ import annotations

import hashlib
import logging
import subprocess
from pathlib import Path

from ._utils import detect_container_cmd, find_containers_dir

logger = logging.getLogger("scitex")


def build(
    def_name: str = "scitex-cloud-shared-v0.1.0",
    output_dir: str | Path | None = None,
    force: bool = False,
) -> Path:
    """Build Apptainer/Singularity SIF from .def file.

    Parameters
    ----------
    def_name : str
        Name of the .def file (without extension).
    output_dir : str or Path, optional
        Directory for the output .sif file. Defaults to same dir as .def.
    force : bool
        Force rebuild even if .def is unchanged.

    Returns
    -------
    Path
        Path to the built .sif file.

    Raises
    ------
    FileNotFoundError
        If .def file or container command not found.
    RuntimeError
        If build fails.
    """
    cmd = detect_container_cmd()
    containers_dir = find_containers_dir()
    def_path = containers_dir / f"{def_name}.def"

    if not def_path.exists():
        raise FileNotFoundError(f"Definition file not found: {def_path}")

    out_dir = Path(output_dir) if output_dir else def_path.parent
    sif_path = out_dir / f"{def_name}.sif"
    hash_file = out_dir / ".def-hash"

    current_hash = _hash_file(def_path)

    if not force and sif_path.exists() and hash_file.exists():
        stored_hash = hash_file.read_text().strip()
        if current_hash == stored_hash:
            logger.info("SIF is up-to-date (hash: %s...)", current_hash[:12])
            return sif_path

    logger.info("Building %s from %s", sif_path.name, def_path.name)
    result = subprocess.run(
        ["sudo", cmd, "build", "--force", str(sif_path), str(def_path)],
        capture_output=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Build failed with exit code {result.returncode}")

    hash_file.write_text(current_hash + "\n")
    logger.info("Build complete: %s", sif_path)
    return sif_path


def _hash_file(path: Path) -> str:
    """Compute SHA256 hash of a file."""
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


# EOF
