#!/usr/bin/env python3
# Timestamp: "2026-01-24 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/plt/utils/_metadata/_csv.py

"""
CSV column naming and hash utilities for figure metadata.

Provides functions for extracting CSV column information from scitex history
and computing data hashes for reproducibility verification.
"""

from typing import List, Optional


def _get_csv_column_names(
    trace_id: str, ax_row: int = 0, ax_col: int = 0, variables: list = None
) -> dict:
    """
    Get the CSV column names for a given trace.

    Parameters
    ----------
    trace_id : str
        Unique ID of the trace (e.g., "plot_0", "scatter_1")
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
    from .._csv_column_naming import get_csv_column_name

    if variables is None:
        variables = ["x", "y"]

    data_ref = {}
    for var in variables:
        data_ref[var] = get_csv_column_name(var, ax_row, ax_col, trace_id=trace_id)

    return data_ref


def _extract_csv_columns_from_history(ax) -> list:
    """
    Extract CSV column names from scitex history for all plot types.

    Parameters
    ----------
    ax : AxisWrapper or matplotlib.axes.Axes
        The axes to extract CSV column info from

    Returns
    -------
    list
        List of dictionaries containing CSV column mappings for each tracked plot
    """
    # Get axes position for CSV column naming
    ax_row, ax_col = 0, 0
    if hasattr(ax, "_scitex_metadata") and "position_in_grid" in ax._scitex_metadata:
        pos = ax._scitex_metadata["position_in_grid"]
        ax_row, ax_col = pos[0], pos[1]

    csv_columns_list = []

    if not hasattr(ax, "history") or len(ax.history) == 0:
        return csv_columns_list

    for trace_index, (record_id, record) in enumerate(ax.history.items()):
        if not isinstance(record, tuple) or len(record) < 4:
            continue

        id_val, method, tracked_dict, kwargs = record

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
) -> List[str]:
    """
    Get CSV column names for a specific plotting method using trace index.

    Parameters
    ----------
    id_val : str
        The plot ID
    method : str
        The plotting method name
    tracked_dict : dict
        The tracked data dictionary
    kwargs : dict
        The keyword arguments passed to the plot
    ax_row : int
        Row index of axes in grid
    ax_col : int
        Column index of axes in grid
    trace_index : int
        Index of this trace

    Returns
    -------
    list
        List of column names that will be in the CSV
    """
    from .._csv_column_naming import get_csv_column_name

    columns = []

    method_columns = {
        ("plot", "stx_line"): ["x", "y"],
        ("scatter", "plot_scatter"): ["x", "y"],
        ("bar", "barh"): ["x", "height"],
        ("hist",): ["bins", "counts"],
        ("boxplot", "stx_box"): ["data"],
        ("violinplot", "stx_violin"): ["data"],
        ("errorbar",): ["x", "y", "yerr"],
        ("fill_between",): ["x", "y1", "y2"],
        ("imshow", "stx_heatmap", "stx_image"): ["data"],
        ("stx_kde", "stx_ecdf"): ["x", "y"],
        ("stx_mean_std", "stx_mean_ci", "stx_median_iqr", "stx_shaded_line"): [
            "x",
            "y",
            "lower",
            "upper",
        ],
    }

    for methods, vars in method_columns.items():
        if method in methods:
            columns = [
                get_csv_column_name(v, ax_row, ax_col, trace_index=trace_index)
                for v in vars
            ]
            return columns

    # Handle seaborn methods
    if method.startswith("sns_"):
        sns_type = method.replace("sns_", "")
        sns_columns = {
            ("boxplot", "violinplot"): ["data"],
            ("scatterplot", "lineplot"): ["x", "y"],
            ("barplot",): ["x", "y"],
            ("histplot",): ["bins", "counts"],
            ("kdeplot",): ["x", "y"],
        }
        for types, vars in sns_columns.items():
            if sns_type in types:
                columns = [
                    get_csv_column_name(v, ax_row, ax_col, trace_index=trace_index)
                    for v in vars
                ]
                return columns

    return columns


def _get_csv_columns_for_method(
    id_val, method, tracked_dict, kwargs, ax_index: int
) -> List[str]:
    """
    Get CSV column names for a specific plotting method.

    Uses the same formatters that generate the CSV to ensure consistency.

    Parameters
    ----------
    id_val : str
        The plot ID
    method : str
        The plotting method name
    tracked_dict : dict
        The tracked data dictionary
    kwargs : dict
        The keyword arguments passed to the plot
    ax_index : int
        Flattened index of axes

    Returns
    -------
    list
        List of column names that will be in the CSV
    """
    # format_record removed in figrecipe migration; use pattern-based fallback directly
    return _get_csv_columns_fallback(id_val, method, tracked_dict, kwargs, ax_index)


def _get_csv_columns_fallback(
    id_val, method, tracked_dict, kwargs, ax_index: int
) -> List[str]:
    """Fallback pattern-based CSV column name generation."""
    prefix = f"ax_{ax_index:02d}_"
    columns = []
    args = tracked_dict.get("args", []) if tracked_dict else []

    if method in ("boxplot", "stx_box"):
        columns = _get_boxplot_columns(args, kwargs, prefix, id_val)
    elif method in ("plot", "stx_line"):
        columns = [f"{prefix}{id_val}_plot_x", f"{prefix}{id_val}_plot_y"]
    elif method in ("scatter", "plot_scatter"):
        columns = [f"{prefix}{id_val}_scatter_x", f"{prefix}{id_val}_scatter_y"]
    elif method in ("bar", "barh"):
        columns = [f"{prefix}{id_val}_bar_x", f"{prefix}{id_val}_bar_height"]
    elif method == "hist":
        columns = [f"{prefix}{id_val}_hist_bins", f"{prefix}{id_val}_hist_counts"]
    elif method in ("violinplot", "stx_violin"):
        columns = _get_violin_columns(args, prefix, id_val)
    elif method == "errorbar":
        columns = [
            f"{prefix}{id_val}_errorbar_x",
            f"{prefix}{id_val}_errorbar_y",
            f"{prefix}{id_val}_errorbar_yerr",
        ]
    elif method == "fill_between":
        columns = [
            f"{prefix}{id_val}_fill_x",
            f"{prefix}{id_val}_fill_y1",
            f"{prefix}{id_val}_fill_y2",
        ]
    elif method in ("imshow", "stx_heatmap", "stx_image"):
        if args and hasattr(args[0], "shape") and len(args[0].shape) >= 2:
            columns = [f"{prefix}{id_val}_image_data"]
    elif method in ("stx_kde", "stx_ecdf"):
        suffix = method.replace("stx_", "")
        columns = [f"{prefix}{id_val}_{suffix}_x", f"{prefix}{id_val}_{suffix}_y"]
    elif method in ("stx_mean_std", "stx_mean_ci", "stx_median_iqr", "stx_shaded_line"):
        suffix = method.replace("stx_", "")
        columns = [
            f"{prefix}{id_val}_{suffix}_x",
            f"{prefix}{id_val}_{suffix}_y",
            f"{prefix}{id_val}_{suffix}_lower",
            f"{prefix}{id_val}_{suffix}_upper",
        ]
    elif method.startswith("sns_"):
        columns = _get_seaborn_columns(method, prefix, id_val)

    return columns


def _get_boxplot_columns(args, kwargs, prefix, id_val) -> List[str]:
    """Get columns for boxplot data."""
    import numpy as np

    columns = []
    if len(args) >= 1:
        data = args[0]
        labels = kwargs.get("labels", None) if kwargs else None

        from scitex.types import is_listed_X as scitex_types_is_listed_X

        if isinstance(data, np.ndarray) or scitex_types_is_listed_X(data, [float, int]):
            if labels and len(labels) == 1:
                columns.append(f"{prefix}{id_val}_{labels[0]}")
            else:
                columns.append(f"{prefix}{id_val}_boxplot_0")
        else:
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

    return columns


def _get_violin_columns(args, prefix, id_val) -> List[str]:
    """Get columns for violin plot data."""
    columns = []
    if len(args) >= 1:
        data = args[0]
        try:
            num_violins = len(data)
            for i in range(num_violins):
                columns.append(f"{prefix}{id_val}_violin_{i}")
        except TypeError:
            columns.append(f"{prefix}{id_val}_violin_0")
    return columns


def _get_seaborn_columns(method, prefix, id_val) -> List[str]:
    """Get columns for seaborn plots."""
    sns_type = method.replace("sns_", "")
    if sns_type in ("boxplot", "violinplot"):
        return [f"{prefix}{id_val}_{sns_type}_data"]
    elif sns_type in ("scatterplot", "lineplot"):
        return [f"{prefix}{id_val}_{sns_type}_x", f"{prefix}{id_val}_{sns_type}_y"]
    elif sns_type == "barplot":
        return [f"{prefix}{id_val}_barplot_x", f"{prefix}{id_val}_barplot_y"]
    elif sns_type == "histplot":
        return [f"{prefix}{id_val}_histplot_bins", f"{prefix}{id_val}_histplot_counts"]
    elif sns_type == "kdeplot":
        return [f"{prefix}{id_val}_kdeplot_x", f"{prefix}{id_val}_kdeplot_y"]
    return []


def _compute_csv_hash_from_df(df) -> Optional[str]:
    """
    Compute a hash of CSV data from a DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame to compute hash from

    Returns
    -------
    str or None
        SHA256 hash (first 16 chars) or None if unable to compute
    """
    import hashlib

    try:
        if df is None or df.empty:
            return None

        csv_string = df.to_csv(index=False)
        hash_obj = hashlib.sha256(csv_string.encode("utf-8"))
        return hash_obj.hexdigest()[:16]

    except Exception:
        return None


def _compute_csv_hash(ax_or_df) -> Optional[str]:
    """
    Compute a hash of the CSV data for reproducibility verification.

    Parameters
    ----------
    ax_or_df : AxisWrapper, matplotlib.axes.Axes, or pandas.DataFrame
        The axes or DataFrame to compute hash from

    Returns
    -------
    str or None
        SHA256 hash (first 16 chars) or None if unable to compute
    """
    import hashlib

    import pandas as pd

    if isinstance(ax_or_df, pd.DataFrame):
        return _compute_csv_hash_from_df(ax_or_df)

    ax = ax_or_df

    if not hasattr(ax, "export_as_csv"):
        return None

    try:
        ax_index = 0
        df = ax.export_as_csv()

        if df is None or df.empty:
            return None

        prefix = f"ax_{ax_index:02d}_"
        new_cols = []
        for col in df.columns:
            col_str = str(col)
            if not col_str.startswith(prefix):
                col_str = f"{prefix}{col_str}"
            new_cols.append(col_str)
        df.columns = new_cols

        csv_string = df.to_csv(index=False)
        hash_obj = hashlib.sha256(csv_string.encode("utf-8"))
        return hash_obj.hexdigest()[:16]

    except Exception:
        return None


# EOF
