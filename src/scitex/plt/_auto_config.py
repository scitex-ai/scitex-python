#!/usr/bin/env python3
# Timestamp: "2026-02-17 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/plt/_auto_config.py
"""Auto-configure matplotlib with SciTeX defaults.

Called once at ``import scitex.plt`` time to register fonts, load the
SCITEX style preset, apply rcParams, and set up the colour cycle.
"""

import os

import matplotlib as mpl
import matplotlib.font_manager as fm
import matplotlib.pyplot as _plt

__all__ = ["configure"]


def _register_arial_fonts() -> bool:
    """Register Arial fonts if available."""
    try:
        fm.findfont("Arial", fallback_to_default=False)
        return True
    except Exception:
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

            try:
                fm.findfont("Arial", fallback_to_default=False)
                return True
            except Exception:
                pass
        return False


def _apply_rcparams(figrecipe_available: bool, load_style_fn):
    """Apply SciTeX style configuration as global rcParams."""
    if figrecipe_available:
        try:
            load_style_fn("SCITEX")
        except Exception:
            pass

    from .styles import resolve_style_value

    mm_to_pt = 2.83465

    font_size = resolve_style_value("fonts.axis_label_pt", None, 7)
    title_size = resolve_style_value("fonts.title_pt", None, 8)
    tick_size = resolve_style_value("fonts.tick_label_pt", None, 7)
    legend_size = resolve_style_value("fonts.legend_pt", None, 6)

    trace_mm = resolve_style_value("lines.trace_mm", None, 0.2)
    line_width = trace_mm * mm_to_pt

    axes_thickness_mm = resolve_style_value("axes.thickness_mm", None, 0.2)
    axes_linewidth = axes_thickness_mm * mm_to_pt

    hide_top = resolve_style_value("behavior.hide_top_spine", None, True, bool)
    hide_right = resolve_style_value("behavior.hide_right_spine", None, True, bool)

    dpi = int(resolve_style_value("output.dpi", None, 300))

    axes_w = resolve_style_value("axes.width_mm", None, 40)
    axes_h = resolve_style_value("axes.height_mm", None, 28)
    margin_l = resolve_style_value("margins.left_mm", None, 20)
    margin_r = resolve_style_value("margins.right_mm", None, 20)
    margin_b = resolve_style_value("margins.bottom_mm", None, 20)
    margin_t = resolve_style_value("margins.top_mm", None, 20)
    fig_w_mm = axes_w + margin_l + margin_r
    fig_h_mm = axes_h + margin_b + margin_t
    figsize_inch = (fig_w_mm / 25.4, fig_h_mm / 25.4)

    mpl_config = {
        "figure.dpi": max(100, dpi // 3),
        "savefig.dpi": dpi,
        "figure.figsize": figsize_inch,
        "font.size": font_size,
        "axes.titlesize": title_size,
        "axes.labelsize": font_size,
        "xtick.labelsize": tick_size,
        "ytick.labelsize": tick_size,
        "legend.fontsize": legend_size,
        "legend.frameon": False,
        "legend.loc": "best",
        "figure.autolayout": True,
        "axes.spines.top": not hide_top,
        "axes.spines.right": not hide_right,
        "axes.linewidth": axes_linewidth,
        "lines.linewidth": line_width,
        "lines.markersize": 6.0,
        "grid.linewidth": axes_linewidth,
        "grid.alpha": 0.3,
        "mathtext.fontset": "dejavusans",
        "mathtext.default": "regular",
    }

    mpl.rcParams.update(mpl_config)


def _setup_font_family(arial_enabled: bool):
    """Configure font family based on Arial availability."""
    if arial_enabled:
        mpl.rcParams["font.family"] = "Arial"
        mpl.rcParams["font.sans-serif"] = [
            "Arial",
            "Helvetica",
            "DejaVu Sans",
            "Liberation Sans",
        ]
    else:
        mpl.rcParams["font.family"] = "sans-serif"
        mpl.rcParams["font.sans-serif"] = [
            "Helvetica",
            "DejaVu Sans",
            "Liberation Sans",
            "sans-serif",
        ]
        import logging

        logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)


def _setup_color_cycle(color_module):
    """Set up color cycle from scitex colors."""
    try:
        _rgba_norm_cycle = {
            k: tuple(color_module.update_alpha(v, 1.0))
            for k, v in color_module.PARAMS.get("RGBA_NORM_FOR_CYCLE", {}).items()
        }
        if _rgba_norm_cycle:
            mpl.rcParams["axes.prop_cycle"] = _plt.cycler(
                color=list(_rgba_norm_cycle.values())
            )
    except Exception:
        pass


def configure(figrecipe_available: bool, load_style_fn, color_module):
    """Run the full auto-configuration sequence.

    Parameters
    ----------
    figrecipe_available : bool
        Whether figrecipe is importable.
    load_style_fn : callable
        The ``load_style`` function (may be a stub).
    color_module : module
        ``scitex.plt.color`` module for the colour cycle.
    """
    arial_enabled = _register_arial_fonts()
    _setup_font_family(arial_enabled)
    _apply_rcparams(figrecipe_available, load_style_fn)
    _setup_color_cycle(color_module)


# EOF
