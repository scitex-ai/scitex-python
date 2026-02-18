#!/usr/bin/env python3
# Timestamp: "2025-11-19 13:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/plt/utils/_collect_figure_metadata.py

"""
Collect metadata from matplotlib figures for embedding in saved images.

This module provides utilities to automatically extract dimension, styling,
and configuration information from matplotlib figures and axes, making saved
figures self-documenting and reproducible.
"""

__FILE__ = __file__

from typing import Dict, List, Optional, Union

from scitex import logging

logger = logging.getLogger(__name__)

# Precision settings for JSON output
PRECISION = {
    "mm": 2,  # Millimeters: 0.01mm precision (10 microns)
    "inch": 3,  # Inches: 0.001 inch precision
    "position": 3,  # Normalized position: 0.001 precision
    "lim": 2,  # Axis limits: 2 decimal places
    "linewidth": 2,  # Line widths: 0.01 precision
}


class FixedFloat:
    """
    A float wrapper that preserves fixed decimal places in JSON output.

    Example: FixedFloat(0.25, 3) -> "0.250" in JSON
    """

    def __init__(self, value: float, precision: int):
        self.value = round(value, precision)
        self.precision = precision

    def __repr__(self):
        return f"{self.value:.{self.precision}f}"

    def __float__(self):
        return self.value


def _round_value(
    value: Union[float, int], precision: int, fixed: bool = False
) -> Union[float, int, "FixedFloat"]:
    """
    Round a single value to specified precision.

    Parameters
    ----------
    value : float or int
        Value to round
    precision : int
        Number of decimal places
    fixed : bool
        If True, return FixedFloat with fixed decimal places (e.g., 0.250)
        If False, return float (e.g., 0.25)
    """
    if isinstance(value, int):
        if fixed:
            return FixedFloat(float(value), precision)
        return value
    if isinstance(value, float):
        if fixed:
            return FixedFloat(value, precision)
        return round(value, precision)
    return value


def _round_list(values: List, precision: int, fixed: bool = False) -> List:
    """Round all values in a list."""
    return [_round_value(v, precision, fixed) for v in values]


def _round_dict(d: dict, precision_map: dict = None) -> dict:
    """
    Round all float values in a dict based on key-specific precision.

    Parameters
    ----------
    d : dict
        Dictionary to process
    precision_map : dict, optional
        Mapping of key patterns to precision values.
        Default uses PRECISION settings based on key names.
    """
    if precision_map is None:
        precision_map = {}

    result = {}
    for key, value in d.items():
        # Determine precision based on key name
        if "mm" in key.lower():
            prec = PRECISION["mm"]
        elif "inch" in key.lower():
            prec = PRECISION["inch"]
        elif "position" in key.lower() or key in ("left", "bottom", "right", "top"):
            prec = PRECISION["position"]
        elif "lim" in key.lower():
            prec = PRECISION["lim"]
        elif "width" in key.lower() and "line" in key.lower():
            prec = PRECISION["linewidth"]
        else:
            prec = precision_map.get(key, 3)  # Default 3 decimals

        if isinstance(value, dict):
            result[key] = _round_dict(value, precision_map)
        elif isinstance(value, list):
            result[key] = _round_list(value, prec)
        elif isinstance(value, float):
            result[key] = _round_value(value, prec)
        else:
            result[key] = value

    return result


def _collect_single_axes_metadata(fig, ax, ax_index: int) -> dict:
    """
    Collect metadata for a single axes object.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The parent figure
    ax : matplotlib.axes.Axes
        The axes to collect metadata from
    ax_index : int
        Index of this axes in the figure (for position tracking)

    Returns
    -------
    dict
        Metadata dictionary for this axes containing:
        - size_mm, size_inch, size_px
        - position_ratio
        - position_in_grid
        - margins_mm, margins_inch
        - bbox_mm, bbox_inch, bbox_px
        - x_axis_bottom, y_axis_left (axis info)
    """
    ax_metadata = {}

    try:
        from ._figure_from_axes_mm import get_dimension_info

        dim_info = get_dimension_info(fig, ax)

        # Size in multiple units
        ax_metadata["size_mm"] = dim_info.get("axes_size_mm", [])
        if "axes_size_inch" in dim_info:
            ax_metadata["size_inch"] = dim_info["axes_size_inch"]
        if "axes_size_px" in dim_info:
            ax_metadata["size_px"] = dim_info["axes_size_px"]

        # Position in figure coordinates (normalized 0-1 values)
        # Uses matplotlib terminology: bounds_figure_fraction
        if "axes_position" in dim_info:
            ax_metadata["bounds_figure_fraction"] = list(dim_info["axes_position"])

        # Position in grid (row, col)
        if (
            hasattr(ax, "_scitex_metadata")
            and "position_in_grid" in ax._scitex_metadata
        ):
            ax_metadata["position_in_grid"] = ax._scitex_metadata["position_in_grid"]
        else:
            # Calculate from ax_index if we have grid info
            ax_metadata["position_in_grid"] = [ax_index, 0]  # Default single column

        # Margins in mm and inch
        if "margins_mm" in dim_info:
            ax_metadata["margins_mm"] = dim_info["margins_mm"]
        if "margins_inch" in dim_info:
            ax_metadata["margins_inch"] = dim_info["margins_inch"]

        # Bounding box with intuitive keys
        if "axes_bbox_px" in dim_info:
            bbox = dim_info["axes_bbox_px"]
            # Convert from x0/y0/x1/y1 to x_left/y_bottom/x_right/y_top
            ax_metadata["bbox_px"] = {
                "x_left": bbox.get("x0", bbox.get("x_left", 0)),
                "x_right": bbox.get("x1", bbox.get("x_right", 0)),
                "y_top": bbox.get("y0", bbox.get("y_top", 0)),
                "y_bottom": bbox.get("y1", bbox.get("y_bottom", 0)),
                "width": bbox.get("width", 0),
                "height": bbox.get("height", 0),
            }
        if "axes_bbox_mm" in dim_info:
            bbox = dim_info["axes_bbox_mm"]
            ax_metadata["bbox_mm"] = {
                "x_left": bbox.get("x0", bbox.get("x_left", 0)),
                "x_right": bbox.get("x1", bbox.get("x_right", 0)),
                "y_top": bbox.get("y0", bbox.get("y_top", 0)),
                "y_bottom": bbox.get("y1", bbox.get("y_bottom", 0)),
                "width": bbox.get("width", 0),
                "height": bbox.get("height", 0),
            }
        if "axes_bbox_inch" in dim_info:
            bbox = dim_info["axes_bbox_inch"]
            ax_metadata["bbox_inch"] = {
                "x_left": bbox.get("x0", bbox.get("x_left", 0)),
                "x_right": bbox.get("x1", bbox.get("x_right", 0)),
                "y_top": bbox.get("y0", bbox.get("y_top", 0)),
                "y_bottom": bbox.get("y1", bbox.get("y_bottom", 0)),
                "width": bbox.get("width", 0),
                "height": bbox.get("height", 0),
            }

    except Exception as e:
        logger.warning(f"Could not extract dimension info for axes {ax_index}: {e}")

    # Extract axes labels and units
    # X-axis - using matplotlib terminology (xaxis)
    xlabel = ax.get_xlabel()
    x_label, x_unit = _parse_label_unit(xlabel)
    ax_metadata["xaxis"] = {
        "label": x_label,
        "unit": x_unit,
        "scale": ax.get_xscale(),
        "lim": list(ax.get_xlim()),
    }

    # Y-axis - using matplotlib terminology (yaxis)
    ylabel = ax.get_ylabel()
    y_label, y_unit = _parse_label_unit(ylabel)
    ax_metadata["yaxis"] = {
        "label": y_label,
        "unit": y_unit,
        "scale": ax.get_yscale(),
        "lim": list(ax.get_ylim()),
    }

    return ax_metadata


def _restructure_style(flat_style: dict) -> dict:
    """
    Restructure flat style_mm dict into hierarchical structure with explicit scopes.

    Converts:
        {"axis_thickness_mm": 0.2, "tick_length_mm": 0.8, ...}
    To:
        {
            "global": {"fonts": {...}, "padding": {...}},
            "axes_default": {"axes": {...}, "ticks": {...}},
            "artist_default": {"lines": {...}, "markers": {...}}
        }

    Style scopes:
    - global: rcParams-like settings (fonts, padding) applied to entire figure
    - axes_default: default axes appearance (can be overridden per-axes)
    - artist_default: default artist appearance (can be overridden per-artist)
    """
    result = {
        "global": {
            "fonts": {},
            "padding": {},
        },
        "axes_default": {
            "axes": {},
            "ticks": {},
        },
        "artist_default": {
            "lines": {},
            "markers": {},
        },
    }

    # Mapping from flat keys to hierarchical structure (scope, category, key)
    key_mapping = {
        # Axes-level defaults
        "axis_thickness_mm": ("axes_default", "axes", "thickness_mm"),
        "axes_thickness_mm": ("axes_default", "axes", "thickness_mm"),
        "tick_length_mm": ("axes_default", "ticks", "length_mm"),
        "tick_thickness_mm": ("axes_default", "ticks", "thickness_mm"),
        "n_ticks": ("axes_default", "ticks", "n_ticks"),
        # Artist-level defaults (Line2D, markers)
        "trace_thickness_mm": ("artist_default", "lines", "thickness_mm"),
        "line_thickness_mm": ("artist_default", "lines", "thickness_mm"),
        "marker_size_mm": ("artist_default", "markers", "size_mm"),
        "scatter_size_mm": ("artist_default", "markers", "scatter_size_mm"),
        # Global defaults (rcParams-like)
        "font_family": ("global", "fonts", "family"),
        "font_family_requested": ("global", "fonts", "family_requested"),
        "font_family_actual": ("global", "fonts", "family_actual"),
        "axis_font_size_pt": ("global", "fonts", "axis_size_pt"),
        "tick_font_size_pt": ("global", "fonts", "tick_size_pt"),
        "title_font_size_pt": ("global", "fonts", "title_size_pt"),
        "legend_font_size_pt": ("global", "fonts", "legend_size_pt"),
        "suptitle_font_size_pt": ("global", "fonts", "suptitle_size_pt"),
        "annotation_font_size_pt": ("global", "fonts", "annotation_size_pt"),
        "label_pad_pt": ("global", "padding", "label_pt"),
        "tick_pad_pt": ("global", "padding", "tick_pt"),
        "title_pad_pt": ("global", "padding", "title_pt"),
    }

    for key, value in flat_style.items():
        if key in key_mapping:
            scope, category, new_key = key_mapping[key]
            result[scope][category][new_key] = value
        else:
            # Unknown keys go to a misc section or are kept at top level
            # For now, skip unknown keys to keep structure clean
            pass

    # Remove empty categories within each scope
    for scope in list(result.keys()):
        result[scope] = {k: v for k, v in result[scope].items() if v}
        # Remove empty scopes
        if not result[scope]:
            del result[scope]

    return result


