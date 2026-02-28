#!/usr/bin/env python3
# Timestamp: "2025-11-19 12:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/plt/utils/_figure_mm.py

"""
Millimeter-based figure creation utilities for matplotlib.

This module provides functions to create matplotlib figures and axes with
precise millimeter-based control over dimensions, margins, and styling.
This is particularly useful for creating publication-quality figures that
need to meet specific size requirements (e.g., Nature, Science journals).

Supports dark/light theme modes for eye-friendly visualization.
"""

__FILE__ = __file__

from typing import TYPE_CHECKING, Dict, Optional, Tuple

import matplotlib.pyplot as plt
from figrecipe.utils import mm_to_inch, mm_to_pt
from matplotlib.axes import Axes

# Default theme color palettes
# Both modes use transparent background by default for flexibility
# Dark mode: all text elements (labels, ticks, spines) use same soft white color
# Light mode: all text elements use black
THEME_COLORS = {
    "dark": {
        "background": "transparent",  # Transparent for overlay on dark backgrounds
        "axes_bg": "transparent",  # Transparent axes background
        "text": "#e8e8e8",  # Soft white (reduced strain)
        "spine": "#e8e8e8",  # Same as text (like black in light mode)
        "tick": "#e8e8e8",  # Same as text
        "grid": "#3a3a4a",  # Subtle grid
    },
    "light": {
        "background": "transparent",  # Transparent for overlay on light backgrounds
        "axes_bg": "transparent",  # Transparent axes background
        "text": "black",  # Black text
        "spine": "black",  # Black spines
        "tick": "black",  # Black ticks
        "grid": "#cccccc",  # Light gray grid
    },
}


def _apply_theme_colors(  # noqa: C901
    ax: Axes, theme: str = "light", custom_colors: Optional[Dict[str, str]] = None
) -> None:
    """
    Apply theme colors to axes for dark/light mode support.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Target axes to apply theme to
    theme : str
        Color theme: "light" or "dark" (default: "light")
    custom_colors : dict, optional
        Custom color overrides. Keys: background, axes_bg, text, spine, tick, grid

    Examples
    --------
    >>> fig, ax = plt.subplots()
    >>> _apply_theme_colors(ax, theme="dark")  # Eye-friendly dark mode
    """
    # Get base theme colors
    colors = THEME_COLORS.get(theme, THEME_COLORS["light"]).copy()

    # Apply custom overrides
    if custom_colors:
        colors.update(custom_colors)

    # Apply axes background
    if colors["axes_bg"] != "transparent":
        ax.set_facecolor(colors["axes_bg"])
        ax.patch.set_alpha(1.0)
    else:
        ax.patch.set_alpha(0.0)

    # Apply figure background if accessible
    fig = ax.get_figure()
    if fig is not None:
        if colors["background"] != "transparent":
            fig.patch.set_facecolor(colors["background"])
            fig.patch.set_alpha(1.0)
        else:
            fig.patch.set_alpha(0.0)

    # Apply text colors (labels, titles)
    ax.xaxis.label.set_color(colors["text"])
    ax.yaxis.label.set_color(colors["text"])
    ax.title.set_color(colors["text"])

    # Apply spine colors
    for spine in ax.spines.values():
        spine.set_color(colors["spine"])

    # Apply tick colors (both marks and labels)
    ax.tick_params(colors=colors["tick"], which="both")
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_color(colors["tick"])

    # Apply legend colors if legend exists
    legend = ax.get_legend()
    if legend is not None:
        # Legend text color
        for text in legend.get_texts():
            text.set_color(colors["text"])
        # Legend title if present
        title = legend.get_title()
        if title:
            title.set_color(colors["text"])
        # Legend frame
        frame = legend.get_frame()
        if frame:
            if colors["axes_bg"] != "transparent":
                frame.set_facecolor(colors["axes_bg"])
            frame.set_edgecolor(colors["spine"])

    # Store theme in axes metadata for reference
    if hasattr(ax, "_scitex_metadata"):
        ax._scitex_metadata["theme"] = theme
        ax._scitex_metadata["theme_colors"] = colors


if TYPE_CHECKING:
    from scitex.plt._subplots._AxisWrapper import AxisWrapper
    from scitex.plt._subplots._FigWrapper import FigWrapper


