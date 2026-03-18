#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-10 (ywatanabe)"
# File: ./scitex_session_demo/scripts/scitex_session_demo_decorator.py
# ----------------------------------------
from __future__ import annotations

import os

__FILE__ = "./scitex_session_demo/scripts/scitex_session_demo_decorator.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Demonstrates scitex session decorator (@stx.session)
  - Shows automatic CLI generation from function signature
  - Demonstrates session-managed execution
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
    - ./scitex_session_demo_decorator.py_out/sample_data.npy
    - ./scitex_session_demo_decorator.py_out/visualization.jpg
    - ./scitex_session_demo_decorator.py_out/results.json

Key Differences from Manual Session Management:
  - No need for run_main() wrapper function
  - No need for parse_args() function (auto-generated from signature)
  - No need to manually call stx.session.start() or stx.session.close()
  - Session variables (CONFIG, plt, CC, rng) auto-injected as globals
  - CLI automatically generated from function parameters
  - Cleaner, more concise code
"""

"""Imports"""
import numpy as np

import scitex as stx
from scitex.logging import getLogger
from scitex.session import session

logger = getLogger(__name__)

"""Functions & Classes"""


def generate_sample_data(n_samples=100):
    """Generate synthetic data for demonstration."""

    # Use session-managed random number generator for reproducibility
    x = rng("data").uniform(0, 10, n_samples)
    noise = rng("noise").normal(0, 0.5, n_samples)
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

    ax.set_xyt("X", "Y", "SciTeX Demo (Decorator): Sample Data Visualization")

    ax.legend()
    ax.grid(True, alpha=0.3)

    stx.io.save(fig, "./visualization.jpg")

    return coeffs


def compute_statistics(x, y):
    """Compute basic statistics."""

    stats = {
        "x_mean": float(np.mean(x)),
        "x_std": float(np.std(x)),
        "y_mean": float(np.mean(y)),
        "y_std": float(np.std(y)),
        "correlation": float(np.corrcoef(x, y)[0, 1]),
        "n_samples": len(x),
    }

    return stats


@session(verbose=False, agg=True)
def demo(n_samples: int = 100, show_config: bool = False):
    """
    SciTeX session decorator demonstration.

    This function demonstrates the @stx.session decorator which:
    - Automatically generates CLI from function signature
    - Manages session lifecycle (start/close)
    - Injects session variables (CONFIG, plt, CC, rng)
    - Handles errors and cleanup

    Args:
        n_samples: Number of samples to generate
        show_config: Show session configuration details
    """

    # Session variables are automatically available as globals:
    # - CONFIG: Session configuration dict
    # - plt: matplotlib.pyplot (configured)
    # - CC: Custom Colors
    # - rng: Random state manager

    logger.info("Starting SciTeX session decorator demo")

    if show_config:
        logger.info(f"Session ID: {CONFIG['ID']}")
        logger.info(f"Output directory: {CONFIG['SDIR']}")
        logger.info(f"Script: {CONFIG['SCRIPT']}")

    # Generate data
    logger.info(f"Generating {n_samples} samples")
    x, y = generate_sample_data(n_samples)

    # Save raw data
    stx.io.save(np.column_stack([x, y]), "./sample_data.npy")
    logger.info("Saved sample data")

    # Visualize
    logger.info("Creating visualization")
    coeffs = visualize_data(x, y)

    # Compute statistics
    logger.info("Computing statistics")
    stats = compute_statistics(x, y)
    stats["regression_slope"] = float(coeffs[0])
    stats["regression_intercept"] = float(coeffs[1])

    # Save results
    stx.io.save(stats, "./results.json")
    logger.success("Demo completed successfully")

    return 0


if __name__ == "__main__":
    # No arguments = CLI mode with session management
    # The decorator automatically:
    # 1. Parses CLI arguments based on function signature
    # 2. Starts session
    # 3. Injects CONFIG, plt, CC, rng as globals
    # 4. Runs function
    # 5. Closes session
    demo()

# CLI Usage:
# python scitex_session_demo_decorator.py --n-samples 100
# python scitex_session_demo_decorator.py --n-samples 200 --show-config
# python scitex_session_demo_decorator.py --help

# EOF
