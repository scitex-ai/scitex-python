#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-20 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/examples/scitex/io/bundle/pltz.py

"""
Demonstrates FTS plot bundle creation and loading.

FTS bundles (replacing legacy .plot) contain:
- node.json: Bundle metadata
- encoding.json: Data-to-visual mappings
- theme.json: Styling
- data/: Raw data files
- exports/: PNG/SVG/PDF renders
"""

import numpy as np
import pandas as pd

import scitex as stx
import scitex.io as sio
from scitex.dev.plt import plot_mpl_hist, plot_stx_line, plot_stx_scatter


@stx.session
def main(
    CONFIG=stx.session.INJECTED,
    plt=stx.session.INJECTED,
    rngg=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """Demonstrates FTS plot bundle functionality."""
    logger.info("Starting FTS plot bundle demo")
    sdir = CONFIG["SDIR_RUN"]
    rng = rng("plot_demo")

    # 1. Basic plot bundle
    logger.info("Creating basic plot bundle")
    fig, ax = plot_stx_line(plt, rng)
    sio.save(fig, sdir / "line_plot.stx")
    plt.close(fig)
    logger.success("Basic bundle created")

    # 2. Bundle with embedded DataFrame
    logger.info("Creating bundle with DataFrame")
    df = pd.DataFrame(
        {
            "time": np.arange(10),
            "value_a": rng.standard_normal(10),
            "value_b": rng.standard_normal(10) + 1,
        }
    )
    fig, ax = plt.subplots()
    ax.plot(df["time"], df["value_a"], "o-", label="Group A")
    ax.plot(df["time"], df["value_b"], "s-", label="Group B")
    ax.set_xyt("Time", "Value", "Time Series with Data")
    ax.legend()
    sio.save(fig, sdir / "with_data.stx", data=df)
    plt.close(fig)
    logger.success("DataFrame bundle created")

    # 3. Scatter plot bundle
    logger.info("Creating scatter bundle")
    fig, ax = plot_stx_scatter(plt, rng)
    sio.save(fig, sdir / "scatter.stx")
    plt.close(fig)

    # 4. Histogram bundle
    logger.info("Creating histogram bundle")
    fig, ax = plot_mpl_hist(plt, rng)
    sio.save(fig, sdir / "histogram.stx")
    plt.close(fig)

    # 5. Dark mode demo
    logger.info("Creating dark mode bundle")
    fig, ax = plt.subplots(theme="dark")
    x = np.linspace(0, 2 * np.pi, 100)
    ax.plot(x, np.cos(x), linewidth=2, label="cos(x)")
    ax.set_xyt("x", "y", "Dark Mode Demo")
    ax.legend()
    sio.save(fig, sdir / "dark_mode.stx")
    plt.close(fig)

    # 6. Custom axis size (mm-based)
    logger.info("Creating custom size bundle")
    fig, ax = plt.subplots(axes_width_mm=60, axes_height_mm=40)
    ax.plot(x, np.sin(2 * x), linewidth=2)
    ax.set_xyt("x", "y", "Custom Size (60mm x 40mm)")
    sio.save(fig, sdir / "custom_size.stx")
    plt.close(fig)

    # 7. ZIP archive
    logger.info("Creating ZIP archive")
    fig, ax = plt.subplots()
    ax.bar(["A", "B", "C"], [10, 20, 15])
    ax.set_xyt(None, "Count", "Bar Chart")
    sio.save(fig, sdir / "bar_chart.zip", as_zip=True)
    plt.close(fig)
    logger.success("ZIP bundle created")

    logger.success("Demo completed")
    return 0


if __name__ == "__main__":
    main()

# EOF