def create_figure_ax_mm(
    fig_width_mm: float = 35.0,
    fig_height_mm: float = 24.5,
    dpi: int = 300,
    *,
    left_margin_mm: float = 4.0,
    right_margin_mm: float = 2.0,
    bottom_margin_mm: float = 4.0,
    top_margin_mm: float = 2.0,
    style: Optional[Dict] = None,
) -> Tuple["FigWrapper", "AxisWrapper"]:
    """
    Create a Matplotlib figure and a single Axes with millimeter control.

    This function creates a figure with exact millimeter dimensions and positions
    the axes with specified margins. All measurements are in millimeters, allowing
    for precise control over the final output size.

    Parameters
    ----------
    fig_width_mm : float, optional
        Total figure width in millimeters (default: 35.0)
    fig_height_mm : float, optional
        Total figure height in millimeters (default: 24.5)
    dpi : int, optional
        Resolution in dots per inch for saving (default: 300)
    left_margin_mm : float, optional
        Left margin between figure edge and axis box, in millimeters (default: 4.0)
    right_margin_mm : float, optional
        Right margin between figure edge and axis box, in millimeters (default: 2.0)
    bottom_margin_mm : float, optional
        Bottom margin between figure edge and axis box, in millimeters (default: 4.0)
    top_margin_mm : float, optional
        Top margin between figure edge and axis box, in millimeters (default: 2.0)
    style : dict or None, optional
        Optional style specification dictionary. If provided, will be passed to
        apply_style_mm(). Expected keys:
        - 'axis_thickness_mm': Axis spine thickness in mm
        - 'trace_thickness_mm': Plot line thickness in mm
        - 'tick_length_mm': Tick mark length in mm
        - 'tick_thickness_mm': Tick mark thickness in mm
        - 'axis_font_size_pt': Axis label font size in points
        - 'tick_font_size_pt': Tick label font size in points

    Returns
    -------
    fig : matplotlib.figure.Figure
        Created figure with specified dimensions
    ax : matplotlib.axes.Axes
        Created axes occupying the specified mm box with margins

    Examples
    --------
    Create a basic figure with default settings:

    >>> fig, ax = create_figure_ax_mm()
    >>> ax.plot([0, 1], [0, 1])
    >>> fig.savefig("test.png", dpi=300)

    Create a figure with custom dimensions and style:

    >>> style = {
    ...     'axis_thickness_mm': 0.2,
    ...     'trace_thickness_mm': 0.12,
    ...     'tick_length_mm': 0.8,
    ...     'tick_thickness_mm': 0.2,
    ...     'axis_font_size_pt': 7,
    ...     'tick_font_size_pt': 7,
    ... }
    >>> fig, ax = create_figure_ax_mm(
    ...     fig_width_mm=35,
    ...     fig_height_mm=24.5,
    ...     dpi=300,
    ...     left_margin_mm=4,
    ...     right_margin_mm=2,
    ...     bottom_margin_mm=4,
    ...     top_margin_mm=2,
    ...     style=style,
    ... )
    >>> ax.plot(x, y)
    >>> fig.savefig("test.tiff", dpi=300)

    Notes
    -----
    - The final saved figure will have exact physical dimensions when printed
      or embedded in documents (Word, PowerPoint, LaTeX)
    - The display size in browser/screen may appear different from the physical
      size, but the saved file will be correct
    - Use dpi=300 for high-quality publication figures
    """
    # Convert figure size from mm to inches (matplotlib uses inches)
    figsize_inch = (mm_to_inch(fig_width_mm), mm_to_inch(fig_height_mm))
    fig = plt.figure(figsize=figsize_inch, dpi=dpi)

    # Calculate axes position in figure coordinates [0–1]
    # The axes box occupies the space between margins
    axis_width_mm = fig_width_mm - left_margin_mm - right_margin_mm
    axis_height_mm = fig_height_mm - bottom_margin_mm - top_margin_mm

    # Convert to figure coordinates (0 to 1)
    left = left_margin_mm / fig_width_mm
    bottom = bottom_margin_mm / fig_height_mm
    width = axis_width_mm / fig_width_mm
    height = axis_height_mm / fig_height_mm

    # Create axes with exact position and transparent background if requested
    ax = fig.add_axes([left, bottom, width, height])
    # Make axes background transparent when figure background is transparent
    if fig.get_facecolor() == (0, 0, 0, 0) or fig.get_facecolor() == "none":
        ax.patch.set_alpha(0.0)

    # Apply styling if provided
    if style is not None:
        apply_style_mm(ax, style)

    # Tag axes with metadata for later embedding
    # Calculate actual axes size from figure size and margins
    axes_width_mm = fig_width_mm - left_margin_mm - right_margin_mm
    axes_height_mm = fig_height_mm - bottom_margin_mm - top_margin_mm

    ax._scitex_metadata = {
        "created_with": "scitex.plt.utils.create_figure_ax_mm",
        "mode": "publication",  # This function always uses publication mode
        "figure_size_mm": (fig_width_mm, fig_height_mm),
        "axes_size_mm": (axes_width_mm, axes_height_mm),
        "margin_mm": {
            "left": left_margin_mm,
            "right": right_margin_mm,
            "bottom": bottom_margin_mm,
            "top": top_margin_mm,
        },
        "style_mm": style,
    }

    # Wrap in scitex wrappers for consistent API
    from scitex.plt._subplots._AxisWrapper import AxisWrapper
    from scitex.plt._subplots._FigWrapper import FigWrapper

    fig_wrapped = FigWrapper(fig)
    ax_wrapped = AxisWrapper(fig_wrapped, ax, track=False)

    # Store axes reference in FigWrapper
    fig_wrapped.axes = ax_wrapped  # type: ignore[attr-defined]

    return fig_wrapped, ax_wrapped


