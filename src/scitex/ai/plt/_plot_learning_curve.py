#!/usr/bin/env python3
# Timestamp: "2025-10-02 19:50:54 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ml/plt/plot_learning_curve.py
# ----------------------------------------
from __future__ import annotations

import os

__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
# Time-stamp: "2024-03-12 19:52:48 (ywatanabe)"

import argparse
import re

import numpy as np
import pandas as pd

import scitex
from scitex.plt.color import to_hex


def _prepare_metrics_df(metrics_df):
    """Prepare metrics DataFrame with i_global as index."""
    if metrics_df.index.name != "i_global":
        try:
            metrics_df = metrics_df.set_index("i_global")
        except KeyError:
            print(
                "Error: The DataFrame does not contain a column named 'i_global'. "
                "Please check the column names."
            )
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    metrics_df["i_global"] = metrics_df.index  # alias
    return metrics_df


def _configure_accuracy_axis(ax, metric_key):
    """Configure y-axis for accuracy metrics."""
    if re.search("[aA][cC][cC]", metric_key):
        ax.set_ylim(0, 1)
        ax.set_yticks([0, 0.5, 1.0])
    return ax


def _plot_training_data(ax, metrics_df, metric_key, linewidth=1, color=None):
    """Plot training phase data as line."""
    if color is None:
        color = to_hex("blue")

    is_training = scitex.str.search("^[Tt]rain(ing)?", metrics_df.step, as_bool=True)[0]
    training_df = metrics_df[is_training]

    if len(training_df) > 0:
        ax.plot(
            training_df.index,
            training_df[metric_key],
            label="Training",
            color=color,
            linewidth=linewidth,
        )
        ax.legend()

    return ax


def _plot_validation_data(ax, metrics_df, metric_key, markersize=3, color=None):
    """Plot validation phase data as scatter."""
    if color is None:
        color = to_hex("green")

    is_validation = scitex.str.search(
        "^[Vv]alid(ation)?", metrics_df.step, as_bool=True
    )[0]
    validation_df = metrics_df[is_validation]

    if len(validation_df) > 0:
        ax.scatter(
            validation_df.index,
            validation_df[metric_key],
            label="Validation",
            color=color,
            s=markersize,
            alpha=0.9,
        )
        ax.legend()
    return ax


def _plot_test_data(ax, metrics_df, metric_key, markersize=3, color=None):
    """Plot test phase data as scatter."""
    if color is None:
        color = to_hex("red")

    is_test = scitex.str.search("^[Tt]est", metrics_df.step, as_bool=True)[0]
    test_df = metrics_df[is_test]

    if len(test_df) > 0:
        ax.scatter(
            test_df.index,
            test_df[metric_key],
            label="Test",
            color=color,
            s=markersize,
            alpha=0.9,
        )
        ax.legend()
    return ax


def _add_epoch_vlines(ax, metrics_df, color="grey"):
    """Add vertical lines at epoch boundaries."""
    epoch_starts = metrics_df[metrics_df["i_batch"] == 0].index.values
    ax.vlines(
        x=epoch_starts,
        ymin=-1e4,
        ymax=1e4,
        linestyle="--",
        color=color,
    )
    return ax


def _select_epoch_ticks(metrics_df, max_n_ticks=4):
    """Select representative epoch tick positions and labels."""
    unique_epochs = metrics_df["i_epoch"].drop_duplicates().values
    epoch_starts = (
        metrics_df[metrics_df["i_batch"] == 0]["i_global"].drop_duplicates().values
    )

    if len(epoch_starts) > max_n_ticks:
        selected_ticks = np.linspace(
            epoch_starts[0], epoch_starts[-1], max_n_ticks, dtype=int
        )
        selected_labels = [
            metrics_df[metrics_df["i_global"] == tick]["i_epoch"].iloc[0]
            for tick in selected_ticks
        ]
    else:
        selected_ticks = epoch_starts
        selected_labels = unique_epochs
    return selected_ticks, selected_labels


