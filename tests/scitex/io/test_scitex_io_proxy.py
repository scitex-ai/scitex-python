#!/usr/bin/env python3
"""Integration contract for ``scitex.io`` as a thin umbrella over ``scitex_io``.

The umbrella delegates core I/O to the standalone ``scitex_io`` package.
These tests pin the boundary: registry-level helpers are re-exports
(same identity as the standalone), while ``save`` and ``load`` are
deliberately *umbrella wrappers* (different identity — they add the
clew/path/session integration that doesn't belong in standalone).
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


def test_save_is_not_the_scitex_io_save():
    """``scitex.io.save`` is the umbrella's clew/path/session-integrated wrapper."""
    # Arrange
    standalone_save = getattr(scitex_io, "save", None)
    # Act
    umbrella_save = sio.save
    # Assert
    assert umbrella_save is not standalone_save


def test_load_is_not_the_scitex_io_load():
    """``scitex.io.load`` is the umbrella's wrapper, with its own added behaviour."""
    # Arrange
    standalone_load = getattr(scitex_io, "load", None)
    # Act
    umbrella_load = sio.load
    # Assert
    assert umbrella_load is not standalone_load
