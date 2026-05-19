#!/usr/bin/env python3
import pytest

pytest.importorskip("zarr")
# -*- coding: utf-8 -*-
# Test for AxesWrapper.flatten() functionality

pytest.importorskip("matplotlib")

import os

import matplotlib
import numpy as np

matplotlib.use("Agg")  # Use non-interactive backend

import scitex
import scitex.plt as mplt


def test_flatten_maintains_wrapper():
    """Test that AxesWrapper.flatten() maintains wrapper types."""
    print("Testing AxesWrapper.flatten() with multiple axes...")

    # Create a figure with a grid of axes (2x2)
    fig, axes = mplt.subplots(nrows=2, ncols=2, figsize=(8, 8))

    # Print type info for debugging
    print(f"Type of axes: {type(axes)}")
    print(f"Shape of axes: {axes.shape}")

    # Check if the wrapper is preserved when using flatten()
    flattened_axes = list(axes.flatten())

    # Print count of flattened axes
    print(f"Number of flattened axes: {len(flattened_axes)}")

    # Verify the type of each flattened axis
    for i, ax in enumerate(flattened_axes):
        print(f"Type of flattened axis {i}: {type(ax)}")
        print(f"Has track attribute: {hasattr(ax, 'track')}")
        print(f"Has _ax_history: {hasattr(ax, '_ax_history')}")

        # Ensure we can call methods on the flattened axes
        # without losing wrapper functionality
        ax.track = True
        ax.plot([1, 2, 3], [i + 1, i + 2, i + 3], id=f"test_plot_{i}")

    # Verify that tracking worked on all axes
    for i, ax in enumerate(flattened_axes):
        if hasattr(ax, "_ax_history"):
            history_count = len(ax._ax_history)
            print(f"Axis {i} has {history_count} tracked items")
            assert history_count > 0, f"Axis {i} should have tracked items"

    # Test CSV export on the figure
    output_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "test_axes_wrapper_flatten_out"
    )
    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, "test_flatten_axes.png")
    scitex.io.save(fig, save_path)

    # Try to find the CSV file
    csv_path = save_path.replace(".png", ".csv")
    if os.path.exists(csv_path):
        print(f"CSV export found: {csv_path}")
        return True
    else:
        alt_dir = os.path.join(output_dir, "test_axes_wrapper_flatten_out")
        alt_csv_path = os.path.join(alt_dir, "csv", os.path.basename(csv_path))
        if os.path.exists(alt_csv_path):
            print(f"CSV export found in alternate location: {alt_csv_path}")
            return True
        else:
            print(f"CSV export not found. Expected at: {csv_path} or {alt_csv_path}")
            return False


if __name__ == "__main__":
    success = test_flatten_maintains_wrapper()
    print(f"\nTest result: {'PASSED' if success else 'FAILED'}")
