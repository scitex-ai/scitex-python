#!/usr/bin/env python3
# Timestamp: 2026-05-28
# File: src/scitex/io/bundle/kinds/_plot/_proxy.py

"""Umbrella proxies that route `.plot` bundle I/O through figrecipe.

figrecipe owns figure I/O via `.plt.zip`/`.fig.zip`. The umbrella's
`scitex.io.bundle` surface still accepts a dict-shaped API, so these
thin proxies adapt between the two.

`load_plot_bundle` mirrors figrecipe.load_bundle (which handles both ZIP
and directory inputs) and returns the dict shape the umbrella callers
expect. `save_plot_bundle` writes a minimal directory bundle (spec JSON
+ optional CSV) — figrecipe's `save_bundle(fig, ...)` is figure-driven,
not dict-driven, so we cannot delegate the dict path through it.
"""

import json
import warnings
from pathlib import Path
from typing import Any, Dict

__all__ = ["load_plot_bundle", "save_plot_bundle"]


def load_plot_bundle(bundle_dir: Path) -> Dict[str, Any]:
    """Load a `.plot` bundle (directory) via figrecipe.

    Parameters
    ----------
    bundle_dir : Path
        Path to the bundle directory (or extracted-ZIP staging dir).

    Returns
    -------
    dict
        Dict with `spec`, `basename`, and (if present) `data`.
    """
    bundle_dir = Path(bundle_dir)

    # Legacy `.plot` directory shape gets a deprecation hint; figrecipe's
    # load_bundle still reads it via _load_from_directory.
    name = bundle_dir.name
    if name.endswith(".plot") and bundle_dir.is_dir():
        warnings.warn(
            "Loading the legacy `.plot` directory bundle. Use `.plt.zip` "
            "instead. The `.plot` directory format will be removed in a "
            "future release.",
            DeprecationWarning,
            stacklevel=2,
        )

    result: Dict[str, Any] = {"basename": "plot"}

    try:
        from figrecipe import load_bundle as _fr_load_bundle

        spec, _style, data = _fr_load_bundle(bundle_dir)
        result["spec"] = spec
        if data is not None:
            result["data"] = data
        return result
    except (ImportError, FileNotFoundError):
        # Fall through to legacy in-place reader below.
        pass

    # Legacy fallback: read first non-hidden .json + .csv from the dir.
    spec_file = next(
        (f for f in bundle_dir.glob("*.json") if not f.name.startswith(".")),
        None,
    )
    if spec_file is not None:
        with open(spec_file) as f:
            result["spec"] = json.load(f)
        result["basename"] = spec_file.stem
    else:
        result["spec"] = None

    csv_file = next(
        (f for f in bundle_dir.glob("*.csv") if not f.name.startswith(".")),
        None,
    )
    if csv_file is not None:
        try:
            import pandas as pd

            result["data"] = pd.read_csv(csv_file)
        except ImportError:
            with open(csv_file) as f:
                result["data"] = f.read()

    return result


def save_plot_bundle(data: Dict[str, Any], dir_path: Path) -> None:
    """Save a `.plot` bundle (directory) from a dict payload.

    The dict-driven save path predates figrecipe and is kept as a
    minimal in-place writer. Use `figrecipe.save_bundle(fig, ...)` for
    the figure-driven path.

    Parameters
    ----------
    data : dict
        Bundle payload (``spec``, ``data``, optional ``basename``,
        ``png``/``svg``/``pdf``).
    dir_path : Path
        Target bundle directory.
    """
    import shutil

    dir_path = Path(dir_path)
    basename = data.get("basename", "plot")

    spec = data.get("spec", {})
    with open(dir_path / f"{basename}.json", "w") as f:
        json.dump(spec, f, indent=2)

    if "data" in data and data["data"] is not None:
        csv_file = dir_path / f"{basename}.csv"
        df = data["data"]
        if hasattr(df, "to_csv"):
            df.to_csv(csv_file, index=False)
        else:
            with open(csv_file, "w") as f:
                f.write(str(df))

    for fmt in ("png", "svg", "pdf"):
        export_data = data.get(fmt)
        if export_data is None:
            continue
        out_file = dir_path / f"{basename}.{fmt}"
        if isinstance(export_data, bytes):
            with open(out_file, "wb") as f:
                f.write(export_data)
        elif isinstance(export_data, (str, Path)) and Path(export_data).exists():
            shutil.copy(export_data, out_file)


# EOF
