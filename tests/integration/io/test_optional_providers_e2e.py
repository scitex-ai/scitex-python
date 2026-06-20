#!/usr/bin/env python3
"""End-to-end integration: ``scitex.io.save`` routes through optional providers.

These tests pin the ecosystem-wide synergy contract from the umbrella
side. ``scitex.io.save`` is the umbrella's clew/path-integrated wrapper
around ``scitex_io.save``. When figrecipe and scitex_stats are
installed, scitex_io's ``_optional_providers`` registry routes
``.plt.zip`` / ``.fig.zip`` to figrecipe and ``.stats.zip`` to
scitex_stats. From the umbrella caller's perspective this should "just
work" — one call to ``scitex.io.save`` and the right domain package
handles the I/O.

We exercise the *umbrella* side here. The provider-registration
mechanics are covered in scitex-io's own test suite; the per-package
bundle internals are covered in figrecipe/scitex-stats themselves.
"""

import pytest

import scitex.io as sio

figrecipe = pytest.importorskip("figrecipe", reason="figrecipe optional extra")
scitex_stats = pytest.importorskip("scitex_stats", reason="scitex_stats optional extra")


def test_umbrella_save_writes_plt_zip_via_figrecipe_provider(tmp_path):
    """``scitex.io.save(fig, '*.plt.zip')`` routes through figrecipe."""
    # Arrange: a minimal recorded figure figrecipe can serialise.
    fig, ax = figrecipe.subplots()
    ax.plot([1, 2, 3], [4, 5, 6])
    target = tmp_path / "panel.plt.zip"
    # Act
    sio.save(fig, str(target), verbose=False)
    # Assert
    assert target.exists()


def test_umbrella_save_writes_stats_zip_via_scitex_stats_provider(tmp_path):
    """``scitex.io.save(stats_dict, '*.stats.zip')`` routes through scitex_stats."""
    # Arrange: a minimal stats spec dict the bundle format accepts.
    payload = {
        "spec": {
            "schema": "scitex.stats.stats",
            "version": "1.0.0",
            "comparisons": [{"p_value": 0.04}],
        }
    }
    target = tmp_path / "results.stats.zip"
    # Act
    sio.save(payload, str(target), verbose=False)
    # Assert
    assert target.exists()


def test_umbrella_load_round_trips_stats_zip(tmp_path):
    """A ``.stats.zip`` round-trips through ``scitex.io.{save,load}`` with spec preserved."""
    # Arrange
    spec = {
        "schema": "scitex.stats.stats",
        "version": "1.0.0",
        "comparisons": [{"p_value": 0.04}],
    }
    target = tmp_path / "results.stats.zip"
    sio.save({"spec": spec}, str(target), verbose=False)
    # Act
    loaded = sio.load(str(target))
    # Assert
    assert loaded["spec"] == spec
