#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-01 19:16:25 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/examples/plt/demo_style_config/demo_style_config.py


"""
Demo: SciTeX Style Configuration

Style Control Levels
====================
1. Global level (stx.plt.subplots):
   - Axes dimensions, margins, fonts, default line thickness
   - Example: stx.plt.subplots(axes_width_mm=60, trace_thickness_mm=0.3)

2. Plot level (ax.plot, ax.scatter, etc.):
   - Per-call override via style= dict
   - Example: ax.plot(x, y, style={"trace_thickness_mm": 0.5})

Priority Cascade
================
For each style value: direct kwarg → env var → yaml config → default

Style Management
================
- load_style(path): Load style from YAML/JSON file
- save_style(path): Export current style to file
- set_style(style_dict): Change active style globally

Naming Conventions
==================
- YAML keys: axes.width_mm (hierarchical with dots)
- Env vars: SCITEX_PLT_AXES_WIDTH_MM (prefix + dots→underscores + UPPERCASE)
- Python kwargs: axes_width_mm (flat names)

Usage
=====
    python demo_style_config.py
    SCITEX_PLT_AXES_WIDTH_MM=60 python demo_style_config.py
"""

import numpy as np
import scitex as stx
from pathlib import Path

OUTPUT_DIR = "./style_config_out"


def demo_all_parameters():
    """Demo all stx.plt.subplots() parameters with None defaults (cascade resolution)."""
    fig, ax = stx.plt.subplots(
        # nrows, ncols
        1,
        1,
        # Tracking
        track=None,
        sharex=None,
        sharey=None,
        constrained_layout=None,
        # Dimensions (mm) - None triggers cascade: env → yaml → default
        axes_width_mm=None,  # cascade (40 default, scalar or list)
        axes_height_mm=None,  # cascade (28 default, scalar or list)
        margin_left_mm=None,  # cascade (20 default)
        margin_right_mm=None,  # cascade (20 default)
        margin_bottom_mm=None,  # cascade (20 default)
        margin_top_mm=None,  # cascade (20 default)
        space_w_mm=None,  # cascade (8 default)
        space_h_mm=None,  # cascade (10 default)
        axes_thickness_mm=None,  # cascade (0.2 default)
        tick_length_mm=None,  # cascade (0.8 default)
        tick_thickness_mm=None,  # cascade (0.2 default)
        trace_thickness_mm=None,  # cascade (0.2 default)
        marker_size_mm=None,  # cascade (0.8 default)
        # Fonts (pt) - None triggers cascade: env → yaml → default
        axis_font_size_pt=None,  # cascade (7 default)
        tick_font_size_pt=None,  # cascade (7 default)
        title_font_size_pt=None,  # cascade (8 default)
        legend_font_size_pt=None,  # cascade (6 default)
        suptitle_font_size_pt=None,  # cascade (8 default)
        # Other - None triggers cascade: env → yaml → default
        n_ticks=None,  # cascade (4 default)
        mode=None,  # cascade (publication default)
        dpi=None,  # cascade (300 default)
        transparent=None,
    )
    x = np.linspace(0, 2 * np.pi, 100)
    ax.plot(x, np.sin(x), label="sin")
    ax.plot(x, np.cos(x), label="cos")
    ax.set_xyt("X", "Y", "All Parameters Explicit")
    ax.legend()
    return fig


def demo_default():
    """Default - uses cascade resolution automatically."""
    fig, ax = stx.plt.subplots()
    x = np.linspace(0, 2 * np.pi, 100)
    ax.plot(x, np.sin(x), label="sin")
    ax.plot(x, np.cos(x), label="cos")
    ax.set_xyt("X", "Y", "Default (cascade)")
    ax.legend()
    return fig


def demo_direct_override():
    """Direct override takes highest priority."""
    fig, ax = stx.plt.subplots(axes_width_mm=60, axes_height_mm=40)
    x = np.linspace(0, 5, 100)
    ax.fill_between(x, np.sin(x), alpha=0.3)
    ax.plot(x, np.sin(x))
    ax.set_xyt("X", "Y", "Direct Override (60x40mm)")
    return fig


