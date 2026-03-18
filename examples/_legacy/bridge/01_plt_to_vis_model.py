#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2025-12-09
# File: ./examples/bridge/01_plt_to_vis_model.py
"""
Example: Convert matplotlib figure to vis FigureModel

Demonstrates the plt → vis bridge workflow:
1. Create a matplotlib figure with plots
2. Convert to vis FigureModel (JSON-serializable)
3. Inspect the structured model

This is useful for:
- Exporting figures to GUI editors
- Serializing figure state for reproducibility
- Building figure preview systems

Usage:
    python 01_plt_to_vis_model.py
"""

import json
from pathlib import Path

import numpy as np
import scitex as stx
from scitex.bridge import figure_to_vis_model


@stx.session
def main(
    CONFIG=stx.INJECTED,
    plt=stx.INJECTED,
    logger=stx.INJECTED,
):
    """Convert matplotlib figure to vis FigureModel."""
    out = Path(CONFIG.SDIR_OUT)

    # 1. Create a figure with two subplots
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    # Left subplot: line plot
    x = [1, 2, 3, 4, 5]
    y = [2, 4, 3, 5, 4]
    axes[0].plot(x, y, "b-o", label="Data")
    axes[0].set_xyt(x="X Axis", y="Y Axis", t="Line Plot")
    axes[0].legend(frameon=False)

    # Right subplot: scatter plot
    x2 = np.random.randn(50)
    y2 = x2 + np.random.randn(50) * 0.5
    axes[1].scatter(x2, y2, c="red", alpha=0.6)
    axes[1].set_xyt(x="Variable A", y="Variable B", t="Scatter Plot")

    fig.suptitle("Example Figure")

    # 2. Convert to vis FigureModel
    model = figure_to_vis_model(fig)

    # 3. Inspect the model
    logger.info("=" * 60)
    logger.info("FigureModel Summary")
    logger.info("=" * 60)
    logger.info(f"Dimensions: {model.width_mm:.1f} x {model.height_mm:.1f} mm")
    logger.info(f"Layout: {model.nrows} x {model.ncols}")
    logger.info(f"DPI: {model.dpi}")
    logger.info(f"Suptitle: {model.suptitle}")
    logger.info(f"Number of axes: {len(model.axes)}")

    logger.info("-" * 60)
    logger.info("Axes Details")
    logger.info("-" * 60)
    for i, ax_dict in enumerate(model.axes):
        logger.info(f"Axes {i}:")
        logger.info(f"  Position: row={ax_dict.get('row')}, col={ax_dict.get('col')}")
        logger.info(f"  Title: {ax_dict.get('title')}")
        logger.info(f"  X Label: {ax_dict.get('xlabel')}")
        logger.info(f"  Y Label: {ax_dict.get('ylabel')}")

    # 4. Export as JSON
    model_dict = model.to_dict()
    json_str = json.dumps(model_dict, indent=2, default=str)

    json_path = out / "plt_to_vis_model.json"
    stx.io.save(json_str, json_path)
    logger.info(f"JSON exported to: {json_path}")

    # Save figure
    png_path = out / "plt_to_vis_model.png"
    stx.io.save(fig, png_path)
    logger.info(f"Figure saved to: {png_path}")

    fig.close()
    logger.info("Done!")


if __name__ == "__main__":
    main()

# EOF
