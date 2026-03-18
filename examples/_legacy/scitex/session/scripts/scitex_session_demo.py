#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-16 03:12:19 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/scitex_session_demo/scripts/scitex_session_demo.py
# ----------------------------------------
from __future__ import annotations

import os

__FILE__ = "./scitex_session_demo/scripts/scitex_session_demo.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Demonstrates basic scitex framework features
  - Generates sample data (synthetic dataset)
  - Performs simple visualization
  - Shows logging capabilities
  - Demonstrates configuration management
  - Saves results to organized output directory

Dependencies:
  - packages:
    - scitex
    - numpy
    - matplotlib

IO:
  - input-files:
    - None (generates synthetic data)

  - output-files:
    - ./demo.py_out/sample_data.npy
    - ./demo.py_out/visualization.png
    - ./demo.py_out/results.json
"""

"""Imports"""
import argparse

import numpy as np

import scitex as stx
from scitex import logging

logger = logging.getLogger(__name__)

"""Parameters"""
# CONFIG = stx.io.load_configs()


"""Functions & Classes"""


def generate_sample_data(n_samples=100):
    """Generate synthetic data for demonstration."""

    x = np.random.uniform(0, 10, n_samples)
    noise = np.random.normal(0, 0.5, n_samples)
    y = 2 * x + 3 + noise

    return x, y


def visualize_data(x, y):
    """Create visualization of the data."""

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot_scatter(x, y, alpha=0.6, label="Data points")

    # Add regression line
    coeffs = np.polyfit(x, y, 1)
    line_x = np.linspace(x.min(), x.max(), 100)
    line_y = coeffs[0] * line_x + coeffs[1]
    ax.stx_line(line_x, line_y, "r--", label=f"y = {coeffs[0]:.2f}x + {coeffs[1]:.2f}")

    ax.set_xyt("X", "Y", "SciTeX Demo: Sample Data Visualization")

    ax.legend()
    ax.grid(True, alpha=0.3)

    stx.io.save(fig, "./visualization.jpg")

    return coeffs


def compute_statistics(x, y):
    """Compute basic statistics."""
    import numpy as np

    stats = {
        "x_mean": float(np.mean(x)),
        "x_std": float(np.std(x)),
        "y_mean": float(np.mean(y)),
        "y_std": float(np.std(y)),
        "correlation": float(np.corrcoef(x, y)[0, 1]),
        "n_samples": len(x),
    }

    return stats


def main(args):
    """Main execution function."""

    # Generate data
    x, y = generate_sample_data(args.n_samples)

    # Save raw data
    stx.io.save(np.column_stack([x, y]), "./sample_data.npy")

    # Visualize
    coeffs = visualize_data(x, y)

    # Compute statistics
    stats = compute_statistics(x, y)
    stats["regression_slope"] = float(coeffs[0])
    stats["regression_intercept"] = float(coeffs[1])

    # Save results
    stx.io.save(stats, "./results.json")

    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    import scitex as stx

    parser = argparse.ArgumentParser(description="SciTeX Framework Demo Script")
    parser.add_argument(
        "--n-samples",
        "-n",
        type=int,
        default=100,
        help="Number of samples to generate (default: %(default)s)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        default=False,
        help="Enable verbose output (default: %(default)s)",
    )
    args = parser.parse_args()
    return args


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt, rng

    import sys

    import matplotlib.pyplot as plt

    import scitex as stx

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        sdir_suffix=None,
        verbose=args.verbose,
        agg=True,
    )

    exit_status = main(args)

    stx.session.close(
        CONFIG,
        verbose=args.verbose,
        notify=False,
        message="Demo completed",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

# EOF
