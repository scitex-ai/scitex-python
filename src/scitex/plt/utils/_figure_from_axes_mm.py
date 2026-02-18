#!/usr/bin/env python3
# Timestamp: "2025-11-19 12:30:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/plt/utils/_figure_from_axes_mm.py

"""
Create figures by specifying AXES size (not figure size).

This is the inverse of create_figure_ax_mm() - you specify the desired
axes box size, and the figure size is automatically calculated based on margins.

Key insight: For publication, you care about the axes box size (the actual plot area),
not the total figure size. The figure size is just axes + margins.
"""

__FILE__ = __file__

from typing import TYPE_CHECKING, Dict, Optional, Tuple

import matplotlib.pyplot as plt
from figrecipe.utils import mm_to_inch

if TYPE_CHECKING:
    from scitex.plt._subplots._AxisWrapper import AxisWrapper
    from scitex.plt._subplots._FigWrapper import FigWrapper


def create_axes_with_size_mm(
    axes_width_mm: float = 30.0,
    axes_height_mm: float = 21.0,
    dpi: int = 300,
    *,
    margin_mm: Optional[Dict[str, float]] = None,
    style_mm: Optional[Dict[str, float]] = None,
    mode: str = "publication",  # "publication" or "display"
) -> Tuple["FigWrapper", "AxisWrapper"]:
    """
    Create figure by specifying AXES box size (not figure size).

    This is the key function for publication-quality figures where you need
    exact control over the axes box dimensions. The figure size is automatically
    calculated as: figure_size = axes_size + margins

    Parameters
    ----------
    axes_width_mm : float, optional
        Axes box width in millimeters (default: 30.0)
        This is the actual plot area, excluding labels and ticks
    axes_height_mm : float, optional
        Axes box height in millimeters (default: 21.0)
    dpi : int, optional
        Resolution for saving (default: 300 for publication, 100 for display)
    margin_mm : dict, optional
        Margins around axes box in mm. Default:
        {'left': 5, 'right': 2, 'top': 2, 'bottom': 5}
        These accommodate axis labels, tick labels, and titles
    style_mm : dict, optional
        Styling specifications. See apply_style_mm() for details
    mode : str, optional
        'publication' (default) - Exact mm control, dpi=300
        'display' - Larger for screen viewing, dpi=100

    Returns
    -------
    fig : matplotlib.figure.Figure
        Created figure (size = axes + margins)
    ax : matplotlib.axes.Axes
        Created axes with exact specified dimensions

    Examples
    --------
    Create a 30mm × 21mm axes box for publication:

    >>> fig, ax = create_axes_with_size_mm(
    ...     axes_width_mm=30,
    ...     axes_height_mm=21,
    ...     dpi=300,
    ...     mode='publication'
    ... )
    >>> ax.plot(x, y)
    >>> fig.savefig('figure.tiff', dpi=300, bbox_inches='tight')

    Create larger version for display:

    >>> fig, ax = create_axes_with_size_mm(
    ...     axes_width_mm=30,
    ...     axes_height_mm=21,
    ...     mode='display'  # Will scale up for screen
    ... )

    Notes
    -----
    Key dimensions explained:
    - axes_width_mm: The actual plot area width
    - axes_height_mm: The actual plot area height
    - margins: Space for labels, ticks, titles
    - figure_size: Automatically calculated as axes + margins

    When saving with bbox_inches='tight', matplotlib will crop the figure
    to the minimum bounding box, so the final saved size will be close to
    (but slightly larger than) the axes size due to labels.
    """
    # Set default margins if not provided
    if margin_mm is None:
        margin_mm = {
            "left": 5.0,  # Space for y-axis label and tick labels
            "right": 2.0,  # Minimal right margin
            "bottom": 5.0,  # Space for x-axis label and tick labels
            "top": 2.0,  # Space for title (if any)
        }

    # Apply mode-specific settings
    if mode == "display":
        # Scale up for better screen visibility
        scale_factor = 3.0  # Display at 3x size
        axes_width_mm *= scale_factor
        axes_height_mm *= scale_factor
        margin_mm = {k: v * scale_factor for k, v in margin_mm.items()}
        dpi = 100  # Lower DPI for screen
    elif mode == "publication":
        dpi = max(dpi, 300)  # Ensure at least 300 DPI

    # Calculate figure size = axes size + margins
    fig_width_mm = axes_width_mm + margin_mm.get("left", 0) + margin_mm.get("right", 0)
    fig_height_mm = (
        axes_height_mm + margin_mm.get("bottom", 0) + margin_mm.get("top", 0)
    )

    # Convert to inches for matplotlib
    figsize_inch = (mm_to_inch(fig_width_mm), mm_to_inch(fig_height_mm))
    fig = plt.figure(figsize=figsize_inch, dpi=dpi)

    # Calculate axes position in figure coordinates [0-1]
    left = margin_mm.get("left", 0) / fig_width_mm
    bottom = margin_mm.get("bottom", 0) / fig_height_mm
    width = axes_width_mm / fig_width_mm
    height = axes_height_mm / fig_height_mm

    # Create axes
    ax = fig.add_axes([left, bottom, width, height])

    # Apply styling if provided
    if style_mm is not None:
        from ._figure_mm import apply_style_mm

        apply_style_mm(ax, style_mm)

    # Tag axes with metadata for later embedding
    ax._scitex_metadata = {
        "created_with": "scitex.plt.utils.create_axes_with_size_mm",
        "mode": mode,
        "axes_size_mm": (axes_width_mm, axes_height_mm),
        "margin_mm": margin_mm,
        "style_mm": style_mm,
    }

    # Wrap in scitex wrappers for consistent API
    from scitex.plt._subplots._AxisWrapper import AxisWrapper
    from scitex.plt._subplots._FigWrapper import FigWrapper

    fig_wrapped = FigWrapper(fig)
    ax_wrapped = AxisWrapper(fig_wrapped, ax, track=False)

    # Store axes reference in FigWrapper
    fig_wrapped.axes = ax_wrapped  # type: ignore[attr-defined]

    return fig_wrapped, ax_wrapped


