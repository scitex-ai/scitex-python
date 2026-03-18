#!/usr/bin/env python3
# Timestamp: "2025-12-19 07:10:57 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/examples/fig/auto_crop_visualization.py


"""
Auto-Crop Visualization Example

Demonstrates the coordinate-based auto-crop functionality with
blueprint-style visualizations showing:
- Canvas boundaries with dimension annotations
- Element bounding boxes with labels and positions
- Rulers (horizontal and vertical)
- Before/after comparison

Usage:
    python auto_crop_visualization.py
    python auto_crop_visualization.py --save-bundles  # Also save as .stx bundles
"""

import copy
import tempfile
from pathlib import Path

import scitex as stx
from scitex import INJECTED
from scitex.canvas import (
    Figz,
    auto_crop_layout,
    content_bounds,
    plot_auto_crop_comparison,
    plot_layout,
)


def demo_basic_auto_crop(plt):
    """Demo 1: Basic auto-crop with single element."""
    print("\n" + "=" * 60)
    print("Demo 1: Basic Auto-Crop (Single Element)")
    print("=" * 60)

    # Create elements far from origin
    elements = [
        {
            "id": "A",
            "type": "panel",
            "position": {"x_mm": 50, "y_mm": 40},
            "size": {"width_mm": 60, "height_mm": 40},
        }
    ]
    canvas_before = {"width_mm": 170, "height_mm": 120}

    # Show before state
    print(f"Before: Canvas {canvas_before['width_mm']}x{canvas_before['height_mm']} mm")
    print(
        f"  Element A at ({elements[0]['position']['x_mm']}, "
        f"{elements[0]['position']['y_mm']})"
    )

    # Apply auto-crop
    elements_after, canvas_after = auto_crop_layout(elements, margin_mm=5)

    print(f"\nAfter: Canvas {canvas_after['width_mm']}x{canvas_after['height_mm']} mm")
    print(
        f"  Element A at ({elements_after[0]['position']['x_mm']}, "
        f"{elements_after[0]['position']['y_mm']})"
    )

    # Visualize
    fig = plot_auto_crop_comparison(
        elements,
        elements_after,
        canvas_before,
        canvas_after,
        title="Demo 1: Basic Auto-Crop (Single Element)",
    )
    return fig


def demo_multi_element_auto_crop(plt):
    """Demo 2: Auto-crop with multiple scattered elements."""
    print("\n" + "=" * 60)
    print("Demo 2: Multi-Element Auto-Crop")
    print("=" * 60)

    # Create multiple elements scattered on canvas
    elements = [
        {
            "id": "A",
            "type": "panel",
            "position": {"x_mm": 50, "y_mm": 30},
            "size": {"width_mm": 40, "height_mm": 30},
        },
        {
            "id": "B",
            "type": "panel",
            "position": {"x_mm": 100, "y_mm": 20},
            "size": {"width_mm": 50, "height_mm": 50},
        },
        {
            "id": "C",
            "type": "text",
            "position": {"x_mm": 60, "y_mm": 70},
            "size": {"width_mm": 30, "height_mm": 15},
        },
    ]
    canvas_before = {"width_mm": 200, "height_mm": 150}

    # Calculate content bounds
    bounds = content_bounds(elements)
    print(
        f"Content bounds: x={bounds['x_mm']}, y={bounds['y_mm']}, "
        f"w={bounds['width_mm']}, h={bounds['height_mm']}"
    )

    # Apply auto-crop
    elements_after, canvas_after = auto_crop_layout(elements, margin_mm=10)

    print(f"\nBefore: {canvas_before['width_mm']}x{canvas_before['height_mm']} mm")
    print(f"After:  {canvas_after['width_mm']}x{canvas_after['height_mm']} mm")
    print(
        f"Reduction: {100 * (1 - (canvas_after['width_mm'] * canvas_after['height_mm']) / (canvas_before['width_mm'] * canvas_before['height_mm'])):.1f}%"
    )

    # Visualize
    fig = plot_auto_crop_comparison(
        elements,
        elements_after,
        canvas_before,
        canvas_after,
        title="Demo 2: Multi-Element Auto-Crop",
    )
    return fig


