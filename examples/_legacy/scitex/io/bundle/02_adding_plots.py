#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-21 03:12:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/examples/scitex/io/bundle/02_adding_plots.py

"""
Example 02: Creating Multi-Panel Figures

Demonstrates:
- Creating individual FTS bundles for each plot (kind=plot)
- Creating composite figure containers (kind=figure)
- Using add_child() to embed and position panels
- Self-contained bundles with children/ directory
"""

import numpy as np

import scitex as stx
import scitex.io as sio
from scitex import INJECTED
from scitex.io.bundle import FTS


def create_line_plot(plt, out_dir, logger):
    """Create line plot bundle."""
    x = np.linspace(0, 10, 100)
    fig, ax = plt.subplots(figsize=(3, 2.5))
    ax.plot(x, np.sin(x), label="sin(x)")
    ax.plot(x, np.cos(x), label="cos(x)")
    ax.legend()
    ax.set_title("Trigonometric Functions")

    sio.save(fig, out_dir / "plot_A.zip")
    plt.close(fig)
    logger.info("Saved plot_A (line)")


def create_scatter_plot(plt, out_dir, logger):
    """Create scatter plot bundle."""
    np.random.seed(42)
    fig, ax = plt.subplots(figsize=(3, 2.5))
    ax.scatter(np.random.randn(50), np.random.randn(50))
    ax.set_title("Random Scatter")

    sio.save(fig, out_dir / "plot_B.zip")
    plt.close(fig)
    logger.info("Saved plot_B (scatter)")


def create_bar_plot(plt, out_dir, logger):
    """Create bar plot bundle."""
    fig, ax = plt.subplots(figsize=(3, 2.5))
    ax.bar(["A", "B", "C", "D"], [4, 7, 2, 8])
    ax.set_title("Category Values")

    sio.save(fig, out_dir / "plot_C.zip")
    plt.close(fig)
    logger.info("Saved plot_C (bar)")


def create_box_plot(plt, out_dir, logger):
    """Create box plot bundle."""
    fig, ax = plt.subplots(figsize=(3, 2.5))
    data = [np.random.randn(50) + i for i in range(4)]
    ax.boxplot(data)
    ax.set_title("Distribution Comparison")

    sio.save(fig, out_dir / "plot_D.zip")
    plt.close(fig)
    logger.info("Saved plot_D (box)")


def create_composite_figure(out_dir, logger):
    """Create composite figure with all panels."""
    container = FTS(
        out_dir / "multi_panel.zip",
        create=True,
        kind="figure",
        name="Multi-Panel Figure",
        size_mm={"width": 170, "height": 130},
    )

    # Add children with position and labels
    container.add_child(out_dir / "plot_A.zip", row=0, col=0, label="A")
    container.add_child(out_dir / "plot_B.zip", row=0, col=1, label="B")
    container.add_child(out_dir / "plot_C.zip", row=1, col=0, label="C")
    container.add_child(out_dir / "plot_D.zip", row=1, col=1, label="D")

    container.save(render=True)
    return container


@stx.session(verbose=False, agg=True)
def main(plt=INJECTED, CONFIG=INJECTED, logger=INJECTED):
    """Create multiple plot bundles and combine into figure."""
    logger.info("Example 02: Creating Multi-Panel Figure")

    out_dir = CONFIG["SDIR_OUT"]

    # Create individual panels
    create_line_plot(plt, out_dir, logger)
    create_scatter_plot(plt, out_dir, logger)
    create_bar_plot(plt, out_dir, logger)
    create_box_plot(plt, out_dir, logger)

    # Create composite figure
    container = create_composite_figure(out_dir, logger)

    logger.info(f"Saved container: {container.path}")
    logger.info(f"Children: {container.node.children}")
    logger.info(f"Layout: {container.node.layout}")

    # Reload and verify
    reloaded = FTS(out_dir / "multi_panel.zip")
    children = reloaded.load_children()
    logger.info(f"Reloaded {len(children)} embedded children")

    logger.success("Example 02 completed!")


if __name__ == "__main__":
    main()

# EOF
