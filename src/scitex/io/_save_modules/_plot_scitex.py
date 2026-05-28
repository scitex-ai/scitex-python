#!/usr/bin/env python3
# Timestamp: 2025-12-19
# File: /home/ywatanabe/proj/scitex-code/src/scitex/io/_save_modules/_plot_scitex.py

"""Save matplotlib figures as SciTeX bundles (ZIP or directory) with plot content type."""

import json
import tempfile
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np


def _create_stx_spec(bundle_type, title, size):
    """Create a spec dictionary for .stx bundle.

    Parameters
    ----------
    bundle_type : str
        Type of bundle ('plot', 'figure', 'stats')
    title : str
        Title/name of the bundle
    size : dict
        Size info with width_mm, height_mm, dpi

    Returns
    -------
    dict
        Spec dictionary
    """
    return {
        "schema": {"name": f"scitex.{bundle_type}", "version": "1.0.0"},
        "id": f"{bundle_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        "type": bundle_type,
        "title": title,
        "size": size,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }


def _extract_data_from_figure(fig):
    """Extract plotted data from matplotlib figure lines.

    Returns DataFrame with x/y columns for each trace, or None if no data.
    """
    import pandas as pd

    extracted_data = {}
    axes_list = list(fig.axes) if hasattr(fig.axes, "__iter__") else [fig.axes]

    for ax_idx, ax in enumerate(axes_list):
        for line_idx, line in enumerate(ax.get_lines()):
            label = line.get_label()
            if label is None or label.startswith("_"):
                label = f"series_{line_idx}"

            xdata, ydata = line.get_data()
            if len(xdata) > 0:
                x_col = f"ax{ax_idx}_line{line_idx}_x"
                y_col = f"ax{ax_idx}_line{line_idx}_y"
                extracted_data[x_col] = np.array(xdata, dtype=float)
                extracted_data[y_col] = np.array(ydata, dtype=float)

    if not extracted_data:
        return None

    # Pad arrays to same length
    max_len = max(len(v) for v in extracted_data.values())
    padded = {}
    for k, v in extracted_data.items():
        if len(v) < max_len:
            padded[k] = np.pad(v, (0, max_len - len(v)), constant_values=np.nan)
        else:
            padded[k] = v

    return pd.DataFrame(padded)


def _build_encoding_from_figure(fig, csv_df):
    """Build encoding.json data from matplotlib figure.

    Encoding captures data→visual mappings for scientific reproducibility.
    """
    from scitex.schema import ENCODING_VERSION

    traces = []
    axes_list = list(fig.axes) if hasattr(fig.axes, "__iter__") else [fig.axes]

    for ax_idx, ax in enumerate(axes_list):
        for line_idx, line in enumerate(ax.get_lines()):
            label = line.get_label()
            if label is None or label.startswith("_"):
                label = f"line_{line_idx}"

            trace = {
                "trace_id": f"ax{ax_idx}_line{line_idx}",
                "bindings": [],
            }

            # X binding
            if csv_df is not None:
                x_col = f"ax{ax_idx}_line{line_idx}_x"
                y_col = f"ax{ax_idx}_line{line_idx}_y"
                if x_col in csv_df.columns:
                    trace["bindings"].append(
                        {
                            "channel": "x",
                            "column": x_col,
                            "scale": "linear",
                        }
                    )
                if y_col in csv_df.columns:
                    trace["bindings"].append(
                        {
                            "channel": "y",
                            "column": y_col,
                            "scale": "linear",
                        }
                    )

            if trace["bindings"]:
                traces.append(trace)

    return {
        "schema": {"name": "scitex.plt.encoding", "version": ENCODING_VERSION},
        "traces": traces,
    }


def _build_theme_from_figure(fig):
    """Build theme.json data from matplotlib figure.

    Theme captures pure aesthetics without affecting scientific meaning.
    """
    from scitex.schema import THEME_VERSION

    # Extract colors from figure
    fig_facecolor = fig.get_facecolor()
    axes_list = list(fig.axes) if hasattr(fig.axes, "__iter__") else [fig.axes]

    ax_facecolor = "white"
    if axes_list:
        try:
            ax_facecolor = axes_list[0].get_facecolor()
            if isinstance(ax_facecolor, (tuple, list)):
                ax_facecolor = f"#{int(ax_facecolor[0] * 255):02x}{int(ax_facecolor[1] * 255):02x}{int(ax_facecolor[2] * 255):02x}"
        except Exception:
            pass

    # Extract trace styles
    traces = []
    for ax_idx, ax in enumerate(axes_list):
        for line_idx, line in enumerate(ax.get_lines()):
            trace_style = {
                "trace_id": f"ax{ax_idx}_line{line_idx}",
            }
            try:
                color = line.get_color()
                if color:
                    trace_style["color"] = color
                lw = line.get_linewidth()
                if lw:
                    trace_style["linewidth"] = float(lw)
                ls = line.get_linestyle()
                if ls:
                    trace_style["linestyle"] = ls
                marker = line.get_marker()
                if marker and marker != "None":
                    trace_style["marker"] = marker
                ms = line.get_markersize()
                if ms:
                    trace_style["markersize"] = float(ms)
                alpha = line.get_alpha()
                if alpha is not None:
                    trace_style["alpha"] = float(alpha)
            except Exception:
                pass

            if len(trace_style) > 1:  # More than just trace_id
                traces.append(trace_style)

    return {
        "schema": {"name": "scitex.plt.theme", "version": THEME_VERSION},
        "colors": {
            "mode": "light",
            "background": "transparent",
            "axes_bg": ax_facecolor if isinstance(ax_facecolor, str) else "white",
        },
        "typography": {
            "family": "sans-serif",
            "size_pt": 7.0,
        },
        "traces": traces,
        "grid": False,
    }


