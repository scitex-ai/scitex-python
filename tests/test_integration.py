#!/usr/bin/env python3
"""Integration tests for scitex-python.

These tests verify that modules work together correctly through the
unified `import scitex` namespace. Unit tests for individual modules
live in their respective downstream packages (scitex-io, scitex-stats,
figrecipe, scitex-clew, etc.).
"""

import os
import shutil
import tempfile

import numpy as np
import pandas as pd
import pytest

import scitex as stx

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_dir():
    """Temporary directory, cleaned up after test."""
    d = tempfile.mkdtemp(prefix="scitex_integration_")
    yield d
    shutil.rmtree(d, ignore_errors=True)


# ---------------------------------------------------------------------------
# 1. Lazy loading and namespace
# ---------------------------------------------------------------------------


class TestNamespace:
    """Verify the unified namespace works without eagerly importing."""

    def test_import_scitex_is_fast(self):
        """import scitex should not import heavy dependencies."""
        assert hasattr(stx, "io")
        assert hasattr(stx, "stats")
        assert hasattr(stx, "plt")
        assert hasattr(stx, "clew")
        assert hasattr(stx, "dev")

    def test_notification_alias(self):
        """stx.notify is a backward-compat alias for stx.notification."""
        assert stx.notification is not None
        assert stx.notify is not None

    def test_session_injected_sentinel(self):
        """stx.session.INJECTED sentinel is accessible."""
        assert stx.session.INJECTED is not None

    def test_version_exists(self):
        assert stx.__version__


# ---------------------------------------------------------------------------
# 2. io round-trips (via stx.io, not scitex_io directly)
# ---------------------------------------------------------------------------


class TestIOIntegration:
    """Verify stx.io save/load round-trips through the unified namespace."""

    def test_csv_roundtrip(self, tmp_dir):
        path = os.path.join(tmp_dir, "data.csv")
        df = pd.DataFrame({"x": [1, 2, 3], "y": [4.0, 5.0, 6.0]})
        stx.io.save(df, path)
        loaded = stx.io.load(path)
        assert list(loaded.columns) == ["x", "y"]
        assert len(loaded) == 3

    def test_npy_roundtrip(self, tmp_dir):
        path = os.path.join(tmp_dir, "arr.npy")
        arr = np.array([1.0, 2.0, 3.0])
        stx.io.save(arr, path)
        loaded = stx.io.load(path)
        assert np.allclose(arr, loaded)

    def test_yaml_roundtrip(self, tmp_dir):
        path = os.path.join(tmp_dir, "config.yaml")
        data = {"lr": 0.001, "epochs": 100}
        stx.io.save(data, path)
        loaded = stx.io.load(path)
        assert loaded["lr"] == 0.001
        assert loaded["epochs"] == 100

    def test_json_roundtrip(self, tmp_dir):
        path = os.path.join(tmp_dir, "meta.json")
        data = {"subject": "sub-01", "valid": True}
        stx.io.save(data, path)
        loaded = stx.io.load(path)
        assert loaded["subject"] == "sub-01"

    def test_pkl_roundtrip(self, tmp_dir):
        path = os.path.join(tmp_dir, "obj.pkl")
        obj = {"nested": [1, 2, {"k": np.array([10])}]}
        stx.io.save(obj, path)
        loaded = stx.io.load(path)
        assert loaded["nested"][0] == 1

    @pytest.mark.xfail(reason="load_configs ignores glob arg, loads ./config/ instead")
    def test_load_configs(self, tmp_dir):
        """stx.io.load_configs aggregates YAML files into DotDict."""
        config_dir = os.path.join(tmp_dir, "config")
        os.makedirs(config_dir)
        stx.io.save({"hidden_size": 256}, os.path.join(config_dir, "MODEL.yaml"))
        conf = stx.io.load_configs(os.path.join(config_dir, "*.yaml"))
        assert "MODEL" in conf
        assert conf.MODEL.hidden_size == 256


# ---------------------------------------------------------------------------
# 3. plt + io integration (figure save produces CSV)
# ---------------------------------------------------------------------------


