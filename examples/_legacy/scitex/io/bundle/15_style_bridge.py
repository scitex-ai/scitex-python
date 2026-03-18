#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-21 03:12:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/examples/scitex/io/bundle/16_style_bridge.py

"""
Example 16: Encoding and Theme Separation

Demonstrates:
- encoding.json: Data-to-visual mappings
- theme.json: Visual aesthetics
- Clear separation of concerns
"""

import json
import shutil

import numpy as np
import pandas as pd

import scitex as stx
import scitex.io as sio
from scitex import INJECTED
from scitex.io.bundle import FTS


def cleanup_existing(out_dir, name):
    """Remove existing bundle."""
    path = out_dir / name
    if path.exists():
        shutil.rmtree(path) if path.is_dir() else path.unlink()


def create_sample_data():
    """Create sample signal data."""
    np.random.seed(42)
    return pd.DataFrame(
        {
            "time": np.arange(50),
            "signal": np.sin(np.linspace(0, 4 * np.pi, 50))
            + np.random.normal(0, 0.1, 50),
            "noise": np.random.normal(0, 0.3, 50),
        }
    )


def create_plot(plt, df, out_dir):
    """Create and save plot as FTS bundle."""
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.plot(df["time"], df["signal"], label="Signal", linewidth=1.5)
    ax.plot(df["time"], df["noise"], label="Noise", linewidth=1, alpha=0.7)
    ax.legend()
    ax.set_xlabel("Time")
    ax.set_ylabel("Amplitude")
    ax.set_title("Signal vs Noise")

    bundle_path = out_dir / "encoding_theme_demo.zip"
    sio.save(fig, bundle_path, data=df)
    plt.close(fig)

    return bundle_path


def create_encoding():
    """Create encoding specification."""
    return {
        "traces": [
            {
                "trace_id": "Signal",
                "x": {"column": "time", "type": "quantitative"},
                "y": {"column": "signal", "type": "quantitative"},
                "color": {"value": "#1f77b4"},
            },
            {
                "trace_id": "Noise",
                "x": {"column": "time", "type": "quantitative"},
                "y": {"column": "noise", "type": "quantitative"},
                "color": {"value": "#ff7f0e"},
            },
        ],
        "axes": {
            "x": {"title": "Time (s)", "domain": [0, 50]},
            "y": {"title": "Amplitude (mV)", "domain": [-1.5, 1.5]},
        },
    }


def create_theme():
    """Create theme specification."""
    return {
        "mode": "light",
        "colors": {
            "background": "#ffffff",
            "text": "#333333",
            "grid": "#e0e0e0",
        },
        "fonts": {
            "family": "sans-serif",
            "title_size": 12,
            "label_size": 10,
            "tick_size": 8,
        },
        "figure_title": {
            "text": "Signal Analysis",
            "prefix": "Figure",
            "number": 1,
        },
    }


def configure_bundle(bundle_path, logger):
    """Configure bundle with encoding and theme."""
    bundle = FTS(bundle_path)

    logger.info("\n" + "=" * 60)
    logger.info("ENCODING (data-to-visual mapping)")
    logger.info("=" * 60)

    bundle.encoding = create_encoding()

    logger.info("Encoding defines:")
    logger.info("  - Which columns map to x, y")
    logger.info("  - Trace colors and labels")
    logger.info("  - Axis titles and domains")

    logger.info("\n" + "=" * 60)
    logger.info("THEME (visual aesthetics)")
    logger.info("=" * 60)

    bundle.theme = create_theme()

    logger.info("Theme defines:")
    logger.info("  - Color scheme (light/dark mode)")
    logger.info("  - Font family and sizes")
    logger.info("  - Figure title and numbering")

    bundle.save()

    return bundle


def show_file_contents(bundle_path, logger):
    """Show encoding and theme file contents."""
    logger.info("\n" + "=" * 60)
    logger.info("FILE CONTENTS")
    logger.info("=" * 60)

    encoding_path = bundle_path / "encoding.json"
    if encoding_path.exists():
        with open(encoding_path) as f:
            enc = json.load(f)
        logger.info("\nencoding.json:")
        logger.info(f"  traces: {len(enc.get('traces', []))}")
        for t in enc.get("traces", []):
            logger.info(
                f"    - {t.get('trace_id')}: {t.get('y', {}).get('column')} -> y"
            )

    theme_path = bundle_path / "theme.json"
    if theme_path.exists():
        with open(theme_path) as f:
            thm = json.load(f)
        logger.info("\ntheme.json:")
        logger.info(f"  mode: {thm.get('mode')}")
        logger.info(f"  fonts: {thm.get('fonts', {}).get('family')}")
        logger.info(f"  figure_title: {thm.get('figure_title', {}).get('text')}")


def print_summary(logger):
    """Print separation of concerns summary."""
    logger.info("\n" + "=" * 60)
    logger.info("SEPARATION OF CONCERNS")
    logger.info("=" * 60)

    logger.info("\nencoding.json answers: WHAT to visualize")
    logger.info("  - Data column bindings")
    logger.info("  - Trace definitions")
    logger.info("  - Axis mappings")

    logger.info("\ntheme.json answers: HOW to visualize")
    logger.info("  - Colors and fonts")
    logger.info("  - Titles and captions")
    logger.info("  - Visual style")

    logger.info("\nBenefits:")
    logger.info("  - Change style without touching data bindings")
    logger.info("  - Swap data while keeping visualization spec")
    logger.info("  - Clear, maintainable bundle structure")
    logger.info("=" * 60)


@stx.session(verbose=False, agg=True)
def main(plt=INJECTED, CONFIG=INJECTED, logger=INJECTED):
    """Demonstrate encoding/theme separation."""
    logger.info("Example 16: Encoding and Theme Separation")

    out_dir = CONFIG["SDIR_OUT"]

    cleanup_existing(out_dir, "encoding_theme_demo.zip")

    df = create_sample_data()
    bundle_path = create_plot(plt, df, out_dir)
    configure_bundle(bundle_path, logger)
    show_file_contents(bundle_path, logger)
    print_summary(logger)

    logger.success("Example 16 completed!")


if __name__ == "__main__":
    main()

# EOF
