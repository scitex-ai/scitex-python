#!/usr/bin/env python3
"""Create Clew example pipeline in a target directory."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional


def _find_examples_dir() -> Optional[Path]:
    """Locate the bundled Clew examples directory.

    Tries multiple paths:
    1. Bundled with package: clew/_example_data/ (pip-installed)
    2. Docker mount: /scitex-python/examples/scitex/clew
    3. Source repo: ../../../../examples/scitex/clew
    """
    candidates = [
        Path(__file__).resolve().parent / "_example_data",
        Path("/scitex-python/examples/scitex/clew"),
        Path(__file__).resolve().parent.parent.parent.parent
        / "examples"
        / "scitex"
        / "clew",
    ]
    for candidate in candidates:
        if candidate.exists() and candidate.is_dir():
            return candidate
    return None


def init_examples(dest: str | Path, variant: str = "sequential") -> dict:
    """Copy Clew example scripts to a destination directory.

    Copies only the runnable scripts (.py, .sh) and README — not
    the output directories.  Users run ``00_run_all.sh`` themselves
    to generate outputs and populate the verification database.

    Parameters
    ----------
    dest : str or Path
        Destination directory.  Created if it does not exist.
        Existing script files are overwritten.
    variant : str, optional
        Example variant: "sequential" (default) or "multi_parent".

    Returns
    -------
    dict
        ``{"path": str, "files": list[str], "file_count": int, "variant": str}``

    Raises
    ------
    FileNotFoundError
        If the bundled examples cannot be located.
    ValueError
        If variant is not recognized.
    """
    valid_variants = ("sequential", "multi_parent")
    if variant not in valid_variants:
        raise ValueError(f"Unknown variant {variant!r}. Choose from: {valid_variants}")

    src_dir = _find_examples_dir()
    if src_dir is None:
        raise FileNotFoundError(
            "Clew example directory not found. "
            "Ensure scitex-python is installed with examples."
        )

    # For non-default variants, look in subdirectory
    if variant != "sequential":
        variant_dir = src_dir / variant
        if variant_dir.exists():
            src_dir = variant_dir
        else:
            raise FileNotFoundError(
                f"Example variant {variant!r} not found at {variant_dir}"
            )

    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)

    # Copy only scripts and docs, skip _out directories
    copied = []
    for src_file in sorted(src_dir.iterdir()):
        if src_file.is_dir():
            continue
        dst_file = dest / src_file.name
        shutil.copy2(src_file, dst_file)
        copied.append(src_file.name)

    return {
        "path": str(dest),
        "files": copied,
        "file_count": len(copied),
        "variant": variant,
    }


# EOF
