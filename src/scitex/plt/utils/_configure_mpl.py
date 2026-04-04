#!/usr/bin/env python3
# Timestamp: "2025-12-02 12:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/plt/utils/_configure_mpl.py


import logging
from typing import Any, Dict, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np

import scitex
from scitex.dict import DotDict

logger = logging.getLogger(__name__)


def configure_mpl(
    plt,
    fig_size_mm: Optional[Tuple[float, float]] = None,
    fig_scale: float = 1.0,
    dpi_display: Optional[int] = None,
    dpi_save: Optional[int] = None,
    autolayout: bool = True,
    n_ticks: Optional[int] = None,
    hide_top_right_spines: Optional[bool] = None,
    line_width: Optional[float] = None,
    alpha: float = 1.0,
    enable_latex: bool = False,
    latex_preamble: Optional[str] = None,
    verbose: bool = False,
    **kwargs,
) -> Tuple[Any, Dict]:
    """Configures Matplotlib settings for publication-quality plots.

    All default values are loaded from SCITEX_STYLE.yaml. Parameters passed
    directly to this function override the YAML values.

    Parameters
    ----------
    plt : matplotlib.pyplot
        Matplotlib pyplot module
    fig_size_mm : tuple of float, optional
        Figure width and height in millimeters. If None, calculated from
        YAML axes dimensions + margins.
    fig_scale : float, optional
        Scaling factor for figure size, by default 1.0
    dpi_display : int, optional
        Display resolution in DPI. If None, uses YAML output.dpi / 3.
    dpi_save : int, optional
        Saving resolution in DPI. If None, uses YAML output.dpi.
    autolayout : bool, optional
        Whether to enable automatic tight layout, by default True
    hide_top_right_spines : bool, optional
        Whether to hide top and right spines. If None, uses YAML behavior settings.
    line_width : float, optional
        Default line width in points. If None, converts YAML lines.trace_mm to pt.
    alpha : float, optional
        Color transparency, by default 1.0
    n_ticks : int, optional
        Number of ticks on each axis. If None, uses YAML ticks.n_ticks.
    verbose : bool, optional
        Whether to print configuration details, by default False

    Returns
    -------
    tuple
        (plt, DotDict of RGBA colors) - Access as COLORS.blue or COLORS['blue']

    Notes
    -----
    Style values are resolved from SCITEX_STYLE.yaml located at:
    scitex/plt/styles/SCITEX_STYLE.yaml

    The YAML file contains all default values for:
    - Axes dimensions (width_mm, height_mm, thickness_mm)
    - Margins and spacing
    - Font sizes (axis_label_pt, tick_label_pt, title_pt, legend_pt)
    - Line thicknesses (trace_mm, errorbar_mm, etc.)
    - Tick settings (length_mm, thickness_mm, direction, n_ticks)
    - Output settings (dpi, transparent)
    - Behavior flags (hide_top_spine, hide_right_spine, grid)
    """
    # Load style from YAML
    from scitex.plt.styles import load_style, resolve_style_value

    style = load_style()

    # mm to pt conversion factor
    mm_to_pt = 2.83465

    # Resolve values with priority: direct → env → yaml → default
    # If parameter is None, use YAML value; otherwise use the passed value

    # Figure size: calculate from axes + margins if not specified
    if fig_size_mm is None:
        axes_w = resolve_style_value("axes.width_mm", None, 40)
        axes_h = resolve_style_value("axes.height_mm", None, 28)
        margin_l = resolve_style_value("margins.left_mm", None, 20)
        margin_r = resolve_style_value("margins.right_mm", None, 20)
        margin_b = resolve_style_value("margins.bottom_mm", None, 20)
        margin_t = resolve_style_value("margins.top_mm", None, 20)
        fig_size_mm = (axes_w + margin_l + margin_r, axes_h + margin_b + margin_t)

    # DPI
    yaml_dpi = int(resolve_style_value("output.dpi", None, 300))
    if dpi_save is None:
        dpi_save = yaml_dpi
    if dpi_display is None:
        dpi_display = max(100, yaml_dpi // 3)  # Lower DPI for display

    # Line width: convert from mm to pt if using YAML value
    if line_width is None:
        trace_mm = resolve_style_value("lines.trace_mm", None, 0.2)
        line_width = trace_mm * mm_to_pt

    # Ticks
    if n_ticks is None:
        n_ticks = int(resolve_style_value("ticks.n_ticks", None, 4))

    # Spines
    if hide_top_right_spines is None:
        hide_top = resolve_style_value("behavior.hide_top_spine", None, True, bool)
        hide_right = resolve_style_value("behavior.hide_right_spine", None, True, bool)
        hide_top_right_spines = hide_top and hide_right

    # Font sizes from YAML
    font_size = resolve_style_value("fonts.axis_label_pt", None, 7)
    title_size = resolve_style_value("fonts.title_pt", None, 8)
    tick_size = resolve_style_value("fonts.tick_label_pt", None, 7)
    legend_size = resolve_style_value("fonts.legend_pt", None, 6)

    # Axis thickness from YAML
    axes_linewidth = resolve_style_value("axes.thickness_mm", None, 0.2) * mm_to_pt

    # Colors
    RGBA = {
        k: scitex.plt.color.update_alpha(v, alpha)
        for k, v in scitex.plt.color.PARAMS["RGBA"].items()
    }

    RGBA_NORM = {
        k: tuple(scitex.plt.color.update_alpha(v, alpha))
        for k, v in scitex.plt.color.PARAMS["RGBA_NORM"].items()
    }

    RGBA_NORM_FOR_CYCLE = {
        k: tuple(scitex.plt.color.update_alpha(v, alpha))
        for k, v in scitex.plt.color.PARAMS["RGBA_NORM_FOR_CYCLE"].items()
    }

    # Normalize figure size from mm to inches
    figsize_inch = (
        fig_size_mm[0] / 25.4 * fig_scale,
        fig_size_mm[1] / 25.4 * fig_scale,
    )

    # Prepare matplotlib configuration using YAML-derived values
    mpl_config = {
        # Resolution
        "figure.dpi": dpi_display,
        "savefig.dpi": dpi_save,
        # Figure Size
        "figure.figsize": figsize_inch,
        # Font Sizes from YAML
        "font.size": font_size,
        "axes.titlesize": title_size,
        "axes.labelsize": font_size,
        "xtick.labelsize": tick_size,
        "ytick.labelsize": tick_size,
        # Legend configuration from YAML
        "legend.fontsize": legend_size,
        "legend.frameon": False,
        "legend.loc": "best",
        # Auto Layout
        "figure.autolayout": autolayout,
        # Top and Right Axes from YAML
        "axes.spines.top": not hide_top_right_spines,
        "axes.spines.right": not hide_top_right_spines,
        # Spine width from YAML (converted from mm to pt)
        "axes.linewidth": axes_linewidth,
        # Custom color cycle
        "axes.prop_cycle": plt.cycler(color=list(RGBA_NORM_FOR_CYCLE.values())),
        # Line width from YAML (converted from mm to pt)
        "lines.linewidth": line_width,
        "lines.markersize": 6.0,
        # Grid (if used)
        "grid.linewidth": axes_linewidth,
        "grid.alpha": 0.3,
    }

    # Configure LaTeX rendering if enabled with enhanced fallback
    if enable_latex:
        latex_success = False
        try:
            # Try to enable LaTeX rendering
            test_config = {
                "text.usetex": True,
                "text.latex.preamble": latex_preamble
                or r"\usepackage{amsmath}\usepackage{amssymb}",
                "font.family": "serif",
                "font.serif": ["Computer Modern Roman"],
                "mathtext.fontset": "cm",
            }

            # Test LaTeX capability before applying
            with plt.rc_context(test_config):
                try:
                    # Create a test figure to verify LaTeX works
                    fig, ax = plt.subplots(figsize=(1, 1))
                    ax.text(0.5, 0.5, r"$x^2 + y^2 = r^2$", usetex=True)
                    fig.canvas.draw()  # Force rendering
                    plt.close(fig)
                    latex_success = True
                except Exception as latex_error:
                    plt.close(fig)
                    if verbose:
                        print(f"⚠️  LaTeX test render failed: {latex_error}")
                    raise latex_error

            if latex_success:
                mpl_config.update(test_config)
                if verbose:
                    print("✅ LaTeX rendering enabled and tested")

        except Exception as e:
            if verbose:
                print(f"⚠️  LaTeX rendering failed, falling back to mathtext: {e}")
                print("    This may be due to missing LaTeX fonts or Node.js conflicts")

            # Enhanced fallback to mathtext with better configuration
            mpl_config.update(
                {
                    "text.usetex": False,
                    "mathtext.default": "regular",
                    "font.family": "serif",
                    "mathtext.fontset": "cm",
                    "mathtext.fallback": "cm",  # Fallback font for missing symbols
                }
            )

            # Enable LaTeX fallback mode in the str module
            try:
                from scitex.str import set_fallback_mode

                set_fallback_mode("force_mathtext")
                if verbose:
                    print("📝 Enabled automatic LaTeX fallback mode")
            except ImportError:
                if verbose:
                    print("⚠️  LaTeX fallback module not available")

    else:
        # Use sans-serif fonts without LaTeX
        # Try to enable Arial explicitly
        import os

        import matplotlib.font_manager as fm

        # Try to detect and register Arial fonts
        arial_enabled = False
        try:
            # First check if Arial is already available
            fm.findfont("Arial", fallback_to_default=False)
            arial_enabled = True
        except Exception:
            # Search for Arial font files and register them
            arial_paths = [
                f
                for f in fm.findSystemFonts()
                if os.path.basename(f).lower().startswith("arial")
            ]

            if arial_paths:
                for path in arial_paths:
                    try:
                        fm.fontManager.addfont(path)
                    except Exception:
                        pass

                # Verify Arial is now available
                try:
                    fm.findfont("Arial", fallback_to_default=False)
                    arial_enabled = True
                except Exception:
                    pass

        # Configure font family
        if arial_enabled:
            mpl_config.update(
                {
                    "text.usetex": False,
                    "font.family": "Arial",
                    "font.sans-serif": [
                        "Arial",
                        "Helvetica",
                        "DejaVu Sans",
                        "Liberation Sans",
                    ],
                    "mathtext.fontset": "dejavusans",
                    "mathtext.default": "regular",
                }
            )
        else:
            # Fall back to sans-serif with Helvetica/DejaVu Sans
            mpl_config.update(
                {
                    "text.usetex": False,
                    "font.family": "sans-serif",
                    "font.sans-serif": [
                        "Helvetica",
                        "DejaVu Sans",
                        "Liberation Sans",
                        "sans-serif",
                    ],
                    "mathtext.fontset": "dejavusans",
                    "mathtext.default": "regular",
                }
            )

            # Warn user about missing Arial using scitex.logging
            from scitex import logging as _logging

            _logger = _logging.getLogger(__name__)
            _logger.warning(
                "Arial font not found. Using fallback fonts (Helvetica/DejaVu Sans). "
                "For publication figures with Arial: sudo apt-get install ttf-mscorefonts-installer && fc-cache -fv"
            )

        # Suppress matplotlib's own font warnings
        import logging

        logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)

        # Set fallback mode to mathtext
        try:
            from scitex.str import set_fallback_mode

            set_fallback_mode("force_mathtext")
        except ImportError:
            pass

    # Update Matplotlib configuration
    plt.rcParams.update(mpl_config)

    if verbose:
        colors_str = "\n".join(
            f"  {color_str}: {rgba}" for color_str, rgba in RGBA.items()
        )
        config_msg = (
            f"\n{'-' * 40}\n"
            f"Matplotlib has been configured as follows:\n\n"
            f"Figure DPI (Display): {dpi_display} DPI\n"
            f"Figure DPI (Save): {dpi_save} DPI\n"
            f"Figure Size (Not the Axis Size): "
            f"{fig_size_mm[0] * fig_scale:.1f} x "
            f"{fig_size_mm[1] * fig_scale:.1f} mm (width x height)\n"
            f"\nHide Top and Right Axes: {hide_top_right_spines}\n"
            f"Line Width: {line_width}\n"
            f"\nCustom Colors (RGBA):\n"
            f"{colors_str}\n"
            f"{'-' * 40}"
        )
        logger.info(config_msg)

    # Store n_ticks for later use
    plt._n_ticks = n_ticks

    # Add a utility function to plt
    def set_n_ticks(ax, n=None):
        if n is None:
            n = plt._n_ticks
        ax.xaxis.set_major_locator(plt.MaxNLocator(n))
        ax.yaxis.set_major_locator(plt.MaxNLocator(n))

    plt.set_n_ticks = set_n_ticks

    # Convert to DotDict for convenient access (COLORS.blue or COLORS['blue'])
    return plt, DotDict(RGBA_NORM)


