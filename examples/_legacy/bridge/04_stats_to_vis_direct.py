#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2025-12-09
# File: ./examples/bridge/04_stats_to_vis_direct.py
"""
Example: Direct stats → vis conversion (without matplotlib)

Demonstrates converting StatResult directly to vis AnnotationModel:
1. Create StatResult objects
2. Convert to vis AnnotationModel
3. Add to FigureModel
4. Position stat annotations

This is useful for:
- Building figure specifications programmatically
- Server-side figure generation
- GUI-first workflows where vis model comes first

Usage:
    python 04_stats_to_vis_direct.py
"""

import json
from pathlib import Path

import scitex as stx
from scitex.bridge import (
    stat_result_to_annotation,
    add_stats_to_figure_model,
    position_stat_annotation,
)
from scitex.schema import create_stat_result
from scitex.canvas.model import FigureModel


@stx.session
def main(
    CONFIG=stx.INJECTED,
    logger=stx.INJECTED,
):
    """Direct stats to vis conversion without matplotlib."""
    out = Path(CONFIG.SDIR_OUT)

    # 1. Create StatResult objects
    stats_list = [
        create_stat_result("t-test", "t", 3.45, 0.001),
        create_stat_result("pearson", "r", 0.85, 0.0001),
        create_stat_result("anova", "F", 12.3, 0.002),
    ]

    logger.info("=" * 60)
    logger.info("Created StatResults")
    logger.info("=" * 60)
    for s in stats_list:
        logger.info(
            f"  {s.test_type}: {s.statistic['name']} = {s.statistic['value']:.2f}, "
            f"p = {s.p_value:.4f}, stars = '{s.stars}'"
        )

    # 2. Convert each to AnnotationModel
    logger.info("-" * 60)
    logger.info("Converted to AnnotationModels")
    logger.info("-" * 60)

    for s in stats_list:
        ann = stat_result_to_annotation(s, format_style="compact")
        logger.info(f"  Type: {ann.annotation_type}")
        logger.info(f"  Text: '{ann.text}'")
        logger.info(f"  Position: ({ann.x}, {ann.y})")

    # 3. Create a FigureModel and add stats
    figure_model = FigureModel(
        width_mm=170,  # Single column width
        height_mm=120,
        nrows=1,
        ncols=2,
        axes=[
            {
                "row": 0,
                "col": 0,
                "xlabel": "Group",
                "ylabel": "Value",
                "title": "Comparison",
                "plots": [],
            },
            {
                "row": 0,
                "col": 1,
                "xlabel": "X",
                "ylabel": "Y",
                "title": "Correlation",
                "plots": [],
            },
        ],
    )

    # Add first two stats to axes 0, third to axes 1
    add_stats_to_figure_model(
        figure_model,
        stats_list[:2],
        axes_index=0,
        format_style="asterisk",
    )

    add_stats_to_figure_model(
        figure_model,
        stats_list[2:],
        axes_index=1,
        format_style="compact",
    )

    logger.info("-" * 60)
    logger.info("FigureModel with Stats")
    logger.info("-" * 60)
    logger.info(f"Dimensions: {figure_model.width_mm} x {figure_model.height_mm} mm")

    for i, ax_dict in enumerate(figure_model.axes):
        annotations = ax_dict.get("annotations", [])
        logger.info(f"Axes {i} ({ax_dict.get('title')}):")
        logger.info(f"  Annotations: {len(annotations)}")
        for j, ann in enumerate(annotations):
            logger.info(
                f"    [{j}] text='{ann.get('text')}', pos=({ann.get('x')}, {ann.get('y')})"
            )

    # 4. Demonstrate position_stat_annotation
    logger.info("-" * 60)
    logger.info("Custom Positioning")
    logger.info("-" * 60)

    bounds = {"x_min": 0, "x_max": 100, "y_min": 0, "y_max": 1000}

    for corner in ["top-right", "top-left", "bottom-right", "bottom-left"]:
        pos = position_stat_annotation(
            stats_list[0],
            bounds,
            preferred_corner=corner,
        )
        logger.info(f"  {corner:15s}: x={pos.x:6.1f}, y={pos.y:7.1f} ({pos.unit})")

    # 5. Export as JSON
    json_output = json.dumps(figure_model.to_dict(), indent=2)
    json_path = out / "stats_to_vis_direct.json"
    stx.io.save(json_output, json_path)
    logger.info(f"JSON exported to: {json_path}")

    logger.info("Done!")


if __name__ == "__main__":
    main()

# EOF