def apply_style_mm(ax: Axes, style: Dict) -> float:
    """
    Apply Nature-like style using millimeter-based settings.

    This function applies styling to matplotlib axes using millimeter and point
    measurements for precise control over visual elements. This is useful for
    meeting journal requirements (e.g., Nature, Science specifications).

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Target axes to apply styling to
    style : dict
        Dictionary containing styling parameters. Supported keys:
        - 'axis_thickness_mm' (float): Spine line width in mm (default: 0.2)
        - 'trace_thickness_mm' (float): Plot line width in mm (default: 0.12)
        - 'tick_length_mm' (float): Tick mark length in mm (default: 0.8)
        - 'tick_thickness_mm' (float): Tick mark width in mm (default: 0.2)
        - 'tick_cap_width_mm' (float): Tick cap width in mm (default: 0.8)
        - 'marker_size_mm' (float): Default marker size in mm (default: 0.8)
        - 'axis_font_size_pt' (float): Axis label font size in points (default: 8)
        - 'tick_font_size_pt' (float): Tick label font size in points (default: 7)
        - 'n_ticks' (int): Number of ticks on each axis (default: 4)
        - 'theme' (str): Color theme "light" or "dark" (default: "light")
        - 'theme_colors' (dict): Custom theme color overrides

    Returns
    -------
    float
        Trace line width in points, to be used with ax.plot(..., lw=trace_lw)

    Examples
    --------
    >>> fig, ax = plt.subplots()
    >>> style = {
    ...     'axis_thickness_mm': 0.2,
    ...     'trace_thickness_mm': 0.12,
    ...     'tick_length_mm': 0.8,
    ...     'tick_thickness_mm': 0.2,
    ...     'axis_font_size_pt': 7,
    ...     'tick_font_size_pt': 7,
    ...     'theme': 'dark',  # Enable dark mode
    ... }
    >>> trace_lw = apply_style_mm(ax, style)
    >>> ax.plot(x, y, lw=trace_lw)

    Notes
    -----
    - All thickness/width measurements are converted from mm to points
    - Font sizes are specified directly in points
    - The returned trace linewidth should be used when plotting to maintain
      consistent styling across all plot elements
    """
    # Apply theme colors (dark/light mode)
    theme = style.get("theme", "light")
    theme_colors = style.get("theme_colors", None)
    _apply_theme_colors(ax, theme, theme_colors)

    # Convert spine thickness from mm to points
    axis_lw_pt = mm_to_pt(style.get("axis_thickness_mm", 0.2))
    for spine in ax.spines.values():
        spine.set_linewidth(axis_lw_pt)

    # Convert trace thickness from mm to points
    trace_lw_pt = mm_to_pt(style.get("trace_thickness_mm", 0.12))

    # Convert marker size from mm to points and set as default
    # Marker size in matplotlib is specified in points
    marker_size_mm = style.get("marker_size_mm")
    if marker_size_mm is not None:
        marker_size_pt = mm_to_pt(marker_size_mm)
        import matplotlib as mpl

        mpl.rcParams["lines.markersize"] = marker_size_pt

    # Configure tick parameters (all mm values converted to points)
    # width = tick line thickness, length = tick line length
    # pad = distance between ticks and tick labels (Nature-style: 1.5pt)
    tick_pad_pt = style.get("tick_pad_pt", 1.5)
    ax.tick_params(
        direction="out",
        length=mm_to_pt(style.get("tick_length_mm", 0.8)),
        width=mm_to_pt(style.get("tick_thickness_mm", 0.2)),
        pad=tick_pad_pt,  # Tight padding for Nature-style figures
    )

    # Apply font sizes and family (Arial for Nature-style look)
    axis_fs = style.get("axis_font_size_pt", 7)
    tick_fs = style.get("tick_font_size_pt", 7)
    title_fs = style.get("title_font_size_pt", 7)
    legend_fs = style.get("legend_font_size_pt", 6)
    label_pad_pt = style.get("label_pad_pt", 1.5)  # Nature-style tight padding
    font_family = style.get("font_family", "Arial")

    ax.xaxis.label.set_fontsize(axis_fs)
    ax.xaxis.label.set_fontfamily(font_family)
    ax.xaxis.labelpad = label_pad_pt  # Set tight label padding
    ax.yaxis.label.set_fontsize(axis_fs)
    ax.yaxis.label.set_fontfamily(font_family)
    ax.yaxis.labelpad = label_pad_pt  # Set tight label padding

    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontsize(tick_fs)
        label.set_fontfamily(font_family)

    # Set title font, size, and padding
    ax.title.set_fontfamily(font_family)
    ax.title.set_fontsize(title_fs)

    # Set title padding (distance from top of axes box)
    # Nature-style: 4pt (tighter than matplotlib default ~6pt)
    title_pad_pt = style.get("title_pad_pt", 4)
    # Apply padding by re-setting the title with the pad parameter
    # This works even if title is empty
    ax.set_title(ax.get_title(), pad=title_pad_pt)

    # Set legend font size if legend exists
    legend = ax.get_legend()
    if legend is not None:
        for text in legend.get_texts():
            text.set_fontsize(legend_fs)
            text.set_fontfamily(font_family)

    # Disable grids by default
    ax.grid(False)

    # Ensure axes spines are in front of plot elements (e.g., histogram bars)
    # Set high zorder on spines so they appear on top
    for spine in ax.spines.values():
        spine.set_zorder(1000)
    # Also ensure ticks are on top
    ax.tick_params(zorder=1000)

    # Note: n_ticks is NOT applied here at figure creation time
    # because we don't know yet if axes will be categorical or numerical.
    # MaxNLocator will be applied in post-processing after plotting,
    # only to numerical (non-categorical) axes.
    # See _AxisWrapper.py for the implementation.

    # Return trace linewidth for use in plotting
    return trace_lw_pt  # type: ignore[no-any-return]


