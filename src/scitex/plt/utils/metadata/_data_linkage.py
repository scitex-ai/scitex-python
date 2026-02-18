#!/usr/bin/env python3
# File: scitex/plt/utils/metadata/_data_linkage.py

"""
CSV data linkage utilities.

This module provides functions to extract CSV column mappings and compute
data hashes for linking JSON metadata to CSV data files.

This module has been refactored: the implementation is now split across multiple
specialized modules. This file serves as a backward compatibility layer and
contains legacy functions.
"""

import numpy as np

# Import from specialized modules
from ._csv_column_extraction import (
    _extract_csv_columns_from_history,
    _get_csv_columns_for_method_with_index,
)
from ._csv_hash import _compute_csv_hash, _compute_csv_hash_from_df
from ._csv_verification import assert_csv_json_consistency, verify_csv_json_consistency
from ._recipe_extraction import (
    collect_recipe_metadata,
)

__all__ = [
    "_extract_csv_columns_from_history",
    "_get_csv_columns_for_method_with_index",
    "_compute_csv_hash",
    "_compute_csv_hash_from_df",
    "assert_csv_json_consistency",
    "verify_csv_json_consistency",
    "collect_recipe_metadata",
    "_get_csv_columns_for_method",  # Legacy function
]


def _get_csv_columns_for_method(
    id_val, method, tracked_dict, kwargs, ax_index: int
) -> list:
    """
    Get CSV column names for a specific plotting method (legacy function).

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
    # format_record removed in figrecipe migration; use pattern-based generation directly
    # Fallback: Pattern-based column name generation
    prefix = f"ax_{ax_index:02d}_"
    columns = []

    # Get args from tracked_dict
    args = tracked_dict.get("args", []) if tracked_dict else []

    if method in ("boxplot", "stx_box"):
        # Boxplot: one column per box
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


# Demo code (from original module)
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
    from ._core import collect_figure_metadata

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