def get_dimension_info(fig, ax) -> Dict:
    """
    Get all dimension information about a figure/axes for debugging.

    This is a helper function to understand the relationship between
    mm, inches, pixels, and DPI. Very useful when you're confused!

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure object
    ax : matplotlib.axes.Axes
        Axes object

    Returns
    -------
    dict
        Dictionary containing all dimension information:
        - figure_size_inch: Figure size in inches
        - figure_size_mm: Figure size in millimeters
        - figure_size_px: Figure size in pixels
        - axes_position: Axes position in figure coordinates [0-1]
        - axes_size_inch: Axes size in inches
        - axes_size_mm: Axes size in millimeters
        - axes_size_px: Axes size in pixels
        - dpi: Resolution in dots per inch
        - conversion_factor: mm per inch (25.4)

    Examples
    --------
    >>> fig, ax = create_axes_with_size_mm(30, 21)
    >>> info = get_dimension_info(fig, ax)
    >>> print(f"Axes size: {info['axes_size_mm']} mm")
    >>> print(f"Axes size: {info['axes_size_px']} pixels at {info['dpi']} DPI")
    """
    from figrecipe.utils import MM_PER_INCH, inch_to_mm

    # Figure dimensions
    fig_width_inch, fig_height_inch = fig.get_size_inches()
    dpi = fig.dpi

    fig_width_mm = inch_to_mm(fig_width_inch)
    fig_height_mm = inch_to_mm(fig_height_inch)
    fig_width_px = int(fig_width_inch * dpi)
    fig_height_px = int(fig_height_inch * dpi)

    # Draw the figure to finalize layout (constrained_layout, tight_layout, etc.)
    # This ensures we get the ACTUAL axes position after all adjustments
    fig.canvas.draw()

    # Get actual axes position using window_extent (actual pixel coordinates)
    # This accounts for tight_layout, constrained_layout, and label adjustments
    bbox = ax.get_window_extent()

    # Convert from display coordinates (bottom-left origin) to figure pixels
    axes_x0_px = int(round(bbox.x0))
    axes_x1_px = int(round(bbox.x1))
    # Convert to top-left origin for web/canvas compatibility
    axes_y0_px = int(round(fig_height_px - bbox.y1))  # Top edge (flipped for web)
    axes_y1_px = int(round(fig_height_px - bbox.y0))  # Bottom edge (X-axis position)

    axes_width_px = int(round(bbox.width))
    axes_height_px = int(round(bbox.height))

    # Convert to inches and mm
    axes_width_inch = bbox.width / dpi
    axes_height_inch = bbox.height / dpi
    axes_width_mm = inch_to_mm(axes_width_inch)
    axes_height_mm = inch_to_mm(axes_height_inch)

    # Calculate mm coordinates
    axes_x0_mm = (bbox.x0 / dpi) * MM_PER_INCH
    axes_x1_mm = (bbox.x1 / dpi) * MM_PER_INCH
    axes_y0_mm = ((fig_height_px - bbox.y1) / dpi) * MM_PER_INCH  # Top (flipped)
    axes_y1_mm = ((fig_height_px - bbox.y0) / dpi) * MM_PER_INCH  # Bottom (flipped)

    # Also get normalized position for reference
    pos = ax.get_position()

    return {
        # Figure dimensions
        "figure_size_inch": (fig_width_inch, fig_height_inch),
        "figure_size_mm": (fig_width_mm, fig_height_mm),
        "figure_size_px": (fig_width_px, fig_height_px),
        # Axes dimensions
        "axes_position": (pos.x0, pos.y0, pos.width, pos.height),
        "axes_size_inch": (axes_width_inch, axes_height_inch),
        "axes_size_mm": (axes_width_mm, axes_height_mm),
        "axes_size_px": (axes_width_px, axes_height_px),
        # Axes bounding box in pixels (for canvas/web alignment, origin top-left)
        # x0: left edge (Y-axis position), x1: right edge
        # y0: top edge, y1: bottom edge (X-axis position)
        "axes_bbox_px": {
            "x0": axes_x0_px,
            "y0": axes_y0_px,
            "x1": axes_x1_px,
            "y1": axes_y1_px,
            "width": axes_width_px,
            "height": axes_height_px,
        },
        # Axes bounding box in mm
        "axes_bbox_mm": {
            "x0": axes_x0_mm,
            "y0": axes_y0_mm,
            "x1": axes_x1_mm,
            "y1": axes_y1_mm,
            "width": axes_width_mm,
            "height": axes_height_mm,
        },
        # Settings
        "dpi": dpi,
        "mm_per_inch": MM_PER_INCH,
    }


