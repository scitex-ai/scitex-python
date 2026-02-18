#!/usr/bin/env python3
# Timestamp: 2026-02-19
# Author: ywatanabe
# File: tests/scitex/plt/test__migration_stability.py
"""
Integration tests confirming scitex.plt -> figrecipe migration stability.

Verifies that:
- stx.plt.subplots() returns figrecipe RecordingFigure/RecordingAxes
- All stx_* scientific plot methods are accessible and callable
- AxisWrapper / FigWrapper are fully removed
- Recording capability is functional
- Color submodule and io.save integration still work
"""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as mplt
import numpy as np
import pytest

import scitex as stx
import scitex.plt as plt

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def fig_ax():
    fig, ax = plt.subplots()
    yield fig, ax
    mplt.close("all")


@pytest.fixture
def fig_ax_multi():
    fig, axes = plt.subplots(1, 3)
    yield fig, axes
    mplt.close("all")


# ---------------------------------------------------------------------------
# TestMigrationBackend
# ---------------------------------------------------------------------------


class TestMigrationBackend:
    """Verify figrecipe classes are returned and legacy classes are gone."""

    def test_subplots_returns_recording_figure(self, fig_ax):
        """stx.plt.subplots() must return a figrecipe RecordingFigure."""
        fig, _ = fig_ax
        assert hasattr(fig, "_recorder"), (
            f"Expected RecordingFigure with _recorder, got {type(fig)}"
        )

    def test_subplots_returns_recording_axes(self, fig_ax):
        """Returned axes must be RecordingAxes (has SciTexMixin methods)."""
        _, ax = fig_ax
        assert hasattr(ax, "stx_mean_std"), (
            f"Expected RecordingAxes with stx_mean_std, got {type(ax)}"
        )

    def test_save_is_figrecipe_save(self):
        """plt.save must resolve to figrecipe, not scitex internals."""
        assert plt.save.__module__.startswith("figrecipe"), (
            f"plt.save module is '{plt.save.__module__}', expected figrecipe.*"
        )

    def test_no_axiswrapper(self):
        """AxisWrapper must be unimportable from scitex.plt after migration."""
        with pytest.raises(ImportError):
            from scitex.plt import AxisWrapper  # noqa: F401

    def test_no_figwrapper(self):
        """FigWrapper must be unimportable from scitex.plt after migration."""
        with pytest.raises(ImportError):
            from scitex.plt import FigWrapper  # noqa: F401


# ---------------------------------------------------------------------------
# TestStyleMethods
# ---------------------------------------------------------------------------


class TestStyleMethods:
    """Verify style/decoration methods provided by figrecipe mixins."""

    def test_set_xyt(self, fig_ax):
        """ax.set_xyt() should label axes and set title without error."""
        _, ax = fig_ax
        assert callable(getattr(ax, "set_xyt", None)), "set_xyt not callable"
        ax.set_xyt("X label", "Y label", "Plot Title")

    def test_hide_spines(self, fig_ax):
        """ax.hide_spines() should run without error."""
        _, ax = fig_ax
        assert callable(getattr(ax, "hide_spines", None)), "hide_spines not callable"
        ax.hide_spines()

    def test_sci_note(self, fig_ax):
        """ax.sci_note() should apply scientific notation without error."""
        _, ax = fig_ax
        assert callable(getattr(ax, "sci_note", None)), "sci_note not callable"
        ax.plot([1, 2], [1e6, 2e6])
        ax.sci_note()


# ---------------------------------------------------------------------------
# TestSciTexMethods
# ---------------------------------------------------------------------------


