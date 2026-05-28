#!/usr/bin/env python3
# Timestamp: 2026-01-07
# File: /home/ywatanabe/proj/scitex-code/src/scitex/io/bundle/_mpl_helpers.py

"""Matplotlib helper functions for bundle creation."""

import warnings
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from matplotlib.figure import Figure as MplFigure

    from .kinds._plot._dataclasses import Encoding, Theme


def _get_scitex_axes(fig: "MplFigure") -> Optional[Any]:
    """Legacy stub — AxisWrapper CSV export removed in figrecipe migration."""
    return None


def _simplify_csv_columns(csv_df: "Any") -> "Any":
    """CSV columns already use figrecipe-compatible format: r{row}c{col}_{caller}-{id}_{var}.

    This function is now a pass-through since the new format is already simple and consistent.
    Kept for backward compatibility with any code that calls it.
    """
    # New format r{row}c{col}_{caller}-{id}_{var} is already simple
    # No simplification needed
    return csv_df


def _build_encoding_from_csv_columns(csv_df: "Any") -> "Encoding":
    """Build encoding from CSV column names (simple or verbose format).

    Handles:
    1. Simple: x, y, trace_x, trace_y, ax0_0_trace_x
    2. Verbose: ax-row-{row}-col-{col}_trace-id-{id}_variable-{var}

    This ensures encoding references match actual data columns.
    """
    from .kinds._plot._dataclasses import ChannelEncoding, Encoding, TraceEncoding

    if csv_df is None or csv_df.empty:
        return Encoding(traces=[])

    from figrecipe._utils._csv_column_naming import parse_csv_column_name

    # Group columns by trace (for verbose format)
    trace_columns = {}  # {(ax_row, ax_col, trace_id): {variable: column_name}}

    for col in csv_df.columns:
        parsed = parse_csv_column_name(col)
        if parsed["valid"]:
            key = (parsed["ax_row"], parsed["ax_col"], parsed["trace_id"])
            if key not in trace_columns:
                trace_columns[key] = {}
            trace_columns[key][parsed["variable"]] = col

    # Build traces from verbose column names
    traces = []
    for (ax_row, ax_col, trace_id), variables in trace_columns.items():
        trace = TraceEncoding(
            trace_id=f"ax-row-{ax_row}-col-{ax_col}_trace-id-{trace_id}",
            x=ChannelEncoding(column=variables.get("x")) if "x" in variables else None,
            y=ChannelEncoding(column=variables.get("y")) if "y" in variables else None,
        )
        traces.append(trace)

    # If no verbose columns found, try simple column names
    if not traces:
        columns = list(csv_df.columns)
        # Check for common x/y patterns
        x_col = None
        y_col = None
        for col in columns:
            col_lower = col.lower()
            if col_lower in ("x", "time", "index"):
                x_col = col
            elif col_lower in ("y", "value", "values"):
                y_col = col
        # If no pattern match, use first two numeric columns
        if x_col is None or y_col is None:
            numeric_cols = csv_df.select_dtypes(include=["number"]).columns.tolist()
            if len(numeric_cols) >= 2:
                if x_col is None:
                    x_col = numeric_cols[0]
                if y_col is None:
                    y_col = (
                        numeric_cols[1] if numeric_cols[1] != x_col else numeric_cols[0]
                    )
            elif len(numeric_cols) == 1:
                if x_col is None:
                    x_col = numeric_cols[0]
                if y_col is None:
                    y_col = numeric_cols[0]

        if x_col and y_col:
            trace = TraceEncoding(
                trace_id="main",
                x=ChannelEncoding(column=x_col),
                y=ChannelEncoding(column=y_col),
            )
            traces.append(trace)

    return Encoding(traces=traces)


