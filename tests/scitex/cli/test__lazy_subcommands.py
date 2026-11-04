#!/usr/bin/env python3
# File: ./tests/scitex/cli/test__lazy_subcommands.py

"""Tests for the registry-driven lazy-subcommand builder.

CLI-standardization slice 5 contract:
- retired duplicate namespaces (notify/verify/events/socialia) are never
  registered as lazy subcommands,
- the scitex-scholar entry point shape (``_cli_main:cli``) is probed,
- fallback one-liners exist so root help never degrades to the bare
  subcommand name for known peers,
- every mounted name maps to a canonical §4a help category (the `Other`
  catch-all stays empty).

No mocks (ecosystem no-mock policy): assertions run against the real
builder output for the current environment.
"""

import os

import pytest

from scitex.cli._lazy_subcommands import (
    CATEGORY_ORDER,
    DEPRECATED_ALIASES,
    _PEER_CLI_PROBES,
    build_lazy_subcommands,
    command_category,
)


def _cli_dir() -> str:
    """Resolve the package's cli dir (works for editable + site-packages)."""
    import scitex.cli

    return os.path.dirname(scitex.cli.__file__)


class TestDeprecatedAliasExclusion:
    """Retired duplicates never appear as lazy subcommands."""

    def test_retired_alias_names_are_not_registered(self):
        # Arrange
        subcommands = build_lazy_subcommands(_cli_dir())
        # Act
        leaked = [name for name in DEPRECATED_ALIASES if name in subcommands]
        # Assert
        assert leaked == []

    def test_every_alias_target_is_a_mounted_canonical_name(self):
        # Arrange
        subcommands = build_lazy_subcommands(_cli_dir())
        # Act
        missing_targets = [
            target
            for target, _remove_in in DEPRECATED_ALIASES.values()
            if target not in subcommands
        ]
        # Assert
        assert missing_targets == []

    def test_figrecipe_and_plt_documented_alias_pair_stays_mounted(self):
        # plt is a documented identity-alias package, NOT a retired duplicate.
        pytest.importorskip("scitex_dev")
        # Arrange
        subcommands = build_lazy_subcommands(_cli_dir())
        # Act
        mounted = {"figrecipe", "plt"} & set(subcommands)
        # Assert
        assert mounted == {"figrecipe", "plt"}


class TestScholarProbe:
    """scitex-scholar's entry point shape is probed."""

    def test_probe_table_includes_scholar_cli_main_shape(self):
        # Arrange
        probes = _PEER_CLI_PROBES
        # Act
        matches = [probe for probe in probes if probe == ("_cli_main", "cli")]
        # Assert
        assert matches == [("_cli_main", "cli")]

    def test_scholar_candidates_include_standalone_entry_point(self):
        pytest.importorskip("scitex_dev")
        # Arrange
        subcommands = build_lazy_subcommands(_cli_dir())
        # Act
        candidates, _attr, _help = subcommands["scholar"]
        # Assert
        assert ("scitex_scholar._cli_main", "cli") in tuple(candidates)


class TestWriterOverride:
    """The writer wrapper file overrides the (broken) generic probes."""

    def test_writer_is_registered_via_wrapper_module(self):
        pytest.importorskip("scitex_dev")
        # Arrange
        subcommands = build_lazy_subcommands(_cli_dir())
        # Act
        module_path, _attr, _help = subcommands["writer"]
        # Assert
        assert module_path == "scitex.cli.writer"


class TestFallbackHelp:
    """Root help one-liners never degrade to the bare subcommand name."""

    @pytest.mark.parametrize(
        "sub", ["dataset", "git", "hpc", "newb", "datetime", "social", "tunnel"]
    )
    def test_known_peer_help_is_not_the_bare_name(self, sub):
        pytest.importorskip("scitex_dev")
        # Arrange
        subcommands = build_lazy_subcommands(_cli_dir())
        # Act
        _path, _attr, help_text = subcommands[sub]
        # Assert
        assert help_text != sub