if __name__ == "__main__":
    import numpy as np

    # Example usage
    print("Creating a test figure with mm control...")

    # Define Nature-like style
    nature_style = {
        "axis_thickness_mm": 0.2,
        "trace_thickness_mm": 0.12,
        "tick_length_mm": 0.8,
        "tick_thickness_mm": 0.2,
        "axis_font_size_pt": 8,
        "tick_font_size_pt": 7,
    }

    # Create figure with exact dimensions
    fig, ax = create_figure_ax_mm(
        fig_width_mm=35,
        fig_height_mm=35 * 0.7,  # Height is 70% of width
        dpi=300,
        left_margin_mm=4.0,
        right_margin_mm=2.0,
        bottom_margin_mm=4.0,
        top_margin_mm=2.0,
        style=nature_style,
    )

    # Plot some data
    x = np.linspace(0, 2 * np.pi, 100)
    y = np.sin(x)
    trace_lw = mm_to_pt(nature_style["trace_thickness_mm"])
    ax.plot(x, y, color="tab:blue", lw=trace_lw)

    # Add labels
    ax.set_title("Test Plot with mm Control")
    ax.set_xlabel("X axis (rad)")
    ax.set_ylabel("Y axis")

    # Save the figure
    output_path = "/tmp/test_mm_control.png"
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Figure saved to: {output_path}")
    print(f"Physical size: 35 mm × {35 * 0.7:.1f} mm")

# EOF
