#!/usr/bin/env python3
# Timestamp: "2026-02-17 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/plt/_spec_builders.py
"""Build figrecipe spec dicts from parameter dicts.

This module converts query-style parameter dicts (from REST APIs, CLIs, etc.)
into figrecipe-compatible spec dicts. It is the single source of truth for
kind registries and spec construction logic.

Usage
-----
>>> from scitex.plt import build_spec, build_spec_from_csv
>>> spec = build_spec({"kind": "line", "y": "1,2,3,4", "title": "Demo"})
>>> spec = build_spec_from_csv("/tmp/data.csv", {"kind": "scatter", "x_col": "x", "y_col": "y"})
"""

from typing import Dict, List, Union

__all__ = [
    "XY_KINDS",
    "DATA_KINDS",
    "LABEL_KINDS",
    "MATRIX_KINDS",
    "ALL_KINDS",
    "KIND_ALIASES",
    "build_spec",
    "build_spec_from_csv",
]

# ---- Kind registries --------------------------------------------------------

XY_KINDS = {"line", "scatter", "step", "errorbar", "stem", "bar", "barh"}
DATA_KINDS = {"hist", "box", "boxplot", "violin", "violinplot"}
LABEL_KINDS = {"pie"}
MATRIX_KINDS = {"heatmap", "imshow"}

ALL_KINDS = XY_KINDS | DATA_KINDS | LABEL_KINDS | MATRIX_KINDS
KIND_ALIASES = {"box": "boxplot", "violin": "violinplot"}

_UNSUPPORTED_MSG = (
    "Use: line, scatter, bar, barh, hist, box, violin, pie, "
    "heatmap, step, errorbar, stem"
)


# ---- Parse helpers ----------------------------------------------------------


def _parse_floats(s: str) -> List[float]:
    return [float(x.strip()) for x in s.split(",") if x.strip()]


def _parse_strings(s: str) -> List[str]:
    return [x.strip() for x in s.split(",") if x.strip()]


def _try_parse_floats(s: str) -> list:
    try:
        return _parse_floats(s)
    except ValueError:
        return _parse_strings(s)


# ---- Internal builders ------------------------------------------------------


def _init_spec(params: dict) -> tuple:
    kind = params.get("kind", "").lower()
    if not kind:
        raise ValueError("'kind' parameter is required")

    plot_kind = KIND_ALIASES.get(kind, kind)

    figure: Dict = {"style": "SCITEX"}
    if "width" in params:
        figure["width_mm"] = int(params["width"])
    if "height" in params:
        figure["height_mm"] = int(params["height"])

    spec: Dict = {"figure": figure, "plots": []}
    plot_entry: Dict = {"type": plot_kind}

    return spec, plot_entry, kind, plot_kind


def _finalize_spec(spec: dict, plot_entry: dict, params: dict) -> dict:
    color = params.get("color", "")
    if color:
        plot_entry["color"] = color

    spec["plots"].append(plot_entry)

    for key in ("title", "xlabel", "ylabel"):
        val = params.get(key, "")
        if val:
            spec[key] = val

    return spec


def _validate_kind(kind: str) -> None:
    if kind not in ALL_KINDS and kind not in KIND_ALIASES:
        raise ValueError(f"Unsupported kind: '{kind}'. {_UNSUPPORTED_MSG}")


def _build_xy(spec, plot_entry, params, kind):
    y_str = params.get("y", "")
    if not y_str:
        raise ValueError(f"'y' parameter is required for kind={kind}")
    plot_entry["y"] = _parse_floats(y_str)

    x_str = params.get("x", "")
    if x_str:
        x_vals = _try_parse_floats(x_str)
        if isinstance(x_vals[0], str):
            spec["xticks"] = {
                "positions": list(range(len(x_vals))),
                "labels": x_vals,
            }
            plot_entry["x"] = list(range(len(x_vals)))
        else:
            plot_entry["x"] = x_vals

    yerr_str = params.get("yerr", "")
    if yerr_str:
        plot_entry["yerr"] = _parse_floats(yerr_str)
        if kind != "errorbar":
            plot_entry["type"] = "errorbar"


def _build_distribution(spec, plot_entry, params, kind, plot_kind):
    groups = []
    group_labels = []

    data_str = params.get("data", "")
    if not data_str:
        raise ValueError(f"'data' parameter is required for kind={kind}")
    groups.append(_parse_floats(data_str))
    group_labels.append("Group 1")

    for i in range(2, 7):
        extra = params.get(f"data{i}", "")
        if extra:
            groups.append(_parse_floats(extra))
            group_labels.append(f"Group {i}")

    labels_str = params.get("labels", "")
    if labels_str:
        group_labels = _parse_strings(labels_str)

    if plot_kind in ("boxplot", "violinplot"):
        plot_entry["data"] = groups
        plot_entry["positions"] = list(range(len(groups)))
        spec["xticks"] = {
            "positions": list(range(len(groups))),
            "labels": group_labels[: len(groups)],
        }
    else:
        if len(groups) == 1:
            plot_entry["x"] = groups[0]
        else:
            plot_entry["x"] = groups


