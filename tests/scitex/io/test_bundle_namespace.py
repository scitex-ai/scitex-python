#!/usr/bin/env python3
"""Integration contract for the umbrella ``scitex.io.bundle`` re-export.

After the full bundle-subpackage migration, ``scitex.io.bundle`` is a
thin re-export of ``scitex_io.bundle``. The umbrella's contract is that
its dispatch facade (``load``, ``save``, ``validate``, ``Bundle``,
``BundleType``, …) and the kind handlers (image, text, shape, table
out of the box; figure / plot / stats when their domain packages are
installed) remain reachable through the historical import path.
"""

import importlib

import pytest


def _umbrella_bundle():
    """The umbrella's ``scitex.io.bundle`` re-export module.

    ``scitex.io.bundle`` is a thin re-export whose ``__file__`` is the
    standalone ``scitex_io/bundle/__init__.py``; it is a *distinct module
    object* from ``scitex_io.bundle`` (the umbrella loads it as its own
    sub-namespace), so the contract these tests pin is *provenance +
    reachability*, not cross-boundary object identity (which a sibling
    test's ``importlib.reload`` can churn)."""
    return importlib.import_module("scitex.io.bundle")


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
    bundle = _umbrella_bundle()
    # Act
    attr = getattr(bundle, name, None)
    # Assert
    assert attr is not None


def test_bundle_is_backed_by_the_scitex_io_implementation():
    """The umbrella bundle re-export is physically backed by ``scitex_io``.

    Provenance check (``__file__`` lives under the ``scitex_io`` package
    tree) rather than object identity — pollution-proof and still proves the
    umbrella isn't shipping a forked implementation.
    """
    # Arrange
    bundle = _umbrella_bundle()
    # Act
    backed_by_scitex_io = "scitex_io" in (getattr(bundle, "__file__", "") or "")
    # Assert
    assert backed_by_scitex_io is True


def test_bundle_load_is_defined_in_scitex_io():
    """``scitex.io.bundle.load`` is the scitex_io dispatcher (by provenance).

    The callable's defining source file lives under the ``scitex_io`` package
    tree, proving the load reached through the historical umbrella bundle path
    is the standalone's implementation — without a reload-fragile ``is``
    comparison (the umbrella re-export gives it a ``scitex.io.bundle.*``
    ``__module__`` but the code object still points at the scitex_io source).
    """
    # Arrange
    bundle = _umbrella_bundle()
    # Act
    source_file = getattr(getattr(bundle.load, "__code__", None), "co_filename", "")
    # Assert
    assert "scitex_io" in source_file


def test_kinds_subpackage_importable():
    """``scitex_io.bundle.kinds`` is a real subpackage."""
    # Arrange
    # Act
    from scitex_io.bundle import kinds

    # Assert
    assert hasattr(kinds, "__path__")
