#!/usr/bin/env python3
# Timestamp: "2025-10-02 19:44:06 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ml/plt/plot_pre_rec_curve.py
# ----------------------------------------
from __future__ import annotations

import os

__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import argparse

import numpy as np
from sklearn.metrics import average_precision_score, precision_recall_curve

from scitex.plt.color import get_colors_from_cmap


def _solve_intersection(f1, a, b):
    """Determine intersection of line (y = ax + b) and iso-f1 curve."""
    _a = 2 * a
    _b = -a * f1 + 2 * b - f1
    _c = -b * f1

    x_f = (-_b + np.sqrt(_b**2 - 4 * _a * _c)) / (2 * _a)
    y_f = a * x_f + b

    return (x_f, y_f)


def _to_onehot(class_indices, n_classes):
    """Convert class indices to one-hot encoding."""
    eye = np.eye(n_classes, dtype=int)
    return eye[class_indices]


def plot_pre_rec_curve(true_class, pred_proba, labels, ax=None, spath=None):
    """
    Plot precision-recall curve.

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
        Precision-recall metrics
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
    precision = dict()
    recall = dict()
    threshold = dict()
    pre_rec_auc = dict()
    for i in range(n_classes):
        true_class_i_onehot = true_class_onehot[:, i]
        pred_proba_i = pred_proba[:, i]

        try:
            precision[i], recall[i], threshold[i] = precision_recall_curve(
                true_class_i_onehot,
                pred_proba_i,
            )
            pre_rec_auc[i] = average_precision_score(true_class_i_onehot, pred_proba_i)
        except Exception as e:
            print(e)
            precision[i], recall[i], threshold[i], pre_rec_auc[i] = (
                np.nan,
                np.nan,
                np.nan,
                np.nan,
            )

    ## Average precision: micro and macro

    # A "micro-average": quantifying score on all classes jointly
    precision["micro"], recall["micro"], threshold["micro"] = precision_recall_curve(
        true_class_onehot.ravel(), pred_proba.ravel()
    )
    pre_rec_auc["micro"] = average_precision_score(
        true_class_onehot, pred_proba, average="micro"
    )

    # macro
    _pre_rec_aucs = []
    for i in range(n_classes):
        try:
            _pre_rec_aucs.append(
                average_precision_score(
                    true_class_onehot[:, i], pred_proba[:, i], average="macro"
                )
            )
        except Exception:
            print(
                f'\nPRE-REC-AUC for "{labels[i]}" was not defined and NaN-filled '
                "for a calculation purpose (for the macro avg.)\n"
            )
            _pre_rec_aucs.append(np.nan)
    pre_rec_auc["macro"] = np.nanmean(_pre_rec_aucs)

    # pre_rec_auc["macro"] = average_precision_score(
    #     true_class_onehot, pred_proba, average="macro"
    # )

    # Plot Precision-Recall curve for each class and iso-f1 curves
    # Use scitex color palette for consistent styling
    colors = get_colors_from_cmap("tab10", n_classes)

    if ax is None:
        fig, ax = stx.plt.subplots()
    else:
        fig = ax.get_figure()
    ax.set_box_aspect(1)
    lines = []
    legends = []

    # iso-F1: By definition, an iso-F1 curve contains all points
    #         in the precision/recall space whose F1 scores are the same.
    f_scores = np.linspace(0.2, 0.8, num=4)
    # for f_score in f_scores:
    for i_f, f_score in enumerate(f_scores):
        x = np.linspace(0.01, 1)  # num=50
        y = f_score * x / (2 * x - f_score)
        (l,) = ax.plot(x[y >= 0], y[y >= 0], color="gray", alpha=0.2)

        # ax.annotate("f1={0:0.1f}".format(f_score), xy=(0.9, y[45] + 0.02))
        x_f, y_f = _solve_intersection(f_score, 0.5, 0.5)
        ax.annotate(f"f1={f_score:0.1f}", xy=(x_f - 0.1, y_f - 0.1 * 0.5))
        # ax.annotate("f1={0:0.1f}".format(f_score), xy=(y[35] - 0.02 * (3 - i_f), 0.85))

    lines.append(l)
    legends.append("iso-f1 curves")

    """
    ## In this project, average precision-recall curve is not drawn.
    (l,) = ax.plot(recall["micro"], precision["micro"], color="gold", lw=2)
    lines.append(l)
    legends.append("micro-average\n(AUC = {0:0.2f})" "".format(pre_rec_auc["micro"]))
    """

    ## Each Class
    for i in range(n_classes):
        (l,) = ax.plot(recall[i], precision[i], color=colors[i], lw=2)
        lines.append(l)
        legends.append(f"{labels[i]} (AUC = {pre_rec_auc[i]:0.2f})")

    # fig = plt.gcf()
    fig.subplots_adjust(bottom=0.25)
    ax.set_xlim([-0.01, 1.01])
    ax.set_ylim([-0.01, 1.01])
    ax.set_xticks([0.0, 0.5, 1.0])
    ax.set_yticks([0.0, 0.5, 1.0])
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_title("Precision-Recall Curve")
    ax.legend(lines, legends, loc="lower left")

    metrics = dict(
        pre_rec_auc=pre_rec_auc,
        precision=precision,
        recall=recall,
        threshold=threshold,
    )

    # Save figure if spath is provided
    if spath is not None:
        from pathlib import Path

        # Resolve to absolute path to prevent _out directory creation
        spath_abs = Path(spath).resolve() if isinstance(spath, (str, Path)) else spath
        stx.io.save(fig, str(spath_abs), use_caller_path=False)

    return fig, metrics


def main(args):
    """Demo Precision-Recall curve plotting with MNIST dataset."""
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

    fig, metrics_dict = plot_pre_rec_curve(y_test, predicted_proba, labels)

    import scitex

    scitex.io.save(fig, "plot_pre_rec_curve_demo.jpg")
    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Demo Precision-Recall curve plotting")
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
