#!/usr/bin/env python3
"""FAIL-LOUD deprecation-shim tests for the umbrella ``scitex.gen`` surface.

``scitex.gen`` is no longer a re-export of the standalone ``scitex_gen``. It is
a deprecation shim: every attribute access raises ``AttributeError`` naming the
focused package the symbol moved to (no fallback, no proxy). These tests pin
that fail-loud contract with real imports — no mocks, no monkeypatch (STX-NM002).

AAA structure, one assertion per test (``pytest.raises(..., match=...)`` folds
the message check into the single assertion).
"""

from __future__ import annotations

import importlib

import pytest

import scitex as stx


def test_importing_gen_module_returns_the_umbrella_attribute():
    """Importing the shim is side-effect-free and yields the same object."""
    # Arrange
    expected = stx.gen
    # Act
    mod = importlib.import_module("scitex.gen")
    # Assert
    assert mod is expected


def test_gen_module_has_empty_public_surface():
    """The shim exports nothing publicly — every name fails loud on access."""
    # Arrange
    mod = stx.gen
    # Act
    public = mod.__all__
    # Assert
    assert public == []


def test_to_z_raises_attribute_error_naming_linalg():
    """``scitex.gen.to_z`` points migrants at scitex.linalg."""
    # Arrange
    mod = stx.gen
    # Act
    expectation = pytest.raises(AttributeError, match=r"scitex\.linalg")
    # Assert
    with expectation:
        _ = mod.to_z


def test_to_even_raises_attribute_error_naming_math():
    """``scitex.gen.to_even`` points migrants at scitex.math."""
    # Arrange
    mod = stx.gen
    # Act
    expectation = pytest.raises(AttributeError, match=r"scitex\.math")
    # Assert
    with expectation:
        _ = mod.to_even


def test_timestamper_raises_attribute_error_naming_datetime():
    """``scitex.gen.TimeStamper`` points migrants at scitex.datetime."""
    # Arrange
    mod = stx.gen
    # Act
    expectation = pytest.raises(AttributeError, match=r"scitex\.datetime")
    # Assert
    with expectation:
        _ = mod.TimeStamper


def test_dimhandler_raises_attribute_error_naming_linalg():
    """``scitex.gen.DimHandler`` points migrants at scitex.linalg."""
    # Arrange
    mod = stx.gen
    # Act
    expectation = pytest.raises(AttributeError, match=r"scitex\.linalg")
    # Assert
    with expectation:
        _ = mod.DimHandler


def test_mapped_symbol_message_states_deprecated_and_removed():
    """Mapped-symbol errors say the old name was deprecated AND removed."""
    # Arrange
    mod = stx.gen
    # Act
    expectation = pytest.raises(AttributeError, match=r"deprecated and removed")
    # Assert
    with expectation:
        _ = mod.to_z


def test_unmapped_name_raises_generic_fail_loud_error():
    """An unmapped attribute hits the generic retirement error, not a guess."""
    # Arrange
    mod = stx.gen
    # Act
    expectation = pytest.raises(AttributeError, match=r"deprecated and being retired")
    # Assert
    with expectation:
        _ = mod.some_symbol_that_was_never_mapped


def test_unmapped_name_message_lists_focused_packages():
    """The generic error enumerates the focused packages to look in."""
    # Arrange
    mod = stx.gen
    # Act
    expectation = pytest.raises(
        AttributeError,
        match=r"math/linalg/datetime/io/context/os/sh/str/introspect/stats",
    )
    # Assert
    with expectation:
        _ = mod.some_symbol_that_was_never_mapped


def test_gen_does_not_fall_back_to_standalone_scitex_gen():
    """The shim must NOT proxy to scitex_gen — to_z exists there but must fail
    on the umbrella surface (no fallback)."""
    # Arrange
    mod = stx.gen
    # Act
    expectation = pytest.raises(AttributeError)
    # Assert
    with expectation:
        _ = mod.to_z


# EOF
