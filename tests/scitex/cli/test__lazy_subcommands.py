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
        from scitex.cli.main import cli

        missing_targets = [
            target
            for alias, (target, _remove_in) in DEPRECATED_ALIASES.items()
            if alias in cli.commands
            and (target[0] if isinstance(target, tuple) else target) not in subcommands
        ]
        # Assert
        assert missing_targets == []

    def test_figure_cli_names_follow_shared_owned_eligibility(self):
        # A console declaration can still be a foreign, unowned alias target.
        from scitex_dev.cli_providers import list_cli_providers

        # Arrange
        subcommands = build_lazy_subcommands(_cli_dir())
        expected = {
            row.name
            for row in list_cli_providers()
            if row.distribution in {"figrecipe", "scitex-plt"}
            and row.status in {"declared", "legacy_unknown"}
        }
        # Act
        mounted = {"figrecipe", "plt"} & set(subcommands)
        # Assert
        assert mounted == expected


class TestScholarMetadata:
    """The exact installed console is authoritative; modules are never guessed."""

    def test_scholar_has_only_its_owned_canonical_target(self):
        # Arrange
        from importlib.metadata import distribution

        owner = distribution("scitex-scholar")
        (entry,) = (
            ep
            for ep in owner.entry_points
            if ep.group == "console_scripts" and ep.name == "scitex-scholar"
        )
        subcommands = build_lazy_subcommands(_cli_dir())
        # Act
        target, _attr, _help = subcommands["scholar"]
        # Assert
        assert (target.distribution, tuple(target)) == (
            "scitex-scholar",
            ((entry.module, entry.attr),),
        )


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

    @pytest.mark.parametrize("sub", ["dev", "sdk", "config", "social", "writer"])
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
    script = r"""
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
sdk_view=cli.get_command(click.Context(cli),"sdk")
actual=sdk_view.get_command(click.Context(sdk_view),component)
expected=sdk.get_command(click.Context(sdk),component)
runner=CliRunner()
left=runner.invoke(cli,['sdk',component,'--help'],prog_name='scitex')
right=runner.invoke(sdk,[component,'--help'],prog_name='scitex-sdk')
print(json.dumps({'same_sdk_group':actual is expected and expected is not None,
 'umbrella_help':left.exit_code==0 and 'Usage:' in left.output,
 'standalone_help':right.exit_code==0 and 'Usage:' in right.output,
 'retired_imports':[n for n in sys.modules if n.split('.')[0] in {'scitex_app','scitex_ui'}]}))
"""
    environment = dict(os.environ, SCITEX_DIR=str(tmp_path / "state"))
    # Act
    child = subprocess.run(
        [sys.executable, "-I", "-c", script, source_root, component],
        env=environment,
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
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


class TestDeclaredDatabaseEntrypoint:
    """The installed leaf's real console group is the umbrella group."""

    def test_database_group_identity(self):
        # Arrange
        import click
        from scitex_db.__main__ import main

        from scitex.cli.main import cli

        # Act
        mounted = cli.get_command(click.Context(cli), "db")
        # Assert
        assert mounted is main

    def test_database_help_uses_declared_group(self):
        # Arrange
        from click.testing import CliRunner

        from scitex.cli.main import cli

        # Act
        result = CliRunner().invoke(cli, ["db", "--help"])
        # Assert
        assert result.exit_code == 0, result.output


@pytest.fixture
def owned_console_provider(tmp_path):
    """Publish real, private installed metadata; never patch the metadata API."""
    import importlib
    import sys

    root = tmp_path / "installed"
    root.mkdir()
    package = root / "owned_cli_demo"
    package.mkdir()
    imported, called = tmp_path / "imported", tmp_path / "called"
    (package / "__init__.py").write_text(
        "from pathlib import Path\nimport click\n"
        f"Path({str(imported)!r}).touch()\n"
        "@click.group()\ndef command():\n"
        "    raise AssertionError('business callback must not execute')\n"
        "def function():\n"
        f"    Path({str(called)!r}).touch()\n"
    )
    metadata = root / "owned_cli_demo-1.0.dist-info"
    metadata.mkdir()
    (metadata / "METADATA").write_text(
        "Metadata-Version: 2.1\nName: owned-cli-demo\nVersion: 1.0\n"
    )
    (metadata / "RECORD").write_text("owned_cli_demo/__init__.py,,\n")
    entries = metadata / "entry_points.txt"
    sys.path.insert(0, str(root))
    importlib.invalidate_caches()
    try:
        yield entries, imported, called
    finally:
        sys.path.remove(str(root))
        sys.modules.pop("owned_cli_demo", None)
        importlib.invalidate_caches()


def test_owned_console_metadata_does_not_import_provider(owned_console_provider):
    # Arrange
    from scitex_dev.cli_providers import list_cli_providers

    entries, imported, _called = owned_console_provider
    entries.write_text("[scitex.cli]\ndemo = owned_cli_demo:command\n")
    # Act
    rows = list_cli_providers(path=[entries.parent.parent])
    candidates = tuple(
        tuple(row.target.split(":", 1)) for row in rows if row.status == "declared"
    )
    # Assert
    assert (candidates, imported.exists()) == ((("owned_cli_demo", "command"),), False)


@pytest.mark.parametrize(
    "declarations",
    [
        "demo = owned_cli_demo:command\ndemo = owned_cli_demo:function\n",
        "demo = foreign_provider:command\n",
        "demo = owned_cli_demo.bad-path:command\n",
    ],
)
def test_ambiguous_or_foreign_console_refused(owned_console_provider, declarations):
    # Arrange
    from scitex_dev.cli_providers import list_cli_providers

    entries, imported, _called = owned_console_provider
    entries.write_text("[scitex.cli]\n" + declarations)
    # Act
    rows = list_cli_providers(path=[entries.parent.parent])
    candidates = tuple(
        tuple(row.target.split(":", 1)) for row in rows if row.status == "declared"
    )
    # Assert
    assert (candidates, imported.exists()) == ((), False)


def test_plain_console_function_never_called(owned_console_provider):
    # Arrange
    import click
    from scitex_dev.cli_providers import list_cli_providers

    from scitex.cli.main import LazyGroup

    entries, _imported, called = owned_console_provider
    entries.write_text("[scitex.cli]\ndemo = owned_cli_demo:function\n")
    rows = list_cli_providers(path=[entries.parent.parent])
    candidates = tuple(
        tuple(row.target.split(":", 1)) for row in rows if row.status == "declared"
    )
    root = LazyGroup(name="control", lazy_subcommands={"demo": (candidates, "", "")})
    # Act
    result = root.get_command(click.Context(root), "demo")
    # Assert
    assert (result, called.exists()) == (None, False)


def test_owned_click_group_help_never_calls_callback(owned_console_provider):
    # Arrange
    from click.testing import CliRunner
    from scitex_dev.cli_providers import list_cli_providers

    from scitex.cli.main import LazyGroup

    entries, _imported, _called = owned_console_provider
    entries.write_text("[scitex.cli]\ndemo = owned_cli_demo:command\n")
    rows = list_cli_providers(path=[entries.parent.parent])
    candidates = tuple(
        tuple(row.target.split(":", 1)) for row in rows if row.status == "declared"
    )
    root = LazyGroup(name="control", lazy_subcommands={"demo": (candidates, "", "")})
    # Act
    result = CliRunner().invoke(root, ["demo", "--help"])
    # Assert
    assert result.exit_code == 0, result.output