class TestSciTexMethods:
    """Verify all stx_* scientific plotting methods are functional."""

    def test_stx_mean_std(self, fig_ax):
        """ax.stx_mean_std() should plot mean +/- SD bands."""
        _, ax = fig_ax
        ax.stx_mean_std(np.random.randn(10, 5))

    def test_stx_mean_ci(self, fig_ax):
        """ax.stx_mean_ci() should plot mean +/- 95% CI bands."""
        _, ax = fig_ax
        ax.stx_mean_ci(np.random.randn(10, 5))

    def test_stx_median_iqr(self, fig_ax):
        """ax.stx_median_iqr() should plot median +/- IQR bands."""
        _, ax = fig_ax
        ax.stx_median_iqr(np.random.randn(10, 5))

    def test_stx_ecdf(self, fig_ax):
        """ax.stx_ecdf() should plot empirical CDF."""
        _, ax = fig_ax
        ax.stx_ecdf(np.random.randn(100))

    def test_stx_conf_mat(self, fig_ax):
        """ax.stx_conf_mat() should render a 2x2 confusion matrix."""
        _, ax = fig_ax
        ax.stx_conf_mat(np.array([[10, 2], [3, 15]]))

    def test_stx_heatmap(self, fig_ax):
        """ax.stx_heatmap() should render a 4x4 heatmap."""
        _, ax = fig_ax
        ax.stx_heatmap(np.random.randn(4, 4))

    def test_stx_violin(self, fig_ax):
        """ax.stx_violin() should render violin plots for two groups."""
        _, ax = fig_ax
        ax.stx_violin([np.random.randn(20), np.random.randn(20)])

    def test_stx_raster(self, fig_ax):
        """ax.stx_raster() should render a spike raster plot."""
        _, ax = fig_ax
        ax.stx_raster([[0.1, 0.5, 0.9], [0.2, 0.7]])

    def test_stx_fillv(self, fig_ax):
        """ax.stx_fillv() should add vertical shaded regions."""
        _, ax = fig_ax
        ax.plot([0, 1], [0, 1])
        ax.stx_fillv([0.2], [0.5])


# ---------------------------------------------------------------------------
# TestRecordingCapability
# ---------------------------------------------------------------------------


class TestRecordingCapability:
    """Verify figrecipe's call-recording mechanism works end-to-end."""

    def test_calls_recorded(self, fig_ax):
        """plot() calls must be captured in _recorder.figure_record."""
        fig, ax = fig_ax
        ax.plot([1, 2, 3], [4, 5, 6])
        figure_record = fig._recorder.figure_record
        # At least one axes entry must have at least one recorded call
        assert len(figure_record.axes) >= 1, "No axes entries recorded"
        calls_total = sum(len(ar.calls) for ar in figure_record.axes.values())
        assert calls_total >= 1, "No calls recorded after ax.plot()"

    def test_recipe_structure(self, fig_ax):
        """RecordingFigure._recorder.figure_record must have an .axes dict."""
        fig, ax = fig_ax
        ax.plot([1, 2], [1, 2])
        recorder = fig._recorder
        assert hasattr(recorder, "figure_record"), "_recorder missing figure_record"
        fr = recorder.figure_record
        assert hasattr(fr, "axes"), "figure_record missing .axes"
        assert isinstance(fr.axes, dict), (
            f"figure_record.axes is {type(fr.axes)}, expected dict"
        )


# ---------------------------------------------------------------------------
# TestColorModule
# ---------------------------------------------------------------------------


class TestColorModule:
    """Verify scitex.plt.color submodule is still accessible post-migration."""

    def test_color_module_accessible(self):
        """plt.color attribute must exist on the scitex.plt module."""
        assert hasattr(plt, "color"), "scitex.plt.color submodule not accessible"

    def test_hex_colors_accessible(self):
        """HEX color dict must be importable from scitex.plt.color."""
        from scitex.plt.color import HEX

        assert isinstance(HEX, dict), f"HEX is {type(HEX)}, expected dict"
        assert len(HEX) > 0, "HEX dict is empty"


# ---------------------------------------------------------------------------
# TestIoSaveIntegration
# ---------------------------------------------------------------------------


class TestIoSaveIntegration:
    """Verify that figure saving works via both plt.save and stx.io.save."""

    def test_io_save_fig_creates_png(self, tmp_path):
        """stx.io.save(fig, path) must create a PNG file on disk."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [4, 5, 6])
        out = str(tmp_path / "test_io.png")
        try:
            stx.io.save(fig, out)
            assert (tmp_path / "test_io.png").exists(), "PNG not created by io.save"
        finally:
            mplt.close("all")

    def test_plt_save_creates_png(self, tmp_path):
        """plt.save(fig, path, validate=False) must create a PNG file."""
        fig, ax = plt.subplots()
        ax.plot([1, 2], [1, 2])
        out = str(tmp_path / "test_plt.png")
        try:
            plt.save(fig, out, validate=False, verbose=False)
            assert (tmp_path / "test_plt.png").exists(), "PNG not created by plt.save"
        finally:
            mplt.close("all")
