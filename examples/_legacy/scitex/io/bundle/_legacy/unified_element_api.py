#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-19 09:15:01 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/examples/fig/unified_element_api.py


"""
Example: Unified Element API for .stx Bundles

This example demonstrates:
1. Creating a figure bundle with the unified element API
2. Adding various element types (text, shape, plot, figure)
3. Understanding the coordinate system (origin at top-left)
4. Nested coordinates (child elements relative to parent)

Coordinate System:
    (0,0) ──────────────────► x_mm
      │
      │   ┌─────────────────────────┐
      │   │  Figure Canvas          │
      │   │  (170mm × 120mm)        │
      │   │                         │
      │   │   Element A             │
      │   │   └── child annotation  │
      │   │       (local coords)    │
      │   └─────────────────────────┘
      ▼
    y_mm

Key Concepts:
- Everything is an "element" - no special "panel" terminology
- All positions are relative to parent's top-left (0,0)
- Child bundles have their own coordinate space
"""

import numpy as np

import scitex as stx
from scitex import INJECTED
from scitex.canvas import Figz
from scitex.canvas import to_absolute

# =============================================================================
# Plot Creation Functions
# =============================================================================


def create_line_plot(plt):
    """Create a line plot with trigonometric functions.

    Parameters
    ----------
    plt : module
        Matplotlib pyplot module

    Returns
    -------
    matplotlib.figure.Figure
        The created figure
    """
    fig, ax = plt.subplots()
    x = np.linspace(0, 10, 100)
    ax.plot(x, np.sin(x), label="sin(x)")
    ax.plot(x, np.cos(x), label="cos(x)")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend()
    ax.set_title("Panel A: Trigonometric")
    return fig


def create_scatter_plot(plt):
    """Create a scatter plot with random data.

    Parameters
    ----------
    plt : module
        Matplotlib pyplot module

    Returns
    -------
    matplotlib.figure.Figure
        The created figure
    """
    fig, ax = plt.subplots()
    np.random.seed(42)
    ax.scatter(np.random.randn(50), np.random.randn(50), alpha=0.7)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("Panel B: Scatter")
    return fig


def create_bar_chart(plt):
    """Create a bar chart with categorical data.

    Parameters
    ----------
    plt : module
        Matplotlib pyplot module

    Returns
    -------
    matplotlib.figure.Figure
        The created figure
    """
    fig, ax = plt.subplots()
    categories = ["A", "B", "C", "D"]
    values = [4, 7, 2, 8]
    ax.bar(categories, values)
    ax.set_ylabel("Value")
    ax.set_title("Panel C: Bar Chart")
    return fig


def create_histogram(plt):
    """Create a histogram with random data.

    Parameters
    ----------
    plt : module
        Matplotlib pyplot module

    Returns
    -------
    matplotlib.figure.Figure
        The created figure
    """
    fig, ax = plt.subplots()
    data = np.random.randn(1000)
    ax.hist(data, bins=30, edgecolor="black")
    ax.set_xlabel("Value")
    ax.set_ylabel("Frequency")
    ax.set_title("Panel D: Histogram")
    return fig


# =============================================================================
# Element Addition Functions
# =============================================================================


def add_text_elements(figz, logger):
    """Add text elements to the figure bundle.

    Parameters
    ----------
    figz : Figz
        The figure bundle to add elements to
    logger : Logger
        Logger instance for output
    """
    # Title at top center
    figz.add_element(
        element_id="title",
        element_type="text",
        content="My Publication Figure",
        position={"x_mm": 85, "y_mm": 5},
        fontsize=14,
        ha="center",
        va="top",
    )

    # Subtitle
    figz.add_element(
        "subtitle",
        "text",
        "Demonstrating the unified element API",
        {"x_mm": 85, "y_mm": 12},
        fontsize=10,
        ha="center",
    )

    logger.info(f"Added text elements: {figz.list_element_ids('text')}")


def add_shape_elements(figz, logger):
    """Add shape elements (arrows, brackets) to the figure bundle.

    Parameters
    ----------
    figz : Figz
        The figure bundle to add elements to
    logger : Logger
        Logger instance for output
    """
    # Arrow pointing to something interesting
    figz.add_element(
        "arrow1",
        "shape",
        content={
            "shape_type": "arrow",
            "start": {"x_mm": 60, "y_mm": 50},
            "end": {"x_mm": 80, "y_mm": 40},
        },
        position={"x_mm": 0, "y_mm": 0},
    )

    # Bracket for comparison
    figz.add_element(
        "bracket1",
        "shape",
        content={
            "shape_type": "bracket",
            "start": {"x_mm": 20, "y_mm": 80},
            "end": {"x_mm": 60, "y_mm": 80},
        },
        position={"x_mm": 0, "y_mm": 0},
    )

    # Statistical significance label
    figz.add_element(
        "sig_label",
        "text",
        "***",
        {"x_mm": 40, "y_mm": 75},
        fontsize=12,
        ha="center",
    )

    logger.info(f"Added shape elements: {figz.list_element_ids('shape')}")


