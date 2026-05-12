#!/usr/bin/env python3
import pytest

pytest.importorskip("zarr")
# -*- coding: utf-8 -*-
# Test different flatten approaches for AxesWrapper

pytest.importorskip("matplotlib")

import os

import matplotlib
import numpy as np

matplotlib.use("Agg")  # Use non-interactive backend

import scitex
import scitex.plt as mplt


def test_flatten_alternatives():
    """Test different approaches to flatten AxesWrapper."""
    print("\nTesting flatten approaches for AxesWrapper...")

    # Create a figure with multiple axes
    fig, axes = mplt.subplots(nrows=2, ncols=2, figsize=(8, 8))

    print(f"Type of axes: {type(axes)}")
    print(f"Shape of axes: {axes.shape}")

    # Approach 1: Direct iteration with axes.flatten()
    print("\nApproach 1: Direct iteration")
    try:
        for i, ax in enumerate(axes.flatten()):
            print(f"  Axis {i} type: {type(ax)}")
            ax.set_title(f"Axis {i}")
        approach1_success = True
    except Exception as e:
        print(f"  Error: {e}")
        approach1_success = False

    # Approach 2: Convert flatten result to list
    print("\nApproach 2: Convert to list")
    try:
        flat_axes = list(axes.flatten())
        for i, ax in enumerate(flat_axes):
            print(f"  Axis {i} type: {type(ax)}")
            ax.set_title(f"Axis {i} (list)")
        approach2_success = True
    except Exception as e:
        print(f"  Error: {e}")
        approach2_success = False

    # Approach 3: Try to use numpy.array().flatten()
    print("\nApproach 3: numpy.array().flatten()")
    try:
        flat_np = np.array(axes).flatten()
        for i, ax in enumerate(flat_np):
            print(f"  Axis {i} type: {type(ax)}")
            ax.set_title(f"Axis {i} (numpy)")
        approach3_success = True
    except Exception as e:
        print(f"  Error: {e}")
        approach3_success = False

    # Create a single test plot to confirm plotting works on flattened axes
    if approach2_success:
        print("\nPlotting on flattened axes...")
        for i, ax in enumerate(flat_axes):
            ax.plot([1, 2, 3], [i + 1, i + 2, i + 3], id=f"test_plot_{i}")

    # Save the figure to confirm everything worked
    output_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "test_flatten_alternative_out"
    )
    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, "test_flatten_alternative.png")
    scitex.io.save(fig, save_path)

    return {
        "Direct iteration": approach1_success,
        "Convert to list": approach2_success,
        "numpy.array().flatten()": approach3_success,
    }


if __name__ == "__main__":
    results = test_flatten_alternatives()

    print("\nTest Results:")
    for approach, success in results.items():
        print(f"{approach}: {'PASSED' if success else 'FAILED'}")

    print(
        f"\nRecommended approach: {'Convert to list' if results['Convert to list'] else None}"
    )
    print("Example: axes = list(axes.flatten())")