def collect_figure_metadata(fig, ax=None) -> Dict:
    """
    Collect all metadata from figure and axes for embedding in saved images.

    This function automatically extracts:
    - Software versions (scitex, matplotlib)
    - Timestamp
    - Figure UUID (unique identifier)
    - Figure/axes dimensions (mm, inch, px)
    - DPI settings
    - Margins
    - Styling parameters (if available)
    - Mode (display/publication)
    - Creation method
    - Plot type and axes information

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to collect metadata from
    ax : matplotlib.axes.Axes, optional
        Primary axes to collect dimension info from.
        If not provided, uses first axes in figure.

    Returns
    -------
    dict
        Complete metadata dictionary ready for embedding via scitex.io.embed_metadata()

    Examples
    --------
    >>> from scitex.plt.utils import create_axes_with_size_mm, collect_figure_metadata
    >>> fig, ax = create_axes_with_size_mm(30, 21, mode='publication')
    >>> ax.plot(x, y)
    >>> metadata = collect_figure_metadata(fig, ax)
    >>> print(metadata['dimensions']['axes_size_mm'])
    (30.0, 21.0)

    Notes
    -----
    This function is automatically called by FigWrapper.savefig() when
    embed_metadata=True (the default). You typically don't need to call it manually.

    The collected metadata enables:
    - Reproducing exact figure dimensions later
    - Matching styling across multiple figures
    - Documenting figure provenance
    - Debugging dimension/DPI issues
    """
    import datetime
    import uuid

    import matplotlib

    import scitex

    # Base metadata with cleaner structure:
    # - runtime: software/creation info
    # - figure: figure-level properties
    # - axes: axes-level properties
    # - style: styling parameters
    # - plot: plot content (title, type, traces, legend)
    # - data: CSV linkage (path, hash, columns)
    metadata = {
        "scitex_schema": "scitex.plt.figure",
        "scitex_schema_version": "0.1.0",
        "figure_uuid": str(uuid.uuid4()),
        "runtime": {
            "scitex_version": scitex.__version__,
            "matplotlib_version": matplotlib.__version__,
            "created_at": datetime.datetime.now().isoformat(),
        },
    }

    # Collect all axes from figure
    # Keep AxisWrappers for metadata access, but also track grid shape
    all_axes = []  # List of (ax_wrapper_or_mpl, row, col) tuples
    grid_shape = (1, 1)  # Default single axes

    if ax is not None:
        # Handle AxesWrapper (multi-axes) - extract individual AxisWrappers with positions
        if hasattr(ax, "_axes_scitex"):
            import numpy as np

            axes_array = ax._axes_scitex
            if isinstance(axes_array, np.ndarray):
                grid_shape = axes_array.shape
                for idx, ax_item in enumerate(axes_array.flat):
                    row = idx // grid_shape[1]
                    col = idx % grid_shape[1]
                    all_axes.append((ax_item, row, col))
            else:
                all_axes = [(axes_array, 0, 0)]
        # Handle AxisWrapper (single axes)
        elif hasattr(ax, "_axis_mpl"):
            all_axes = [(ax, 0, 0)]
        else:
            # Assume it's a matplotlib axes
            all_axes = [(ax, 0, 0)]
    elif hasattr(fig, "axes") and len(fig.axes) > 0:
        # Fallback to figure axes (linear indexing)
        for idx, ax_item in enumerate(fig.axes):
            all_axes.append((ax_item, 0, idx))

    # Helper to unwrap AxisWrapper to matplotlib axes
    def _unwrap_ax(ax_item):
        if hasattr(ax_item, "_axis_mpl"):
            return ax_item._axis_mpl
        return ax_item

    # Add figure-level properties (extracted from first axes for figure dimensions)
    if all_axes:
        try:
            from ._figure_from_axes_mm import get_dimension_info

            first_ax_tuple = all_axes[0]
            first_ax_mpl = _unwrap_ax(first_ax_tuple[0])
            dim_info = get_dimension_info(fig, first_ax_mpl)

            metadata["figure"] = {
                "size_mm": dim_info["figure_size_mm"],
                "size_inch": dim_info["figure_size_inch"],
                "size_px": dim_info["figure_size_px"],
                "dpi": dim_info["dpi"],
            }

            # Add top-level axes_bbox_px for easy access by canvas/web editors
            # Uses x0/y0/x1/y1 format (origin at top-left for web compatibility)
            # x0: left edge (Y-axis position), y1: bottom edge (X-axis position)
            if "axes_bbox_px" in dim_info:
                metadata["axes_bbox_px"] = dim_info["axes_bbox_px"]
            if "axes_bbox_mm" in dim_info:
                metadata["axes_bbox_mm"] = dim_info["axes_bbox_mm"]
        except Exception as e:
            logger.warning(f"Could not extract figure dimension info: {e}")

    # Collect per-axes metadata
    if all_axes:
        metadata["axes"] = {}
        for ax_item, row, col in all_axes:
            # Use row-col format: ax_00, ax_01, ax_10, ax_11 for 2x2 grid
            ax_key = f"ax_{row}{col}"
            try:
                ax_mpl = _unwrap_ax(ax_item)
                ax_metadata = _collect_single_axes_metadata(
                    fig, ax_mpl, row * grid_shape[1] + col
                )
                if ax_metadata:
                    # Add grid position info
                    ax_metadata["grid_position"] = {"row": row, "col": col}
                    metadata["axes"][ax_key] = ax_metadata
            except Exception as e:
                logger.warning(f"Could not extract metadata for {ax_key}: {e}")

    # Add scitex-specific metadata if axes was tagged
    scitex_meta = None
    if ax is not None and hasattr(ax, "_scitex_metadata"):
        scitex_meta = ax._scitex_metadata
    elif hasattr(fig, "_scitex_metadata"):
        scitex_meta = fig._scitex_metadata

    if scitex_meta:
        # Extract stats separately for top-level access
        if "stats" in scitex_meta:
            stats_list = scitex_meta["stats"]
            # Determine first_ax_key from axes metadata
            first_ax_key = None
            if "axes" in metadata and metadata["axes"]:
                first_ax_key = next(iter(metadata["axes"].keys()), None)
            # Add plot_id and ax_id to each stats entry if not present
            for stat in stats_list:
                if isinstance(stat, dict):
                    # Try to get plot info from metadata
                    if stat.get("plot_id") is None:
                        if "plot" in metadata and "ax_id" in metadata["plot"]:
                            stat["plot_id"] = metadata["plot"]["ax_id"]
                        elif first_ax_key:
                            stat["plot_id"] = first_ax_key
                    if "ax_id" not in stat and first_ax_key:
                        stat["ax_id"] = first_ax_key
            metadata["stats"] = stats_list

        # Extract style_mm to dedicated "style" section with hierarchical structure
        if "style_mm" in scitex_meta:
            metadata["style"] = _restructure_style(scitex_meta["style_mm"])

        # Extract mode to figure section
        if "mode" in scitex_meta:
            if "figure" not in metadata:
                metadata["figure"] = {}
            metadata["figure"]["mode"] = scitex_meta["mode"]

        # Extract created_with to runtime section
        if "created_with" in scitex_meta:
            metadata["runtime"]["created_with"] = scitex_meta["created_with"]

        # Note: axes_size_mm and position_in_grid are now handled per-axes
        # in _collect_single_axes_metadata() and stored under axes.ax_00, axes.ax_01, etc.

    # Add actual font information
    try:
        from ._get_actual_font import get_actual_font_name

        actual_font = get_actual_font_name()

        # Store both requested and actual font in style.global.fonts section
        if "style" in metadata:
            # Ensure global.fonts section exists
            if "global" not in metadata["style"]:
                metadata["style"]["global"] = {}
            if "fonts" not in metadata["style"]["global"]:
                metadata["style"]["global"]["fonts"] = {}

            # Get requested font from global.fonts.family or default to Arial
            requested_font = metadata["style"]["global"]["fonts"].get("family", "Arial")
            # Remove redundant family - keep only family_requested and family_actual
            if "family" in metadata["style"]["global"]["fonts"]:
                del metadata["style"]["global"]["fonts"]["family"]
            metadata["style"]["global"]["fonts"]["family_requested"] = requested_font
            metadata["style"]["global"]["fonts"]["family_actual"] = actual_font

            # Warn if requested and actual fonts differ
            if requested_font != actual_font:
                try:
                    from scitex.logging import getLogger

                    logger = getLogger(__name__)
                    logger.warning(
                        f"Font mismatch: Requested '{requested_font}' but using '{actual_font}'. "
                        f"For {requested_font}: sudo apt-get install ttf-mscorefonts-installer && fc-cache -fv"
                    )
                except ImportError:
                    logger.warning(
                        f"Font mismatch: Requested '{requested_font}' but using '{actual_font}'"
                    )
        else:
            # If no style section, add font info to runtime section
            metadata["runtime"]["font_family_actual"] = actual_font
    except Exception:
        # If font detection fails, continue without it
        pass

    # Extract plot content and axes labels
    # For multi-axes figures, we need to handle AxesWrapper specially
    primary_ax = ax
    if ax is not None:
        # Handle AxesWrapper (multi-axes) - use first axis for primary plot info
        if hasattr(ax, "_axes_scitex"):
            import numpy as np

            axes_array = ax._axes_scitex
            if isinstance(axes_array, np.ndarray) and axes_array.size > 0:
                primary_ax = axes_array.flat[0]
            else:
                primary_ax = axes_array

    if primary_ax is not None:
        try:
            # Try to get scitex AxisWrapper for history access
            # This is needed because matplotlib axes don't have the tracking history
            ax_for_history = primary_ax

            # If ax is a raw matplotlib axes, try to find the scitex wrapper
            if not hasattr(primary_ax, "history"):
                # Check if primary_ax has a scitex wrapper stored on it
                if hasattr(primary_ax, "_scitex_wrapper"):
                    ax_for_history = primary_ax._scitex_wrapper
                # Check if figure has scitex axes reference
                elif hasattr(fig, "axes") and hasattr(fig.axes, "history"):
                    ax_for_history = fig.axes
                # Check for FigWrapper's axes attribute
                elif hasattr(fig, "_fig_scitex") and hasattr(fig._fig_scitex, "axes"):
                    ax_for_history = fig._fig_scitex.axes
                # Check if the figure object itself has scitex_axes
                elif hasattr(fig, "_scitex_axes"):
                    ax_for_history = fig._scitex_axes

            # Add n_ticks to axes metadata if available from style
            if (
                "style" in metadata
                and "ticks" in metadata["style"]
                and "n_ticks" in metadata["style"]["ticks"]
            ):
                n_ticks = metadata["style"]["ticks"]["n_ticks"]
                # Add n_ticks to each axes' axis info
                if "axes" in metadata:
                    for ax_key in metadata["axes"]:
                        ax_data = metadata["axes"][ax_key]
                        if "xaxis" in ax_data:
                            ax_data["xaxis"]["n_ticks"] = n_ticks
                        if "yaxis" in ax_data:
                            ax_data["yaxis"]["n_ticks"] = n_ticks

            # Initialize plot section for plot content
            plot_info = {}

            # Add ax_id to match the axes key in metadata["axes"]
            # This links plot info to the corresponding axes entry
            ax_row, ax_col = 0, 0  # Default for single axes
            if (
                hasattr(primary_ax, "_scitex_metadata")
                and "position_in_grid" in primary_ax._scitex_metadata
            ):
                pos = primary_ax._scitex_metadata["position_in_grid"]
                ax_row, ax_col = pos[0], pos[1]
            # Use same format as axes keys: ax_00, ax_01, etc.
            plot_info["ax_id"] = (
                f"ax_{ax_row:02d}"
                if ax_row == ax_col == 0
                else f"ax_{ax_row * 10 + ax_col:02d}"
            )

            # Extract title - use underlying matplotlib axes if needed
            ax_mpl = (
                primary_ax._axis_mpl if hasattr(primary_ax, "_axis_mpl") else primary_ax
            )
            title = ax_mpl.get_title()
            if title:
                plot_info["title"] = title

            # Detect plot type and method from axes history or lines
            # Use ax_for_history which has the scitex history if available
            plot_type, method = _detect_plot_type(ax_for_history)
            if plot_type:
                plot_info["type"] = plot_type
            if method:
                plot_info["method"] = method

            # Extract style preset if available
            if (
                hasattr(primary_ax, "_scitex_metadata")
                and "style_preset" in primary_ax._scitex_metadata
            ):
                if "style" not in metadata:
                    metadata["style"] = {}
                metadata["style"]["preset"] = primary_ax._scitex_metadata[
                    "style_preset"
                ]
            elif (
                hasattr(fig, "_scitex_metadata")
                and "style_preset" in fig._scitex_metadata
            ):
                if "style" not in metadata:
                    metadata["style"] = {}
                metadata["style"]["preset"] = fig._scitex_metadata["style_preset"]

            # Extract artists and legend - add to axes section (matplotlib terminology)
            # Artists and legend belong to axes, not a separate plot section
            ax_row, ax_col = 0, 0
            if (
                hasattr(primary_ax, "_scitex_metadata")
                and "position_in_grid" in primary_ax._scitex_metadata
            ):
                pos = primary_ax._scitex_metadata["position_in_grid"]
                ax_row, ax_col = pos[0], pos[1]
            ax_key = (
                f"ax_{ax_row:02d}"
                if ax_row == ax_col == 0
                else f"ax_{ax_row * 10 + ax_col:02d}"
            )

            if "axes" in metadata and ax_key in metadata["axes"]:
                # Add artists to axes
                artists = _extract_artists(primary_ax)
                if artists:
                    metadata["axes"][ax_key]["artists"] = artists

                # Add legend to axes
                legend_info = _extract_legend_info(primary_ax)
                if legend_info:
                    metadata["axes"][ax_key]["legend"] = legend_info

            # Add plot section if we have content
            if plot_info:
                metadata["plot"] = plot_info

            # Data section for CSV linkage
            # Note: Per-trace column mappings are in plot.traces[i].csv_columns
            # This section provides:
            # - csv_hash: for verifying data integrity
            # - csv_path: path to CSV file (added by _save.py)
            # - columns_actual: actual column names in CSV (added by _save.py after export)
            data_info = {}

            # Compute CSV data hash for reproducibility verification
            csv_hash = _compute_csv_hash(ax_for_history)
            if csv_hash:
                data_info["csv_hash"] = csv_hash

            # csv_path and columns_actual will be added by _save.py after actual CSV export
            # This ensures single source of truth - actual columns, not predictions

            # Add data section if we have content
            if data_info:
                metadata["data"] = data_info

        except Exception as e:
            # If Phase 1 extraction fails, continue without it
            logger.warning(f"Could not extract Phase 1 metadata: {e}")

    # Apply precision rounding to all numeric values
    metadata = _round_metadata(metadata)

    return metadata


def _round_metadata(metadata: dict) -> dict:
    """
    Apply appropriate precision rounding to all numeric values in metadata.

    Precision rules:
    - mm values: 2 decimal places (0.01mm = 10 microns)
    - inch values: 3 decimal places
    - position values: 3 decimal places
    - axis limits: 2 decimal places
    - linewidth: 2 decimal places
    - px values: integers (no decimals)
    """
    result = {}

    for key, value in metadata.items():
        if key in ("scitex_schema", "scitex_schema_version", "figure_uuid"):
            # String fields - no rounding
            result[key] = value
        elif key == "runtime":
            # Runtime section - no numeric values to round
            result[key] = value
        elif key == "figure":
            result[key] = _round_figure_section(value)
        elif key == "axes":
            result[key] = _round_axes_section(value)
        elif key == "style":
            result[key] = _round_style_section(value)
        elif key == "plot":
            result[key] = _round_plot_section(value)
        elif key == "data":
            # Data section - no numeric values to round (hashes, paths, column names)
            result[key] = value
        elif key == "stats":
            # Stats section - preserve precision for statistical values
            result[key] = value
        else:
            result[key] = value

    return result


def _round_figure_section(fig_data: dict) -> dict:
    """Round values in figure section."""
    result = {}
    for key, value in fig_data.items():
        if key == "size_mm":
            # Fixed 2 decimals for mm: [80.00, 68.00]
            result[key] = _round_list(value, PRECISION["mm"], fixed=True)
        elif key == "size_inch":
            # Fixed 3 decimals for inch: [3.150, 2.677]
            result[key] = _round_list(value, PRECISION["inch"], fixed=True)
        elif key == "size_px":
            result[key] = [int(v) for v in value]  # Pixels are integers
        elif key == "dpi":
            result[key] = int(value)
        else:
            result[key] = value
    return result


def _round_axes_section(axes_data: dict) -> dict:
    """Round values in axes section.

    Handles both flat structure (legacy) and nested structure (ax_00, ax_01, ...).
    """
    result = {}
    for key, value in axes_data.items():
        # Check if this is a nested axes key (ax_00, ax_01, etc.)
        if key.startswith("ax_") and isinstance(value, dict):
            # Recursively round the nested axes data
            result[key] = _round_single_axes_data(value)
        else:
            # Handle flat structure (legacy) or non-axes keys
            result[key] = _round_single_axes_data({key: value}).get(key, value)
    return result


