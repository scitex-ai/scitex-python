#!/usr/bin/env python3
"""Surface contract for ``scitex.io``.

The umbrella module re-exports scitex_io plus a few umbrella-specific
additions (``save`` / ``load`` wrappers, ``bundle`` submodule,
``load_configs``). These tests pin the public surface so a future
refactor that drops an export raises immediately, not in a downstream
project.
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
    # Arrange
    # Act
    attr = getattr(sio, name, None)
    # Assert
    assert attr is not None


def test_save_is_umbrella_wrapper_not_scitex_io_save():
    """``scitex.io.save`` is the umbrella's clew/path-integrated wrapper, not the bare scitex_io.save."""
    # Arrange
    import scitex_io

    # Act
    same_function = sio.save is getattr(scitex_io, "save", object())
    # Assert
    assert same_function is False


def test_load_is_umbrella_wrapper_not_scitex_io_load():
    """``scitex.io.load`` is the umbrella's wrapper, not the bare scitex_io.load."""
    # Arrange
    import scitex_io

    # Act
    same_function = sio.load is getattr(scitex_io, "load", object())
    # Assert
    assert same_function is False


def test_bundle_submodule_is_a_package():
    """``scitex.io.bundle`` is an importable package, not a placeholder."""
    # Arrange
    # Act
    bundle = sio.bundle
    # Assert
    assert hasattr(bundle, "__path__")
