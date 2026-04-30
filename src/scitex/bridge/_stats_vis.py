#!/usr/bin/env python3
# File: ./src/scitex/bridge/_stats_vis.py
# Time-stamp: "2024-12-09 10:00:00 (ywatanabe)"
"""
Bridge module for stats ↔ vis integration.

Provides adapters to:
- Convert StatResult to vis AnnotationModel
- Add statistical annotations to FigureModel
- Position stat annotations using vis coordinate system

Coordinate Convention
---------------------
This module uses **data coordinates** for positioning (via Position with
unit="data"). This matches the vis model's approach where positions
correspond to actual data values on the plot.

- Positions are in the same units as the plot data
- position_stat_annotation() returns Position(unit="data")
- For normalized positioning, use axes_bounds to define the data range

This differs from _stats_plt which uses axes coordinates (0-1 normalized).
When bridging between plt and vis, coordinate transformation may be needed.
"""

from typing import Dict, List, Optional, Tuple

# Import GUI classes from FTS (single source of truth)
from scitex.io.bundle.kinds._stats import Position

# Legacy model imports - may not be available
try:
    from scitex.io.bundle.kinds._plot._models import (
        AnnotationModel,
        AxesModel,
        FigureModel,
        TextStyle,
    )

    VIS_MODEL_AVAILABLE = True
except ImportError:
    AnnotationModel = None
    FigureModel = None
    AxesModel = None
    TextStyle = None
    VIS_MODEL_AVAILABLE = False

# StatResult placeholder for type hints (actual usage is through dict)
StatResult = dict  # Use dict as StatResult is deprecated


def stat_result_to_annotation(
    stat_result: StatResult,
    format_style: str = "asterisk",
    x: Optional[float] = None,
    y: Optional[float] = None,
) -> AnnotationModel:
    """
    Convert a StatResult to a vis AnnotationModel.

    Parameters
    ----------
    stat_result : StatResult
        The statistical result to convert
    format_style : str
        Format style for the text ("asterisk", "compact", "detailed", "publication")
    x : float, optional
        X position (data coordinates). Overrides stat_result positioning
    y : float, optional
        Y position (data coordinates). Overrides stat_result positioning

    Returns
    -------
    AnnotationModel
        Annotation model for vis rendering
    """
    # Get formatted text
    text = stat_result.format_text(format_style)

    # Determine position
    if x is None or y is None:
        positioning = stat_result.positioning
        if positioning and positioning.position:
            pos = positioning.position
            x = x if x is not None else pos.x
            y = y if y is not None else pos.y
        else:
            # Default center-top position (will be overridden by positioning logic)
            x = x if x is not None else 0.5
            y = y if y is not None else 0.95

    # Build text style from stat styling
    styling = stat_result.styling
    text_style = TextStyle(
        fontsize=styling.font_size_pt if styling else 7.0,
        color=styling.color if styling else "#000000",
        ha="center",
        va="top",
    )

    # Create annotation model
    return AnnotationModel(
        annotation_type="text",
        text=text,
        x=x,
        y=y,
        annotation_id=stat_result.plot_id or f"stat_{id(stat_result)}",
        style=text_style,
    )


def add_stats_to_figure_model(
    figure_model: FigureModel,
    stat_results: List[StatResult],
    axes_index: int = 0,
    format_style: str = "asterisk",
    auto_position: bool = True,
) -> FigureModel:
    """
    Add statistical results as annotations to a FigureModel.

    Parameters
    ----------
    figure_model : FigureModel
        The figure model to annotate
    stat_results : List[StatResult]
        List of statistical results to add
    axes_index : int
        Index of axes to add annotations to
    format_style : str
        Format style for the text
    auto_position : bool
        Whether to automatically position stats to avoid overlap

    Returns
    -------
    FigureModel
        The modified figure model (same instance)
    """
    if not stat_results:
        return figure_model

    # Ensure axes exist
    if axes_index >= len(figure_model.axes):
        raise IndexError(f"Axes index {axes_index} out of range")

    axes_dict = figure_model.axes[axes_index]

    # Get or initialize annotations list
    if "annotations" not in axes_dict:
        axes_dict["annotations"] = []

    # Calculate positions if auto_position
    positions = []
    if auto_position:
        positions = _calculate_stat_positions(
            stat_results,
            len(axes_dict["annotations"]),
        )

    # Add each stat as annotation
    for i, stat_result in enumerate(stat_results):
        x, y = positions[i] if positions else (None, None)
        annotation = stat_result_to_annotation(
            stat_result,
            format_style=format_style,
            x=x,
            y=y,
        )
        axes_dict["annotations"].append(annotation.to_dict())

    return figure_model


def position_stat_annotation(
    stat_result: StatResult,
    axes_bounds: Dict[str, float],
    existing_positions: Optional[List[Tuple[float, float]]] = None,
    preferred_corner: str = "top-right",
) -> Position:
    """
    Calculate optimal position for a stat annotation.

    Parameters
    ----------
    stat_result : StatResult
        The statistical result to position
    axes_bounds : Dict[str, float]
        Axes bounds with keys: x_min, x_max, y_min, y_max
    existing_positions : List[Tuple[float, float]], optional
        List of existing annotation positions to avoid
    preferred_corner : str
        Preferred corner: "top-left", "top-right", "bottom-left", "bottom-right"

    Returns
    -------
    Position
        Calculated position in data coordinates
    """
    existing = existing_positions or []

    # Get axes range
    x_min = axes_bounds.get("x_min", 0)
    x_max = axes_bounds.get("x_max", 1)
    y_min = axes_bounds.get("y_min", 0)
    y_max = axes_bounds.get("y_max", 1)

    x_range = x_max - x_min
    y_range = y_max - y_min

    # Calculate corner positions (as fraction, then convert to data)
    corner_fractions = {
        "top-right": (0.95, 0.95),
        "top-left": (0.05, 0.95),
        "bottom-right": (0.95, 0.05),
        "bottom-left": (0.05, 0.05),
        "top-center": (0.5, 0.95),
        "bottom-center": (0.5, 0.05),
    }

    # Start with preferred corner
    base_x, base_y = corner_fractions.get(preferred_corner, (0.95, 0.95))
    x = x_min + base_x * x_range
    y = y_min + base_y * y_range

    # Check overlap and adjust if needed
    min_dist = (
        stat_result.positioning.min_distance_mm if stat_result.positioning else 2.0
    )

    for ex_x, ex_y in existing:
        dist = ((x - ex_x) ** 2 + (y - ex_y) ** 2) ** 0.5
        if dist < min_dist:
            # Shift down
            y -= min_dist * 1.5

    return Position(x=x, y=y, unit="data")


def _calculate_stat_positions(
    stat_results: List[StatResult],
    existing_count: int = 0,
) -> List[Tuple[float, float]]:
    """
    Calculate non-overlapping positions for multiple stats.

    Parameters
    ----------
    stat_results : List[StatResult]
        List of stats to position
    existing_count : int
        Number of existing annotations

    Returns
    -------
    List[Tuple[float, float]]
        List of (x, y) positions in axes coordinates (0-1)
    """
    positions = []
    y_start = 0.95
    y_step = 0.05

    for i, stat in enumerate(stat_results):
        # Stack vertically from top
        y = y_start - (i + existing_count) * y_step
        x = 0.5  # Center

        # Check stat's own positioning preference
        if stat.positioning and stat.positioning.position:
            pos = stat.positioning.position
            x = pos.x
            y = pos.y

        positions.append((x, y))

    return positions


__all__ = [
    "stat_result_to_annotation",
    "add_stats_to_figure_model",
    "position_stat_annotation",
]


# EOF