def _round_single_axes_data(ax_data: dict) -> dict:
    """Round values for a single axes' data."""
    result = {}
    for key, value in ax_data.items():
        if key == "size_mm":
            # Fixed 2 decimals: [40.00, 28.00]
            result[key] = _round_list(value, PRECISION["mm"], fixed=True)
        elif key == "size_inch":
            # Fixed 3 decimals: [1.575, 1.102]
            result[key] = _round_list(value, PRECISION["inch"], fixed=True)
        elif key == "size_px":
            result[key] = [int(v) for v in value]
        elif key in ("position", "position_ratio", "bounds_figure_fraction"):
            # Fixed 3 decimals: [0.250, 0.294, 0.500, 0.412]
            result[key] = _round_list(value, PRECISION["position"], fixed=True)
        elif key == "position_in_grid":
            result[key] = [int(v) for v in value]
        elif key == "margins_mm":
            # Fixed 2 decimals: {"left": 20.00, ...}
            result[key] = {
                k: _round_value(v, PRECISION["mm"], fixed=True)
                for k, v in value.items()
            }
        elif key == "margins_inch":
            # Fixed 3 decimals: {"left": 0.787, ...}
            result[key] = {
                k: _round_value(v, PRECISION["inch"], fixed=True)
                for k, v in value.items()
            }
        elif key == "bbox_mm":
            # Fixed 2 decimals
            result[key] = {
                k: _round_value(v, PRECISION["mm"], fixed=True)
                for k, v in value.items()
            }
        elif key == "bbox_inch":
            # Fixed 3 decimals
            result[key] = {
                k: _round_value(v, PRECISION["inch"], fixed=True)
                for k, v in value.items()
            }
        elif key == "bbox_px":
            result[key] = {k: int(v) for k, v in value.items()}
        elif key in ("xaxis", "yaxis", "xaxis_top", "yaxis_right"):
            # Axis info (label, unit, scale, lim, n_ticks) - using matplotlib terminology
            axis_result = {}
            for ak, av in value.items():
                if ak == "lim":
                    # Fixed 2 decimals for limits: [-0.31, 6.60]
                    axis_result[ak] = _round_list(av, PRECISION["lim"], fixed=True)
                elif ak == "n_ticks":
                    axis_result[ak] = int(av)
                else:
                    axis_result[ak] = av
            result[key] = axis_result
        elif key == "legend":
            # Legend has no floats to round, pass through
            result[key] = value
        elif key == "artists":
            # Round artist values
            result[key] = [_round_artist(a) for a in value]
        else:
            result[key] = value
    return result


def _round_style_section(style_data: dict) -> dict:
    """Round values in hierarchical style section with scopes.

    Handles structure like:
        {
            "global": {"fonts": {...}, "padding": {...}},
            "axes_default": {"axes": {...}, "ticks": {...}},
            "artist_default": {"lines": {...}, "markers": {...}}
        }
    """
    result = {}
    for scope, scope_data in style_data.items():
        if scope in ("global", "axes_default", "artist_default"):
            # Handle scope-level dict
            result[scope] = {}
            for category, category_data in scope_data.items():
                if isinstance(category_data, dict):
                    result[scope][category] = _round_style_subsection(
                        category, category_data
                    )
                else:
                    result[scope][category] = category_data
        elif isinstance(scope_data, dict):
            # Fallback for flat structure (backward compatibility)
            result[scope] = _round_style_subsection(scope, scope_data)
        elif isinstance(scope_data, float):
            if "_mm" in scope:
                result[scope] = _round_value(scope_data, PRECISION["mm"], fixed=True)
            elif "_pt" in scope:
                result[scope] = _round_value(scope_data, 1, fixed=True)
            else:
                result[scope] = _round_value(scope_data, 2)
        elif isinstance(scope_data, int):
            result[scope] = scope_data
        else:
            result[scope] = scope_data
    return result


def _round_style_subsection(category: str, data: dict) -> dict:
    """Round values in a style subsection based on category."""
    result = {}
    for key, value in data.items():
        if isinstance(value, float):
            if "_mm" in key or category in ("axes", "ticks", "lines", "markers"):
                # mm values: 2 decimals
                result[key] = _round_value(value, PRECISION["mm"], fixed=True)
            elif "_pt" in key or category in ("fonts", "padding"):
                # pt values: 1 decimal
                result[key] = _round_value(value, 1, fixed=True)
            else:
                result[key] = _round_value(value, 2)
        elif isinstance(value, int):
            result[key] = value
        else:
            result[key] = value
    return result


def _round_plot_section(plot_data: dict) -> dict:
    """Round values in plot section."""
    result = {}
    for key, value in plot_data.items():
        if key == "artists":
            result[key] = [_round_artist(a) for a in value]
        elif key == "legend":
            result[key] = value  # Legend has no floats to round
        else:
            result[key] = value
    return result


def _round_artist(artist: dict) -> dict:
    """Round values in a single artist."""
    result = {}
    for key, value in artist.items():
        if key == "style" and isinstance(value, dict):
            # Legacy: Round values in style dict (for backward compatibility)
            style_result = {}
            for sk, sv in value.items():
                if sk in ("linewidth_pt", "markersize_pt"):
                    # Fixed 2 decimals: 0.57
                    style_result[sk] = _round_value(
                        sv, PRECISION["linewidth"], fixed=True
                    )
                else:
                    style_result[sk] = sv
            result[key] = style_result
        elif key == "backend" and isinstance(value, dict):
            # New two-layer structure: round values in backend.props
            backend_result = {"name": value.get("name", "matplotlib")}
            if "artist_class" in value:
                backend_result["artist_class"] = value["artist_class"]
            if "props" in value and isinstance(value["props"], dict):
                props_result = {}
                for pk, pv in value["props"].items():
                    if pk in ("linewidth_pt", "markersize_pt"):
                        # Fixed 2 decimals: 0.57
                        props_result[pk] = _round_value(
                            pv, PRECISION["linewidth"], fixed=True
                        )
                    elif pk == "size":
                        # Scatter size: 1 decimal
                        props_result[pk] = _round_value(pv, 1, fixed=True)
                    else:
                        props_result[pk] = pv
                backend_result["props"] = props_result
            result[key] = backend_result
        elif key == "geometry" and isinstance(value, dict):
            # Round geometry values (for bar charts)
            geom_result = {}
            for gk, gv in value.items():
                if isinstance(gv, float):
                    geom_result[gk] = _round_value(gv, 4, fixed=False)
                else:
                    geom_result[gk] = gv
            result[key] = geom_result
        elif key == "zorder":
            result[key] = int(value) if isinstance(value, (int, float)) else value
        else:
            result[key] = value
    return result


# Backward compatibility alias
_round_trace = _round_artist


def _parse_label_unit(label_text: str) -> tuple:
    """
    Parse label text to extract label and unit.

    Handles formats like:
    - "Time [s]" -> ("Time", "s")
    - "Amplitude (a.u.)" -> ("Amplitude", "a.u.")
    - "Value" -> ("Value", "")

    Parameters
    ----------
    label_text : str
        The full label text from axes

    Returns
    -------
    tuple
        (label, unit) where unit is empty string if not found
    """
    import re

    if not label_text:
        return "", ""

    # Try to match [...] pattern first (preferred format)
    match = re.match(r"^(.+?)\s*\[([^\]]+)\]$", label_text)
    if match:
        return match.group(1).strip(), match.group(2).strip()

    # Try to match (...) pattern
    match = re.match(r"^(.+?)\s*\(([^\)]+)\)$", label_text)
    if match:
        return match.group(1).strip(), match.group(2).strip()

    # No unit found
    return label_text.strip(), ""


def _get_csv_column_names(
    trace_id: str, ax_row: int = 0, ax_col: int = 0, variables: list = None
) -> dict:
    """
    Get CSV column names using the single source of truth naming convention.

    Format: ax-row-{row}-col-{col}_trace-id-{id}_variable-{var}

    Parameters
    ----------
    trace_id : str
        The trace identifier (e.g., "sine", "step")
    ax_row : int
        Row position of axes in grid (default: 0)
    ax_col : int
        Column position of axes in grid (default: 0)
    variables : list, optional
        List of variable names (default: ["x", "y"])

    Returns
    -------
    dict
        Dictionary mapping variable names to CSV column names
    """
    from ._csv_column_naming import get_csv_column_name

    if variables is None:
        variables = ["x", "y"]

    data_ref = {}
    for var in variables:
        data_ref[var] = get_csv_column_name(var, ax_row, ax_col, trace_id=trace_id)

    return data_ref


