#!/usr/bin/env python3
# Timestamp: "2025-10-02 19:44:13 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ml/plt/plot_roc_curve.py
# ----------------------------------------
from __future__ import annotations

import os

__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import argparse

import numpy as np
from sklearn.metrics import roc_auc_score, roc_curve

import scitex
from scitex.plt.color import get_colors_from_cmap


def _to_onehot(class_indices, n_classes):
    """Convert class indices to one-hot encoding."""
    eye = np.eye(n_classes, dtype=int)
    return eye[class_indices]


def plot_roc_curve(true_class, pred_proba, labels, ax=None, spath=None):
    """
    Plot ROC-AUC curve.

    Parameters
    ----------
    true_class : array-like
        True class labels
    pred_proba : array-like
        Predicted probabilities
    labels : list
        Class labels
    ax : matplotlib axis, optional
        Axis to plot on. If None, creates new figure
    spath : str, optional
        Path to save figure

    Returns
    -------
    fig : matplotlib.figure.Figure
        Figure object
    metrics : dict
        ROC metrics
    """
    import scitex as stx

    # Use label_binarize to be multi-label like settings
    n_classes = len(labels)

    # Handle 1D pred_proba (binary classification with only positive class probabilities)
    if pred_proba.ndim == 1:
        # Convert to 2D: [P(class=0), P(class=1)]
        pred_proba = np.column_stack([1 - pred_proba, pred_proba])

    # Convert string labels to integer indices if needed
    if true_class.dtype.kind in ("U", "S", "O"):  # Unicode, bytes, or object (string)
        label_to_idx = {label: idx for idx, label in enumerate(labels)}
        true_class_idx = np.array([label_to_idx[tc] for tc in true_class])
    else:
        true_class_idx = true_class

    true_class_onehot = _to_onehot(true_class_idx, n_classes)

    # For each class
    fpr = dict()
    tpr = dict()
    threshold = dict()
    roc_auc = dict()
    for i in range(n_classes):
        true_class_i_onehot = true_class_onehot[:, i]
        pred_proba_i = pred_proba[:, i]

        try:
            fpr[i], tpr[i], threshold[i] = roc_curve(true_class_i_onehot, pred_proba_i)
            roc_auc[i] = roc_auc_score(true_class_i_onehot, pred_proba_i)
        except Exception as e:
            print(e)
            fpr[i], tpr[i], threshold[i], roc_auc[i] = (
                [np.nan],
                [np.nan],
                [np.nan],
                np.nan,
            )

    ## Average fpr: micro and macro

    # A "micro-average": quantifying score on all classes jointly
    fpr["micro"], tpr["micro"], threshold["micro"] = roc_curve(
        true_class_onehot.ravel(), pred_proba.ravel()
    )
    roc_auc["micro"] = roc_auc_score(true_class_onehot, pred_proba, average="micro")

    # macro
    _roc_aucs = []
    for i in range(n_classes):
        try:
            _roc_aucs.append(
                roc_auc_score(
                    true_class_onehot[:, i], pred_proba[:, i], average="macro"
                )
            )
        except Exception:
            print(
                f'\nROC-AUC for "{labels[i]}" was not defined and NaN-filled '
                "for a calculation purpose (for the macro avg.)\n"
            )
            _roc_aucs.append(np.nan)
    roc_auc["macro"] = np.nanmean(_roc_aucs)

    # Plot FPR-TPR curve for each class and iso-f1 curves
    # Use scitex color palette for consistent styling
    colors = get_colors_from_cmap("tab10", n_classes)

    if ax is None:
        fig, ax = stx.plt.subplots()
    else:
        fig = ax.get_figure()
    ax.set_box_aspect(1)
    lines = []
    legends = []

    ## Chance Level (the diagonal line)
    (l,) = ax.plot(
        np.linspace(0.01, 1),
        np.linspace(0.01, 1),
        color="gray",
        lw=2,
        linestyle="--",
        alpha=0.8,
    )
    lines.append(l)
    legends.append("Chance")

    ## Each Class
    for i in range(n_classes):
        (l,) = ax.plot(fpr[i], tpr[i], color=colors[i], lw=2)
        lines.append(l)
        legends.append(f"{labels[i]} (AUC = {roc_auc[i]:0.2f})")

    # fig = plt.gcf()
    fig.subplots_adjust(bottom=0.25)
    ax.set_xlim([-0.01, 1.01])
    ax.set_ylim([-0.01, 1.01])
    ax.set_xticks([0.0, 0.5, 1.0])
    ax.set_yticks([0.0, 0.5, 1.0])
    ax.set_xlabel("FPR")
    ax.set_ylabel("TPR")
    ax.set_title("ROC Curve")
    ax.legend(lines, legends, loc="lower right")

    metrics = dict(roc_auc=roc_auc, fpr=fpr, tpr=tpr, threshold=threshold)

    # Save figure if spath is provided
    if spath is not None:
        from pathlib import Path

        # Resolve to absolute path to prevent _out directory creation
        spath_abs = Path(spath).resolve() if isinstance(spath, (str, Path)) else spath
        scitex.io.save(fig, str(spath_abs), use_caller_path=False)

    return fig, metrics


def main(args):
    """Demo ROC AUC plotting with MNIST dataset."""
    from sklearn import datasets, svm
    from sklearn.model_selection import train_test_split

    np.random.seed(42)

    digits = datasets.load_digits()
    n_samples = len(digits.images)
    data = digits.images.reshape((n_samples, -1))

    clf = svm.SVC(gamma=0.001, probability=True)

    X_train, X_test, y_train, y_test = train_test_split(
        data, digits.target, test_size=0.5, shuffle=False
    )

    clf.fit(X_train, y_train)
    predicted_proba = clf.predict_proba(X_test)

    n_classes = len(np.unique(digits.target))
    labels = [f"Class {i}" for i in range(n_classes)]

    # plt.rcParams["font.size"] = 20
    # plt.rcParams["legend.fontsize"] = "xx-small"
    # plt.rcParams["figure.figsize"] = (16 * 1.2, 9 * 1.2)

    y_test[y_test == 9] = 8  # override 9 as 8

    fig, metrics_dict = plot_roc_curve(
        true_class=y_test, pred_proba=predicted_proba, labels=labels
    )

    scitex.io.save(fig, "plot_roc_curve_demo.jpg")
    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Demo ROC AUC plotting")
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


# Backward compatibility alias
roc_auc = plot_roc_curve

# EOF
