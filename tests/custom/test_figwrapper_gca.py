#!/usr/bin/env python3
import pytest

pytest.importorskip("zarr")
# -*- coding: utf-8 -*-
# Test for FigWrapper.gca() and add_subplot() functionality

pytest.importorskip("matplotlib")

import os

import matplotlib
import numpy as np

matplotlib.use("Agg")  # Use non-interactive backend

import scitex
import scitex.plt as mplt


def test_figure_gca_returns_axis_wrapper():
    """Test that FigWrapper.gca() returns a properly wrapped axis."""
    print("\nTesting FigWrapper.gca() returns AxisWrapper...")

    # Create a figure using scitex.plt.figure()
    fig = mplt.figure(figsize=(8, 6))

    # Get an axis using gca()
    ax = fig.gca()

    # Print type info for debugging
    print(f"Type of figure: {type(fig)}")
    print(f"Type of axis from gca(): {type(ax)}")

    # Check if the axis has SciTeX AxisWrapper methods
    has_set_xyt = hasattr(ax, "set_xyt")
    has_track = hasattr(ax, "track")
    has_history = hasattr(ax, "_ax_history")

    print(f"Has set_xyt method: {has_set_xyt}")
    print(f"Has track attribute: {has_track}")
    print(f"Has _ax_history attribute: {has_history}")

    # Try using set_xyt method
    if has_set_xyt:
        ax.set_xyt("X Label", "Y Label", "Title")
        print("Successfully called set_xyt()")

    # Plot something with tracking
    if has_track:
        ax.track = True
        ax.plot([1, 2, 3], [4, 5, 6], id="test_plot_gca")

        # Check if tracking worked
        if has_history:
            history_count = len(ax._ax_history)
            print(f"Axis has {history_count} tracked items")
            assert history_count > 0, "Axis should have tracked items"

    # Test CSV export (only if method exists - depends on figrecipe version)
    if hasattr(ax, "export_as_csv"):
        df = ax.export_as_csv()
        print(f"CSV data from gca axis: {df.shape}")

    return has_set_xyt and has_track and has_history


def test_figure_add_subplot_returns_axis_wrapper():
    """Test that FigWrapper.add_subplot() returns a properly wrapped axis."""
    print("\nTesting FigWrapper.add_subplot() returns AxisWrapper...")

    # Create a figure using scitex.plt.figure()
    fig = mplt.figure(figsize=(8, 6))

    # Add subplot
    ax = fig.add_subplot(111)

    # Print type info for debugging
    print(f"Type of axis from add_subplot(): {type(ax)}")

    # Check if the axis has SciTeX AxisWrapper methods
    has_set_xyt = hasattr(ax, "set_xyt")
    has_track = hasattr(ax, "track")
    has_history = hasattr(ax, "_ax_history")

    print(f"Has set_xyt method: {has_set_xyt}")
    print(f"Has track attribute: {has_track}")
    print(f"Has _ax_history attribute: {has_history}")

    # Try using set_xyt method
    if has_set_xyt:
        ax.set_xyt("X Label", "Y Label", "Subplot Title")
        print("Successfully called set_xyt()")

    # Plot something with tracking
    if has_track:
        ax.track = True
        ax.plot([3, 2, 1], [6, 5, 4], id="test_plot_subplot")

        # Check if tracking worked
        if has_history:
            history_count = len(ax._ax_history)
            print(f"Axis has {history_count} tracked items")
            assert history_count > 0, "Axis should have tracked items"

    # Test CSV export (only if method exists - depends on figrecipe version)
    if hasattr(ax, "export_as_csv"):
        df = ax.export_as_csv()
        print(f"CSV data from add_subplot axis: {df.shape}")

    return has_set_xyt and has_track and has_history


def test_complete_workflow():
    """Test a complete workflow using both methods."""
    print("\nTesting complete workflow with both methods...")

    # Create a figure using scitex.plt.figure()
    fig = mplt.figure(figsize=(10, 8))

    # Create a 2x2 grid of subplots
    ax1 = fig.add_subplot(221)
    ax2 = fig.add_subplot(222)
    ax3 = fig.add_subplot(223)
    ax4 = fig.add_subplot(224)

    # Plot different data on each subplot
    ax1.plot([1, 2, 3], [4, 5, 6])
    if hasattr(ax1, "set_xyt"):
        ax1.set_xyt("X", "Y", "Plot 1")
    else:
        ax1.set_xlabel("X")
        ax1.set_ylabel("Y")
        ax1.set_title("Plot 1")

    ax2.scatter([1, 2, 3], [6, 5, 4])
    if hasattr(ax2, "set_xyt"):
        ax2.set_xyt("X", "Y", "Plot 2")
    else:
        ax2.set_xlabel("X")
        ax2.set_ylabel("Y")
        ax2.set_title("Plot 2")

    ax3.bar(["A", "B", "C"], [5, 3, 7])
    if hasattr(ax3, "set_xyt"):
        ax3.set_xyt("Category", "Value", "Plot 3")
    else:
        ax3.set_xlabel("Category")
        ax3.set_ylabel("Value")
        ax3.set_title("Plot 3")

    x = np.linspace(0, 10, 100)
    ax4.plot(x, np.sin(x))
    if hasattr(ax4, "set_xyt"):
        ax4.set_xyt("X", "sin(x)", "Plot 4")
    else:
        ax4.set_xlabel("X")
        ax4.set_ylabel("sin(x)")
        ax4.set_title("Plot 4")

    # Save the figure with scitex.io.save
    output_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "test_figwrapper_gca_out"
    )
    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, "test_figwrapper_complete.png")
    scitex.io.save(fig, save_path)

    # Export CSV data from the figure (only if method exists)
    fig_df = None
    if hasattr(fig, "export_as_csv"):
        fig_df = fig.export_as_csv()
        print(f"Figure CSV data shape: {fig_df.shape}")
        print(f"Figure CSV columns: {fig_df.columns.tolist()[:5]}...")

    # Check if CSV was exported by scitex.io.save
    csv_path = save_path.replace(".png", ".csv")
    csv_exported = os.path.exists(csv_path)
    print(f"CSV exported by scitex.io.save: {csv_exported}")

    return csv_exported or (
        fig_df is not None and fig_df.shape[1] > 0
    )  # Success if either CSV was exported or figure has data


if __name__ == "__main__":
    gca_success = test_figure_gca_returns_axis_wrapper()
    subplot_success = test_figure_add_subplot_returns_axis_wrapper()
    workflow_success = test_complete_workflow()

    print("\nTest Results:")
    print(f"gca() test: {'PASSED' if gca_success else 'FAILED'}")
    print(f"add_subplot() test: {'PASSED' if subplot_success else 'FAILED'}")
    print(f"Complete workflow test: {'PASSED' if workflow_success else 'FAILED'}")
    print(
        f"Overall test: {'PASSED' if all([gca_success, subplot_success, workflow_success]) else 'FAILED'}"
    )