def _extract_artists(ax) -> list:
    """
    Extract artist information including properties and CSV column mapping.

    Uses matplotlib terminology: each drawable element is an Artist.
    Only includes artists that were explicitly created via scitex tracking (top-level calls),
    not internal artists created by matplotlib functions like boxplot() which internally
    call plot() multiple times.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to extract artists from

    Returns
    -------
    list
        List of artist dictionaries with:
        - id: unique identifier
        - artist_class: matplotlib class name (Line2D, PathCollection, etc.)
        - label: legend label
        - style: color, linestyle, linewidth, etc.
        - data_ref: CSV column mapping (matches columns_actual exactly)
    """
    import matplotlib.colors as mcolors

    artists = []

    # Get axes position for CSV column naming
    ax_row, ax_col = 0, 0  # Default for single axes
    if hasattr(ax, "_scitex_metadata") and "position_in_grid" in ax._scitex_metadata:
        pos = ax._scitex_metadata["position_in_grid"]
        ax_row, ax_col = pos[0], pos[1]

    # Get the raw matplotlib axes for accessing lines
    mpl_ax = ax._axis_mpl if hasattr(ax, "_axis_mpl") else ax

    # Try to find scitex wrapper for plot type detection and history access
    ax_for_detection = ax
    if not hasattr(ax, "history") and hasattr(mpl_ax, "_scitex_wrapper"):
        ax_for_detection = mpl_ax._scitex_wrapper

    # Check if we should filter to only tracked artists
    # For plot types that internally call plot (boxplot, errorbar, etc.),
    # we don't export the internal artists EXCEPT explicitly tracked ones
    plot_type, method = _detect_plot_type(ax_for_detection)

    # Plot types where internal line artists should be hidden
    # But we still export artists that have explicit _scitex_id set
    # These plot types create Line2D objects internally that don't have
    # corresponding data in the CSV export
    # NOTE: scatter is NOT included here because scatter plots often have
    # regression lines that should be exported
    internal_plot_types = {
        "boxplot",
        "violin",
        "hist",
        "bar",
        "image",
        "heatmap",
        "kde",
        "ecdf",
        "errorbar",
        "fill",
        "stem",
        "contour",
        "pie",
        "quiver",
        "stream",
    }

    skip_unlabeled = plot_type in internal_plot_types

    # Build a map from scitex_id to full record from history
    # Record format: (tracking_id, method, tracked_dict, kwargs)
    id_to_history = {}
    if hasattr(ax_for_detection, "history"):
        for record_id, record in ax_for_detection.history.items():
            if isinstance(record, tuple) and len(record) >= 2:
                tracking_id = record[0]  # The id used in tracking
                id_to_history[tracking_id] = record  # Store full record

    # Special handling for boxplot and violin - extract semantic components
    # Boxplot creates lines in a specific pattern: for n boxes, there are
    # typically: whiskers (2*n), caps (2*n), median (n), fliers (n)
    is_boxplot = plot_type == "boxplot"
    is_violin = plot_type == "violin"
    is_stem = plot_type == "stem"

    # For boxplot, try to determine the number of boxes and compute stats from history
    num_boxes = 0
    boxplot_stats = []  # Will hold stats for each box
    boxplot_data = None
    if is_boxplot and hasattr(ax_for_detection, "history"):
        for record in ax_for_detection.history.values():
            if isinstance(record, tuple) and len(record) >= 3:
                method_name = record[1]
                if method_name == "boxplot":
                    tracked_dict = record[2]
                    args = tracked_dict.get("args", [])
                    if args and len(args) > 0:
                        data = args[0]
                        if hasattr(data, "__len__") and not isinstance(data, str):
                            # Check if it's list of arrays or single array
                            if hasattr(data[0], "__len__") and not isinstance(
                                data[0], str
                            ):
                                num_boxes = len(data)
                                boxplot_data = data
                            else:
                                num_boxes = 1
                                boxplot_data = [data]
                    break

    # Compute boxplot statistics
    if boxplot_data is not None:
        import numpy as np

        for box_idx, box_data in enumerate(boxplot_data):
            try:
                arr = np.asarray(box_data)
                arr = arr[~np.isnan(arr)]  # Remove NaN values
                if len(arr) > 0:
                    q1 = float(np.percentile(arr, 25))
                    median = float(np.median(arr))
                    q3 = float(np.percentile(arr, 75))
                    iqr = q3 - q1
                    whisker_low = float(max(arr.min(), q1 - 1.5 * iqr))
                    whisker_high = float(min(arr.max(), q3 + 1.5 * iqr))
                    # Fliers are points outside whiskers
                    fliers = arr[(arr < whisker_low) | (arr > whisker_high)]
                    boxplot_stats.append(
                        {
                            "box_index": box_idx,
                            "median": median,
                            "q1": q1,
                            "q3": q3,
                            "whisker_low": whisker_low,
                            "whisker_high": whisker_high,
                            "n_fliers": int(len(fliers)),
                            "n_samples": int(len(arr)),
                        }
                    )
            except (ValueError, TypeError):
                pass

    for i, line in enumerate(mpl_ax.lines):
        # Get ID from _scitex_id attribute (set by scitex plotting functions)
        # This matches the id= kwarg passed to ax.plot()
        scitex_id = getattr(line, "_scitex_id", None)

        # Get label for legend
        label = line.get_label()

        # For internal plot types (boxplot, violin, etc.), skip Line2D artists
        # that were created internally by matplotlib (not explicitly tracked).
        # These internal artists don't have corresponding data in the CSV.
        # BUT: for boxplot/violin/stem, we want to export with semantic labels
        semantic_type = None
        semantic_id = None
        has_boxplot_stats = False
        box_idx = None

        # For stem, always detect semantic type (even with scitex_id)
        if is_stem:
            marker = line.get_marker()
            linestyle = line.get_linestyle()
            if marker and marker != "None" and linestyle == "None":
                # This is the marker line (markers only, no connecting line)
                semantic_type = "stem_marker"
                semantic_id = "stem_markers"
            elif linestyle and linestyle != "None":
                # This is either stemlines or baseline
                # Check if it looks like a baseline (horizontal line at y=0)
                ydata = line.get_ydata()
                if len(ydata) >= 2 and len(set(ydata)) == 1:
                    semantic_type = "stem_baseline"
                    semantic_id = "stem_baseline"
                else:
                    semantic_type = "stem_stem"
                    semantic_id = "stem_lines"
            else:
                semantic_type = "stem_component"
                semantic_id = f"stem_{i}"

        if skip_unlabeled and not scitex_id and label.startswith("_"):
            # For boxplot, assign semantic roles based on position in lines list
            if is_boxplot and num_boxes > 0:
                # Boxplot line order: whiskers (2*n), caps (2*n), medians (n), fliers (n)
                total_whiskers = 2 * num_boxes
                total_caps = 2 * num_boxes
                total_medians = num_boxes

                if i < total_whiskers:
                    box_idx = i // 2
                    whisker_idx = i % 2
                    semantic_type = "boxplot_whisker"
                    semantic_id = f"box_{box_idx}_whisker_{whisker_idx}"
                elif i < total_whiskers + total_caps:
                    cap_i = i - total_whiskers
                    box_idx = cap_i // 2
                    cap_idx = cap_i % 2
                    semantic_type = "boxplot_cap"
                    semantic_id = f"box_{box_idx}_cap_{cap_idx}"
                elif i < total_whiskers + total_caps + total_medians:
                    box_idx = i - total_whiskers - total_caps
                    semantic_type = "boxplot_median"
                    semantic_id = f"box_{box_idx}_median"
                    # Mark this as the primary element to hold stats
                    has_boxplot_stats = True
                else:
                    flier_idx = i - total_whiskers - total_caps - total_medians
                    # Distribute fliers across boxes if we have fewer flier lines than boxes
                    box_idx = flier_idx if flier_idx < num_boxes else num_boxes - 1
                    semantic_type = "boxplot_flier"
                    semantic_id = f"box_{box_idx}_flier"
            elif is_violin:
                # Violin typically has: bodies (patches), then optional lines
                semantic_type = "violin_component"
                semantic_id = f"violin_line_{i}"
            elif is_stem:
                # Already handled above
                pass
            else:
                continue  # Skip for other internal plot types

        artist = {}

        # For scatter plots, check if this Line2D is a regression line
        is_regression_line = False
        if plot_type == "scatter" and label.startswith("_"):
            # Check if this looks like a regression line (straight line with few points)
            xdata = line.get_xdata()
            ydata = line.get_ydata()
            if len(xdata) == 2:  # Regression line typically has 2 points
                is_regression_line = True

        # Store display id/label
        # For stem, use semantic_id as the primary ID to ensure uniqueness
        if semantic_id and is_stem:
            artist["id"] = semantic_id
            if scitex_id:
                artist["group_id"] = scitex_id  # Store original trace id as group
        elif scitex_id:
            artist["id"] = scitex_id
        elif semantic_id:
            artist["id"] = semantic_id
        elif is_regression_line:
            artist["id"] = f"regression_{i}"
        elif not label.startswith("_"):
            artist["id"] = label
        else:
            artist["id"] = f"line_{i}"

        # Semantic layer: mark (plot type) and role (component role)
        # mark: line, scatter, bar, boxplot, violin, heatmap, etc.
        # role: specific component like boxplot_median, violin_body, etc.
        artist["mark"] = "line"  # Line2D is always a line mark
        if semantic_type:
            artist["role"] = semantic_type
        elif is_regression_line:
            artist["role"] = "regression_line"

        # Label (for legend) - use label if not internal
        # legend_included indicates if this artist appears in legend
        if not label.startswith("_"):
            artist["label"] = label
            artist["legend_included"] = True
        else:
            artist["legend_included"] = False

        # zorder for layering
        artist["zorder"] = line.get_zorder()

        # Backend layer: matplotlib-specific properties
        backend = {
            "name": "matplotlib",
            "artist_class": type(line).__name__,  # e.g., "Line2D"
            "props": {},
        }

        # Color - always convert to hex for consistent JSON storage
        color = line.get_color()
        try:
            # mcolors.to_hex handles strings, RGB tuples, RGBA tuples
            color_hex = mcolors.to_hex(color, keep_alpha=False)
            backend["props"]["color"] = color_hex
        except (ValueError, TypeError):
            # Fallback: store as-is
            backend["props"]["color"] = color

        # Line style
        backend["props"]["linestyle"] = line.get_linestyle()

        # Line width
        backend["props"]["linewidth_pt"] = line.get_linewidth()

        # Marker - always include (null if no marker)
        marker = line.get_marker()
        if marker and marker != "None" and marker != "none":
            backend["props"]["marker"] = marker
            backend["props"]["markersize_pt"] = line.get_markersize()
        else:
            backend["props"]["marker"] = None

        artist["backend"] = backend

        # data_ref - CSV column mapping using single source of truth naming
        # Format: ax-row-{row}-col-{col}_trace-id-{id}_variable-{var}
        # Only add data_ref if this is NOT a boxplot/violin internal element
        # (those have semantic_type set but no corresponding CSV data)
        if not semantic_type:
            # Try to find the correct trace_id for data_ref
            # Priority: 1) _scitex_id, 2) History record trace_id, 3) Artist ID
            trace_id_for_ref = None

            if scitex_id:
                # Artist has explicit _scitex_id set
                trace_id_for_ref = scitex_id
            else:
                # Try to find matching history record for this Line2D
                # Look for "plot" method records and match by index
                if hasattr(ax_for_detection, "history"):
                    plot_records = []
                    for record_id, record in ax_for_detection.history.items():
                        if isinstance(record, tuple) and len(record) >= 2:
                            if record[1] == "plot":
                                # Extract trace_id from tracking_id (e.g., "ax_00_plot_0" -> "0")
                                tracking_id = record[0]
                                if tracking_id.startswith("ax_"):
                                    parts = tracking_id.split("_")
                                    if len(parts) >= 4:
                                        trace_id_for_ref = "_".join(parts[3:])
                                    elif len(parts) == 4:
                                        trace_id_for_ref = parts[3]
                                elif tracking_id.startswith("plot_"):
                                    trace_id_for_ref = (
                                        tracking_id[5:]
                                        if len(tracking_id) > 5
                                        else str(i)
                                    )
                                else:
                                    # User-provided ID like "sine"
                                    trace_id_for_ref = tracking_id
                                plot_records.append(trace_id_for_ref)

                    # Match by line index if we have plot records
                    if plot_records:
                        # Find the index of this line among all non-semantic lines
                        non_semantic_line_idx = 0
                        for j, l in enumerate(mpl_ax.lines[:i]):
                            l_label = l.get_label()
                            l_scitex_id = getattr(l, "_scitex_id", None)
                            l_semantic_id = getattr(l, "_scitex_semantic_id", None)
                            # Count only lines that would get data_ref (non-semantic)
                            if not l_semantic_id and not l_label.startswith("_"):
                                non_semantic_line_idx += 1
                            elif l_scitex_id:
                                non_semantic_line_idx += 1

                        if non_semantic_line_idx < len(plot_records):
                            trace_id_for_ref = plot_records[non_semantic_line_idx]

            # Fallback to artist ID
            if not trace_id_for_ref:
                trace_id_for_ref = artist.get("id", str(i))

            artist["data_ref"] = _get_csv_column_names(trace_id_for_ref, ax_row, ax_col)
        elif is_stem and scitex_id:
            # For stem artists, add data_ref pointing to the original trace's columns
            artist["data_ref"] = _get_csv_column_names(scitex_id, ax_row, ax_col)
            # For baseline, mark it as derived (not directly from CSV)
            if semantic_type == "stem_baseline":
                artist["derived"] = True
                artist["data_ref"]["derived_from"] = "y=0"

        # Add boxplot statistics to the median artist
        if has_boxplot_stats and box_idx is not None and box_idx < len(boxplot_stats):
            artist["stats"] = boxplot_stats[box_idx]

        artists.append(artist)

    # Also extract PathCollection artists (scatter points)
    for i, coll in enumerate(mpl_ax.collections):
        if "PathCollection" not in type(coll).__name__:
            continue

        artist = {}

        # Get ID from _scitex_id attribute
        scitex_id = getattr(coll, "_scitex_id", None)
        label = coll.get_label()

        if scitex_id:
            artist["id"] = scitex_id
        elif label and not label.startswith("_"):
            artist["id"] = label
        else:
            artist["id"] = f"scatter_{i}"

        # Semantic layer
        artist["mark"] = "scatter"

        # Legend inclusion
        if label and not label.startswith("_"):
            artist["label"] = label
            artist["legend_included"] = True
        else:
            artist["legend_included"] = False

        artist["zorder"] = coll.get_zorder()

        # Backend layer: matplotlib-specific properties
        backend = {
            "name": "matplotlib",
            "artist_class": type(coll).__name__,  # "PathCollection"
            "props": {},
        }

        try:
            facecolors = coll.get_facecolor()
            if len(facecolors) > 0:
                backend["props"]["facecolor"] = mcolors.to_hex(
                    facecolors[0], keep_alpha=False
                )
        except (ValueError, TypeError, IndexError):
            pass

        try:
            edgecolors = coll.get_edgecolor()
            if len(edgecolors) > 0:
                backend["props"]["edgecolor"] = mcolors.to_hex(
                    edgecolors[0], keep_alpha=False
                )
        except (ValueError, TypeError, IndexError):
            pass

        try:
            sizes = coll.get_sizes()
            if len(sizes) > 0:
                backend["props"]["size"] = float(sizes[0])
        except (ValueError, TypeError, IndexError):
            pass

        artist["backend"] = backend

        # data_ref - CSV column mapping using single source of truth naming
        # Format: ax-row-{row}-col-{col}_trace-id-{id}_variable-{var}
        artist_id = artist.get("id", str(i))
        artist["data_ref"] = _get_csv_column_names(artist_id, ax_row, ax_col)

        artists.append(artist)

    # Extract Rectangle patches (bar/barh/hist charts)
    # First, collect all rectangles to determine group info
    rectangles = []
    for i, patch in enumerate(mpl_ax.patches):
        patch_type = type(patch).__name__
        if patch_type == "Rectangle":
            rectangles.append((i, patch))

    # Determine if this is bar, barh, or hist based on plot_type
    is_bar = plot_type in ("bar", "barh")
    is_hist = plot_type == "hist"

    # Get trace_id from history for data_ref
    trace_id_for_bars = None
    if hasattr(ax_for_detection, "history"):
        for record in ax_for_detection.history.values():
            if isinstance(record, tuple) and len(record) >= 2:
                method_name = record[1]
                if method_name in ("bar", "barh", "hist"):
                    trace_id_for_bars = record[0]
                    break

    bar_count = 0
    for rect_idx, (i, patch) in enumerate(rectangles):
        patch_type = type(patch).__name__

        # Skip internal unlabeled patches for non-bar/hist types
        scitex_id = getattr(patch, "_scitex_id", None)
        label = patch.get_label() if hasattr(patch, "get_label") else ""

        # For bar/hist, we want ALL rectangles even if unlabeled
        if not (is_bar or is_hist):
            if (
                skip_unlabeled
                and not scitex_id
                and (not label or label.startswith("_"))
            ):
                continue

        artist = {}

        # Generate unique ID with index
        base_id = scitex_id or (
            label if label and not label.startswith("_") else trace_id_for_bars or "bar"
        )
        artist["id"] = f"{base_id}_{bar_count}"

        # Add group_id for referencing the whole group
        artist["group_id"] = base_id

        # Semantic layer
        artist["mark"] = "bar"
        if is_hist:
            artist["role"] = "hist_bin"
        else:
            artist["role"] = "bar_body"

        # Legend inclusion - only first bar of a group should be in legend
        if label and not label.startswith("_") and bar_count == 0:
            artist["label"] = label
            artist["legend_included"] = True
        else:
            artist["legend_included"] = False

        artist["zorder"] = patch.get_zorder()

        # Backend layer: matplotlib-specific properties
        backend = {"name": "matplotlib", "artist_class": patch_type, "props": {}}

        try:
            backend["props"]["facecolor"] = mcolors.to_hex(
                patch.get_facecolor(), keep_alpha=False
            )
        except (ValueError, TypeError):
            pass
        try:
            backend["props"]["edgecolor"] = mcolors.to_hex(
                patch.get_edgecolor(), keep_alpha=False
            )
        except (ValueError, TypeError):
            pass
        try:
            backend["props"]["linewidth_pt"] = patch.get_linewidth()
        except (ValueError, TypeError):
            pass

        artist["backend"] = backend

        # Bar geometry
        try:
            artist["geometry"] = {
                "x": patch.get_x(),
                "y": patch.get_y(),
                "width": patch.get_width(),
                "height": patch.get_height(),
            }
        except (ValueError, TypeError):
            pass

        # data_ref with row_index for individual bars
        if trace_id_for_bars:
            if is_hist:
                # Histogram uses specific column names: bin-centers (x), bin-counts (y)
                prefix = f"ax-row-{ax_row}-col-{ax_col}_trace-id-{trace_id_for_bars}_variable-"
                artist["data_ref"] = {
                    "x": f"{prefix}bin-centers",
                    "y": f"{prefix}bin-counts",
                    "row_index": bar_count,
                    "bin_index": bar_count,
                }
            else:
                artist["data_ref"] = _get_csv_column_names(
                    trace_id_for_bars, ax_row, ax_col
                )
                artist["data_ref"]["row_index"] = bar_count

        bar_count += 1
        artists.append(artist)

    # Extract Wedge patches (pie charts)
    wedge_count = 0
    for i, patch in enumerate(mpl_ax.patches):
        patch_type = type(patch).__name__

        if patch_type != "Wedge":
            continue

        artist = {}

        scitex_id = getattr(patch, "_scitex_id", None)
        label = patch.get_label() if hasattr(patch, "get_label") else ""

        if scitex_id:
            artist["id"] = scitex_id
        elif label and not label.startswith("_"):
            artist["id"] = label
        else:
            artist["id"] = f"wedge_{wedge_count}"
            wedge_count += 1

        # Semantic layer
        artist["mark"] = "pie"
        artist["role"] = "pie_wedge"

        if label and not label.startswith("_"):
            artist["label"] = label
            artist["legend_included"] = True
        else:
            artist["legend_included"] = False

        artist["zorder"] = patch.get_zorder()

        # Backend layer
        backend = {"name": "matplotlib", "artist_class": patch_type, "props": {}}
        try:
            backend["props"]["facecolor"] = mcolors.to_hex(
                patch.get_facecolor(), keep_alpha=False
            )
        except (ValueError, TypeError):
            pass

        artist["backend"] = backend
        artists.append(artist)

    # Extract QuadMesh (hist2d) and PolyCollection (hexbin/violin) with colormap info
    # Try to get hist2d result data from history
    hist2d_result = None
    hexbin_result = None
    if hasattr(ax_for_detection, "history"):
        for record in ax_for_detection.history.values():
            if isinstance(record, tuple) and len(record) >= 3:
                method_name = record[1]
                tracked_dict = record[2]
                if method_name == "hist2d" and "result" in tracked_dict:
                    hist2d_result = tracked_dict["result"]
                elif method_name == "hexbin" and "result" in tracked_dict:
                    hexbin_result = tracked_dict["result"]

    for i, coll in enumerate(mpl_ax.collections):
        coll_type = type(coll).__name__

        if coll_type == "QuadMesh":
            artist = {}
            artist["id"] = f"hist2d_{i}"

            # Semantic layer
            artist["mark"] = "heatmap"
            artist["role"] = "hist2d"

            artist["legend_included"] = False
            artist["zorder"] = coll.get_zorder()

            # Backend layer
            backend = {"name": "matplotlib", "artist_class": coll_type, "props": {}}
            try:
                cmap = coll.get_cmap()
                if cmap:
                    backend["props"]["cmap"] = cmap.name
            except (ValueError, TypeError, AttributeError):
                pass
            try:
                backend["props"]["vmin"] = float(coll.norm.vmin) if coll.norm else None
                backend["props"]["vmax"] = float(coll.norm.vmax) if coll.norm else None
            except (ValueError, TypeError, AttributeError):
                pass

            artist["backend"] = backend

            # Extract hist2d result data directly from QuadMesh
            try:
                # Get the count array from the QuadMesh
                arr = coll.get_array()
                if arr is not None and len(arr) > 0:
                    import numpy as np

                    # QuadMesh from hist2d has counts as flattened array
                    # Try to get coordinates from the mesh
                    coords = coll.get_coordinates()
                    if coords is not None and len(coords) > 0:
                        # coords shape is (n_rows+1, n_cols+1, 2) for 2D hist
                        n_ybins = coords.shape[0] - 1
                        n_xbins = coords.shape[1] - 1

                        # Get edges from coordinates
                        xedges = coords[0, :, 0]  # First row, all cols, x-coord
                        yedges = coords[:, 0, 1]  # All rows, first col, y-coord

                        artist["result"] = {
                            "H_shape": [n_ybins, n_xbins],
                            "n_xbins": int(n_xbins),
                            "n_ybins": int(n_ybins),
                            "xedges_range": [float(xedges[0]), float(xedges[-1])],
                            "yedges_range": [float(yedges[0]), float(yedges[-1])],
                            "count_range": [float(arr.min()), float(arr.max())],
                            "total_count": int(arr.sum()),
                        }
            except (IndexError, TypeError, AttributeError, ValueError):
                pass

            artists.append(artist)

        elif coll_type == "PolyCollection" or (
            coll_type == "FillBetweenPolyCollection" and plot_type == "violin"
        ):
            arr = coll.get_array() if hasattr(coll, "get_array") else None

            # Check if this is hexbin (has array data for counts) or violin body
            if arr is not None and len(arr) > 0 and plot_type == "hexbin":
                artist = {}
                artist["id"] = f"hexbin_{i}"

                # Semantic layer
                artist["mark"] = "heatmap"
                artist["role"] = "hexbin"

                artist["legend_included"] = False
                artist["zorder"] = coll.get_zorder()

                # Backend layer
                backend = {"name": "matplotlib", "artist_class": coll_type, "props": {}}
                try:
                    cmap = coll.get_cmap()
                    if cmap:
                        backend["props"]["cmap"] = cmap.name
                except (ValueError, TypeError, AttributeError):
                    pass
                try:
                    backend["props"]["vmin"] = (
                        float(coll.norm.vmin) if coll.norm else None
                    )
                    backend["props"]["vmax"] = (
                        float(coll.norm.vmax) if coll.norm else None
                    )
                except (ValueError, TypeError, AttributeError):
                    pass

                artist["backend"] = backend

                # Add hexbin result info directly from the PolyCollection
                try:
                    artist["result"] = {
                        "n_hexagons": int(len(arr)),
                        "count_range": (
                            [float(arr.min()), float(arr.max())]
                            if len(arr) > 0
                            else None
                        ),
                        "total_count": int(arr.sum()),
                    }
                except (TypeError, AttributeError, ValueError):
                    pass

                artists.append(artist)

            elif plot_type == "violin":
                # This is a violin body (PolyCollection for violin shape)
                artist = {}
                scitex_id = getattr(coll, "_scitex_id", None)
                label = coll.get_label() if hasattr(coll, "get_label") else ""

                if scitex_id:
                    artist["id"] = f"{scitex_id}_body_{i}"
                    artist["group_id"] = scitex_id
                else:
                    artist["id"] = f"violin_body_{i}"

                # Semantic layer
                artist["mark"] = "polygon"
                artist["role"] = "violin_body"

                artist["legend_included"] = False
                artist["zorder"] = coll.get_zorder()

                # Backend layer
                backend = {"name": "matplotlib", "artist_class": coll_type, "props": {}}
                try:
                    facecolors = coll.get_facecolor()
                    if len(facecolors) > 0:
                        backend["props"]["facecolor"] = mcolors.to_hex(
                            facecolors[0], keep_alpha=False
                        )
                except (ValueError, TypeError, IndexError):
                    pass
                try:
                    edgecolors = coll.get_edgecolor()
                    if len(edgecolors) > 0:
                        backend["props"]["edgecolor"] = mcolors.to_hex(
                            edgecolors[0], keep_alpha=False
                        )
                except (ValueError, TypeError, IndexError):
                    pass

                artist["backend"] = backend
                artists.append(artist)

    # Extract AxesImage (imshow)
    for i, img in enumerate(mpl_ax.images):
        img_type = type(img).__name__

        artist = {}

        scitex_id = getattr(img, "_scitex_id", None)
        label = img.get_label() if hasattr(img, "get_label") else ""

        if scitex_id:
            artist["id"] = scitex_id
        elif label and not label.startswith("_"):
            artist["id"] = label
        else:
            artist["id"] = f"image_{i}"

        # Semantic layer
        artist["mark"] = "image"
        artist["role"] = "image"

        artist["legend_included"] = False
        artist["zorder"] = img.get_zorder()

        # Backend layer
        backend = {"name": "matplotlib", "artist_class": img_type, "props": {}}
        try:
            cmap = img.get_cmap()
            if cmap:
                backend["props"]["cmap"] = cmap.name
        except (ValueError, TypeError, AttributeError):
            pass
        try:
            backend["props"]["vmin"] = float(img.norm.vmin) if img.norm else None
            backend["props"]["vmax"] = float(img.norm.vmax) if img.norm else None
        except (ValueError, TypeError, AttributeError):
            pass
        try:
            backend["props"]["interpolation"] = img.get_interpolation()
        except (ValueError, TypeError, AttributeError):
            pass

        artist["backend"] = backend
        artists.append(artist)

    # Extract Text artists (annotations, stats text, etc.)
    text_count = 0
    for i, text_obj in enumerate(mpl_ax.texts):
        text_content = text_obj.get_text()
        if not text_content or text_content.strip() == "":
            continue

        artist = {}

        scitex_id = getattr(text_obj, "_scitex_id", None)

        if scitex_id:
            artist["id"] = scitex_id
        else:
            artist["id"] = f"text_{text_count}"

        # Semantic layer
        artist["mark"] = "text"

        # Try to determine role from content or position
        pos = text_obj.get_position()
        # Check if this looks like stats annotation (contains r=, p=, etc.)
        if any(kw in text_content.lower() for kw in ["r=", "p=", "r²=", "n="]):
            artist["role"] = "stats_annotation"
        else:
            artist["role"] = "annotation"

        artist["legend_included"] = False
        artist["zorder"] = text_obj.get_zorder()

        # Geometry - text position
        artist["geometry"] = {
            "x": pos[0],
            "y": pos[1],
        }

        # Text content
        artist["text"] = text_content

        # Backend layer
        backend = {
            "name": "matplotlib",
            "artist_class": type(text_obj).__name__,
            "props": {},
        }

        try:
            color = text_obj.get_color()
            backend["props"]["color"] = mcolors.to_hex(color, keep_alpha=False)
        except (ValueError, TypeError):
            pass

        try:
            backend["props"]["fontsize_pt"] = text_obj.get_fontsize()
        except (ValueError, TypeError):
            pass

        try:
            backend["props"]["ha"] = text_obj.get_ha()
            backend["props"]["va"] = text_obj.get_va()
        except (ValueError, TypeError):
            pass

        artist["backend"] = backend

        # data_ref for text position - only if text was explicitly tracked (has _scitex_id)
        # Auto-generated text (like contour clabels, pie labels) doesn't have CSV data
        if scitex_id:
            artist["data_ref"] = {
                "x": f"text_{text_count}_x",
                "y": f"text_{text_count}_y",
                "content": f"text_{text_count}_content",
            }

        text_count += 1
        artists.append(artist)

    # Extract LineCollection artists (errorbar lines, etc.)
    for i, coll in enumerate(mpl_ax.collections):
        coll_type = type(coll).__name__

        if coll_type == "LineCollection":
            # LineCollection is used for errorbar caps/lines
            artist = {}

            scitex_id = getattr(coll, "_scitex_id", None)
            label = coll.get_label() if hasattr(coll, "get_label") else ""

            if scitex_id:
                artist["id"] = scitex_id
            elif label and not label.startswith("_"):
                artist["id"] = label
            else:
                artist["id"] = f"linecollection_{i}"

            # Semantic layer - determine role
            artist["mark"] = "line"
            # Check if this is an errorbar based on context
            if plot_type == "bar" or method == "barh":
                artist["role"] = "errorbar"
            elif plot_type == "stem":
                artist["role"] = "stem_stem"
                artist["id"] = "stem_lines"  # Override ID for stem
            else:
                artist["role"] = "line_collection"

            artist["legend_included"] = False
            artist["zorder"] = coll.get_zorder()

            # Backend layer
            backend = {"name": "matplotlib", "artist_class": coll_type, "props": {}}

            try:
                colors = coll.get_colors()
                if len(colors) > 0:
                    backend["props"]["color"] = mcolors.to_hex(
                        colors[0], keep_alpha=False
                    )
            except (ValueError, TypeError, IndexError):
                pass

            try:
                linewidths = coll.get_linewidths()
                if len(linewidths) > 0:
                    backend["props"]["linewidth_pt"] = float(linewidths[0])
            except (ValueError, TypeError, IndexError):
                pass

            artist["backend"] = backend

            # Add data_ref for errorbar LineCollections
            if artist["role"] == "errorbar":
                # Try to find the trace_id from history
                errorbar_trace_id = None
                error_var = "yerr" if method == "bar" else "xerr"
                if hasattr(ax_for_detection, "history"):
                    for record in ax_for_detection.history.values():
                        if isinstance(record, tuple) and len(record) >= 2:
                            method_name = record[1]
                            if method_name in ("bar", "barh"):
                                errorbar_trace_id = record[0]
                                break
                if errorbar_trace_id:
                    base_ref = _get_csv_column_names(errorbar_trace_id, ax_row, ax_col)
                    artist["data_ref"] = {
                        "x": base_ref.get("x"),
                        "y": base_ref.get("y"),
                        error_var: f"ax-row-{ax_row}-col-{ax_col}_trace-id-{errorbar_trace_id}_variable-{error_var}",
                    }
            elif artist["role"] == "stem_stem" and hasattr(ax_for_detection, "history"):
                # Add data_ref for stem LineCollection
                for record in ax_for_detection.history.values():
                    if isinstance(record, tuple) and len(record) >= 2:
                        method_name = record[1]
                        if method_name == "stem":
                            stem_trace_id = record[0]
                            artist["data_ref"] = _get_csv_column_names(
                                stem_trace_id, ax_row, ax_col
                            )
                            break

            artists.append(artist)

    return artists