def print_dimension_info(fig, ax):
    """
    Print dimension information in a human-readable format.

    This helps you understand what's actually happening with your figure!

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure object
    ax : matplotlib.axes.Axes
        Axes object

    Examples
    --------
    >>> fig, ax = create_axes_with_size_mm(30, 21)
    >>> print_dimension_info(fig, ax)
    """
    info = get_dimension_info(fig, ax)

    print("\n" + "=" * 60)
    print("DIMENSION INFORMATION")
    print("=" * 60)

    print("\n📐 FIGURE (total canvas including margins):")
    print(
        f"  • Size (mm):    {info['figure_size_mm'][0]:.2f} × {info['figure_size_mm'][1]:.2f}"
    )
    print(
        f"  • Size (inch):  {info['figure_size_inch'][0]:.3f} × {info['figure_size_inch'][1]:.3f}"
    )
    print(
        f"  • Size (px):    {info['figure_size_px'][0]} × {info['figure_size_px'][1]}"
    )

    print("\n📊 AXES (actual plot area):")
    print(
        f"  • Size (mm):    {info['axes_size_mm'][0]:.2f} × {info['axes_size_mm'][1]:.2f}"
    )
    print(
        f"  • Size (inch):  {info['axes_size_inch'][0]:.3f} × {info['axes_size_inch'][1]:.3f}"
    )
    print(f"  • Size (px):    {info['axes_size_px'][0]} × {info['axes_size_px'][1]}")
    print(
        f"  • Position:     left={info['axes_position'][0]:.3f}, bottom={info['axes_position'][1]:.3f}"
    )

    print("\n⚙️  SETTINGS:")
    print(f"  • DPI:          {info['dpi']}")
    print(f"  • Conversion:   1 inch = {info['mm_per_inch']} mm")

    print("\n💡 KEY RELATIONSHIPS:")
    print("  • pixels = inches × DPI")
    print("  • mm = inches × 25.4")
    print(f"  • At {info['dpi']} DPI:")
    print(f"    - 1 mm = {info['dpi'] / 25.4:.2f} pixels")
    print(f"    - 1 inch = {info['dpi']} pixels")

    print("\n📝 FOR PUBLICATION:")
    print(
        f"  • Save with: fig.savefig('file.tiff', dpi={info['dpi']}, bbox_inches='tight')"
    )
    print(
        f"  • Final size will be approximately {info['axes_size_mm'][0]:.1f} × {info['axes_size_mm'][1]:.1f} mm"
    )
    print("=" * 60 + "\n")


if __name__ == "__main__":
    import numpy as np

    print("=" * 60)
    print("DEMO: Axes-size-based figure creation")
    print("=" * 60)

    # Example 1: Publication mode (exact 30×21 mm axes)
    print("\n1. PUBLICATION MODE (30 mm × 21 mm axes)")
    print("-" * 60)
    fig, ax = create_axes_with_size_mm(
        axes_width_mm=30,
        axes_height_mm=21,
        mode="publication",
        style_mm={
            "axis_thickness_mm": 0.2,
            "tick_length_mm": 0.8,
            "tick_thickness_mm": 0.2,
            "axis_font_size_pt": 8,
            "tick_font_size_pt": 7,
        },
    )

    x = np.linspace(0, 2 * np.pi, 100)
    ax.plot(x, np.sin(x))
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    print_dimension_info(fig, ax)

    fig.savefig("/tmp/publication_mode.png", dpi=300, bbox_inches="tight")
    print("✅ Saved to /tmp/publication_mode.png")
    plt.close(fig)

    # Example 2: Display mode (same axes, scaled 3x for screen)
    print("\n2. DISPLAY MODE (same 30×21 mm, scaled 3x for screen)")
    print("-" * 60)
    fig, ax = create_axes_with_size_mm(
        axes_width_mm=30, axes_height_mm=21, mode="display"
    )

    ax.plot(x, np.sin(x))
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    print_dimension_info(fig, ax)

    fig.savefig("/tmp/display_mode.png", dpi=100)
    print("✅ Saved to /tmp/display_mode.png")
    plt.close(fig)

# EOF
