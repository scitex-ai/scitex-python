#!/usr/bin/env python3
"""Surface contract for ``scitex.cli``.

The umbrella CLI package exposes the root ``cli`` click group plus the
recursive-help / JSON-introspection helpers (``group_to_json``,
``help_recursive_to_json``, ``print_help_recursive``). These tests pin the
public surface and that the root group is a real click group with mounted
subcommands. No mocks — the click group is exercised directly.
"""

import click
import pytest

import scitex.cli as cli_pkg

_EXPECTED_PUBLIC = [
    "cli",
    "main",
    "group_to_json",
    "help_recursive_to_json",
    "print_help_recursive",
    "format_python_signature",
]


@pytest.mark.parametrize("name", _EXPECTED_PUBLIC)
def test_public_attribute_present(name):
    # Arrange
    module = cli_pkg
    # Act
    present = hasattr(module, name)
    # Assert
    assert present, f"scitex.cli is missing public attribute {name!r}"


def test_cli_root_is_a_click_group():
    # Arrange
    root = cli_pkg.cli
    # Act
    is_group = isinstance(root, click.Group)
    # Assert
    assert is_group


def test_cli_root_has_mounted_subcommands():
    # Arrange
    root = cli_pkg.cli
    # Act
    commands = root.commands
    # Assert
    assert len(commands) > 0


# EOF