# Backward compatibility alias
_extract_traces = _extract_artists


def _extract_legend_info(ax) -> Optional[dict]:
    """
    Extract legend information from axes.

    Uses matplotlib terminology for legend properties.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to extract legend from

    Returns
    -------
    dict or None
        Legend info dictionary with matplotlib properties, or None if no legend
    """
    legend = ax.get_legend()
    if legend is None:
        return None

    legend_info = {
        "visible": legend.get_visible(),
        "loc": legend._loc if hasattr(legend, "_loc") else "best",
        "frameon": legend.get_frame_on() if hasattr(legend, "get_frame_on") else True,
    }

    # ncol - number of columns
    if hasattr(legend, "_ncols"):
        legend_info["ncol"] = legend._ncols
    elif hasattr(legend, "_ncol"):
        legend_info["ncol"] = legend._ncol

    # Extract legend handles with artist references
    # This allows reconstructing the legend by referencing artists
    handles = []
    texts = legend.get_texts()
    legend_handles = legend.legend_handles if hasattr(legend, "legend_handles") else []

    # Get the raw matplotlib axes for accessing lines to match IDs
    mpl_ax = ax._axis_mpl if hasattr(ax, "_axis_mpl") else ax

    for i, text in enumerate(texts):
        label_text = text.get_text()
        handle_entry = {"label": label_text}

        # Try to get artist_id from corresponding handle
        artist_id = None
        if i < len(legend_handles):
            handle = legend_handles[i]
            # Check if handle has scitex_id
            if hasattr(handle, "_scitex_id"):
                artist_id = handle._scitex_id

        # Fallback: find matching artist by label in axes artists
        if artist_id is None:
            # Check lines
            for line in mpl_ax.lines:
                line_label = line.get_label()
                if line_label == label_text:
                    if hasattr(line, "_scitex_id"):
                        artist_id = line._scitex_id
                    elif not line_label.startswith("_"):
                        artist_id = line_label
                    break

        # Check collections (scatter)
        if artist_id is None:
            for coll in mpl_ax.collections:
                coll_label = coll.get_label() if hasattr(coll, "get_label") else ""
                if coll_label == label_text:
                    if hasattr(coll, "_scitex_id"):
                        artist_id = coll._scitex_id
                    elif coll_label and not coll_label.startswith("_"):
                        artist_id = coll_label
                    break

        # Check patches (bar/hist/pie)
        if artist_id is None:
            for patch in mpl_ax.patches:
                patch_label = patch.get_label() if hasattr(patch, "get_label") else ""
                if patch_label == label_text:
                    if hasattr(patch, "_scitex_id"):
                        artist_id = patch._scitex_id
                    elif patch_label and not patch_label.startswith("_"):
                        artist_id = patch_label
                    break

        # Check images (imshow)
        if artist_id is None:
            for img in mpl_ax.images:
                img_label = img.get_label() if hasattr(img, "get_label") else ""
                if img_label == label_text:
                    if hasattr(img, "_scitex_id"):
                        artist_id = img._scitex_id
                    elif img_label and not img_label.startswith("_"):
                        artist_id = img_label
                    break

        if artist_id:
            handle_entry["artist_id"] = artist_id

        handles.append(handle_entry)

    if handles:
        legend_info["handles"] = handles

    return legend_info


