#!/usr/bin/env python3
"""Integration contract for the umbrella ``scitex.io.bundle`` re-export.

After the full bundle-subpackage migration, ``scitex.io.bundle`` is a
thin re-export of ``scitex_io.bundle``. The umbrella's contract is that
its dispatch facade (``load``, ``save``, ``validate``, ``Bundle``,
``BundleType``, …) and the kind handlers (image, text, shape, table
out of the box; figure / plot / stats when their domain packages are
installed) remain reachable through the historical import path.
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


def test_bundle_resolves_to_scitex_io_implementation():
    """``scitex.io.bundle`` is a re-export of ``scitex_io.bundle``."""
    # Arrange
    import scitex_io.bundle as standalone

    # Act
    same_bundle_class = bundle.Bundle is standalone.Bundle
    # Assert
    assert same_bundle_class is True


def test_bundle_load_is_re_export_from_scitex_io():
    """``scitex.io.bundle.load`` is the standalone's dispatcher."""
    # Arrange
    import scitex_io.bundle as standalone

    # Act
    same = bundle.load is standalone.load
    # Assert
    assert same is True


def test_kinds_subpackage_importable():
    """``scitex_io.bundle.kinds`` is a real subpackage."""
    # Arrange
    # Act
    from scitex_io.bundle import kinds

    # Assert
    assert hasattr(kinds, "__path__")