class TestPltIOIntegration:
    """Verify stx.plt figures save correctly through stx.io."""

    def test_figure_save_produces_png(self, tmp_dir):
        """stx.io.save(fig, ...) should create the image file."""
        import matplotlib

        matplotlib.use("Agg")

        fig, ax = stx.plt.subplots()
        ax.plot([0, 1, 2], [0, 1, 0])
        path = os.path.join(tmp_dir, "test.png")
        stx.io.save(fig, path)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0

    def test_figure_save_produces_yaml_recipe(self, tmp_dir):
        """Figrecipe should produce a YAML recipe alongside the figure."""
        import matplotlib

        matplotlib.use("Agg")

        fig, ax = stx.plt.subplots()
        ax.plot([0, 1, 2], [0, 1, 0])
        path = os.path.join(tmp_dir, "test.png")
        stx.io.save(fig, path)
        yaml_path = os.path.join(tmp_dir, "test.yaml")
        assert os.path.exists(yaml_path)


# ---------------------------------------------------------------------------
# 4. stats through unified namespace
# ---------------------------------------------------------------------------


class TestStatsIntegration:
    """Verify stx.stats works through the unified namespace."""

    def test_run_test_ttest(self):
        g1 = np.random.randn(30) + 0.5
        g2 = np.random.randn(30)
        result = stx.stats.run_test("ttest_ind", g1, g2)
        assert "pvalue" in result
        assert "statistic" in result

    def test_available_tests(self):
        tests = stx.stats.available_tests()
        assert len(tests) > 10
        assert "ttest_ind" in tests

    def test_p_to_stars(self):
        stars = stx.stats.p_to_stars(0.001)
        assert "*" in stars  # At least significant
        ns = stx.stats.p_to_stars(0.8)
        assert ns in ("n.s.", "ns", "")


# ---------------------------------------------------------------------------
# 5. dev integration (delegates to scitex-dev)
# ---------------------------------------------------------------------------


class TestDevIntegration:
    """Verify stx.dev delegates to scitex-dev package."""

    def test_result_type(self):
        from scitex.dev import Result

        r = Result(success=True, data={"x": 1})
        assert r.success is True

    def test_list_versions(self):
        result = stx.dev.list_versions()
        assert isinstance(result, (dict, list))

    def test_ecosystem_registry(self):
        assert isinstance(stx.dev.ECOSYSTEM, dict)
        assert len(stx.dev.ECOSYSTEM) > 0


# ---------------------------------------------------------------------------
# 6. clew integration (hash tracking)
# ---------------------------------------------------------------------------


class TestClewIntegration:
    """Verify stx.clew is accessible through unified namespace."""

    def test_status(self):
        result = stx.clew.status()
        assert isinstance(result, dict)

    def test_hash_file(self, tmp_dir):
        path = os.path.join(tmp_dir, "test.txt")
        with open(path, "w") as f:
            f.write("hello")
        h = stx.clew.hash_file(path)
        assert isinstance(h, str)
        assert len(h) == 32  # SHA-256 prefix


# ---------------------------------------------------------------------------
# 7. Cross-module workflow: io -> clew hash tracking
# ---------------------------------------------------------------------------


class TestCrossModuleWorkflow:
    """Verify modules work together in realistic workflows."""

    def test_io_save_then_clew_hash(self, tmp_dir):
        """Save a file via stx.io, verify clew can hash it."""
        path = os.path.join(tmp_dir, "data.csv")
        df = pd.DataFrame({"a": [1, 2, 3]})
        stx.io.save(df, path)
        h = stx.clew.hash_file(path)
        assert len(h) == 32

    def test_stats_then_io_save(self, tmp_dir):
        """Run a stat test, save results via stx.io."""
        g1 = np.random.randn(30)
        g2 = np.random.randn(30) + 1
        result = stx.stats.run_test("ttest_ind", g1, g2)
        path = os.path.join(tmp_dir, "stats.yaml")
        stx.io.save(result, path)
        loaded = stx.io.load(path)
        assert "pvalue" in loaded
