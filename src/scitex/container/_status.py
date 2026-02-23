#!/usr/bin/env python3
"""List available containers and their build status."""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime
from pathlib import Path

from ._utils import find_containers_dir

logger = logging.getLogger("scitex")


def status(containers_dir: str | Path | None = None) -> list[dict]:
    """List available containers and their status.

    Parameters
    ----------
    containers_dir : str or Path, optional
        Directory containing .def files. Auto-detected if not given.

    Returns
    -------
    list[dict]
        List of container info dicts with keys:
        name, def_path, sif_path, sif_size, sif_date,
        hash_current, hash_stored, needs_rebuild.
    """
    cdir = Path(containers_dir) if containers_dir else find_containers_dir()
    results = []

    for def_path in sorted(cdir.glob("*.def")):
        name = def_path.stem
        sif_path = def_path.with_suffix(".sif")
        hash_file = cdir / ".def-hash"

        current_hash = _hash_file(def_path)
        stored_hash = ""
        if hash_file.exists():
            stored_hash = hash_file.read_text().strip()

        info: dict = {
            "name": name,
            "def_path": str(def_path),
            "sif_path": str(sif_path) if sif_path.exists() else None,
            "sif_size": None,
            "sif_date": None,
            "hash_current": current_hash,
            "hash_stored": stored_hash or None,
            "needs_rebuild": True,
        }

        if sif_path.exists():
            stat = sif_path.stat()
            info["sif_size"] = _human_size(stat.st_size)
            info["sif_date"] = datetime.fromtimestamp(stat.st_mtime).strftime(
                "%Y-%m-%d %H:%M"
            )
            info["needs_rebuild"] = current_hash != stored_hash

        results.append(info)

    return results


def _hash_file(path: Path) -> str:
    """Compute SHA256 hash of a file."""
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _human_size(nbytes: int) -> str:
    """Convert bytes to human-readable size."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(nbytes) < 1024:
            return f"{nbytes:.1f} {unit}"
        nbytes /= 1024
    return f"{nbytes:.1f} PB"


# EOF
