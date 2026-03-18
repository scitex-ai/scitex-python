#!/usr/bin/env python3
"""Demonstrate validation set support in all time series splitters."""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scitex.ml.classification.time_series import (
    TimeSeriesStratifiedSplit,
    TimeSeriesSlidingWindowSplit,
    TimeSeriesBlockingSplit,
    TimeSeriesCalendarSplit
)

def demo_stratified_with_val():
    """Demo TimeSeriesStratifiedSplit with validation."""
    print("\n" + "="*60)
    print("TimeSeriesStratifiedSplit with Validation")
    print("="*60)

    # Generate data
    np.random.seed(42)
    n_samples = 300
    X = np.random.randn(n_samples, 5)
    y = np.random.randint(0, 2, n_samples)
    timestamps = pd.date_range('2023-01-01', periods=n_samples, freq='D')

    # Create splitter with validation
    splitter = TimeSeriesStratifiedSplit(
        n_splits=3,
        test_ratio=0.2,
        val_ratio=0.15,  # 15% validation
        gap=5
    )

    # Run splits
    for fold, (train_idx, val_idx, test_idx) in enumerate(splitter.split_with_val(X, y, timestamps)):
        print(f"\nFold {fold}:")
        print(f"  Train: samples {train_idx[0]:3d}-{train_idx[-1]:3d} ({len(train_idx):3d} samples)")
        print(f"  Val:   samples {val_idx[0]:3d}-{val_idx[-1]:3d} ({len(val_idx):3d} samples)")
        print(f"  Test:  samples {test_idx[0]:3d}-{test_idx[-1]:3d} ({len(test_idx):3d} samples)")

        # Verify temporal order
        assert timestamps[train_idx].max() < timestamps[val_idx].min(), "Train must come before validation"
        assert timestamps[val_idx].max() < timestamps[test_idx].min(), "Validation must come before test"
        print("  ✓ Temporal order verified")

    # Visualize
    fig = splitter.plot_splits(X, y, timestamps)
    fig.suptitle("TimeSeriesStratifiedSplit with Validation", fontsize=14)
    plt.savefig("stratified_with_val_demo.png")
    plt.close()

def demo_sliding_window_with_val():
    """Demo TimeSeriesSlidingWindowSplit with validation."""
    print("\n" + "="*60)
    print("TimeSeriesSlidingWindowSplit with Validation")
    print("="*60)

    # Generate data
    np.random.seed(42)
    n_samples = 300
    X = np.random.randn(n_samples, 5)
    y = np.random.randint(0, 2, n_samples)
    timestamps = np.arange(n_samples)

    # Create splitter with validation
    splitter = TimeSeriesSlidingWindowSplit(
        window_size=100,
        step_size=30,
        test_size=20,
        val_ratio=0.2,  # 20% of window for validation
        gap=5
    )

    # Run splits
    for fold, (train_idx, val_idx, test_idx) in enumerate(splitter.split_with_val(X, y, timestamps)):
        if fold >= 3:  # Limit output
            break
        print(f"\nFold {fold}:")
        print(f"  Train: samples {train_idx[0]:3d}-{train_idx[-1]:3d} ({len(train_idx):3d} samples)")
        print(f"  Val:   samples {val_idx[0]:3d}-{val_idx[-1]:3d} ({len(val_idx):3d} samples)")
        print(f"  Test:  samples {test_idx[0]:3d}-{test_idx[-1]:3d} ({len(test_idx):3d} samples)")

        # Verify temporal order
        assert timestamps[train_idx].max() < timestamps[val_idx].min(), "Train must come before validation"
        assert timestamps[val_idx].max() < timestamps[test_idx].min(), "Validation must come before test"
        print("  ✓ Temporal order verified")

    # Visualize
    fig = splitter.plot_splits(X, y, timestamps)
    fig.suptitle("TimeSeriesSlidingWindowSplit with Validation", fontsize=14)
    plt.savefig("sliding_window_with_val_demo.png")
    plt.close()