def demo_env_override():
    """Environment variable override."""
    import os
    from scitex.plt.styles import resolve_style_value

    env_width = os.getenv("SCITEX_PLT_AXES_WIDTH_MM")
    width = resolve_style_value("axes.width_mm")

    fig, ax = stx.plt.subplots()
    ax.text(
        0.5,
        0.5,
        f"SCITEX_PLT_AXES_WIDTH_MM={env_width or 'not set'}\nResolved: {width}mm",
        ha="center",
        va="center",
        transform=ax.transAxes,
        fontsize=8,
    )
    ax.set_xyt(None, None, "Env Override Demo")
    return fig


def demo_multiple_axes():
    """Multiple axes with default styling."""
    fig, axes = stx.plt.subplots(2, 2)
    for i, ax in enumerate(axes.flat):
        ax.plot(np.random.randn(50).cumsum())
        ax.set_xyt("X", "Y", f"Axes {i+1}")
    return fig


def demo_plot_level_style():
    """Plot-level style override for individual lines.

    Global level: trace_thickness_mm=0.2 (from cascade)
    Plot level: style={"trace_thickness_mm": 0.5} (per-line override)
    """
    fig, ax = stx.plt.subplots()
    x = np.linspace(0, 2 * np.pi, 100)

    # Line 1: uses global default (0.2mm from cascade)
    ax.plot(x, np.sin(x), label="default (0.2mm)")

    # Line 2: plot-level override via style dict
    ax.plot(x, np.cos(x), style={"trace_thickness_mm": 0.5}, label="style override (0.5mm)")

    # Line 3: direct matplotlib override
    from scitex.plt.utils import mm_to_pt
    ax.plot(x, np.sin(x + 1), linewidth=mm_to_pt(0.8), label="direct lw (0.8mm)")

    ax.set_xyt("X", "Y", "Plot-Level Style Control")
    ax.legend()
    return fig


def demo_style_management():
    """Demo style export, import, and change.

    Shows:
        - save_style(): Export style to YAML/JSON
        - load_style(): Import style from file
        - set_style(): Change active style globally
    """
    from scitex.plt.styles import save_style, load_style, set_style, get_style

    # Export current style
    export_path = Path(OUTPUT_DIR) / "exported_style.yaml"
    save_style(export_path)
    print(f"Exported style to: {export_path}")

    # Create figure with default style
    fig, axes = stx.plt.subplots(1, 3, axes_width_mm=30)
    x = np.linspace(0, 2 * np.pi, 100)

    # Access axes via .flat for consistent iteration
    ax_list = list(axes.flat)

    # Plot 1: Default style
    ax_list[0].plot(x, np.sin(x))
    ax_list[0].set_xyt("X", "Y", "Default")

    # Plot 2: Change style globally
    set_style({"trace_thickness_mm": 0.5})
    ax_list[1].plot(x, np.sin(x))
    ax_list[1].set_xyt("X", "Y", "set_style(0.5mm)")

    # Plot 3: Reset to default
    set_style(None)
    ax_list[2].plot(x, np.sin(x))
    ax_list[2].set_xyt("X", "Y", "Reset")

    return fig


def demo_print_config():
    """Print resolved configuration."""
    from scitex.plt.styles import SCITEX_STYLE

    print("\n=== SCITEX_STYLE (cascade: env → yaml → default) ===")
    for key in [
        "axes_width_mm",
        "axes_height_mm",
        "dpi",
        "n_ticks",
        "axis_font_size_pt",
        "tick_font_size_pt",
    ]:
        print(f"  {key}: {SCITEX_STYLE.get(key)}")
    print()


if __name__ == "__main__":
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    demo_print_config()

    demos = [
        ("all_parameters", demo_all_parameters),
        ("default", demo_default),
        ("direct_override", demo_direct_override),
        ("env_override", demo_env_override),
        ("multiple_axes", demo_multiple_axes),
        ("plot_level_style", demo_plot_level_style),
        ("style_management", demo_style_management),
    ]

    for name, func in demos:
        fig = func()
        path = f"{OUTPUT_DIR}/{name}.png"
        fig.savefig(path)
        print(f"Saved: {path}")
        stx.plt.close()

    print(f"\nAll demos saved to {OUTPUT_DIR}/")

# EOF