def validate_encoding_csv_link(encoding: "Encoding", csv_df: "Any") -> list:
    """Validate that encoding column references exist in CSV data.

    Args:
        encoding: Encoding object with trace definitions
        csv_df: DataFrame with CSV data

    Returns
    -------
        List of validation errors (empty if valid)
    """
    errors = []

    if csv_df is None or csv_df.empty:
        return errors

    csv_columns = set(csv_df.columns)

    for trace in encoding.traces:
        if trace.x and trace.x.column:
            if trace.x.column not in csv_columns:
                errors.append(f"Encoding references missing column: {trace.x.column}")
        if trace.y and trace.y.column:
            if trace.y.column not in csv_columns:
                errors.append(f"Encoding references missing column: {trace.y.column}")

    return errors


def extract_data_from_mpl_figure(fig: "MplFigure") -> Optional[Any]:
    """Extract plotted data from matplotlib figure.

    Uses scitex.plt tracking if available (supports all 60+ plot types),
    otherwise falls back to extracting from rendered figure.
    """
    import numpy as np
    import pandas as pd

    # Try scitex.plt tracking first (supports all plot types)
    scitex_ax = _get_scitex_axes(fig)
    if scitex_ax is not None:
        try:
            csv_df = scitex_ax.export_as_csv()
            if csv_df is not None and not csv_df.empty:
                return csv_df
        except Exception:
            pass

    # Fallback: extract from rendered figure (limited plot types)
    from figrecipe._hitmap import as_mpl_figure

    from ._extractors import extract_bar_data, extract_line_data, extract_scatter_data

    extracted_data = {}
    # Normalise figrecipe RecordingFigure -> matplotlib Figure so fig.axes is a
    # flat list of Axes (a RecordingFigure exposes a nested [[ax], ...] grid).
    fig = as_mpl_figure(fig)
    axes_list = list(fig.axes) if hasattr(fig.axes, "__iter__") else [fig.axes]

    for ax_idx, ax in enumerate(axes_list):
        extracted_data.update(extract_line_data(ax, ax_idx))
        extracted_data.update(extract_scatter_data(ax, ax_idx))
        extracted_data.update(extract_bar_data(ax, ax_idx))

    if not extracted_data:
        return None

    max_len = max(len(v) for v in extracted_data.values())
    padded = {}
    for k, v in extracted_data.items():
        if len(v) < max_len:
            padded[k] = np.pad(v, (0, max_len - len(v)), constant_values=np.nan)
        else:
            padded[k] = v

    return pd.DataFrame(padded)


def _build_encoding_from_history(
    history: dict, ax_row: int = 0, ax_col: int = 0
) -> "Encoding":
    """Build encoding from scitex.plt axes history.

    Converts tracking history to Encoding with column names matching
    the figrecipe-compatible CSV format: r{row}c{col}_{caller}-{id}_{var}

    Parameters
    ----------
    history : dict
        History dict: {trace_id: (trace_id, method, tracked_dict, kwargs)}
    ax_row : int
        Row position of axes in grid
    ax_col : int
        Column position of axes in grid

    Returns
    -------
    Encoding
        Encoding object with traces referencing CSV column names.
    """
    from figrecipe._utils._csv_column_naming import get_csv_column_name, sanitize_id

    from .kinds._plot._dataclasses import ChannelEncoding, Encoding, TraceEncoding

    traces = []

    # Track per-method counters for auto-generated IDs
    method_counters = {}

    for record_id, record in history.items():
        if not isinstance(record, tuple) or len(record) < 4:
            continue

        id_val, method, tracked_dict, kwargs = record

        # Extract user-provided id from kwargs if present
        user_id = kwargs.get("id") if kwargs else None

        # Determine trace_id: use user-provided id or auto-generate
        if user_id:
            trace_id = sanitize_id(user_id)
        else:
            # Auto-generate: per-method counter
            counter = method_counters.get(method, 0)
            method_counters[method] = counter + 1
            trace_id = str(counter)

        # Build column names using the new format
        x_col = get_csv_column_name("x", ax_row, ax_col, method, trace_id=trace_id)
        y_col = get_csv_column_name("y", ax_row, ax_col, method, trace_id=trace_id)

        # Create trace encoding
        trace = TraceEncoding(
            trace_id=f"{method}-{trace_id}",
            x=ChannelEncoding(column=x_col),
            y=ChannelEncoding(column=y_col),
        )
        traces.append(trace)

    return Encoding(traces=traces)