def plot_learning_curve(
    metrics_df,
    keys,
    title="Title",
    max_n_ticks=4,
    scattersize=3,
    linewidth=1,
    yscale="linear",
    spath=None,
):
    """Plot learning curves from training metrics.

    This is mainly used by scitex/ml/training/_LearningCurveLogger.py

    Parameters
    ----------
    metrics_df : pd.DataFrame
        DataFrame with columns: step, i_global, i_epoch, i_batch, and metric columns
    keys : list of str
        Metric names to plot
    title : str
        Plot title
    max_n_ticks : int
        Maximum number of ticks on x-axis
    scattersize : float
        Size of scatter points for validation/test
    linewidth : float
        Width of training line
    yscale : str
        Y-axis scale ('linear' or 'log')
    spath : str, optional
        Save path for the figure

    Returns
    -------
    fig : matplotlib.figure.Figure
        Figure containing learning curves

    Example
    -------
    >>> print(metrics_df)
    #                 step  i_global  i_epoch  i_batch      loss
    # 0       Training         0        0        0  0.717023
    # 1       Training         1        0        1  0.703844
    # ...
    # [123271 rows x 5 columns]
    """
    # Prepare data
    metrics_df = _prepare_metrics_df(metrics_df)
    selected_ticks, selected_labels = _select_epoch_ticks(metrics_df, max_n_ticks)

    # Create subplots
    fig, axes = scitex.plt.subplots(len(keys), 1, sharex=True, sharey=False)
    axes = axes if len(keys) != 1 else [axes]

    # Configure axes
    axes[-1].set_xlabel("Iteration #")
    fig.text(0.5, 0.95, title, ha="center")

    # Plot each metric
    for i_metric, metric_key in enumerate(keys):
        ax = axes[i_metric]
        ax.set_yscale(yscale)
        ax.set_ylabel(metric_key)

        # Configure axis for accuracy metrics
        ax = _configure_accuracy_axis(ax, metric_key)

        # Plot training data (line)
        ax = _plot_training_data(ax, metrics_df, metric_key, linewidth=linewidth)

        # Plot validation data (scatter)
        ax = _plot_validation_data(ax, metrics_df, metric_key, markersize=scattersize)

        # Plot test data if it exists (scatter)
        if "Test" in metrics_df["step"].values:
            ax = _plot_test_data(ax, metrics_df, metric_key, markersize=scattersize)

    # Save if path provided
    if spath is not None:
        scitex.io.save(fig, spath, use_caller_path=True)

    return fig


def main(args):
    """Demo learning curve plotting with synthetic data."""
    import numpy as np

    # Create synthetic metrics data
    n_epochs = 10
    n_batches = 100
    data = []
    for i_epoch in range(n_epochs):
        for i_batch in range(n_batches):
            i_global = i_epoch * n_batches + i_batch
            loss = 0.7 * np.exp(-i_global / 200) + 0.1 * np.random.rand()
            acc = min(
                0.95,
                0.3 + 0.6 * (1 - np.exp(-i_global / 300)) + 0.05 * np.random.rand(),
            )
            data.append(
                {
                    "step": "Training",
                    "i_global": i_global,
                    "i_epoch": i_epoch,
                    "i_batch": i_batch,
                    "loss": loss,
                    "accuracy": acc,
                }
            )
        # Add validation metrics at epoch end
        i_global = (i_epoch + 1) * n_batches - 1
        val_loss = 0.75 * np.exp(-i_global / 200) + 0.15 * np.random.rand()
        val_acc = min(
            0.92,
            0.25 + 0.6 * (1 - np.exp(-i_global / 300)) + 0.08 * np.random.rand(),
        )
        data.append(
            {
                "step": "Validation",
                "i_global": i_global,
                "i_epoch": i_epoch,
                "i_batch": n_batches - 1,
                "loss": val_loss,
                "accuracy": val_acc,
            }
        )

    metrics_df = pd.DataFrame(data)
    keys = ["loss", "accuracy"]
    fig = plot_learning_curve(
        metrics_df,
        keys,
        title="Demo Learning Curve",
        yscale="linear",
        spath="learning_curve_demo.jpg",
    )
    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Demo learning curve plotting")
    return parser.parse_args()


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
        verbose=False,
        agg=True,
    )

    exit_status = main(args)

    stx.session.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

# EOF