def demo_blocking_with_val():
    """Demo TimeSeriesBlockingSplit with validation."""
    print("\n" + "="*60)
    print("TimeSeriesBlockingSplit with Validation")
    print("="*60)

    # Generate data with multiple subjects
    np.random.seed(42)
    n_subjects = 4
    n_per_subject = 100
    n_samples = n_subjects * n_per_subject

    X = np.random.randn(n_samples, 5)
    y = np.random.randint(0, 2, n_samples)
    timestamps = np.tile(np.arange(n_per_subject), n_subjects)
    groups = np.repeat(np.arange(n_subjects), n_per_subject)

    # Create splitter with validation
    splitter = TimeSeriesBlockingSplit(
        n_splits=3,
        test_ratio=0.2,
        val_ratio=0.15  # 15% validation per subject
    )

    # Run splits
    for fold, (train_idx, val_idx, test_idx) in enumerate(splitter.split_with_val(X, y, timestamps, groups)):
        if fold >= 2:  # Limit output
            break
        print(f"\nFold {fold}:")
        print(f"  Train: {len(train_idx):3d} samples across subjects")
        print(f"  Val:   {len(val_idx):3d} samples across subjects")
        print(f"  Test:  {len(test_idx):3d} samples across subjects")

        # Verify temporal order per subject
        for subj in np.unique(groups):
            subj_train = train_idx[groups[train_idx] == subj]
            subj_val = val_idx[groups[val_idx] == subj]
            subj_test = test_idx[groups[test_idx] == subj]

            if len(subj_train) > 0 and len(subj_val) > 0:
                assert timestamps[subj_train].max() < timestamps[subj_val].min(), f"Subject {subj}: Train before val"
            if len(subj_val) > 0 and len(subj_test) > 0:
                assert timestamps[subj_val].max() < timestamps[subj_test].min(), f"Subject {subj}: Val before test"
        print("  ✓ Temporal order verified for all subjects")

    # Visualize
    fig = splitter.plot_splits(X, y, timestamps, groups)
    fig.suptitle("TimeSeriesBlockingSplit with Validation", fontsize=14)
    plt.savefig("blocking_with_val_demo.png")
    plt.close()

def demo_calendar_with_val():
    """Demo TimeSeriesCalendarSplit with validation."""
    print("\n" + "="*60)
    print("TimeSeriesCalendarSplit with Validation")
    print("="*60)

    # Generate data
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', '2023-12-31', freq='D')
    n_samples = len(dates)
    X = np.random.randn(n_samples, 5)
    y = np.random.randint(0, 2, n_samples)

    # Create splitter with validation
    splitter = TimeSeriesCalendarSplit(
        interval='M',
        n_train_intervals=6,
        n_val_intervals=1,  # 1 month validation
        n_test_intervals=1   # 1 month test
    )

    # Run splits
    for fold, (train_idx, val_idx, test_idx) in enumerate(splitter.split_with_val(X, y, timestamps=dates)):
        if fold >= 3:  # Limit output
            break
        print(f"\nFold {fold}:")
        train_start = dates[train_idx[0]].strftime('%Y-%m-%d')
        train_end = dates[train_idx[-1]].strftime('%Y-%m-%d')
        val_start = dates[val_idx[0]].strftime('%Y-%m-%d')
        val_end = dates[val_idx[-1]].strftime('%Y-%m-%d')
        test_start = dates[test_idx[0]].strftime('%Y-%m-%d')
        test_end = dates[test_idx[-1]].strftime('%Y-%m-%d')

        print(f"  Train: {train_start} to {train_end} ({len(train_idx):3d} samples)")
        print(f"  Val:   {val_start} to {val_end} ({len(val_idx):3d} samples)")
        print(f"  Test:  {test_start} to {test_end} ({len(test_idx):3d} samples)")

        # Verify temporal order
        assert dates[train_idx].max() < dates[val_idx].min(), "Train must come before validation"
        assert dates[val_idx].max() < dates[test_idx].min(), "Validation must come before test"
        print("  ✓ Temporal order verified")

    # Visualize
    fig = splitter.plot_splits(X, y, dates)
    fig.suptitle("TimeSeriesCalendarSplit with Validation", fontsize=14)
    plt.savefig("calendar_with_val_demo.png")
    plt.close()

if __name__ == "__main__":
    print("Time Series Cross-Validation with Validation Sets Demo")
    print("=" * 60)

    # Run all demos
    demo_stratified_with_val()
    demo_sliding_window_with_val()
    demo_blocking_with_val()
    demo_calendar_with_val()

    print("\n" + "="*60)
    print("✓ All validation demos completed successfully!")
    print("Generated visualizations:")
    print("  - stratified_with_val_demo.png")
    print("  - sliding_window_with_val_demo.png")
    print("  - blocking_with_val_demo.png")
    print("  - calendar_with_val_demo.png")