def _detect_plot_type(ax) -> tuple:
    """
    Detect the primary plot type and method from axes content.

    Checks for:
    - Lines -> "line"
    - Scatter collections -> "scatter"
    - Bar containers -> "bar"
    - Patches (histogram) -> "hist"
    - Box plot -> "boxplot"
    - Violin plot -> "violin"
    - Image -> "image"
    - Contour -> "contour"
    - KDE -> "kde"

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axes to analyze

    Returns
    -------
    tuple
        (plot_type, method) where method is the actual plotting function used,
        or (None, None) if unclear
    """
    # Check scitex history FIRST (most reliable for scitex plots)
    # History format: dict with keys as IDs and values as tuples (id, method, tracked_dict, kwargs)
    if hasattr(ax, "history") and len(ax.history) > 0:
        # Get all methods from history
        methods = []
        for record in ax.history.values():
            if isinstance(record, tuple) and len(record) >= 2:
                methods.append(record[1])  # record[1] is the method name

        # Check methods in priority order (more specific first)
        for method in methods:
            if method == "stx_heatmap":
                return "heatmap", "stx_heatmap"
            elif method == "stx_kde":
                return "kde", "stx_kde"
            elif method == "stx_ecdf":
                return "ecdf", "stx_ecdf"
            elif method == "stx_violin":
                return "violin", "stx_violin"
            elif method in ("stx_box", "boxplot"):
                return "boxplot", method
            elif method == "stx_line":
                return "line", "stx_line"
            elif method == "plot_scatter":
                return "scatter", "plot_scatter"
            elif method == "stx_mean_std":
                return "line", "stx_mean_std"
            elif method == "stx_mean_ci":
                return "line", "stx_mean_ci"
            elif method == "stx_median_iqr":
                return "line", "stx_median_iqr"
            elif method == "stx_shaded_line":
                return "line", "stx_shaded_line"
            elif method == "sns_boxplot":
                return "boxplot", "sns_boxplot"
            elif method == "sns_violinplot":
                return "violin", "sns_violinplot"
            elif method == "sns_scatterplot":
                return "scatter", "sns_scatterplot"
            elif method == "sns_lineplot":
                return "line", "sns_lineplot"
            elif method == "sns_histplot":
                return "hist", "sns_histplot"
            elif method == "sns_barplot":
                return "bar", "sns_barplot"
            elif method == "sns_stripplot":
                return "scatter", "sns_stripplot"
            elif method == "sns_kdeplot":
                return "kde", "sns_kdeplot"
            elif method == "scatter":
                return "scatter", "scatter"
            elif method == "bar":
                return "bar", "bar"
            elif method == "barh":
                return "bar", "barh"
            elif method == "hist":
                return "hist", "hist"
            elif method == "hist2d":
                return "hist2d", "hist2d"
            elif method == "hexbin":
                return "hexbin", "hexbin"
            elif method == "violinplot":
                return "violin", "violinplot"
            elif method == "errorbar":
                return "errorbar", "errorbar"
            elif method == "fill_between":
                return "fill", "fill_between"
            elif method == "fill_betweenx":
                return "fill", "fill_betweenx"
            elif method == "imshow":
                return "image", "imshow"
            elif method == "matshow":
                return "image", "matshow"
            elif method == "contour":
                return "contour", "contour"
            elif method == "contourf":
                return "contour", "contourf"
            elif method == "stem":
                return "stem", "stem"
            elif method == "step":
                return "step", "step"
            elif method == "pie":
                return "pie", "pie"
            elif method == "quiver":
                return "quiver", "quiver"
            elif method == "streamplot":
                return "stream", "streamplot"
            elif method == "plot":
                return "line", "plot"
            # Note: "plot" method is handled last as a fallback since boxplot uses it internally

    # Check for images (takes priority)
    if len(ax.images) > 0:
        return "image", "imshow"

    # Check for 2D density plots (hist2d, hexbin) - QuadMesh or PolyCollection
    if hasattr(ax, "collections"):
        for coll in ax.collections:
            coll_type = type(coll).__name__
            if "QuadMesh" in coll_type:
                return "hist2d", "hist2d"
            if "PolyCollection" in coll_type and hasattr(coll, "get_array"):
                # hexbin creates PolyCollection with array data
                arr = coll.get_array()
                if arr is not None and len(arr) > 0:
                    return "hexbin", "hexbin"

    # Check for contours
    if hasattr(ax, "collections"):
        for coll in ax.collections:
            if "Contour" in type(coll).__name__:
                return "contour", "contour"

    # Check for bar plots
    if len(ax.containers) > 0:
        # Check if it's a boxplot (has multiple containers with specific structure)
        if any("boxplot" in str(type(c)).lower() for c in ax.containers):
            return "boxplot", "boxplot"
        # Otherwise assume bar plot
        return "bar", "bar"

    # Check for patches (could be histogram, violin, pie, etc.)
    if len(ax.patches) > 0:
        # Check for pie chart (Wedge patches)
        if any("Wedge" in type(p).__name__ for p in ax.patches):
            return "pie", "pie"
        # If there are many rectangular patches, likely histogram
        if len(ax.patches) > 5:
            return "hist", "hist"
        # Check for violin plot
        if any("Poly" in type(p).__name__ for p in ax.patches):
            return "violin", "violinplot"

    # Check for scatter plots (PathCollection)
    if hasattr(ax, "collections") and len(ax.collections) > 0:
        for coll in ax.collections:
            if "PathCollection" in type(coll).__name__:
                return "scatter", "scatter"

    # Check for line plots
    if len(ax.lines) > 0:
        # If there are error bars, it might be errorbar plot
        if any(hasattr(line, "_mpl_error") for line in ax.lines):
            return "errorbar", "errorbar"
        return "line", "plot"

    return None, None


def _extract_csv_columns_from_history(ax) -> list:
    """
    Extract CSV column names from scitex history for all plot types.

    This function generates the exact column names that will be produced
    by export_as_csv(), providing a mapping between JSON metadata and CSV data.

    Parameters
    ----------
    ax : AxisWrapper or matplotlib.axes.Axes
        The axes to extract CSV column info from

    Returns
    -------
    list
        List of dictionaries containing CSV column mappings for each tracked plot,
        e.g., [{"id": "boxplot_0", "method": "boxplot", "columns": ["ax_00_boxplot_0_boxplot_0", "ax_00_boxplot_0_boxplot_1"]}]
    """
    # Get axes position for CSV column naming
    ax_row, ax_col = 0, 0  # Default for single axes
    if hasattr(ax, "_scitex_metadata") and "position_in_grid" in ax._scitex_metadata:
        pos = ax._scitex_metadata["position_in_grid"]
        ax_row, ax_col = pos[0], pos[1]

    csv_columns_list = []

    # Check if we have scitex history
    if not hasattr(ax, "history") or len(ax.history) == 0:
        return csv_columns_list

    # Iterate through history to extract column names
    # Use enumerate to track trace index for proper CSV column naming
    for trace_index, (record_id, record) in enumerate(ax.history.items()):
        if not isinstance(record, tuple) or len(record) < 4:
            continue

        id_val, method, tracked_dict, kwargs = record

        # Generate column names using the same function as _extract_traces
        # This ensures consistency between plot.traces.csv_columns and data.columns
        columns = _get_csv_columns_for_method_with_index(
            id_val, method, tracked_dict, kwargs, ax_row, ax_col, trace_index
        )

        if columns:
            csv_columns_list.append(
                {
                    "id": id_val,
                    "method": method,
                    "columns": columns,
                }
            )

    return csv_columns_list


def _get_csv_columns_for_method_with_index(
    id_val, method, tracked_dict, kwargs, ax_row: int, ax_col: int, trace_index: int
) -> list:
    """
    Get CSV column names for a specific plotting method using trace index.

    This function uses the same naming convention as _extract_traces to ensure
    consistency between plot.traces.csv_columns and data.columns.

    Parameters
    ----------
    id_val : str
        The plot ID (e.g., "sine", "cosine")
    method : str
        The plotting method name (e.g., "plot", "scatter")
    tracked_dict : dict
        The tracked data dictionary
    kwargs : dict
        The keyword arguments passed to the plot
    ax_row : int
        Row index of axes in grid
    ax_col : int
        Column index of axes in grid
    trace_index : int
        Index of this trace (for deduplication)

    Returns
    -------
    list
        List of column names that will be in the CSV
    """
    from ._csv_column_naming import get_csv_column_name

    columns = []

    # Use simplified variable names (x, y, bins, counts, etc.)
    # The full context comes from the column name structure:
    # ax-row_{row}_ax-col_{col}_trace-id_{id}_variable_{var}
    if method in ("plot", "stx_line"):
        columns = [
            get_csv_column_name("x", ax_row, ax_col, trace_index=trace_index),
            get_csv_column_name("y", ax_row, ax_col, trace_index=trace_index),
        ]
    elif method in ("scatter", "plot_scatter"):
        columns = [
            get_csv_column_name("x", ax_row, ax_col, trace_index=trace_index),
            get_csv_column_name("y", ax_row, ax_col, trace_index=trace_index),
        ]
    elif method in ("bar", "barh"):
        columns = [
            get_csv_column_name("x", ax_row, ax_col, trace_index=trace_index),
            get_csv_column_name("height", ax_row, ax_col, trace_index=trace_index),
        ]
    elif method == "hist":
        columns = [
            get_csv_column_name("bins", ax_row, ax_col, trace_index=trace_index),
            get_csv_column_name("counts", ax_row, ax_col, trace_index=trace_index),
        ]
    elif method in ("boxplot", "stx_box"):
        columns = [
            get_csv_column_name("data", ax_row, ax_col, trace_index=trace_index),
        ]
    elif method in ("violinplot", "stx_violin"):
        columns = [
            get_csv_column_name("data", ax_row, ax_col, trace_index=trace_index),
        ]
    elif method == "errorbar":
        columns = [
            get_csv_column_name("x", ax_row, ax_col, trace_index=trace_index),
            get_csv_column_name("y", ax_row, ax_col, trace_index=trace_index),
            get_csv_column_name("yerr", ax_row, ax_col, trace_index=trace_index),
        ]
    elif method == "fill_between":
        columns = [
            get_csv_column_name("x", ax_row, ax_col, trace_index=trace_index),
            get_csv_column_name("y1", ax_row, ax_col, trace_index=trace_index),
            get_csv_column_name("y2", ax_row, ax_col, trace_index=trace_index),
        ]
    elif method in ("imshow", "stx_heatmap", "stx_image"):
        columns = [
            get_csv_column_name("data", ax_row, ax_col, trace_index=trace_index),
        ]
    elif method in ("stx_kde", "stx_ecdf"):
        columns = [
            get_csv_column_name("x", ax_row, ax_col, trace_index=trace_index),
            get_csv_column_name("y", ax_row, ax_col, trace_index=trace_index),
        ]
    elif method in ("stx_mean_std", "stx_mean_ci", "stx_median_iqr", "stx_shaded_line"):
        columns = [
            get_csv_column_name("x", ax_row, ax_col, trace_index=trace_index),
            get_csv_column_name("y", ax_row, ax_col, trace_index=trace_index),
            get_csv_column_name("lower", ax_row, ax_col, trace_index=trace_index),
            get_csv_column_name("upper", ax_row, ax_col, trace_index=trace_index),
        ]
    elif method.startswith("sns_"):
        sns_type = method.replace("sns_", "")
        if sns_type in ("boxplot", "violinplot"):
            columns = [
                get_csv_column_name("data", ax_row, ax_col, trace_index=trace_index),
            ]
        elif sns_type in ("scatterplot", "lineplot"):
            columns = [
                get_csv_column_name("x", ax_row, ax_col, trace_index=trace_index),
                get_csv_column_name("y", ax_row, ax_col, trace_index=trace_index),
            ]
        elif sns_type == "barplot":
            columns = [
                get_csv_column_name("x", ax_row, ax_col, trace_index=trace_index),
                get_csv_column_name("y", ax_row, ax_col, trace_index=trace_index),
            ]
        elif sns_type == "histplot":
            columns = [
                get_csv_column_name("bins", ax_row, ax_col, trace_index=trace_index),
                get_csv_column_name("counts", ax_row, ax_col, trace_index=trace_index),
            ]
        elif sns_type == "kdeplot":
            columns = [
                get_csv_column_name("x", ax_row, ax_col, trace_index=trace_index),
                get_csv_column_name("y", ax_row, ax_col, trace_index=trace_index),
            ]

    return columns


def _compute_csv_hash_from_df(df) -> Optional[str]:
    """
    Compute a hash of CSV data from a DataFrame.

    This is used after actual CSV export to compute the hash from the
    exact data that was written.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame to compute hash from

    Returns
    -------
    str or None
        SHA256 hash of the CSV data (first 16 chars), or None if unable to compute
    """
    import hashlib

    try:
        if df is None or df.empty:
            return None

        # Convert to CSV string for hashing
        csv_string = df.to_csv(index=False)

        # Compute SHA256 hash
        hash_obj = hashlib.sha256(csv_string.encode("utf-8"))
        hash_hex = hash_obj.hexdigest()

        # Return first 16 characters for readability
        return hash_hex[:16]

    except Exception:
        return None


def _compute_csv_hash(ax_or_df) -> Optional[str]:
    """
    Compute a hash of the CSV data for reproducibility verification.

    The hash is computed from the actual data that would be exported to CSV,
    allowing verification that JSON and CSV files are in sync.

    Note: The hash is computed from the AxisWrapper's export_as_csv(), which
    does NOT include the ax_{index:02d}_ prefix. The FigWrapper.export_as_csv()
    adds this prefix. We replicate this prefix addition here.

    Parameters
    ----------
    ax_or_df : AxisWrapper, matplotlib.axes.Axes, or pandas.DataFrame
        The axes to compute CSV hash from, or a pre-exported DataFrame

    Returns
    -------
    str or None
        SHA256 hash of the CSV data (first 16 chars), or None if unable to compute
    """
    import hashlib

    import pandas as pd

    # If it's already a DataFrame, use the direct hash function
    if isinstance(ax_or_df, pd.DataFrame):
        return _compute_csv_hash_from_df(ax_or_df)

    ax = ax_or_df

    # Check if we have scitex history with export capability
    if not hasattr(ax, "export_as_csv"):
        return None

    try:
        # For single axes figures (most common case), ax_index = 0
        ax_index = 0

        # Export the data as CSV from the AxisWrapper
        df = ax.export_as_csv()

        if df is None or df.empty:
            return None

        # Add axis prefix to match what FigWrapper.export_as_csv produces
        # Uses zero-padded index: ax_00_, ax_01_, etc.
        prefix = f"ax_{ax_index:02d}_"
        new_cols = []
        for col in df.columns:
            col_str = str(col)
            if not col_str.startswith(prefix):
                col_str = f"{prefix}{col_str}"
            new_cols.append(col_str)
        df.columns = new_cols

        # Convert to CSV string for hashing
        csv_string = df.to_csv(index=False)

        # Compute SHA256 hash
        hash_obj = hashlib.sha256(csv_string.encode("utf-8"))
        hash_hex = hash_obj.hexdigest()

        # Return first 16 characters for readability
        return hash_hex[:16]

    except Exception:
        return None