def _build_pie(plot_entry, params):
    data_str = params.get("data", "")
    if not data_str:
        raise ValueError("'data' parameter is required for kind=pie")
    plot_entry["x"] = _parse_floats(data_str)

    labels_str = params.get("labels", "")
    if labels_str:
        plot_entry["labels"] = _parse_strings(labels_str)


def _build_matrix(plot_entry, params, kind):
    data_str = params.get("data", "")
    if not data_str:
        raise ValueError(f"'data' parameter is required for kind={kind}")
    flat = _parse_floats(data_str)
    nrows = int(params.get("nrows", 0))
    ncols = int(params.get("ncols", 0))

    import numpy as np

    if nrows and ncols:
        if len(flat) != nrows * ncols:
            raise ValueError(
                f"data length {len(flat)} != nrows*ncols ({nrows}*{ncols})"
            )
        matrix = np.array(flat).reshape(nrows, ncols).tolist()
    else:
        n = len(flat)
        side = int(np.ceil(np.sqrt(n)))
        padded = flat + [0] * (side * side - n)
        matrix = np.array(padded).reshape(side, side).tolist()

    plot_entry["data"] = matrix
    plot_entry["type"] = "imshow"


# ---- Public API -------------------------------------------------------------


def build_spec(params: dict) -> dict:
    """Convert a parameter dict to a figrecipe spec dict.

    Parameters
    ----------
    params : dict
        Flat parameter dict. Required key: ``kind``.
        For XY plots: ``x``, ``y`` (comma-separated floats or strings).
        For distributions: ``data``, ``data2`` .. ``data6``, ``labels``.
        For pie: ``data``, ``labels``.
        For heatmap: ``data``, ``nrows``, ``ncols``.
        Optional: ``color``, ``title``, ``xlabel``, ``ylabel``,
        ``width``, ``height``, ``yerr``.

    Returns
    -------
    dict
        Figrecipe-compatible spec.

    Raises
    ------
    ValueError
        If required parameters are missing or kind is unsupported.
    """
    spec, plot_entry, kind, plot_kind = _init_spec(params)

    if kind in XY_KINDS:
        _build_xy(spec, plot_entry, params, kind)
    elif kind in DATA_KINDS or plot_kind in DATA_KINDS:
        _build_distribution(spec, plot_entry, params, kind, plot_kind)
    elif kind in LABEL_KINDS:
        _build_pie(plot_entry, params)
    elif kind in MATRIX_KINDS:
        _build_matrix(plot_entry, params, kind)
    else:
        _validate_kind(kind)

    return _finalize_spec(spec, plot_entry, params)


def build_spec_from_csv(
    csv_path: Union[str, "Path"],
    params: dict,
) -> dict:
    """Build a figrecipe spec from a CSV file path and parameters.

    Uses figrecipe's native ``data_file`` + column name resolution.

    Parameters
    ----------
    csv_path : str or Path
        Path to the CSV file.
    params : dict
        Flat parameter dict. Required: ``kind``.
        For XY: ``x_col``, ``y_col``.
        For distributions: ``data_col``.
        For pie: ``data_col``, ``labels_col``.
        For heatmap: ``data_col``.

    Returns
    -------
    dict
        Figrecipe-compatible spec.

    Raises
    ------
    ValueError
        If required parameters are missing or kind is unsupported.
    """
    spec, plot_entry, kind, plot_kind = _init_spec(params)
    plot_entry["data_file"] = str(csv_path)

    if kind in XY_KINDS:
        y_col = params.get("y_col", "")
        if not y_col:
            raise ValueError("'y_col' is required for XY plot kinds")
        plot_entry["y"] = y_col
        x_col = params.get("x_col", "")
        if x_col:
            plot_entry["x"] = x_col

    elif kind in DATA_KINDS or plot_kind in DATA_KINDS:
        data_col = params.get("data_col", "")
        if not data_col:
            raise ValueError("'data_col' is required for distribution plots")
        plot_entry["x"] = data_col

    elif kind in LABEL_KINDS:
        data_col = params.get("data_col", "")
        if not data_col:
            raise ValueError("'data_col' is required for pie charts")
        plot_entry["x"] = data_col
        labels_col = params.get("labels_col", "")
        if labels_col:
            plot_entry["labels"] = labels_col

    elif kind in MATRIX_KINDS:
        data_col = params.get("data_col", "")
        if not data_col:
            raise ValueError("'data_col' is required for heatmaps")
        plot_entry["data"] = data_col
        plot_entry["type"] = "imshow"

    else:
        _validate_kind(kind)

    return _finalize_spec(spec, plot_entry, params)


# EOF
