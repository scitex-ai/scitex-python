#!/usr/bin/env python3
# Timestamp: 2025-12-19
# File: /home/ywatanabe/proj/scitex-code/src/scitex/io/_save_modules/_plot_bundle.py

"""Save matplotlib figures as .plot bundles."""

import tempfile
from pathlib import Path

from scitex import logging

logger = logging.getLogger()


def save_plot_bundle(obj, spath, as_zip=False, data=None, layered=True, **kwargs):
    """Save a matplotlib figure as a .plot bundle.

    Bundle structure v2.0 (layered - default):
        plot.plot/
            spec.json           # Semantic: WHAT to plot (canonical)
            style.json          # Appearance: HOW it looks (canonical)
            data.csv            # Raw data (immutable)
            exports/            # PNG, SVG, hitmap
            cache/              # geometry_px.json, render_manifest.json

    Parameters
    ----------
    obj : matplotlib.figure.Figure
        The figure to save.
    spath : str or Path
        Output path (e.g., "plot.plot" or "plot.plot.zip").
    as_zip : bool
        If True, save as ZIP archive.
    data : pandas.DataFrame, optional
        Data to embed in the bundle as plot.csv.
    layered : bool
        If True (default), use new layered format (spec/style/geometry).
    **kwargs
        Additional arguments passed to savefig.
    """
    import shutil

    import matplotlib.figure

    p = Path(spath)

    # Extract basename from path
    basename = p.stem
    if basename.endswith(".plot"):
        basename = basename[:-5]
    elif basename.endswith(".zip"):
        basename = Path(basename).stem
        if basename.endswith(".plot"):
            basename = basename[:-5]

    # Extract figure from various matplotlib object types
    fig = obj
    if hasattr(obj, "figure"):
        fig = obj.figure
    elif hasattr(obj, "fig"):
        fig = obj.fig

    if not isinstance(fig, matplotlib.figure.Figure):
        raise TypeError(f"Expected matplotlib Figure, got {type(obj).__name__}")

    dpi = kwargs.pop("dpi", 300)

    # === Always use layered format ===
    # Determine bundle directory path
    if as_zip:
        temp_dir = Path(tempfile.mkdtemp())
        bundle_dir = temp_dir / f"{basename}.plot"
        zip_path = p if not str(p).endswith(".zip") else p
    else:
        bundle_dir = p if str(p).endswith(".plot") else Path(str(p) + ".plot")
        temp_dir = None

    # CSV via AxisWrapper removed (figrecipe migration); data passed explicitly or None
    csv_df = data

    from scitex.plt.io import save_layered_plot_bundle

    save_layered_plot_bundle(
        fig=fig,
        bundle_dir=bundle_dir,
        basename=basename,
        dpi=dpi,
        csv_df=csv_df,
    )

    # Compress to ZIP if requested
    if as_zip:
        import zipfile

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in bundle_dir.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(bundle_dir.parent)
                    zf.write(file_path, arcname)
        shutil.rmtree(temp_dir)


# EOF