def _get_csv_columns_for_method(
    id_val, method, tracked_dict, kwargs, ax_index: int
) -> list:
    """
    Get CSV column names for a specific plotting method.

    This simulates the actual CSV export to get exact column names.
    It uses the same formatters that generate the CSV to ensure consistency.

    Architecture note:
    - CSV formatters (e.g., _format_boxplot) generate columns WITHOUT ax_ prefix
    - FigWrapper.export_as_csv() adds the ax_{index:02d}_ prefix
    - This function simulates that process to get the final column names

    Parameters
    ----------
    id_val : str
        The plot ID (e.g., "boxplot_0", "plot_0")
    method : str
        The plotting method name (e.g., "boxplot", "plot", "scatter")
    tracked_dict : dict
        The tracked data dictionary
    kwargs : dict
        The keyword arguments passed to the plot
    ax_index : int
        Flattened index of axes (0 for single axes, 0-N for multi-axes)

    Returns
    -------
    list
        List of column names that will be in the CSV (exact match)
    """
    # Import the actual formatters to ensure consistency
    # format_record removed in figrecipe migration; use pattern-based generation directly
    # Pattern-based column name generation
    import numpy as np

    prefix = f"ax_{ax_index:02d}_"
    columns = []

    # Get args from tracked_dict
    args = tracked_dict.get("args", []) if tracked_dict else []

    if method in ("boxplot", "stx_box"):
        # Boxplot: one column per box (mirrors _format_boxplot)
        if len(args) >= 1:
            data = args[0]
            labels = kwargs.get("labels", None) if kwargs else None

            from scitex.types import is_listed_X as scitex_types_is_listed_X

            if isinstance(data, np.ndarray) or scitex_types_is_listed_X(
                data, [float, int]
            ):
                # Single box
                if labels and len(labels) == 1:
                    columns.append(f"{prefix}{id_val}_{labels[0]}")
                else:
                    columns.append(f"{prefix}{id_val}_boxplot_0")
            else:
                # Multiple boxes
                try:
                    num_boxes = len(data)
                    if labels and len(labels) == num_boxes:
                        for label in labels:
                            columns.append(f"{prefix}{id_val}_{label}")
                    else:
                        for i in range(num_boxes):
                            columns.append(f"{prefix}{id_val}_boxplot_{i}")
                except TypeError:
                    columns.append(f"{prefix}{id_val}_boxplot_0")

    elif method in ("plot", "stx_line"):
        # Line plot: x and y columns
        # For single axes (ax_index=0), use simple prefix
        columns.append(f"{prefix}{id_val}_plot_x")
        columns.append(f"{prefix}{id_val}_plot_y")

    elif method in ("scatter", "plot_scatter"):
        columns.append(f"{prefix}{id_val}_scatter_x")
        columns.append(f"{prefix}{id_val}_scatter_y")

    elif method in ("bar", "barh"):
        columns.append(f"{prefix}{id_val}_bar_x")
        columns.append(f"{prefix}{id_val}_bar_height")

    elif method == "hist":
        columns.append(f"{prefix}{id_val}_hist_bins")
        columns.append(f"{prefix}{id_val}_hist_counts")

    elif method in ("violinplot", "stx_violin"):
        if len(args) >= 1:
            data = args[0]
            try:
                num_violins = len(data)
                for i in range(num_violins):
                    columns.append(f"{prefix}{id_val}_violin_{i}")
            except TypeError:
                columns.append(f"{prefix}{id_val}_violin_0")

    elif method == "errorbar":
        columns.append(f"{prefix}{id_val}_errorbar_x")
        columns.append(f"{prefix}{id_val}_errorbar_y")
        columns.append(f"{prefix}{id_val}_errorbar_yerr")

    elif method == "fill_between":
        columns.append(f"{prefix}{id_val}_fill_x")
        columns.append(f"{prefix}{id_val}_fill_y1")
        columns.append(f"{prefix}{id_val}_fill_y2")

    elif method in ("imshow", "stx_heatmap", "stx_image"):
        if len(args) >= 1:
            data = args[0]
            try:
                if hasattr(data, "shape") and len(data.shape) >= 2:
                    columns.append(f"{prefix}{id_val}_image_data")
            except (TypeError, AttributeError):
                pass

    elif method in ("stx_kde", "stx_ecdf"):
        suffix = method.replace("stx_", "")
        columns.append(f"{prefix}{id_val}_{suffix}_x")
        columns.append(f"{prefix}{id_val}_{suffix}_y")

    elif method in ("stx_mean_std", "stx_mean_ci", "stx_median_iqr", "stx_shaded_line"):
        suffix = method.replace("stx_", "")
        columns.append(f"{prefix}{id_val}_{suffix}_x")
        columns.append(f"{prefix}{id_val}_{suffix}_y")
        columns.append(f"{prefix}{id_val}_{suffix}_lower")
        columns.append(f"{prefix}{id_val}_{suffix}_upper")

    elif method.startswith("sns_"):
        sns_type = method.replace("sns_", "")
        if sns_type in ("boxplot", "violinplot"):
            columns.append(f"{prefix}{id_val}_{sns_type}_data")
        elif sns_type in ("scatterplot", "lineplot"):
            columns.append(f"{prefix}{id_val}_{sns_type}_x")
            columns.append(f"{prefix}{id_val}_{sns_type}_y")
        elif sns_type == "barplot":
            columns.append(f"{prefix}{id_val}_barplot_x")
            columns.append(f"{prefix}{id_val}_barplot_y")
        elif sns_type == "histplot":
            columns.append(f"{prefix}{id_val}_histplot_bins")
            columns.append(f"{prefix}{id_val}_histplot_counts")
        elif sns_type == "kdeplot":
            columns.append(f"{prefix}{id_val}_kdeplot_x")
            columns.append(f"{prefix}{id_val}_kdeplot_y")

    return columns


def assert_csv_json_consistency(csv_path: str, json_path: str = None) -> None:
    """
    Assert that CSV data file and its JSON metadata are consistent.

    Raises AssertionError if the column names don't match.

    Parameters
    ----------
    csv_path : str
        Path to the CSV data file
    json_path : str, optional
        Path to the JSON metadata file. If not provided, assumes
        the JSON is at the same location with .json extension.

    Raises
    ------
    AssertionError
        If CSV and JSON column names don't match
    FileNotFoundError
        If CSV or JSON files don't exist

    Examples
    --------
    >>> assert_csv_json_consistency('/tmp/plot.csv')  # Passes silently if valid
    >>> # Or use in tests:
    >>> try:
    ...     assert_csv_json_consistency('/tmp/plot.csv')
    ... except AssertionError as e:
    ...     print(f"Validation failed: {e}")
    """
    result = verify_csv_json_consistency(csv_path, json_path)

    if result["errors"]:
        raise FileNotFoundError("\n".join(result["errors"]))

    if not result["valid"]:
        msg_parts = ["CSV/JSON consistency check failed:"]
        if result["missing_in_csv"]:
            msg_parts.append(
                f"  columns_actual missing in CSV: {result['missing_in_csv']}"
            )
        if result["extra_in_csv"]:
            msg_parts.append(f"  Extra columns in CSV: {result['extra_in_csv']}")
        if result.get("data_ref_missing"):
            msg_parts.append(
                f"  data_ref columns missing in CSV: {result['data_ref_missing']}"
            )
        raise AssertionError("\n".join(msg_parts))


def verify_csv_json_consistency(csv_path: str, json_path: str = None) -> dict:
    """
    Verify consistency between CSV data file and its JSON metadata.

    This function checks that:
    1. Column names in the CSV file match those declared in JSON's columns_actual
    2. Artist data_ref values in JSON match actual CSV column names

    Parameters
    ----------
    csv_path : str
        Path to the CSV data file
    json_path : str, optional
        Path to the JSON metadata file. If not provided, assumes
        the JSON is at the same location with .json extension.

    Returns
    -------
    dict
        Verification result with keys:
        - 'valid': bool - True if CSV and JSON are consistent
        - 'csv_columns': list - Column names found in CSV
        - 'json_columns': list - Column names declared in JSON
        - 'data_ref_columns': list - Column names from artist data_ref
        - 'missing_in_csv': list - Columns in JSON but not in CSV
        - 'extra_in_csv': list - Columns in CSV but not in JSON
        - 'data_ref_missing': list - data_ref columns not found in CSV
        - 'errors': list - Any error messages

    Examples
    --------
    >>> result = verify_csv_json_consistency('/tmp/plot.csv')
    >>> print(result['valid'])
    True
    >>> print(result['missing_in_csv'])
    []
    """
    import json
    import os

    import pandas as pd

    result = {
        "valid": False,
        "csv_columns": [],
        "json_columns": [],
        "data_ref_columns": [],
        "missing_in_csv": [],
        "extra_in_csv": [],
        "data_ref_missing": [],
        "errors": [],
    }

    # Determine JSON path
    if json_path is None:
        base, _ = os.path.splitext(csv_path)
        json_path = base + ".json"

    # Check files exist
    if not os.path.exists(csv_path):
        result["errors"].append(f"CSV file not found: {csv_path}")
        return result
    if not os.path.exists(json_path):
        result["errors"].append(f"JSON file not found: {json_path}")
        return result

    try:
        # Read CSV columns
        df = pd.read_csv(csv_path, nrows=0)  # Just read header
        csv_columns = list(df.columns)
        result["csv_columns"] = csv_columns
    except Exception as e:
        result["errors"].append(f"Error reading CSV: {e}")
        return result

    try:
        # Read JSON metadata
        with open(json_path) as f:
            metadata = json.load(f)

        # Get columns_actual from data section
        json_columns = []
        if "data" in metadata and "columns_actual" in metadata["data"]:
            json_columns = metadata["data"]["columns_actual"]
        result["json_columns"] = json_columns

        # Extract data_ref columns from artists
        # Skip 'derived_from' key as it contains descriptive text, not CSV column names
        # Also skip 'row_index' as it's a numeric index, not a column name
        data_ref_columns = []
        skip_keys = {"derived_from", "row_index"}
        if "axes" in metadata:
            for ax_key, ax_data in metadata["axes"].items():
                if "artists" in ax_data:
                    for artist in ax_data["artists"]:
                        if "data_ref" in artist:
                            for key, val in artist["data_ref"].items():
                                if key not in skip_keys and isinstance(val, str):
                                    data_ref_columns.append(val)
        result["data_ref_columns"] = data_ref_columns

    except Exception as e:
        result["errors"].append(f"Error reading JSON: {e}")
        return result

    # Compare columns_actual with CSV
    csv_set = set(csv_columns)
    json_set = set(json_columns)

    result["missing_in_csv"] = list(json_set - csv_set)
    result["extra_in_csv"] = list(csv_set - json_set)

    # Check data_ref columns exist in CSV (if there are any)
    if data_ref_columns:
        data_ref_set = set(data_ref_columns)
        result["data_ref_missing"] = list(data_ref_set - csv_set)

    # Valid only if columns_actual matches AND data_ref columns are found in CSV
    result["valid"] = (
        len(result["missing_in_csv"]) == 0
        and len(result["extra_in_csv"]) == 0
        and len(result["data_ref_missing"]) == 0
    )

    return result


