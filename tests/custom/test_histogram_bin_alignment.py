#!/usr/bin/env python3
import pytest

pytest.importorskip("zarr")
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-18 19:14:26 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/tests/custom/test_histogram_bin_alignment.py
# ----------------------------------------
pytest.importorskip("matplotlib")

import os

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")  # Use non-interactive backend

import scitex
import scitex.plt as mplt
from scitex.plt.utils import histogram_bin_manager

# Set up output dirs
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE_DIR, "test_histogram_bin_alignment_out")
PNG_DIR = os.path.join(OUT_DIR, "png")
CSV_DIR = os.path.join(OUT_DIR, "csv")

os.makedirs(PNG_DIR, exist_ok=True)
os.makedirs(CSV_DIR, exist_ok=True)


@pytest.mark.xfail(
    reason="Depends on removed AxisWrapper (scitex.plt → figrecipe migration)"
)
def test_matplotlib_histogram_bin_alignment():
    """Test histogram bin alignment with matplotlib histograms."""
    print("Testing matplotlib histogram bin alignment...")

    # Generate test data with different ranges
    np.random.seed(42)
    data1 = np.random.normal(0, 1, 1000)
    data2 = np.random.normal(3, 2, 1000)

    # With bin alignment
    fig1, ax1 = mplt.subplots(figsize=(10, 6))
    ax1.set_title("Histograms with Bin Alignment")

    # Plot two histograms with bin alignment enabled (default)
    ax1.hist(
        data1, bins=20, alpha=0.5, label="Data 1", color="blue", id="aligned_data1"
    )
    ax1.hist(data2, bins=30, alpha=0.5, label="Data 2", color="red", id="aligned_data2")
    ax1.legend()

    # Save figure - should create both PNG and CSV
    plot_path = os.path.join(PNG_DIR, "aligned_histograms.png")
    scitex.io.save(fig1, plot_path)

    # Clear bin manager for next test
    histogram_bin_manager.clear_all()

    # Without bin alignment
    fig2, ax2 = mplt.subplots(figsize=(10, 6))
    ax2.set_title("Histograms without Bin Alignment")

    # Plot two histograms with bin alignment disabled
    ax2.hist(
        data1,
        bins=20,
        alpha=0.5,
        label="Data 1",
        color="blue",
        align_bins=False,
        id="unaligned_data1",
    )
    ax2.hist(
        data2,
        bins=30,
        alpha=0.5,
        label="Data 2",
        color="red",
        align_bins=False,
        id="unaligned_data2",
    )
    ax2.legend()

    # Save figure - should create both PNG and CSV
    plot_path = os.path.join(PNG_DIR, "unaligned_histograms.png")
    scitex.io.save(fig2, plot_path)

    # Load and verify the CSV exports
    aligned_csv = os.path.join(CSV_DIR, "aligned_histograms.csv")
    unaligned_csv = os.path.join(CSV_DIR, "unaligned_histograms.csv")

    assert os.path.exists(aligned_csv), "Aligned histograms CSV not created"
    assert os.path.exists(unaligned_csv), "Unaligned histograms CSV not created"

    # Load the CSV files
    aligned_df = pd.read_csv(aligned_csv)
    unaligned_df = pd.read_csv(unaligned_csv)

    # Verify bin data is present in CSV exports
    for prefix in ["aligned_data1", "aligned_data2"]:
        bin_center_col = next(
            (col for col in aligned_df.columns if f"{prefix}_bin_centers" in col), None
        )
        bin_counts_col = next(
            (col for col in aligned_df.columns if f"{prefix}_bin_counts" in col), None
        )

        assert bin_center_col is not None, f"Bin centers column for {prefix} not found"
        assert bin_counts_col is not None, f"Bin counts column for {prefix} not found"

    # In aligned histograms, bin edges should be the same for both histograms
    aligned_data1_centers = next(
        (
            aligned_df[col]
            for col in aligned_df.columns
            if "aligned_data1_bin_centers" in col
        ),
        None,
    )
    aligned_data2_centers = next(
        (
            aligned_df[col]
            for col in aligned_df.columns
            if "aligned_data2_bin_centers" in col
        ),
        None,
    )

    # Centers should have the same length in aligned case
    assert len(aligned_data1_centers) == len(aligned_data2_centers), (
        "Aligned histograms should have the same number of bins"
    )

    print("Matplotlib histogram bin alignment test passed!")