# def _convert_font_size(size: Union[str, int, float]) -> float:
#     """Converts various font size specifications to numerical values.

#     Parameters
#     ----------
#     size : Union[str, int, float]
#         Font size specification. Can be:
#         - String: 'xx-small', 'x-small', 'small', 'medium', 'large', 'x-large', 'xx-large'
#         - Numeric: direct point size value

#     Returns
#     -------
#     float
#         Font size in points
#     """
#     if isinstance(size, str):
#         size_map = {
#             "xx-small": 9,
#             "x-small": 11,
#             "small": 13,
#             "medium": 15,
#             "large": 18,
#             "x-large": 22,
#             "xx-large": 26,
#         }
#         return size_map.get(size.lower(), 15)
#     elif isinstance(size, (int, float)):
#         return max(float(size), 9.0)  # Ensure minimum size of 9
#     else:
#         raise ValueError(f"Unsupported font size type: {type(size)}")


if __name__ == "__main__":
    plt, CC = configure_mpl(plt)
    fig, axes = plt.subplots(nrows=2, sharex=True, sharey=True)
    x = np.linspace(0, 10, 100)
    for idx_cc, cc_str in enumerate(CC):
        phase_shift = idx_cc * np.pi / len(CC)
        y = np.sin(x + phase_shift)
        axes[0].plot(x, y, label="Default color cycle")
        axes[1].plot(x, y, color=CC[cc_str], label=f"{cc_str}")
    axes[0].legend()
    axes[1].legend()
    plt.show()

# EOF