def add_plot_elements(figz, plt, logger):
    """Add matplotlib plot elements to the figure bundle.

    Parameters
    ----------
    figz : Figz
        The figure bundle to add elements to
    plt : module
        Matplotlib pyplot module
    logger : Logger
        Logger instance for output
    """
    # Panel A: Line plot (top-left)
    fig_a = create_line_plot(plt)
    figz.add_element(
        "plot_A",
        "plot",
        fig_a,
        position={"x_mm": 10, "y_mm": 25},
        size={"width_mm": 70, "height_mm": 50},
    )
    plt.close(fig_a)
    logger.info("  Added plot A (line plot)")

    # Panel B: Scatter plot (top-right)
    fig_b = create_scatter_plot(plt)
    figz.add_element(
        "plot_B",
        "plot",
        fig_b,
        position={"x_mm": 90, "y_mm": 25},
        size={"width_mm": 70, "height_mm": 50},
    )
    plt.close(fig_b)
    logger.info("  Added plot B (scatter plot)")

    # Panel C: Bar chart (bottom-left)
    fig_c = create_bar_chart(plt)
    figz.add_element(
        "plot_C",
        "plot",
        fig_c,
        position={"x_mm": 10, "y_mm": 80},
        size={"width_mm": 70, "height_mm": 50},
    )
    plt.close(fig_c)
    logger.info("  Added plot C (bar chart)")

    # Panel D: Histogram (bottom-right)
    fig_d = create_histogram(plt)
    figz.add_element(
        "plot_D",
        "plot",
        fig_d,
        position={"x_mm": 90, "y_mm": 80},
        size={"width_mm": 70, "height_mm": 50},
    )
    plt.close(fig_d)
    logger.info("  Added plot D (histogram)")

    logger.info(f"  Total plot elements: {len(figz.list_element_ids('plot'))}")


# =============================================================================
# Main Function
# =============================================================================


@stx.session(verbose=False, agg=True)
def main(
    save: bool = True,
    show: bool = False,
    plt=INJECTED,
    CONFIG=INJECTED,
    logger=INJECTED,
):
    """Demonstrate the unified element API.

    Parameters
    ----------
    save : bool
        If True (default), save all outputs
    show : bool
        If True, display the figure (default: False)
    plt : module
        Matplotlib pyplot (injected by @stx.session)
    CONFIG : dict
        Session configuration (injected by @stx.session)
    logger : Logger
        SciTeX logger (injected by @stx.session)
    """
    logger.info("SciTeX Unified Element API Demo")
    logger.info(f"Session ID: {CONFIG['ID']}")

    tmpdir = CONFIG["SDIR_OUT"]
    logger.info(f"Output directory: {tmpdir}")

    # =========================================================================
    # 1. Create Figure Bundle
    # =========================================================================
    logger.info("=" * 60)
    logger.info("1. Creating Figure Bundle")
    logger.info("=" * 60)

    figure_path = tmpdir / "example_figure.stx"
    figz = Figz.create(
        figure_path,
        name="Example Figure",
        size_mm={"width": 170, "height": 120},
        bundle_type="figure",
    )

    logger.info(f"Created: {figz}")
    logger.info(f"Bundle ID: {figz.bundle_id[:8]}...")
    logger.info(f"Size: {figz.size_mm}")
    logger.info(f"Constraints: {figz.constraints}")

    # =========================================================================
    # 2. Add Text Elements
    # =========================================================================
    logger.info("=" * 60)
    logger.info("2. Adding Text Elements")
    logger.info("=" * 60)

    add_text_elements(figz, logger)

    # =========================================================================
    # 3. Add Shape Elements
    # =========================================================================
    logger.info("=" * 60)
    logger.info("3. Adding Shape Elements")
    logger.info("=" * 60)

    add_shape_elements(figz, logger)

    # =========================================================================
    # 4. Add Plot Elements
    # =========================================================================
    logger.info("=" * 60)
    logger.info("4. Adding Matplotlib Plots")
    logger.info("=" * 60)

    add_plot_elements(figz, plt, logger)

    # =========================================================================
    # 5. Coordinate Transformation Demo
    # =========================================================================
    logger.info("=" * 60)
    logger.info("5. Coordinate Transformation")
    logger.info("=" * 60)

    element_a_pos = {"x_mm": 10, "y_mm": 30}
    annotation_local = {"x_mm": 5, "y_mm": 3}
    annotation_absolute = to_absolute(annotation_local, element_a_pos)

    logger.info(f"Element A position: {element_a_pos}")
    logger.info(f"Annotation local position: {annotation_local}")
    logger.info(f"Annotation absolute position: {annotation_absolute}")

    # =========================================================================
    # 6. Save Outputs
    # =========================================================================
    if save:
        logger.info("=" * 60)
        logger.info("6. Saving Outputs")
        logger.info("=" * 60)

        # Save as .stx (ZIP archive)
        figz.save()
        logger.info(f"Saved .stx: {figure_path}")

        # Save as .stx.d (directory bundle)
        dir_path = tmpdir / "example_figure.stx.d"
        dir_path.mkdir(parents=True, exist_ok=True)
        figz.save(dir_path)
        logger.info(f"Saved .stx.d: {dir_path}")

        # # Export as PNG preview
        # png_path = tmpdir / "example_figure.png"
        # png_bytes = figz.render_preview(dpi=150)
        # with open(png_path, "wb") as f:
        #     f.write(png_bytes)
        # logger.info(f"Saved PNG: {png_path}")

    # =========================================================================
    # 7. Verify and Summarize
    # =========================================================================
    logger.info("=" * 60)
    logger.info("7. Verification and Summary")
    logger.info("=" * 60)

    reloaded = Figz(figure_path)
    logger.info(f"Reloaded: {reloaded}")
    logger.info(f"Total elements: {len(reloaded.elements)}")
    logger.info(f"Element types: {set(e['type'] for e in reloaded.elements)}")

    for elem in reloaded.elements:
        elem_id = elem["id"]
        elem_type = elem["type"]
        pos = elem.get("position", {})
        logger.info(
            f"  {elem_id}: type={elem_type}, "
            f"pos=({pos.get('x_mm', 0):.1f}, {pos.get('y_mm', 0):.1f})"
        )

    logger.success("Example completed successfully!")
    logger.info(f"Output saved to: {tmpdir}")

    return 0


if __name__ == "__main__":
    main()

# EOF