def build_encoding_from_mpl_figure(fig: "MplFigure") -> "Encoding":
    """Build encoding specification from matplotlib figure.

    Uses scitex.plt tracking if available (captures actual plot method),
    otherwise falls back to detecting from rendered figure.
    """
    from .kinds._plot._dataclasses import Encoding

    # Try scitex.plt tracking first (knows exact plot method)
    scitex_ax = _get_scitex_axes(fig)
    if scitex_ax is not None and hasattr(scitex_ax, "history") and scitex_ax.history:
        encoding = _build_encoding_from_history(scitex_ax.history)
        if encoding and encoding.traces:
            return encoding

    # Fallback: detect from rendered figure
    from figrecipe._hitmap import as_mpl_figure

    from ._extractors import build_bar_traces, build_line_traces, build_scatter_traces

    traces = []
    # Normalise figrecipe RecordingFigure -> matplotlib Figure (flat axes).
    fig = as_mpl_figure(fig)
    axes_list = list(fig.axes) if hasattr(fig.axes, "__iter__") else [fig.axes]

    for ax_idx, ax in enumerate(axes_list):
        traces.extend(build_line_traces(ax, ax_idx))
        traces.extend(build_scatter_traces(ax, ax_idx))
        traces.extend(build_bar_traces(ax, ax_idx))

    return Encoding(traces=traces)


def build_theme_from_mpl_figure(fig: "MplFigure") -> "Theme":
    """Build theme specification from matplotlib figure."""
    from .kinds._plot._dataclasses import Theme

    return Theme()


def extract_geometry_from_mpl_figure(fig: "MplFigure") -> dict:
    """Extract geometry data from matplotlib figure for hit testing."""
    try:
        from figrecipe._hitmap import (
            extract_path_data,
            extract_selectable_regions,
        )

        return {
            "path_data": extract_path_data(fig),
            "selectable_regions": extract_selectable_regions(fig),
        }
    except Exception:
        return {"elements": []}


def generate_hitmap_from_mpl_figure(fig: "MplFigure", dpi: int = 300) -> tuple:
    """Generate hitmap images from matplotlib figure."""
    try:
        import io

        from figrecipe._hitmap import (
            HITMAP_AXES_COLOR,
            HITMAP_BACKGROUND_COLOR,
            apply_hitmap_colors,
            as_mpl_figure,
            restore_original_colors,
        )

        # Normalise figrecipe RecordingFigure -> matplotlib Figure (flat axes).
        fig = as_mpl_figure(fig)
        axes_list = list(fig.axes) if hasattr(fig.axes, "__iter__") else [fig.axes]
        original_props, color_map, groups = apply_hitmap_colors(fig)

        saved_fig_facecolor = fig.patch.get_facecolor()
        saved_ax_facecolors = []
        for ax in axes_list:
            saved_ax_facecolors.append(ax.get_facecolor())
            ax.set_facecolor(HITMAP_BACKGROUND_COLOR)
            for spine in ax.spines.values():
                spine.set_color(HITMAP_AXES_COLOR)
        fig.patch.set_facecolor(HITMAP_BACKGROUND_COLOR)

        png_buf = io.BytesIO()
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message=".*tight_layout.*")
            fig.savefig(
                png_buf, format="png", dpi=dpi, facecolor=HITMAP_BACKGROUND_COLOR
            )
        png_bytes = png_buf.getvalue()

        svg_buf = io.BytesIO()
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message=".*tight_layout.*")
            fig.savefig(svg_buf, format="svg", facecolor=HITMAP_BACKGROUND_COLOR)
        svg_bytes = svg_buf.getvalue()

        restore_original_colors(original_props)
        fig.patch.set_facecolor(saved_fig_facecolor)
        for i, ax in enumerate(axes_list):
            ax.set_facecolor(saved_ax_facecolors[i])

        return png_bytes, svg_bytes
    except Exception:
        return None, None


