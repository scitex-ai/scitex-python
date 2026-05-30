#!/usr/bin/env python3
"""Surface contract for ``scitex.io``.

The umbrella module is a thin re-export of scitex_io (``save`` / ``load``
are the same objects as the standalone after the bundle decomposition),
plus the ``bundle`` submodule and ``load_configs``. These tests pin the
public surface so a future refactor that drops an export raises
immediately, not in a downstream project.
"""

import pytest

import scitex.io as sio


@pytest.mark.parametrize(
    "name",
    [
        # Primary umbrella wrappers.
        "save",
        "load",
        # Umbrella-specific.
        "bundle",
        "load_configs",
        # Re-exported registry / utility surface from scitex_io.
        "glob",
        "reload",
        "flush",
        "cache",
        "register_loader",
        "register_saver",
        "get_loader",
        "get_saver",
        "list_formats",
    ],
)
def test_public_attribute_present(name):
    """Each declared umbrella export is reachable as ``scitex.io.<name>``."""
    # Arrange: ``bundle`` is a submodule — only bound as an attribute once it
    # has been imported (a sibling test can leave it unimported), so import it
    # explicitly here instead of relying on import order.
    if name == "bundle":
        import importlib

        importlib.import_module("scitex.io.bundle")
    # Act
    attr = getattr(sio, name, None)
    # Assert
    assert attr is not None


def test_save_is_a_pure_reexport_of_scitex_io_save():
    """``scitex.io.save`` is the bare ``scitex_io.save``.

    After the bundle decomposition, the clew/path/session integration moved
    *into* ``scitex_io`` itself, so the umbrella is now a pure thin
    re-export (same object identity) rather than a distinct wrapper.
    """
    # Arrange
    import scitex_io

    # Act
    same_function = sio.save is scitex_io.save
    # Assert
    assert same_function is True


def test_load_is_a_pure_reexport_of_scitex_io_load():
    """``scitex.io.load`` is the bare ``scitex_io.load`` (pure thin re-export)."""
    # Arrange
    import scitex_io

    # Act
    same_function = sio.load is scitex_io.load
    # Assert
    assert same_function is True


def test_bundle_submodule_is_a_package():
    """``scitex.io.bundle`` is an importable package, not a placeholder."""
    # Arrange
    # Act
    bundle = sio.bundle
    # Assert
    assert hasattr(bundle, "__path__")
