#!/usr/bin/env python3
"""Surface contract for ``scitex.helpers``.

The helpers package re-exports the env-loading, install-guidance, and
optional-dep utilities the umbrella relies on. These tests pin the public
``__all__`` so a future move that drops an export raises immediately. No
mocks — the import path is the contract under test.
"""

import importlib

import pytest

import scitex.helpers as helpers

_EXPECTED_PUBLIC = [
    "load_scitex_env",
    "require_module",
    "show_install_guide",
    "PACKAGE_TO_EXTRA",
    "check_optional_deps",
]


@pytest.mark.parametrize("name", _EXPECTED_PUBLIC)
def test_public_attribute_present(name):
    # Arrange
    module = helpers
    # Act
    present = hasattr(module, name)
    # Assert
    assert present, f"scitex.helpers is missing public attribute {name!r}"


def test_all_lists_the_public_surface():
    # Arrange
    expected = set(_EXPECTED_PUBLIC)
    # Act
    declared = set(helpers.__all__)
    # Assert
    assert expected == declared


def test_private_submodules_are_importable():
    # Arrange
    names = ["scitex.helpers._install_guide", "scitex.helpers._optional_deps"]
    # Act
    mods = [importlib.import_module(n) for n in names]
    # Assert
    assert all(m is not None for m in mods)


# EOF
