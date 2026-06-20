#!/usr/bin/env python3
"""Integration contract for ``scitex.io.save`` end-to-end behaviour.

These tests cover the *umbrella* dispatch glue — they confirm that
``scitex.io.save`` and ``scitex.io.load`` route plain, common payloads
through the scitex_io registry plus the umbrella's path-handling and
session-tracking hooks, producing the expected on-disk artefact. Format
internals (CSV parsing, NPY layout, etc.) are the standalone packages'
responsibility and tested there.
"""

import numpy as np

import scitex.io as sio


def test_save_then_load_csv_roundtrip_via_umbrella(tmp_path):
    """A trivial DataFrame survives ``scitex.io.save`` → ``scitex.io.load``."""
    # Arrange
    pd = __import__("pandas")
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4.0, 5.0, 6.0]})
    target = tmp_path / "data.csv"
    # Act
    sio.save(df, str(target), verbose=False)
    loaded = sio.load(str(target))
    # Assert
    assert list(loaded.columns) == ["a", "b"]


def test_save_creates_the_target_file(tmp_path):
    """``save`` writes the target path the caller passed in."""
    # Arrange
    target = tmp_path / "vector.npy"
    arr = np.arange(4)
    # Act
    sio.save(arr, str(target), verbose=False)
    # Assert
    assert target.exists()


def test_load_returns_array_equal_to_what_was_saved(tmp_path):
    """A round-tripped NPY array equals the original element-wise."""
    # Arrange
    target = tmp_path / "vector.npy"
    arr = np.arange(4)
    sio.save(arr, str(target), verbose=False)
    # Act
    loaded = sio.load(str(target))
    # Assert
    assert np.array_equal(loaded, arr)


def test_save_makes_parent_directories_by_default(tmp_path):
    """The umbrella wrapper auto-creates intermediate directories."""
    # Arrange
    target = tmp_path / "nested" / "dir" / "data.json"
    payload = {"hello": "world"}
    # Act
    sio.save(payload, str(target), verbose=False)
    # Assert
    assert target.exists()
