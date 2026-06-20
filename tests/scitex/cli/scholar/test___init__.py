#!/usr/bin/env python3
"""Surface contract for ``scitex.cli.scholar``.

The scholar CLI package mounts the ``scholar`` click group and its
subcommands (``fetch``, ``library``, ``jobs``, ``gui``, …). These tests
pin the public surface and that ``scholar`` is a real click group with
mounted subcommands. No mocks — the click group is exercised directly.
"""

import click
import pytest

import scitex.cli.scholar as scholar_pkg

_EXPECTED_SUBCOMMANDS = ["fetch", "library", "jobs", "gui"]


def test_scholar_is_a_click_group():
    # Arrange
    group = scholar_pkg.scholar
    # Act
    is_group = isinstance(group, click.Group)
    # Assert
    assert is_group


def test_scholar_group_has_mounted_subcommands():
    # Arrange
    group = scholar_pkg.scholar
    # Act
    commands = group.commands
    # Assert
    assert len(commands) > 0


@pytest.mark.parametrize("name", _EXPECTED_SUBCOMMANDS)
def test_expected_subcommand_is_mounted(name):
    # Arrange
    group = scholar_pkg.scholar
    # Act
    present = name in group.commands
    # Assert
    assert present, f"scitex.cli.scholar is missing subcommand {name!r}"


# EOF
