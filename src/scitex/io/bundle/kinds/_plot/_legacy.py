#!/usr/bin/env python3
"""Legacy ``.plot`` directory-bundle dict-API.

This is the umbrella's dict-shaped CRUD over the legacy ``.plot/`` directory
layout. It pre-dates the figrecipe migration; figrecipe owns figure I/O
through ``.plt.zip`` / ``.fig.zip`` going forward (see
``GITIGNORED/tasks/RESUME.md``).

Kept here as umbrella-internal so the bundle dispatcher
(``scitex.io.bundle._core``) can still ``load()`` and ``save()`` legacy
``.plot/`` directories during the deprecation window. Sourced (verbatim
minus a dead ``embed_metadata`` codepath) from the retired
``scitex.plt.io._bundle`` module.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Dict, List

# Schema specification for ``.plot`` bundles. Kept for back-compat with any
# tool that introspected the umbrella's schema descriptor; not referenced by
# the dispatcher itself.
PLOT_SCHEMA_SPEC: Dict[str, Any] = {
    "name": "scitex.plt.plot",
    "version": "1.0.0",
    "required_fields": ["schema"],
    "optional_fields": [
        "backend",
        "plot_type",
        "data",
        "axes",
        "styles",
        "stats",
    ],
}


def load_plot_bundle(bundle_dir: Path) -> Dict[str, Any]:
    """Load ``.plot`` bundle contents from a directory.

    Parameters
    ----------
    bundle_dir : Path
        Path to the bundle directory.

    Returns
    -------
    dict
        ``{"spec": <dict or None>, "basename": <str>, "data": <DataFrame or str>?}``.
    """
    result: Dict[str, Any] = {}

    # Find the spec file (could be plot.json or {basename}.json).
    spec_file = None
    for f in bundle_dir.glob("*.json"):
        if not f.name.startswith("."):
            spec_file = f
            break

    if spec_file and spec_file.exists():
        with open(spec_file) as f:
            result["spec"] = json.load(f)
        result["basename"] = spec_file.stem
    else:
        result["spec"] = None
        result["basename"] = "plot"

    # Find and load CSV data (could be plot.csv or {basename}.csv).
    csv_file = None
    for f in bundle_dir.glob("*.csv"):
        if not f.name.startswith("."):
            csv_file = f
            break

    if csv_file and csv_file.exists():
        try:
            import pandas as pd

            result["data"] = pd.read_csv(csv_file)
        except ImportError:
            with open(csv_file) as f:
                result["data"] = f.read()

    return result


def save_plot_bundle(data: Dict[str, Any], dir_path: Path) -> None:
    """Save ``.plot`` bundle contents to a directory.

    Parameters
    ----------
    data : dict
        Bundle data dictionary. Recognised keys:

        - ``spec``: JSON specification
        - ``data``: CSV data (DataFrame or string)
        - ``basename``: base filename for exports (default ``"plot"``)
        - ``png`` / ``svg`` / ``pdf``: export blobs (bytes or path)
        - ``hitmap_png`` / ``hitmap_svg``: hitmap blobs (bytes or path)
    dir_path : Path
        Bundle directory.
    """
    basename = data.get("basename", "plot")

    # Save specification.
    spec = data.get("spec", {})
    spec_file = dir_path / f"{basename}.json"
    with open(spec_file, "w") as f:
        json.dump(spec, f, indent=2)

    # Save CSV data.
    if "data" in data:
        csv_file = dir_path / f"{basename}.csv"
        df = data["data"]
        if hasattr(df, "to_csv"):
            df.to_csv(csv_file, index=False)
        else:
            with open(csv_file, "w") as f:
                f.write(str(df))

    _save_exports(data, dir_path, basename)
    _save_hitmaps(data, dir_path, basename)

    # Generate overview (best-effort).
    try:
        from ._overview import generate_bundle_overview

        generate_bundle_overview(dir_path, spec, data, basename)
    except Exception as e:
        import logging

        logging.getLogger("scitex").debug(f"Could not generate overview: {e}")


def _save_exports(data: Dict[str, Any], dir_path: Path, basename: str = "plot") -> None:
    """Save export files (PNG, SVG, PDF). Metadata embedding has been retired
    (the upstream ``scitex.io._metadata`` module no longer exists).
    """
    for fmt in ("png", "svg", "pdf"):
        if fmt not in data:
            continue

        out_file = dir_path / f"{basename}.{fmt}"
        export_data = data[fmt]

        if isinstance(export_data, bytes):
            with open(out_file, "wb") as f:
                f.write(export_data)
        elif isinstance(export_data, (str, Path)) and Path(export_data).exists():
            shutil.copy(export_data, out_file)


def _save_hitmaps(data: Dict[str, Any], dir_path: Path, basename: str = "plot") -> None:
    """Save hitmap PNG and SVG files."""
    if "hitmap_png" in data:
        hitmap_file = dir_path / f"{basename}_hitmap.png"
        hitmap_data = data["hitmap_png"]
        if isinstance(hitmap_data, bytes):
            with open(hitmap_file, "wb") as f:
                f.write(hitmap_data)
        elif isinstance(hitmap_data, (str, Path)) and Path(hitmap_data).exists():
            shutil.copy(hitmap_data, hitmap_file)

    if "hitmap_svg" in data:
        hitmap_svg_file = dir_path / f"{basename}_hitmap.svg"
        hitmap_svg_data = data["hitmap_svg"]
        if isinstance(hitmap_svg_data, bytes):
            with open(hitmap_svg_file, "wb") as f:
                f.write(hitmap_svg_data)
        elif (
            isinstance(hitmap_svg_data, (str, Path)) and Path(hitmap_svg_data).exists()
        ):
            shutil.copy(hitmap_svg_data, hitmap_svg_file)


__all__: List[str] = [
    "PLOT_SCHEMA_SPEC",
    "load_plot_bundle",
    "save_plot_bundle",
]