def from_matplotlib(
    fig: "MplFigure",
    path,
    name: Optional[str] = None,
    csv_df: Optional[Any] = None,
    dpi: int = 300,
):
    """Create Bundle from matplotlib figure.

    Args:
        fig: Matplotlib figure object
        path: Output path for bundle (.zip or directory)
        name: Bundle name (defaults to path stem)
        csv_df: Pre-extracted CSV data (uses scitex.plt tracking if None)
        dpi: Resolution for raster exports

    Note:
        Encoding is built from CSV column names (single source of truth).
        This ensures encoding references always match actual data columns.
    """
    import io
    import json
    from pathlib import Path

    from ._Bundle import Bundle
    from ._saver import save_bundle_components

    path = Path(path)

    fig_width_inch, fig_height_inch = fig.get_size_inches()
    size_mm = {
        "width": round(fig_width_inch * 25.4, 2),
        "height": round(fig_height_inch * 25.4, 2),
    }

    bundle = Bundle(path, create=True, kind="plot", name=name, size_mm=size_mm)

    if csv_df is None:
        csv_df = extract_data_from_mpl_figure(fig)

    if csv_df is not None and not csv_df.empty:
        bundle._spec.payload_schema = "scitex.io.bundle.payload.plot@1"

    # Simplify CSV column names for bundle (figrecipe-style)
    # Converts: ax-row-0-col-0_trace-id-sine_variable-x → sine_x (or just x)
    if csv_df is not None and not csv_df.empty:
        csv_df = _simplify_csv_columns(csv_df)

    # Build encoding from actual CSV columns (single source of truth)
    # This ensures encoding references match real data columns
    if csv_df is not None and not csv_df.empty:
        bundle._encoding = _build_encoding_from_csv_columns(csv_df)
        # Validate encoding-CSV link
        errors = validate_encoding_csv_link(bundle._encoding, csv_df)
        if errors:
            warnings.warn(f"Encoding validation errors: {errors}")
    else:
        bundle._encoding = build_encoding_from_mpl_figure(fig)
    bundle._theme = build_theme_from_mpl_figure(fig)

    storage = bundle.storage

    if csv_df is not None and not csv_df.empty:
        csv_bytes = csv_df.to_csv(index=False).encode("utf-8")
        storage.write("payload/data.csv", csv_bytes)

        data_info = {
            "columns": list(csv_df.columns),
            "dtypes": {col: str(dtype) for col, dtype in csv_df.dtypes.items()},
            "shape": list(csv_df.shape),
        }
        storage.write(
            "canonical/data_info.json", json.dumps(data_info, indent=2).encode()
        )

    for fmt in ["png", "svg", "pdf"]:
        buf = io.BytesIO()
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message=".*tight_layout.*")
            fig.savefig(buf, format=fmt, dpi=dpi, bbox_inches="tight")
        storage.write(f"artifacts/exports/figure.{fmt}", buf.getvalue())

    geometry = extract_geometry_from_mpl_figure(fig)
    geometry["space"] = "figure_px"
    storage.write(
        "artifacts/cache/geometry_px.json", json.dumps(geometry, indent=2).encode()
    )

    hitmap_png, hitmap_svg = generate_hitmap_from_mpl_figure(fig, dpi)
    if hitmap_png:
        storage.write("artifacts/cache/hitmap.png", hitmap_png)
    if hitmap_svg:
        storage.write("artifacts/cache/hitmap.svg", hitmap_svg)

    manifest = {"dpi": dpi, "formats": ["png", "svg", "pdf"], "size_mm": size_mm}
    storage.write(
        "artifacts/cache/render_manifest.json", json.dumps(manifest, indent=2).encode()
    )

    save_bundle_components(
        path,
        node=bundle._node,
        encoding=bundle._encoding,
        theme=bundle._theme,
        render=False,
    )

    bundle._dirty = False
    return bundle


__all__ = [
    "extract_data_from_mpl_figure",
    "build_encoding_from_mpl_figure",
    "build_theme_from_mpl_figure",
    "extract_geometry_from_mpl_figure",
    "generate_hitmap_from_mpl_figure",
    "validate_encoding_csv_link",
    "from_matplotlib",
]

# EOF