def collect_recipe_metadata(
    fig,
    ax=None,
    auto_crop: bool = True,
    crop_margin_mm: float = 1.0,
) -> Dict:
    """
    Collect minimal "recipe" metadata from figure - method calls + data refs.

    Unlike `collect_figure_metadata()` which captures every rendered artist,
    this function captures only what's needed to reproduce the figure:
    - Figure/axes dimensions and limits
    - Method calls with arguments (from ax.history)
    - Data column references for CSV linkage
    - Cropping settings

    This produces much smaller JSON files (e.g., 60 lines vs 1300 for histogram).

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to collect metadata from
    ax : matplotlib.axes.Axes or AxisWrapper, optional
        Primary axes to collect from. If not provided, uses first axes.
    auto_crop : bool, optional
        Whether auto-cropping is enabled. Default is True.
    crop_margin_mm : float, optional
        Margin in mm for auto-cropping. Default is 1.0.

    Returns
    -------
    dict
        Minimal metadata dictionary with structure:
        - scitex_schema: "scitex.plt.figure.recipe"
        - scitex_schema_version: "0.2.0"
        - figure: {size_mm, dpi, mode, auto_crop, crop_margin_mm}
        - axes: {ax_00: {xaxis, yaxis, calls: [...]}}
        - data: {csv_path, columns}

    Examples
    --------
    >>> fig, ax = scitex.plt.subplots()
    >>> ax.hist(data, bins=40, id="histogram")
    >>> metadata = collect_recipe_metadata(fig, ax)
    >>> # Result has ~60 lines instead of ~1300
    """
    import datetime
    import uuid

    import matplotlib

    import scitex

    metadata = {
        "scitex_schema": "scitex.plt.figure.recipe",
        "scitex_schema_version": "0.2.0",
        "figure_uuid": str(uuid.uuid4()),
        "runtime": {
            "scitex_version": scitex.__version__,
            "matplotlib_version": matplotlib.__version__,
            "created_at": datetime.datetime.now().isoformat(),
        },
    }

    # Collect axes - handle AxesWrapper (multi-axes) properly
    all_axes = []  # List of (ax_wrapper, row, col) tuples
    grid_shape = (1, 1)

    if ax is not None:
        # Handle AxesWrapper (multi-axes) - extract individual AxisWrappers with positions
        if hasattr(ax, "_axes_scitex"):
            import numpy as np

            axes_array = ax._axes_scitex
            if isinstance(axes_array, np.ndarray):
                grid_shape = axes_array.shape
                for idx, ax_item in enumerate(axes_array.flat):
                    row = idx // grid_shape[1]
                    col = idx % grid_shape[1]
                    all_axes.append((ax_item, row, col))
            else:
                all_axes = [(axes_array, 0, 0)]
        # Handle AxisWrapper (single axes)
        elif hasattr(ax, "_axis_mpl"):
            all_axes = [(ax, 0, 0)]
        else:
            # Assume it's a matplotlib axes
            all_axes = [(ax, 0, 0)]
    elif hasattr(fig, "axes") and len(fig.axes) > 0:
        # Fallback to figure axes (linear indexing)
        for idx, ax_item in enumerate(fig.axes):
            all_axes.append((ax_item, 0, idx))

    # Figure-level properties
    if all_axes:
        try:
            from ._figure_from_axes_mm import get_dimension_info

            first_ax_tuple = all_axes[0]
            first_ax = first_ax_tuple[0]
            # Get underlying matplotlib axis if wrapped
            mpl_ax = getattr(first_ax, "_axis_mpl", first_ax)
            dim_info = get_dimension_info(fig, mpl_ax)

            # Convert to plain lists/floats for JSON serialization
            size_mm = dim_info["figure_size_mm"]
            if hasattr(size_mm, "tolist"):
                size_mm = size_mm.tolist()
            elif isinstance(size_mm, (list, tuple)):
                size_mm = [float(v) if hasattr(v, "value") else v for v in size_mm]

            metadata["figure"] = {
                "size_mm": size_mm,
                "dpi": int(dim_info["dpi"]),
                "auto_crop": auto_crop,
                "crop_margin_mm": crop_margin_mm,
            }

            # Add top-level axes_bbox_px for canvas/web alignment (x0/y0/x1/y1 format)
            # x0: left edge (Y-axis position), y1: bottom edge (X-axis position)
            if "axes_bbox_px" in dim_info:
                bbox = dim_info["axes_bbox_px"]
                metadata["axes_bbox_px"] = {
                    "x0": int(bbox["x0"]),
                    "y0": int(bbox["y0"]),
                    "x1": int(bbox["x1"]),
                    "y1": int(bbox["y1"]),
                    "width": int(bbox["width"]),
                    "height": int(bbox["height"]),
                }
            if "axes_bbox_mm" in dim_info:
                bbox = dim_info["axes_bbox_mm"]
                metadata["axes_bbox_mm"] = {
                    "x0": round(float(bbox["x0"]), 2),
                    "y0": round(float(bbox["y0"]), 2),
                    "x1": round(float(bbox["x1"]), 2),
                    "y1": round(float(bbox["y1"]), 2),
                    "width": round(float(bbox["width"]), 2),
                    "height": round(float(bbox["height"]), 2),
                }
        except Exception:
            pass

    # Add mode from scitex metadata
    scitex_meta = None
    if ax is not None and hasattr(ax, "_scitex_metadata"):
        scitex_meta = ax._scitex_metadata
    elif hasattr(fig, "_scitex_metadata"):
        scitex_meta = fig._scitex_metadata

    if scitex_meta:
        if "figure" not in metadata:
            metadata["figure"] = {}
        if "mode" in scitex_meta:
            metadata["figure"]["mode"] = scitex_meta["mode"]
        # Include style_mm for reproducibility (thickness, fonts, etc.)
        if "style_mm" in scitex_meta:
            metadata["style"] = scitex_meta["style_mm"]

    # Collect per-axes metadata with calls
    if all_axes:
        metadata["axes"] = {}
        for current_ax, row, col in all_axes:
            # Use row-col format: ax_00, ax_01, ax_10, ax_11 for 2x2 grid
            ax_key = f"ax_{row}{col}"

            # Get underlying matplotlib axis if wrapped
            mpl_ax = getattr(current_ax, "_axis_mpl", current_ax)

            ax_meta = {"grid_position": {"row": row, "col": col}}

            # Additional position info from scitex_metadata if available
            if hasattr(current_ax, "_scitex_metadata"):
                pos = current_ax._scitex_metadata.get("position_in_grid")
                if pos:
                    ax_meta["grid_position"] = {"row": pos[0], "col": pos[1]}

            # Axis labels and limits (minimal - for axis alignment)
            try:
                xlim = mpl_ax.get_xlim()
                ylim = mpl_ax.get_ylim()
                ax_meta["xaxis"] = {
                    "label": mpl_ax.get_xlabel() or "",
                    "lim": [round(xlim[0], 4), round(xlim[1], 4)],
                }
                ax_meta["yaxis"] = {
                    "label": mpl_ax.get_ylabel() or "",
                    "lim": [round(ylim[0], 4), round(ylim[1], 4)],
                }
            except Exception:
                pass

            # Method calls from history - the core "recipe"
            # Pass row and col for proper data_ref column naming
            ax_index = row * grid_shape[1] + col
            ax_meta["calls"] = _extract_calls_from_history(current_ax, ax_index)

            metadata["axes"][ax_key] = ax_meta

    return metadata


def _extract_calls_from_history(ax, ax_index: int) -> List[dict]:
    """
    Extract method call records from axis history.

    Parameters
    ----------
    ax : AxisWrapper or matplotlib.axes.Axes
        Axis to extract history from
    ax_index : int
        Index of axis in figure (for CSV column naming)

    Returns
    -------
    list
        List of call records: [{id, method, data_ref, kwargs}, ...]
    """
    calls = []

    # Check for scitex wrapper with history
    if not hasattr(ax, "history") and not hasattr(ax, "_ax_history"):
        return calls

    # Get history dict
    history = getattr(ax, "history", None)
    if history is None:
        history = getattr(ax, "_ax_history", {})

    # Get grid position
    ax_row = 0
    ax_col = 0
    if hasattr(ax, "_scitex_metadata"):
        pos = ax._scitex_metadata.get("position_in_grid", [0, 0])
        ax_row, ax_col = pos[0], pos[1]

    for trace_id, record in history.items():
        # record format: (id, method_name, tracked_dict, kwargs)
        if not isinstance(record, (list, tuple)) or len(record) < 3:
            continue

        call_id, method_name, tracked_dict = record[0], record[1], record[2]
        kwargs = record[3] if len(record) > 3 else {}

        call = {
            "id": str(call_id),
            "method": method_name,
        }

        # Build data_ref from tracked_dict to CSV column names
        data_ref = _build_data_ref(call_id, method_name, tracked_dict, ax_row, ax_col)
        if data_ref:
            call["data_ref"] = data_ref

        # Filter kwargs to only style-relevant ones (not data)
        style_kwargs = _filter_style_kwargs(kwargs, method_name)
        if style_kwargs:
            call["kwargs"] = style_kwargs

        calls.append(call)

    return calls


def _build_data_ref(
    trace_id, method_name: str, tracked_dict: dict, ax_row: int, ax_col: int
) -> dict:
    """
    Build data_ref mapping from tracked_dict to CSV column names.

    Parameters
    ----------
    trace_id : str
        Trace identifier
    method_name : str
        Name of the method called
    tracked_dict : dict
        Data tracked by the method (contains arrays, dataframes)
    ax_row, ax_col : int
        Axis position in grid

    Returns
    -------
    dict
        Mapping of variable names to CSV column names
    """
    prefix = f"ax-row-{ax_row}-col-{ax_col}_trace-id-{trace_id}_variable-"

    data_ref = {}

    # Method-specific column naming
    if method_name == "hist":
        # Histogram: raw data + computed bins
        data_ref["raw_data"] = f"{prefix}raw-data"
        data_ref["bin_centers"] = f"{prefix}bin-centers"
        data_ref["bin_counts"] = f"{prefix}bin-counts"
    elif method_name in ("plot", "scatter", "step", "errorbar"):
        # Standard x, y plots
        data_ref["x"] = f"{prefix}x"
        data_ref["y"] = f"{prefix}y"
        # Check for error bars in tracked_dict
        if tracked_dict and "yerr" in tracked_dict:
            data_ref["yerr"] = f"{prefix}yerr"
        if tracked_dict and "xerr" in tracked_dict:
            data_ref["xerr"] = f"{prefix}xerr"
    elif method_name in ("bar", "barh"):
        data_ref["x"] = f"{prefix}x"
        data_ref["y"] = f"{prefix}y"
    elif method_name == "stem":
        data_ref["x"] = f"{prefix}x"
        data_ref["y"] = f"{prefix}y"
    elif method_name in ("fill_between", "fill_betweenx"):
        data_ref["x"] = f"{prefix}x"
        data_ref["y1"] = f"{prefix}y1"
        data_ref["y2"] = f"{prefix}y2"
    elif method_name in ("imshow", "matshow", "pcolormesh"):
        data_ref["data"] = f"{prefix}data"
    elif method_name in ("contour", "contourf"):
        data_ref["x"] = f"{prefix}x"
        data_ref["y"] = f"{prefix}y"
        data_ref["z"] = f"{prefix}z"
    elif method_name in ("boxplot", "violinplot"):
        data_ref["data"] = f"{prefix}data"
    elif method_name == "pie":
        data_ref["x"] = f"{prefix}x"
    elif method_name in ("quiver", "streamplot"):
        data_ref["x"] = f"{prefix}x"
        data_ref["y"] = f"{prefix}y"
        data_ref["u"] = f"{prefix}u"
        data_ref["v"] = f"{prefix}v"
    elif method_name == "hexbin":
        data_ref["x"] = f"{prefix}x"
        data_ref["y"] = f"{prefix}y"
    elif method_name == "hist2d":
        data_ref["x"] = f"{prefix}x"
        data_ref["y"] = f"{prefix}y"
    elif method_name == "kde":
        data_ref["x"] = f"{prefix}x"
        data_ref["y"] = f"{prefix}y"
    # SciTeX custom methods (stx_*) - use same naming as matplotlib wrappers
    elif method_name == "stx_line":
        data_ref["x"] = f"{prefix}x"
        data_ref["y"] = f"{prefix}y"
    elif method_name in (
        "stx_mean_std",
        "stx_mean_ci",
        "stx_median_iqr",
        "stx_shaded_line",
    ):
        data_ref["x"] = f"{prefix}x"
        data_ref["y_lower"] = f"{prefix}y-lower"
        data_ref["y_middle"] = f"{prefix}y-middle"
        data_ref["y_upper"] = f"{prefix}y-upper"
    elif method_name in ("stx_box", "stx_violin"):
        data_ref["data"] = f"{prefix}data"
    elif method_name == "stx_scatter_hist":
        data_ref["x"] = f"{prefix}x"
        data_ref["y"] = f"{prefix}y"
    elif method_name in ("stx_heatmap", "stx_conf_mat", "stx_image", "stx_raster"):
        data_ref["data"] = f"{prefix}data"
    elif method_name in ("stx_kde", "stx_ecdf"):
        data_ref["x"] = f"{prefix}x"
        data_ref["y"] = f"{prefix}y"
    elif method_name.startswith("stx_"):
        # Generic fallback for other stx_ methods
        data_ref["x"] = f"{prefix}x"
        data_ref["y"] = f"{prefix}y"
    else:
        # Generic fallback for tracked data
        if tracked_dict:
            if "x" in tracked_dict or "args" in tracked_dict:
                data_ref["x"] = f"{prefix}x"
                data_ref["y"] = f"{prefix}y"

    return data_ref


def _filter_style_kwargs(kwargs: dict, method_name: str) -> dict:
    """
    Filter kwargs to only include style-relevant parameters.

    Removes data arrays and internal parameters, keeps style settings
    that affect appearance (color, linewidth, etc.).

    Parameters
    ----------
    kwargs : dict
        Original keyword arguments
    method_name : str
        Name of the method

    Returns
    -------
    dict
        Filtered kwargs with only style parameters
    """
    if not kwargs:
        return {}

    # Style-relevant kwargs to keep
    style_keys = {
        "color",
        "c",
        "facecolor",
        "edgecolor",
        "linecolor",
        "linewidth",
        "lw",
        "linestyle",
        "ls",
        "marker",
        "markersize",
        "ms",
        "markerfacecolor",
        "markeredgecolor",
        "alpha",
        "zorder",
        "label",
        "bins",
        "density",
        "histtype",
        "orientation",
        "width",
        "height",
        "align",
        "cmap",
        "vmin",
        "vmax",
        "norm",
        "levels",
        "extend",
        "scale",
        "units",
        "autopct",
        "explode",
        "shadow",
        "startangle",
    }

    filtered = {}
    for key, value in kwargs.items():
        if key in style_keys:
            # Skip if value is a large array (data, not style)
            if hasattr(value, "__len__") and not isinstance(value, str):
                if len(value) > 10:
                    continue
            # Round float values to 4 decimal places for cleaner JSON
            if isinstance(value, float):
                value = round(value, 4)
            filtered[key] = value

    return filtered


if __name__ == "__main__":
    import numpy as np

    from ._figure_from_axes_mm import create_axes_with_size_mm

    print("=" * 60)
    print("METADATA COLLECTION DEMO")
    print("=" * 60)

    # Create a figure with mm control
    print("\n1. Creating figure with mm control...")
    fig, ax = create_axes_with_size_mm(
        axes_width_mm=30,
        axes_height_mm=21,
        mode="publication",
        style_mm={
            "axis_thickness_mm": 0.2,
            "trace_thickness_mm": 0.12,
            "tick_length_mm": 0.8,
        },
    )

    # Plot something
    x = np.linspace(0, 2 * np.pi, 100)
    ax.plot(x, np.sin(x), "b-")
    ax.set_xlabel("X axis")
    ax.set_ylabel("Y axis")

    # Collect metadata
    print("\n2. Collecting metadata...")
    metadata = collect_figure_metadata(fig, ax)

    # Display metadata
    print("\n3. Collected metadata:")
    print("-" * 60)
    import json

    print(json.dumps(metadata, indent=2))
    print("-" * 60)

    print("\n✅ Metadata collection complete!")
    print("\nKey fields collected:")
    print(f"  • Software version: {metadata['scitex']['version']}")
    print(f"  • Timestamp: {metadata['scitex']['created_at']}")
    if "dimensions" in metadata:
        print(f"  • Axes size: {metadata['dimensions']['axes_size_mm']} mm")
        print(f"  • DPI: {metadata['dimensions']['dpi']}")
    if "runtime" in metadata and "mode" in metadata["runtime"]:
        print(f"  • Mode: {metadata['scitex']['mode']}")
    if "runtime" in metadata and "style_mm" in metadata["runtime"]:
        print("  • Style: Embedded ✓")

# EOF
