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
    _FALLBACK_HELP,
    _PEER_CLI_PROBES,
    CATEGORY_ORDER,
    DEPRECATED_ALIASES,
    _peer_cli_candidates,
    _peer_cli_present,
    _peer_installed,
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
    def test_known_peer_fallback_is_not_the_bare_name(self, sub):
        # Arrange
        table = _FALLBACK_HELP
        # Act
        help_text = table.get(sub, sub)
        # Assert
        assert help_text != sub

    def test_mounted_known_peer_help_is_not_the_bare_name(self):
        pytest.importorskip("scitex_dev")
        # Arrange
        subcommands = build_lazy_subcommands(_cli_dir())
        known = ["dataset", "git", "hpc", "newb", "datetime", "social", "tunnel"]
        # Act
        bare = [
            name
            for name in known
            if name in subcommands and subcommands[name][2] == name
        ]
        # Assert
        assert bare == []


class TestOnlyResolvablePeersAreAdvertised:
    """Unavailable peers are not listed, so no listed name resolves to nothing."""

    def test_uninstalled_peer_is_not_present(self):
        # Arrange
        candidates = _peer_cli_candidates("scitex_no_such_peer_for_probe")
        # Act
        present = _peer_cli_present(candidates)
        # Assert
        assert present is False

    def test_installed_package_without_cli_module_is_not_present(self):
        # Arrange
        candidates = _peer_cli_candidates("json")
        # Act
        present = _peer_cli_present(candidates)
        # Assert
        assert present is False

    def test_installed_peer_with_cli_module_is_present(self):
        pytest.importorskip("scitex_scholar")
        # Arrange
        candidates = _peer_cli_candidates("scitex_scholar")
        # Act
        present = _peer_cli_present(candidates)
        # Assert
        assert present is True

    def test_probe_does_not_execute_a_lazily_registered_peer(self, tmp_path):
        # Arrange: `import scitex` registers peers behind a LazyLoader; a probe
        # that touches `sys.modules[peer].__spec__` executes the peer body.
        import importlib.util
        import sys

        name = "scitex_lazy_probe_fixture"
        package = tmp_path / name
        (package / "_cli").mkdir(parents=True)
        (package / "__init__.py").write_text("raise RuntimeError('executed')\n")
        (package / "_cli" / "__init__.py").write_text("")
        (package / "_cli" / "_main.py").write_text("main = None\n")
        sys.path.insert(0, str(tmp_path))
        try:
            spec = importlib.util.find_spec(name)
            spec.loader = importlib.util.LazyLoader(spec.loader)
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            # Act
            present = _peer_cli_present(_peer_cli_candidates(name))
        finally:
            sys.modules.pop(name, None)
            sys.path.remove(str(tmp_path))
        # Assert
        assert present is True

    def test_uninstalled_peer_is_not_installed(self):
        # Arrange
        name = "scitex_no_such_peer_for_probe"
        # Act
        installed = _peer_installed(name)
        # Assert
        assert installed is False


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
            ("bundle", "Data & Sync"),
            ("mcp", "Service"),
            ("audit-security", "Diagnostics"),
            ("audit-tool", "Diagnostics"),
            ("introspection", "Introspection"),
            ("completion", "Shell"),
            ("install-shell-completion", "Shell"),
            ("print-shell-completion", "Shell"),
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