def save_plot_as_scitex(obj, spath, as_zip=True, basename=None, **kwargs):
    """Save a matplotlib figure as a SciTeX bundle (ZIP or directory).

    Bundle structure:
        plot_name/              # or plot_name.zip (with plot_name/ inside)
            spec.json           # Bundle specification (WHAT to plot)
            encoding.json       # Data→visual mapping (scientific rigor)
            theme.json          # Pure aesthetics (colors, fonts)
            style.json          # Backward compat (encoding + theme merged)
            data/
                data.csv        # Plotted data (tidy format)
                data_info.json  # Column meanings, units, dtypes
            stats/
                stats.json      # Statistical test results (if any)
                stats.csv       # Tabular statistics
            cache/
                geometry_px.json        # Hit areas for GUI editing
                render_manifest.json    # Render metadata
                hitmap.png              # Hit testing image
                hitmap.svg              # Vector hit testing
            exports/
                plot.svg        # Vector export
                plot.png        # Raster export
                plot.pdf        # Publication export
    """
    import matplotlib.figure

    p = Path(spath)

    if basename is None:
        basename = p.stem

    # Extract figure
    fig = obj
    if hasattr(obj, "figure"):
        fig = obj.figure
    elif hasattr(obj, "fig"):
        fig = obj.fig

    if not isinstance(fig, matplotlib.figure.Figure):
        raise TypeError(f"Expected matplotlib Figure, got {type(obj).__name__}")

    dpi = kwargs.pop("dpi", 300)
    data = kwargs.pop("data", None)

    # Get CSV data from figure if not provided
    csv_df = data
    if csv_df is None:
        # CSV via AxisWrapper removed (figrecipe migration); fall back to matplotlib lines
        csv_df = _extract_data_from_figure(fig)

    # Create spec for .stx format
    fig_width_inch, fig_height_inch = fig.get_size_inches()

    spec = _create_stx_spec(
        bundle_type="plot",
        title=basename,
        size={
            "width_mm": round(fig_width_inch * 25.4, 2),
            "height_mm": round(fig_height_inch * 25.4, 2),
            "dpi": dpi,
        },
    )

    # Determine paths
    if as_zip:
        zip_path = p
        temp_dir = Path(tempfile.mkdtemp())
        bundle_dir = temp_dir / basename
    else:
        bundle_dir = p
        temp_dir = None

    bundle_dir.mkdir(parents=True, exist_ok=True)

    # Save spec.json
    with open(bundle_dir / "spec.json", "w") as f:
        json.dump(spec, f, indent=2, default=str)

    # Save style.json (empty default for backward compatibility)
    style_data = {}
    with open(bundle_dir / "style.json", "w") as f:
        json.dump(style_data, f, indent=2)

    # Save encoding.json (data→visual mapping for scientific rigor)
    encoding_data = _build_encoding_from_figure(fig, csv_df)
    with open(bundle_dir / "encoding.json", "w") as f:
        json.dump(encoding_data, f, indent=2)

    # Save theme.json (pure aesthetics)
    theme_data = _build_theme_from_figure(fig)
    with open(bundle_dir / "theme.json", "w") as f:
        json.dump(theme_data, f, indent=2)

    # Create directory structure
    data_dir = bundle_dir / "data"
    stats_dir = bundle_dir / "stats"
    cache_dir = bundle_dir / "cache"
    exports_dir = bundle_dir / "exports"

    data_dir.mkdir(exist_ok=True)
    stats_dir.mkdir(exist_ok=True)
    cache_dir.mkdir(exist_ok=True)
    exports_dir.mkdir(exist_ok=True)

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message=".*tight_layout.*")

        # Save exports with simple names (bundle dir provides context)
        fig.savefig(
            exports_dir / "plot.png",
            dpi=dpi,
            bbox_inches="tight",
            format="png",
            transparent=True,
        )

        fig.savefig(
            exports_dir / "plot.svg",
            bbox_inches="tight",
            format="svg",
        )

        fig.savefig(
            exports_dir / "plot.pdf",
            bbox_inches="tight",
            format="pdf",
        )

    # Save data/data.csv and data/meta.json if available
    if csv_df is not None:
        csv_df.to_csv(data_dir / "data.csv", index=False)

        # Generate metadata for the data
        meta = {
            "columns": list(csv_df.columns),
            "dtypes": {col: str(dtype) for col, dtype in csv_df.dtypes.items()},
            "shape": list(csv_df.shape),
            "description": "Plotted data (tidy format)",
        }
        with open(data_dir / "data_info.json", "w") as f:
            json.dump(meta, f, indent=2)

    # Save cache/geometry_px.json and hitmap images for GUI hit areas
    from ._plot_scitex_hitmap import save_hitmap_geometry_and_images

    save_hitmap_geometry_and_images(fig, cache_dir, dpi)

    # Save cache/render_manifest.json
    render_manifest = {
        "dpi": dpi,
        "format": ["png", "svg", "pdf"],
        "bbox_inches": "tight",
        "size_mm": {
            "width": round(fig_width_inch * 25.4, 2),
            "height": round(fig_height_inch * 25.4, 2),
        },
        "hitmap_png": "cache/hitmap.png",
        "hitmap_svg": "cache/hitmap.svg",
    }
    with open(cache_dir / "render_manifest.json", "w") as f:
        json.dump(render_manifest, f, indent=2)

    # Save stats/stats.json and stats.csv placeholder (empty by default)
    stats_data = {"comparisons": [], "tests": []}
    with open(stats_dir / "stats.json", "w") as f:
        json.dump(stats_data, f, indent=2)

    # Create stats.csv with header for tabular export
    import pandas as pd

    stats_df = pd.DataFrame(
        columns=[
            "test_type",
            "group1",
            "group2",
            "statistic",
            "p_value",
            "effect_size",
            "significant",
        ]
    )
    stats_df.to_csv(stats_dir / "stats.csv", index=False)

    # Generate README.md for self-documentation
    _generate_readme(bundle_dir, basename, spec, csv_df)

    # Pack to ZIP if requested
    if as_zip:
        import shutil
        import zipfile

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in bundle_dir.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(bundle_dir.parent)
                    zf.write(file_path, arcname)
        shutil.rmtree(temp_dir)


