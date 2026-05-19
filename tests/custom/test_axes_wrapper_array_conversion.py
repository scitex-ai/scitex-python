#!/usr/bin/env python3
import pytest

pytest.importorskip("zarr")
# -*- coding: utf-8 -*-
# Test for AxesWrapper numpy array conversion

pytest.importorskip("matplotlib")

import os

import matplotlib
import numpy as np

matplotlib.use("Agg")  # Use non-interactive backend

import scitex
import scitex.plt as mplt


def test_axes_wrapper_array_conversion():
    """Test that AxesWrapper can be converted to a numpy array."""
    print("\nTesting AxesWrapper to numpy array conversion...")

    # Create a figure with multiple axes
    fig, axes = mplt.subplots(nrows=2, ncols=2, figsize=(8, 8))

    # Print information about the axes
    print(f"Type of axes: {type(axes)}")
    print(f"Shape of axes: {axes.shape}")

    # Convert to numpy array
    try:
        ax_array = np.array(axes)
        print(f"Converted to array with shape: {ax_array.shape}")
        print(f"Type of array element: {type(ax_array[0, 0])}")
        conversion_success = True
    except Exception as e:
        print(f"Error converting to array: {e}")
        conversion_success = False

    # Try flattening the array
    try:
        flat_axes = np.array(axes).flatten()
        print(f"Flattened array length: {len(flat_axes)}")
        print(f"Type of flattened element: {type(flat_axes[0])}")
        flatten_success = True
    except Exception as e:
        print(f"Error flattening array: {e}")
        flatten_success = False

    # Try direct flattening with the wrapper's flatten method
    try:
        flat_wrapper = list(axes.flatten())
        print(f"Direct wrapper flatten length: {len(flat_wrapper)}")
        print(f"Type of direct flatten element: {type(flat_wrapper[0])}")
        direct_flatten_success = True
    except Exception as e:
        print(f"Error with direct flatten: {e}")
        direct_flatten_success = False

    return conversion_success, flatten_success, direct_flatten_success


if __name__ == "__main__":
    conversion_success, flatten_success, direct_flatten_success = (
        test_axes_wrapper_array_conversion()
    )

    print("\nTest Results:")
    print(f"Array conversion: {'PASSED' if conversion_success else 'FAILED'}")
    print(f"Array flatten: {'PASSED' if flatten_success else 'FAILED'}")
    print(f"Direct flatten: {'PASSED' if direct_flatten_success else 'FAILED'}")

    overall_success = all([conversion_success, flatten_success, direct_flatten_success])
    print(f"Overall test: {'PASSED' if overall_success else 'FAILED'}")