class TestCommandCategories:
    """§4a fixed ordered categories; `Other` stays empty."""

    def test_category_order_matches_doctrine_4a(self):
        # Arrange
        expected = (
            "Core",
            "Data & Sync",
            "Service",
            "Diagnostics",
            "Introspection",
            "Shell",
            "Other",
        )
        # Act
        actual = CATEGORY_ORDER
        # Assert
        assert actual == expected

    @pytest.mark.parametrize(
        "name,expected",
        [
            ("io", "Core"),
            ("convert", "Data & Sync"),
            ("mcp", "Service"),
            ("audit", "Diagnostics"),
            ("introspect", "Introspection"),
            ("completion", "Shell"),
        ],
    )
    def test_representative_command_maps_to_expected_category(self, name, expected):
        # Arrange
        subcommand_name = name
        # Act
        category = command_category(subcommand_name)
        # Assert
        assert category == expected

    def test_no_mounted_name_falls_into_other_category(self):
        # Arrange
        subcommands = build_lazy_subcommands(_cli_dir())
        # Act
        uncategorized = [
            name
            for name in subcommands
            if command_category(name) not in CATEGORY_ORDER[:-1]
        ]
        # Assert
        assert uncategorized == []


# EOF


@pytest.mark.parametrize("component", ["app", "ui"])
def test_sdk_component_alias_uses_actual_sdk_group_offline(tmp_path, component):
    """Aliases retain the SDK's composed groups without retired imports."""
    # Arrange
    import json
    import subprocess
    import sys
    from pathlib import Path

    import scitex

    source_root = str(Path(scitex.__file__).resolve().parents[1])
    script = r'''
import sys,json
sys.path.insert(0,sys.argv[1])
def guard(event,args):
    if event=='import' and args[0].split('.')[0] in {'scitex_app','scitex_ui'}:
        raise RuntimeError('retired imports are forbidden')
    if event in {'socket.bind','socket.connect','socket.getaddrinfo'}:
        raise RuntimeError('help must stay offline')
sys.addaudithook(guard)
import click
from click.testing import CliRunner
from scitex.cli import cli
from scitex_sdk.cli import main as sdk
component=sys.argv[2]
actual=cli.get_command(click.Context(cli),component)
expected=sdk.get_command(click.Context(sdk),component)
runner=CliRunner()
left=runner.invoke(cli,[component,'--help'],prog_name='scitex')
right=runner.invoke(sdk,[component,'--help'],prog_name='scitex-sdk')
print(json.dumps({'same_sdk_group':actual is expected and expected is not None,
 'umbrella_help':left.exit_code==0 and 'Usage:' in left.output,
 'standalone_help':right.exit_code==0 and 'Usage:' in right.output,
 'retired_imports':[n for n in sys.modules if n.split('.')[0] in {'scitex_app','scitex_ui'}]}))
'''
    environment = dict(os.environ, SCITEX_DIR=str(tmp_path / "state"))
    # Act
    child = subprocess.run(
        [sys.executable, "-I", "-c", script, source_root, component],
        env=environment, capture_output=True, text=True, check=True, timeout=30,
    )
    result = json.loads(child.stdout)
    # Assert
    assert result == {
        "same_sdk_group": True,
        "umbrella_help": True,
        "standalone_help": True,
        "retired_imports": [],
    }


def test_unknown_sdk_component_does_not_fall_back_to_sdk_root():
    """A nonexistent child never exposes a different root command tree."""
    # Arrange
    import click
    from scitex.cli.main import LazyGroup

    root = LazyGroup(
        name="owned-control",
        lazy_subcommands={
            "missing": ((("scitex_sdk.cli", "main::missing-component"),), "unused", "")
        },
    )
    # Act
    actual = root.get_command(click.Context(root), "missing")
    # Assert
    assert actual is None
