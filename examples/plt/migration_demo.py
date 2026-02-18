#!/usr/bin/env python3
# Timestamp: 2026-02-19
# Author: ywatanabe
# File: examples/plt/migration_demo.py
"""
Migration demo: scitex.plt on figrecipe backend.

Shows all key features after the AxisWrapper/FigWrapper -> figrecipe migration.
All plot calls are now handled by figrecipe's RecordingFigure / RecordingAxes.

Run with:
    python examples/plt/migration_demo.py
"""

import matplotlib

matplotlib.use("Agg")

import os
import tempfile

import numpy as np

import scitex as stx


def demo_basic_line(plt):
    """1. Basic line plot - confirm RecordingFigure/RecordingAxes returned."""
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3, 4, 5], [1, 4, 2, 3, 5], label="data")
    ax.set_xyt("X", "Y", "Basic Line Plot")
    ax.hide_spines()

    with tempfile.TemporaryDirectory() as tmpdir:
        plt.save(
            fig, os.path.join(tmpdir, "basic_line.png"), validate=False, verbose=False
        )

    print(f"  fig type : {type(fig).__name__}  (module: {type(fig).__module__})")
    print(f"  ax  type : {type(ax).__name__}  (module: {type(ax).__module__})")
    print(f"  has _recorder : {hasattr(fig, '_recorder')}")
    plt.close("all")


def demo_scientific_methods(plt):
    """2. stx_* scientific methods across a 2x3 grid of axes."""
    data = np.random.randn(50, 8)  # 50 timepoints, 8 trials

    fig, axes = plt.subplots(2, 3, axes_width_mm=40, axes_height_mm=28)
    axes_flat = axes.flatten()

    # Mean +/- SD
    axes_flat[0].stx_mean_std(data)
    axes_flat[0].set_xyt("Time", "Value", "Mean +/- SD")

    # Mean +/- 95 % CI
    axes_flat[1].stx_mean_ci(data)
    axes_flat[1].set_xyt("Time", "Value", "Mean +/- 95% CI")

    # Median +/- IQR
    axes_flat[2].stx_median_iqr(data)
    axes_flat[2].set_xyt("Time", "Value", "Median +/- IQR")

    # ECDF
    axes_flat[3].stx_ecdf(data[:, 0])
    axes_flat[3].set_xyt("Value", "Probability", "ECDF")

    # Confusion matrix
    conf_mat = np.array([[45, 5, 2], [3, 38, 4], [1, 2, 50]])
    axes_flat[4].stx_conf_mat(
        conf_mat,
        x_labels=["A", "B", "C"],
        y_labels=["A", "B", "C"],
    )
    axes_flat[4].set_xyt("Predicted", "True", "Confusion Matrix")

    # Raster plot
    spike_times = [np.sort(np.random.uniform(0, 1, 10)) for _ in range(5)]
    axes_flat[5].stx_raster(spike_times)
    axes_flat[5].set_xyt("Time (s)", "Trial", "Raster Plot")

    with tempfile.TemporaryDirectory() as tmpdir:
        plt.save(
            fig,
            os.path.join(tmpdir, "scientific_methods.png"),
            validate=False,
            verbose=False,
        )
    print("  stx_mean_std / stx_mean_ci / stx_median_iqr : OK")
    print("  stx_ecdf / stx_conf_mat / stx_raster         : OK")
    plt.close("all")


def demo_additional_methods(plt):
    """3. Additional stx_* methods: violin, heatmap, fillv."""
    fig, axes = plt.subplots(1, 3, axes_width_mm=40, axes_height_mm=28)

    # Violin
    axes[0].stx_violin([np.random.randn(30), np.random.randn(30)])
    axes[0].set_xyt("Group", "Value", "Violin")

    # Heatmap
    axes[1].stx_heatmap(np.random.randn(6, 6))
    axes[1].set_xyt("Col", "Row", "Heatmap")

    # Shaded vertical region
    axes[2].plot([0, 1, 2, 3], [0, 1, 0.5, 0.8])
    axes[2].stx_fillv([0.5], [1.5])
    axes[2].set_xyt("X", "Y", "Shaded Region")

    with tempfile.TemporaryDirectory() as tmpdir:
        plt.save(
            fig,
            os.path.join(tmpdir, "additional_methods.png"),
            validate=False,
            verbose=False,
        )
    print("  stx_violin / stx_heatmap / stx_fillv : OK")
    plt.close("all")


def demo_recording_capability(plt):
    """4. Verify figrecipe call-recording works."""
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [4, 5, 6])

    fr = fig._recorder.figure_record
    calls_total = sum(len(ar.calls) for ar in fr.axes.values())
    print(f"  axes recorded   : {len(fr.axes)}")
    print(f"  calls recorded  : {calls_total}")
    assert calls_total >= 1, "Recording failed"
    plt.close("all")


def demo_io_save(plt):
    """5. stx.io.save() integration with RecordingFigure."""
    fig, ax = plt.subplots()
    ax.plot(
        np.linspace(0, 2 * np.pi, 100),
        np.sin(np.linspace(0, 2 * np.pi, 100)),
    )
    ax.set_xyt("Phase (rad)", "Amplitude", "Sine Wave")

    with tempfile.TemporaryDirectory() as tmpdir:
        out = os.path.join(tmpdir, "sine.png")
        stx.io.save(fig, out)
        exists = os.path.exists(out)
        print(f"  io.save created PNG : {exists}")
    plt.close("all")


def demo_color_module(plt):
    """6. Confirm scitex.plt.color submodule is still accessible."""
    assert hasattr(plt, "color"), "plt.color missing"
    from scitex.plt.color import HEX

    assert isinstance(HEX, dict) and len(HEX) > 0
    sample = list(HEX.items())[:3]
    print(f"  HEX sample : {sample}")


@stx.session
def main(
    CONFIG=stx.session.INJECTED,
    plt=stx.session.INJECTED,
    COLORS=stx.session.INJECTED,
    rngg=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    print("scitex.plt -> figrecipe migration demo")
    print("=" * 50)

    print("\n[1] Basic line plot")
    demo_basic_line(plt)

    print("\n[2] Scientific methods (2x3 grid)")
    demo_scientific_methods(plt)

    print("\n[3] Additional methods (violin / heatmap / fillv)")
    demo_additional_methods(plt)

    print("\n[4] Recording capability")
    demo_recording_capability(plt)

    print("\n[5] stx.io.save integration")
    demo_io_save(plt)

    print("\n[6] Color submodule")
    demo_color_module(plt)

    print("\n" + "=" * 50)
    print("Migration demo complete - all features working.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
