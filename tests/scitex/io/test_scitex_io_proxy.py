#!/usr/bin/env python3
"""Integration contract for ``scitex.io`` as a thin umbrella over ``scitex_io``.

The umbrella delegates core I/O to the standalone ``scitex_io`` package.
These tests pin the boundary: after the bundle decomposition the umbrella
is a *pure thin re-export* — registry-level helpers AND ``save`` / ``load``
share object identity with the standalone (the clew/path/session
integration now lives inside ``scitex_io`` itself).
"""

import pytest
import scitex_io

import scitex.io as sio


@pytest.mark.parametrize(
    "name",
    [
        # Registry helpers are pure re-exports.
        "register_loader",
        "register_saver",
        "get_loader",
        "get_saver",
        "list_formats",
        "glob",
        "cache",
        "configure_cache",
        "clear_load_cache",
    ],
)
def test_registry_helper_is_a_re_export(name):
    """Registry-level helpers must be the *same* object as scitex_io's."""
    # Arrange
    standalone = getattr(scitex_io, name)
    # Act
    umbrella = getattr(sio, name)
    # Assert
    assert umbrella is standalone


def test_load_configs_is_re_export_from_scitex_io():
    """``load_configs`` is umbrella-exposed but its implementation lives in scitex_io."""
    # Arrange
    standalone = scitex_io.load_configs
    # Act
    umbrella = sio.load_configs
    # Assert
    assert umbrella is standalone


def test_save_is_the_scitex_io_save():
    """``scitex.io.save`` is a pure re-export of ``scitex_io.save``.

    Post-decomposition the clew/path/session integration lives inside
    ``scitex_io``, so the umbrella shares object identity with it.
    """
    # Arrange
    standalone_save = scitex_io.save
    # Act
    umbrella_save = sio.save
    # Assert
    assert umbrella_save is standalone_save


def test_load_is_the_scitex_io_load():
    """``scitex.io.load`` is a pure re-export of ``scitex_io.load``."""
    # Arrange
    standalone_load = scitex_io.load
    # Act
    umbrella_load = sio.load
    # Assert
    assert umbrella_load is standalone_load
