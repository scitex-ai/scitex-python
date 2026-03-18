#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-05"
# File: ./examples/session_decorator_demo/scripts/session_decorator_demo.py
# ----------------------------------------
"""
Session Decorator Demo - Simplified SciTeX Session Management

Functionalities:
  - Demonstrates @session decorator for simplified session management
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
    - ./session_decorator_demo_out/sample_data.npy
    - ./session_decorator_demo_out/visualization.jpg
    - ./session_decorator_demo_out/results.json

This demo shows the same functionality as scitex_session_demo.py
but with 80% less boilerplate code using the @session decorator.
"""

import numpy as np

import scitex as stx
from scitex import logging
from scitex.session import session

logger = logging.getLogger(__name__)


# ============================================================================
# Helper Functions
# ============================================================================


def generate_sample_data(n_samples=100):
    """Generate synthetic data for demonstration.

    Args:
        n_samples: Number of samples to generate

    Returns:
        x, y: Generated data arrays
    """
    logger.info(f"Generating {n_samples} samples")

    x = np.random.uniform(0, 10, n_samples)
    noise = np.random.normal(0, 0.5, n_samples)
    y = 2 * x + 3 + noise

    return x, y


def visualize_data(x, y):
    """Create visualization of the data.

    Args:
        x: X values
        y: Y values

    Returns:
        coeffs: Regression coefficients
    """
    logger.info("Creating visualization")

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot_scatter(x, y, alpha=0.6, label="Data points")

    # Add regression line
    coeffs = np.polyfit(x, y, 1)
    line_x = np.linspace(x.min(), x.max(), 100)
    line_y = coeffs[0] * line_x + coeffs[1]
    ax.stx_line(line_x, line_y, "r--", label=f"y = {coeffs[0]:.2f}x + {coeffs[1]:.2f}")

    ax.set_xyt("X", "Y", "Session Decorator Demo: Sample Data Visualization")
    ax.legend()
    ax.grid(True, alpha=0.3)

    stx.io.save(fig, "./visualization.jpg")
    logger.success("Visualization saved")

    return coeffs


def compute_statistics(x, y):
    """Compute basic statistics.

    Args:
        x: X values
        y: Y values

    Returns:
        stats: Dictionary of statistics
    """
    logger.info("Computing statistics")

    stats = {
        "x_mean": float(np.mean(x)),
        "x_std": float(np.std(x)),
        "y_mean": float(np.mean(y)),
        "y_std": float(np.std(y)),
        "correlation": float(np.corrcoef(x, y)[0, 1]),
        "n_samples": len(x),
    }

    return stats


# ============================================================================
# Main Function with @session Decorator
# ============================================================================


@session(verbose=True, agg=True)
def main(n_samples: int = 100, verbose: bool = False):
    """Main execution function with @session decorator.

    This demonstrates the simplified session management approach.
    No need for parse_args(), run_main(), or manual session.start()/close()!

    Args:
        n_samples: Number of samples to generate (default: 100)
        verbose: Enable verbose output (default: False)
    """

    # Session is automatically started - CONFIG, plt, CC, rng are available
    logger.info("=" * 60)
    logger.info("Session Decorator Demo Started")
    logger.info("=" * 60)
    logger.info(f"Session ID: {CONFIG['ID']}")
    logger.info(f"Output Directory: {CONFIG['SDIR']}")
    logger.info("=" * 60)

    # Generate data
    logger.info("Step 1: Generating data")
    x, y = generate_sample_data(n_samples)

    # Save raw data
    logger.info("Step 2: Saving raw data")
    stx.io.save(np.column_stack([x, y]), "./sample_data.npy")
    logger.success("Raw data saved")

    # Visualize
    logger.info("Step 3: Creating visualization")
    coeffs = visualize_data(x, y)

    # Compute statistics
    logger.info("Step 4: Computing statistics")
    stats = compute_statistics(x, y)
    stats["regression_slope"] = float(coeffs[0])
    stats["regression_intercept"] = float(coeffs[1])

    # Save results
    logger.info("Step 5: Saving results")
    stx.io.save(stats, "./results.json")
    logger.success("Results saved")

    # Print summary
    logger.info("=" * 60)
    logger.info("Analysis Complete - Summary:")
    logger.info(f"  Samples: {stats['n_samples']}")
    logger.info(f"  X mean: {stats['x_mean']:.3f} ± {stats['x_std']:.3f}")
    logger.info(f"  Y mean: {stats['y_mean']:.3f} ± {stats['y_std']:.3f}")
    logger.info(f"  Correlation: {stats['correlation']:.3f}")
    logger.info(
        f"  Regression: y = {stats['regression_slope']:.2f}x + {stats['regression_intercept']:.2f}"
    )
    logger.info("=" * 60)

    # Session will automatically close and move to FINISHED_SUCCESS/
    return 0


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    # That's it! The decorator handles everything:
    # - Argument parsing from function signature
    # - Session initialization
    # - Execution
    # - Cleanup and error handling
    main()

# EOF
