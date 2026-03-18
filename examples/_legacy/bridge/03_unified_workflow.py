#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2025-12-09
# File: ./examples/bridge/03_unified_workflow.py
"""
Example: Complete bridge workflow

Demonstrates a full workflow using all bridge components:
1. Create matplotlib figure with scitex.plt (tracking enabled)
2. Add statistical annotations
3. Convert to vis FigureModel
4. Export as JSON for GUI consumption

This shows how the bridge layer connects:
- scitex.plt (plotting with tracking)
- scitex.stats (statistical results)
- scitex.canvas (JSON models for GUI)

Usage:
    python 03_unified_workflow.py
"""

import json
from pathlib import Path

import numpy as np
import scitex as stx
from scipy import stats
from scitex.bridge import (
    figure_to_vis_model,
    add_stats_from_results,
    collect_figure_data,
)
from scitex.schema import create_stat_result


@stx.session
def main(
    CONFIG=stx.INJECTED,
    plt=stx.INJECTED,
    logger=stx.INJECTED,
):
    """Complete bridge workflow demonstration."""
    out = Path(CONFIG.SDIR_OUT)

    # 1. Create sample data
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x) + np.random.normal(0, 0.1, 100)
    y2 = np.cos(x) + np.random.normal(0, 0.1, 100)

    # Calculate correlation
    r, p = stats.pearsonr(y1, y2)

    # 2. Create figure with scitex.plt (tracking enabled)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Left: Time series
    axes[0].plot(x, y1, "b-", label="Signal 1", alpha=0.8)
    axes[0].plot(x, y2, "r-", label="Signal 2", alpha=0.8)
    axes[0].set_xyt(x="Time", y="Amplitude", t="Time Series")
    axes[0].legend(frameon=False)

    # Right: Correlation scatter
    axes[1].scatter(y1, y2, c="purple", alpha=0.5, s=20)
    axes[1].set_xyt(x="Signal 1", y="Signal 2", t="Correlation")

    # 3. Create and add statistical result
    stat_result = create_stat_result(
        test_type="pearson",
        statistic_name="r",
        statistic_value=r,
        p_value=p,
    )

    # Add to correlation plot (axes[1])
    add_stats_from_results(
        axes[1],
        stat_result,
        format_style="compact",
    )

    logger.info("=" * 60)
    logger.info("Statistical Result")
    logger.info("=" * 60)
    logger.info(f"Pearson r: {r:.3f}")
    logger.info(f"P-value: {p:.4e}")
    logger.info(f"Formatted: {stat_result.format_text('publication')}")

    # 4. Convert to vis FigureModel
    vis_model = figure_to_vis_model(fig)

    logger.info("=" * 60)
    logger.info("Vis FigureModel")
    logger.info("=" * 60)
    logger.info(f"Size: {vis_model.width_mm:.1f} x {vis_model.height_mm:.1f} mm")
    logger.info(f"Axes count: {len(vis_model.axes)}")

    for i, ax_dict in enumerate(vis_model.axes):
        n_annotations = len(ax_dict.get("annotations", []))
        logger.info(
            f"  Axes {i}: {ax_dict.get('title', 'untitled')}, {n_annotations} annotations"
        )

    # 5. Collect figure data (simpler format)
    fig_data = collect_figure_data(fig)

    logger.info("=" * 60)
    logger.info("Collected Figure Data")
    logger.info("=" * 60)
    logger.info(
        f"Figure dimensions: {fig_data['figure']['width_mm']:.1f} x "
        f"{fig_data['figure']['height_mm']:.1f} mm"
    )
    logger.info(f"Number of axes: {len(fig_data['axes'])}")

    # 6. Note: Stats are auto-saved when fig is saved (as {basename}_stats.csv)
    # The figure save below will auto-create unified_workflow_stats.csv

    # 7. Export as JSON
    export_data = {
        "vis_model": vis_model.to_dict(),
        "stats": [stat_result.to_dict()],
        "metadata": {
            "description": "Example bridge workflow output",
            "tracking_enabled": True,
        },
    }

    json_output = json.dumps(export_data, indent=2, default=str)
    json_path = out / "unified_workflow.json"
    stx.io.save(json_output, json_path)
    logger.info(f"JSON exported to: {json_path}")

    # 8. Save figure
    png_path = out / "unified_workflow.png"
    stx.io.save(fig, png_path)
    logger.info(f"Figure saved to: {png_path}")

    fig.close()
    logger.info("Done!")


if __name__ == "__main__":
    main()

# EOF
