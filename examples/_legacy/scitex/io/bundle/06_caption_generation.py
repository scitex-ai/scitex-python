#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-21 03:12:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/examples/scitex/io/bundle/06_caption_generation.py

"""
Example 06: Theme - Visual Styling and Captions

Demonstrates:
- Setting theme properties (colors, fonts)
- Figure title and caption in theme
- Panel labels configuration
"""

import shutil

import numpy as np

import scitex as stx
import scitex.io as sio
from scitex import INJECTED
from scitex.io.bundle import FTS


def cleanup_existing(out_dir, name):
    """Remove existing bundle."""
    path = out_dir / name
    if path.exists():
        shutil.rmtree(path) if path.is_dir() else path.unlink()


def create_theme():
    """Create theme with figure title and caption."""
    return {
        "mode": "light",
        "figure_title": {
            "text": "Experimental Results",
            "prefix": "Figure",
            "number": 1,
        },
        "caption": {
            "text": "Comparison of sine and cosine functions over one period.",
            "panels": [
                {"label": "A", "description": "Sine function showing periodic oscillation"},
                {"label": "B", "description": "Cosine function phase-shifted by π/2"},
            ],
        },
        "colors": {
            "primary": "#1f77b4",
            "secondary": "#ff7f0e",
            "background": "white",
            "text": "black",
        },
        "fonts": {
            "family": "sans-serif",
            "title_size": 14,
            "label_size": 12,
            "tick_size": 10,
        },
        "panel_labels": {
            "style": "uppercase",
            "fontsize": 12,
            "fontweight": "bold",
            "position": "top-left",
        },
    }


def create_plot(plt, out_dir):
    """Create and save plot as FTS bundle."""
    x = np.linspace(0, 10, 100)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(x, np.sin(x), label="sin(x)")
    ax.plot(x, np.cos(x), label="cos(x)")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("Trigonometric Functions")
    ax.legend()

    sio.save(fig, out_dir / "themed_plot.zip")
    plt.close(fig)


def configure_theme(out_dir, logger):
    """Load bundle and configure theme."""
    bundle = FTS(out_dir / "themed_plot.zip")
    bundle.theme = create_theme()
    bundle.save()

    logger.info("Theme set:")
    logger.info(f"  Mode: {bundle.theme.mode}")
    logger.info(f"  Figure title: {bundle.theme.figure_title}")
    logger.info(f"  Caption: {bundle.theme.caption}")
    logger.info(f"  Colors: {bundle.theme.colors}")
    logger.info(f"  Fonts: {bundle.theme.fonts}")
    logger.info(f"  Panel labels: {bundle.theme.panel_labels}")

    return bundle


def generate_caption(bundle, logger):
    """Generate full caption text from theme."""
    caption_parts = []
    if bundle.theme.figure_title:
        ft = bundle.theme.figure_title
        prefix = ft.prefix if hasattr(ft, "prefix") else "Figure"
        number = ft.number if hasattr(ft, "number") and ft.number else 1
        text = ft.text if hasattr(ft, "text") else ""
        caption_parts.append(f"{prefix} {number}. {text}")

    if bundle.theme.caption:
        cap = bundle.theme.caption
        if hasattr(cap, "text") and cap.text:
            caption_parts.append(cap.text)
        if hasattr(cap, "panels"):
            for panel in cap.panels:
                caption_parts.append(f"({panel.label}) {panel.description}.")

    full_caption = " ".join(caption_parts)
    logger.info(f"\nGenerated caption:\n{full_caption}")


def verify_theme(out_dir, logger):
    """Reload and verify theme."""
    reloaded = FTS(out_dir / "themed_plot.zip")
    logger.info(f"\nReloaded theme mode: {reloaded.theme.mode}")
    logger.info(f"Reloaded theme dict: {reloaded.theme_dict}")


@stx.session(verbose=False, agg=True)
def main(plt=INJECTED, CONFIG=INJECTED, logger=INJECTED):
    """Demonstrate theme specification with captions."""
    logger.info("Example 06: Theme - Visual Styling and Captions")

    out_dir = CONFIG["SDIR_OUT"]

    cleanup_existing(out_dir, "themed_plot.zip")

    create_plot(plt, out_dir)
    bundle = configure_theme(out_dir, logger)
    generate_caption(bundle, logger)
    verify_theme(out_dir, logger)

    logger.success("Example 06 completed!")


if __name__ == "__main__":
    main()

# EOF
