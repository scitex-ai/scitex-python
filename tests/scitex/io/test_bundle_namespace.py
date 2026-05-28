#!/usr/bin/env python3
"""Integration contract for the umbrella-only ``scitex.io.bundle`` namespace.

``scitex.io.bundle`` is the umbrella's bundle-dispatcher facade — it
routes ``load`` / ``save`` / ``validate`` between umbrella-internal
plot, figure, stats, and image bundle kinds. figrecipe owns
``.plt.zip`` / ``.fig.zip`` directly; the umbrella surface is the
multi-kind front door layered on top.

These tests pin the contract callers depend on: the public dispatch
symbols are importable, the bundle-kind subpackage exists, and the
legacy ``.plot`` dict-API still routes through the umbrella's
internal kinds/_plot location (it was relocated in Step C of the
plt-deletion migration).
"""

import pytest

from scitex.io import bundle


@pytest.mark.parametrize(
    "name",
    [
        "load",
        "save",
        "validate",
        "BundleType",
        "Bundle",
    ],
)
def test_bundle_public_symbol_exposed(name):
    """The umbrella bundle facade exposes its dispatch surface."""
    # Arrange
    # Act
    attr = getattr(bundle, name, None)
    # Assert
    assert attr is not None


def test_kinds_subpackage_importable():
    """``scitex.io.bundle.kinds`` is a real subpackage, not a placeholder."""
    # Arrange
    # Act
    from scitex.io.bundle import kinds

    # Assert
    assert hasattr(kinds, "__path__")


def test_legacy_plot_dict_api_lives_in_umbrella_kinds_plot():
    """Step-C move: ``load_plot_bundle`` resolves at the umbrella-internal location."""
    # Arrange
    # Act
    from scitex.io.bundle.kinds._plot._legacy import load_plot_bundle

    # Assert
    assert callable(load_plot_bundle)


def test_legacy_plot_save_lives_in_umbrella_kinds_plot():
    """Step-C move: ``save_plot_bundle`` resolves at the umbrella-internal location."""
    # Arrange
    # Act
    from scitex.io.bundle.kinds._plot._legacy import save_plot_bundle

    # Assert
    assert callable(save_plot_bundle)


def test_overview_renderer_lives_in_umbrella_kinds_plot():
    """``generate_bundle_overview`` is umbrella-only (figrecipe has no overview)."""
    # Arrange
    # Act
    from scitex.io.bundle.kinds._plot._overview import generate_bundle_overview

    # Assert
    assert callable(generate_bundle_overview)
