#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-21 03:12:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/examples/scitex/io/bundle/05_panel_labels.py

"""
Example 05: Encoding - Data to Visual Mapping

Demonstrates:
- Setting encoding (data column to visual property mapping)
- Defining traces with x, y, color mappings
- Working with axes configuration
"""

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


def create_sample_data(rng):
    """Generate sample time series data."""
    return pd.DataFrame({
        "time": np.arange(100),
        "signal_A": np.sin(np.linspace(0, 4 * np.pi, 100)) + rng.normal(0, 0.1, 100),
        "signal_B": np.cos(np.linspace(0, 4 * np.pi, 100)) + rng.normal(0, 0.1, 100),
        "category": ["A"] * 50 + ["B"] * 50,
    })


def create_encoding():
    """Create encoding specification for time series plot."""
    return {
        "traces": [
            {
                "trace_id": "Signal A",
                "x": {"column": "time", "type": "quantitative"},
                "y": {"column": "signal_A", "type": "quantitative"},
                "color": {"value": "#1f77b4"},
            },
            {
                "trace_id": "Signal B",
                "x": {"column": "time", "type": "quantitative"},
                "y": {"column": "signal_B", "type": "quantitative"},
                "color": {"value": "#ff7f0e"},
            },
        ],
        "axes": {
            "x": {
                "title": "Time",
                "type": "quantitative",
                "domain": [0, 100],
            },
            "y": {
                "title": "Amplitude",
                "type": "quantitative",
                "domain": [-1.5, 1.5],
            },
        },
    }


def create_plot(plt, df, out_dir):
    """Create and save plot as FTS bundle."""
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(df["time"], df["signal_A"], label="Signal A")
    ax.plot(df["time"], df["signal_B"], label="Signal B")
    ax.set_xlabel("Time")
    ax.set_ylabel("Amplitude")
    ax.set_title("Time Series Comparison")
    ax.legend()

    sio.save(fig, out_dir / "encoded_plot.zip", data=df)
    plt.close(fig)


def configure_encoding(out_dir, logger):
    """Load bundle and set encoding specification."""
    bundle = FTS(out_dir / "encoded_plot.zip")
    bundle.encoding = create_encoding()
    bundle.save()

    logger.info("Encoding set:")
    logger.info(f"  Traces: {len(bundle.encoding.traces)}")
    for trace in bundle.encoding.traces:
        logger.info(f"    - {trace.trace_id}: x={trace.x}, y={trace.y}")

    return bundle


def verify_encoding(out_dir, logger):
    """Reload and verify encoding."""
    reloaded = FTS(out_dir / "encoded_plot.zip")
    logger.info(f"\nReloaded encoding: {reloaded.encoding_dict}")


@stx.session(verbose=False, agg=True)
def main(plt=INJECTED, CONFIG=INJECTED, logger=INJECTED):
    """Demonstrate encoding specification."""
    logger.info("Example 05: Encoding - Data to Visual Mapping")

    out_dir = CONFIG["SDIR_OUT"]

    cleanup_existing(out_dir, "encoded_plot.zip")

    rng = np.random.default_rng(42)
    df = create_sample_data(rng)

    create_plot(plt, df, out_dir)
    configure_encoding(out_dir, logger)
    verify_encoding(out_dir, logger)

    logger.success("Example 05 completed!")


if __name__ == "__main__":
    main()

# EOF