def demo_figure_auto_crop(plt):
    """Demo 3: Auto-crop using Figz class."""
    print("\n" + "=" * 60)
    print("Demo 3: Figz.auto_crop() Method")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create .stx bundle (new unified API)
        stx_path = Path(tmpdir) / "figure.stx"
        figz = Figz(stx_path, name="figure", size_mm=(200, 150))

        # Add elements at various positions
        figz.add_element(
            element_id="plot_A",
            element_type="panel",
            position={"x_mm": 80, "y_mm": 50},
            size={"width_mm": 60, "height_mm": 45},
        )
        figz.add_element(
            element_id="plot_B",
            element_type="panel",
            position={"x_mm": 80, "y_mm": 100},
            size={"width_mm": 60, "height_mm": 35},
        )
        figz.add_element(
            element_id="title",
            element_type="text",
            content="Figure Title",
            position={"x_mm": 90, "y_mm": 40},
            size={"width_mm": 40, "height_mm": 8},
        )

        # Capture before state
        elements_before = copy.deepcopy(figz.elements)
        size_before = figz.size_mm  # Returns {"width": mm, "height": mm} dict

        print(f"Before: {size_before['width']}x{size_before['height']} mm")
        print(f"  Elements: {len(elements_before)}")

        # Apply auto-crop
        result = figz.auto_crop(margin_mm=8)

        print(
            f"\nAfter: {result['new_size']['width']}x{result['new_size']['height']} mm"
        )
        print(f"  Offset: ({result['offset']['x_mm']}, {result['offset']['y_mm']})")

        # Visualize
        fig = plot_auto_crop_comparison(
            elements_before,
            figz.elements,
            {
                "width_mm": size_before["width"],
                "height_mm": size_before["height"],
            },
            {
                "width_mm": result["new_size"]["width"],
                "height_mm": result["new_size"]["height"],
            },
            title="Demo 3: Figz.auto_crop() Method",
        )
        return fig


def demo_layout_only(plt):
    """Demo 4: Layout visualization only (no auto-crop)."""
    print("\n" + "=" * 60)
    print("Demo 4: Layout Visualization")
    print("=" * 60)

    elements = [
        {
            "id": "Header",
            "type": "text",
            "position": {"x_mm": 5, "y_mm": 5},
            "size": {"width_mm": 160, "height_mm": 10},
        },
        {
            "id": "Panel A",
            "type": "panel",
            "position": {"x_mm": 5, "y_mm": 20},
            "size": {"width_mm": 75, "height_mm": 55},
        },
        {
            "id": "Panel B",
            "type": "panel",
            "position": {"x_mm": 85, "y_mm": 20},
            "size": {"width_mm": 75, "height_mm": 55},
        },
        {
            "id": "Caption",
            "type": "text",
            "position": {"x_mm": 5, "y_mm": 80},
            "size": {"width_mm": 160, "height_mm": 15},
        },
    ]
    canvas = {"width_mm": 170, "height_mm": 100}

    fig, ax = plot_layout(elements, canvas, title="Demo 4: Publication Figure Layout")
    return fig


@stx.session(verbose=False, agg=True)
def main(
    save: bool = True,
    show: bool = False,
    plt=INJECTED,
    CONFIG=INJECTED,
    logger=INJECTED,
):
    """Run all auto-crop visualization demonstrations.

    Parameters
    ----------
    save : bool
        If True (default), save each figure as .png and .stx bundle
    show : bool
        If True, display the figures (default: False)
    plt : module
        Matplotlib pyplot (injected by @stx.session)
    CONFIG : dict
        Session configuration (injected by @stx.session)
    logger : Logger
        SciTeX logger (injected by @stx.session)
    """
    logger.info("SciTeX Auto-Crop & Layout Visualization Demo")
    logger.info(f"Session ID: {CONFIG['ID']}")
    logger.info(f"Output directory: {CONFIG['SDIR_RUN']}")

    figs = []
    demo_names = [
        "demo1_basic_auto_crop",
        "demo2_multi_element",
        "demo3_figure_auto_crop",
        "demo4_layout_only",
    ]

    # Run demos
    figs.append(demo_basic_auto_crop(plt))
    figs.append(demo_multi_element_auto_crop(plt))
    figs.append(demo_figure_auto_crop(plt))
    figs.append(demo_layout_only(plt))

    # Save figures
    if save:
        logger.info("Saving figures...")
        sdir = CONFIG["SDIR_OUT"]

        for fig, name in zip(figs, demo_names):
            # Save as PNG using scitex.io.save
            stx.io.save(fig, sdir / "png" / f"{name}.png")

            # Save as .stx bundle (unified format, ZIP archive)
            stx.io.save(fig, sdir / f"{name}.stx")

            # Also save as .stx.d directory bundle (unzipped)
            stx.io.save(fig, sdir / f"{name}.stx.d")

        logger.success(f"Saved {len(figs)} figures to {sdir}")

    logger.info("All demos completed.")

    # Show visualizations if requested
    if show:
        plt.show()

    return 0


if __name__ == "__main__":
    main()

# EOF
