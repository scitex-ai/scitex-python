#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-21 03:12:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/examples/scitex/io/bundle/11_theme_inheritance.py

"""
Example 11: Theme Configuration

Demonstrates:
- Setting theme properties (mode, colors, fonts)
- Theme structure and customization
- Dark/light mode switching
"""

import shutil

import numpy as np

import scitex as stx
import scitex.io as sio
from scitex import INJECTED
from scitex.io.bundle import FTS


def cleanup_existing(out_dir, names):
    """Remove existing bundles."""
    for name in names:
        path = out_dir / name
        if path.exists():
            shutil.rmtree(path) if path.is_dir() else path.unlink()


def create_light_theme():
    """Create light mode theme configuration."""
    return {
        "mode": "light",
        "colors": {
            "primary": "#1f77b4",
            "secondary": "#ff7f0e",
            "background": "#ffffff",
            "text": "#333333",
            "axis": "#666666",
            "grid": "#e0e0e0",
        },
        "fonts": {
            "family": "sans-serif",
            "title_size": 14,
            "label_size": 12,
            "tick_size": 10,
        },
        "figure_title": {
            "text": "Light Theme Demo",
            "prefix": "Figure",
            "number": 1,
        },
    }


def create_dark_theme():
    """Create dark mode theme configuration."""
    return {
        "mode": "dark",
        "colors": {
            "primary": "#00ff88",
            "secondary": "#ff6b6b",
            "background": "#1a1a1a",
            "text": "#e8e8e8",
            "axis": "#888888",
            "grid": "#333333",
        },
        "fonts": {
            "family": "sans-serif",
            "title_size": 14,
            "label_size": 12,
            "tick_size": 10,
        },
        "figure_title": {
            "text": "Dark Theme Demo",
            "prefix": "Figure",
            "number": 2,
        },
    }


def create_light_bundle(plt, out_dir, logger):
    """Create bundle with light theme."""
    logger.info("\n" + "=" * 60)
    logger.info("LIGHT MODE THEME")
    logger.info("=" * 60)

    x = np.linspace(0, 10, 50)
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.plot(x, np.sin(x), linewidth=1.5, label="sin(x)")
    ax.plot(x, np.cos(x), linewidth=1.5, label="cos(x)")
    ax.legend()
    ax.set_title("Light Mode")

    light_path = out_dir / "theme_light.zip"
    sio.save(fig, light_path)
    plt.close(fig)

    bundle = FTS(light_path)
    bundle.theme = create_light_theme()
    bundle.save()

    logger.info("Light theme configured:")
    logger.info(f"  mode: {bundle.theme.mode}")
    logger.info(f"  colors: {bundle.theme.colors}")
    logger.info(f"  fonts: {bundle.theme.fonts}")

    return light_path


def create_dark_bundle(plt, out_dir, logger):
    """Create bundle with dark theme."""
    logger.info("\n" + "=" * 60)
    logger.info("DARK MODE THEME")
    logger.info("=" * 60)

    x = np.linspace(0, 10, 50)
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.plot(x, np.sin(x), linewidth=1.5, color="#00ff88", label="sin(x)")
    ax.plot(x, np.cos(x), linewidth=1.5, color="#ff6b6b", label="cos(x)")
    ax.legend()
    ax.set_title("Dark Mode")

    dark_path = out_dir / "theme_dark.zip"
    sio.save(fig, dark_path)
    plt.close(fig)

    bundle = FTS(dark_path)
    bundle.theme = create_dark_theme()
    bundle.save()

    logger.info("Dark theme configured:")
    logger.info(f"  mode: {bundle.theme.mode}")
    logger.info(f"  colors: {bundle.theme.colors}")


def demonstrate_theme_switching(light_path, logger):
    """Demonstrate switching theme mode."""
    logger.info("\n" + "=" * 60)
    logger.info("THEME SWITCHING DEMO")
    logger.info("=" * 60)

    bundle = FTS(light_path)
    original_mode = bundle.theme.mode
    logger.info(f"Original mode: {original_mode}")

    # Switch mode while keeping other settings
    bundle.theme = {
        "mode": "dark",
        "colors": bundle.theme.colors,
        "fonts": bundle.theme.fonts,
    }
    bundle.save()
    logger.info(f"Switched to: {bundle.theme.mode}")

    # Verify persistence
    reloaded = FTS(light_path)
    logger.info(f"Verified mode: {reloaded.theme.mode}")


def print_summary(logger):
    """Print theme structure summary."""
    logger.info("\n" + "=" * 60)
    logger.info("Theme Structure Summary:")
    logger.info("  mode: 'light' | 'dark'")
    logger.info("  colors: {primary, secondary, background, text, axis, grid}")
    logger.info("  fonts: {family, title_size, label_size, tick_size}")
    logger.info("  figure_title: {text, prefix, number}")
    logger.info("  caption: {text, panels: [{label, description}]}")
    logger.info("  panel_labels: {style, fontsize, fontweight, position}")
    logger.info("=" * 60)


@stx.session(verbose=False, agg=True)
def main(plt=INJECTED, CONFIG=INJECTED, logger=INJECTED):
    """Demonstrate theme configuration."""
    logger.info("Example 11: Theme Configuration Demo")

    out_dir = CONFIG["SDIR_OUT"]
    np.random.seed(42)

    cleanup_existing(out_dir, ["theme_light.zip", "theme_dark.zip"])

    light_path = create_light_bundle(plt, out_dir, logger)
    create_dark_bundle(plt, out_dir, logger)
    demonstrate_theme_switching(light_path, logger)
    print_summary(logger)

    logger.success("Example 11 completed!")


if __name__ == "__main__":
    main()

# EOF