@pytest.mark.xfail(
    reason="Depends on removed AxisWrapper (scitex.plt → figrecipe migration)"
)
def test_seaborn_histogram_bin_alignment():
    """Test histogram bin alignment with seaborn histplots."""
    print("Testing seaborn histogram bin alignment...")

    # Generate test dataframe
    np.random.seed(42)
    df = pd.DataFrame(
        {
            "group_a": np.random.normal(0, 1, 1000),
            "group_b": np.random.normal(3, 2, 1000),
            "category": np.random.choice(["A", "B"], 1000),
        }
    )

    # With bin alignment
    fig1, ax1 = mplt.subplots(figsize=(10, 6))
    ax1.set_title("Seaborn Histplots with Bin Alignment")

    # Plot two histograms with bin alignment enabled (default)
    ax1.sns_histplot(
        data=df, x="group_a", label="Group A", color="blue", bins=15, id="aligned_sns_a"
    )
    ax1.sns_histplot(
        data=df, x="group_b", label="Group B", color="red", bins=25, id="aligned_sns_b"
    )
    ax1.legend()

    # Save figure - should create both PNG and CSV
    plot_path = os.path.join(PNG_DIR, "aligned_sns_histograms.png")
    scitex.io.save(fig1, plot_path)

    # Clear bin manager for next test
    histogram_bin_manager.clear_all()

    # Without bin alignment
    fig2, ax2 = mplt.subplots(figsize=(10, 6))
    ax2.set_title("Seaborn Histplots without Bin Alignment")

    # Plot two histograms with bin alignment disabled
    ax2.sns_histplot(
        data=df,
        x="group_a",
        label="Group A",
        color="blue",
        bins=15,
        align_bins=False,
        id="unaligned_sns_a",
    )
    ax2.sns_histplot(
        data=df,
        x="group_b",
        label="Group B",
        color="red",
        bins=25,
        align_bins=False,
        id="unaligned_sns_b",
    )
    ax2.legend()

    # Save figure - should create both PNG and CSV
    plot_path = os.path.join(PNG_DIR, "unaligned_sns_histograms.png")
    scitex.io.save(fig2, plot_path)

    # Load and verify the CSV exports
    aligned_csv = os.path.join(CSV_DIR, "aligned_sns_histograms.csv")
    unaligned_csv = os.path.join(CSV_DIR, "unaligned_sns_histograms.csv")

    assert os.path.exists(aligned_csv), "Aligned seaborn histograms CSV not created"
    assert os.path.exists(unaligned_csv), "Unaligned seaborn histograms CSV not created"

    # Load the CSV files
    aligned_df = pd.read_csv(aligned_csv)
    unaligned_df = pd.read_csv(unaligned_csv)

    # Verify bin data is present in CSV exports
    for prefix in ["aligned_sns_a", "aligned_sns_b"]:
        bin_center_col = next(
            (col for col in aligned_df.columns if f"{prefix}_bin_centers" in col), None
        )
        bin_counts_col = next(
            (col for col in aligned_df.columns if f"{prefix}_bin_counts" in col), None
        )

        assert bin_center_col is not None, f"Bin centers column for {prefix} not found"
        assert bin_counts_col is not None, f"Bin counts column for {prefix} not found"

    print("Seaborn histogram bin alignment test passed!")


@pytest.mark.xfail(
    reason="Depends on removed AxisWrapper (scitex.plt → figrecipe migration)"
)
def test_mixed_histogram_bin_alignment():
    """Test histogram bin alignment with a mix of matplotlib and seaborn."""
    print("Testing mixed histogram bin alignment...")

    # Generate test data
    np.random.seed(42)
    data = np.random.normal(0, 1, 1000)
    df = pd.DataFrame({"values": data})

    # With bin alignment
    fig, ax = mplt.subplots(figsize=(10, 6))
    ax.set_title("Mixed Histogram Types with Bin Alignment")

    # Plot both matplotlib and seaborn histograms on same axis
    ax.hist(
        data, bins=20, alpha=0.5, label="Matplotlib Hist", color="blue", id="mixed_mpl"
    )
    ax.sns_histplot(
        data=df,
        x="values",
        alpha=0.5,
        label="Seaborn Histplot",
        color="red",
        bins=30,
        id="mixed_sns",
    )
    ax.legend()

    # Save figure - should create both PNG and CSV
    plot_path = os.path.join(PNG_DIR, "mixed_histograms.png")
    scitex.io.save(fig, plot_path)

    # Load and verify the CSV export
    mixed_csv = os.path.join(CSV_DIR, "mixed_histograms.csv")
    assert os.path.exists(mixed_csv), "Mixed histograms CSV not created"

    # Load the CSV file
    mixed_df = pd.read_csv(mixed_csv)

    # Verify bin data is present in CSV exports
    for prefix in ["mixed_mpl", "mixed_sns"]:
        bin_center_col = next(
            (col for col in mixed_df.columns if f"{prefix}_bin_centers" in col), None
        )
        bin_counts_col = next(
            (col for col in mixed_df.columns if f"{prefix}_bin_counts" in col), None
        )

        assert bin_center_col is not None, f"Bin centers column for {prefix} not found"
        assert bin_counts_col is not None, f"Bin counts column for {prefix} not found"

    print("Mixed histogram bin alignment test passed!")


if __name__ == "__main__":
    print(f"Output directory: {OUT_DIR}")
    test_matplotlib_histogram_bin_alignment()
    test_seaborn_histogram_bin_alignment()
    test_mixed_histogram_bin_alignment()
    print("All histogram bin alignment tests completed successfully!")