def _generate_readme(bundle_dir, basename, spec, csv_df):
    """Generate README.md for self-documentation."""
    from datetime import datetime

    readme_lines = [
        f"# {basename} SciTeX Bundle",
        "",
        "## Overview",
        "",
        f"- **Type**: {spec.get('type', 'plot')}",
        f"- **Created**: {datetime.now().isoformat()}",
        f"- **Bundle ID**: {spec.get('bundle_id', 'N/A')}",
        "",
        "## Structure",
        "",
        "```",
        f"{basename}/",
        "├── spec.json           # What to plot (data mapping)",
        "├── encoding.json       # Data→visual mapping (scientific rigor)",
        "├── theme.json          # Pure aesthetics (colors, fonts)",
        "├── style.json          # Backward compat (= encoding + theme)",
        "├── data/",
        "│   ├── data.csv        # Raw data",
        "│   └── data_info.json  # Column metadata",
        "├── stats/",
        "│   ├── stats.json      # Statistical results",
        "│   └── stats.csv       # Tabular statistics",
        "├── cache/",
        "│   ├── geometry_px.json    # Hit areas (regenerable)",
        "│   ├── render_manifest.json",
        "│   ├── hitmap.png      # Hit testing image",
        "│   └── hitmap.svg      # Vector hit testing",
        "└── exports/",
        "    ├── plot.png        # Raster export",
        "    ├── plot.svg        # Vector export",
        "    └── plot.pdf        # Publication export",
        "```",
        "",
    ]

    if csv_df is not None:
        readme_lines.extend(
            [
                "## Data Columns",
                "",
                "| Column | Type | Description |",
                "|--------|------|-------------|",
            ]
        )
        for col in csv_df.columns:
            dtype = str(csv_df[col].dtype)
            readme_lines.append(f"| {col} | {dtype} | - |")
        readme_lines.append("")

    readme_lines.extend(
        [
            "## Usage",
            "",
            "```python",
            "from scitex.io.bundle import Bundle",
            "",
            f'bundle = Bundle("{basename}.zip")  # or "{basename}/" directory',
            "bundle.show()  # Display",
            'bundle.export("output.png")  # Export',
            "```",
            "",
            "---",
            "*Generated by SciTeX*",
        ]
    )

    with open(bundle_dir / "README.md", "w") as f:
        f.write("\n".join(readme_lines))


# EOF
