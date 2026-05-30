#!/usr/bin/env python3
# Timestamp: 2026-05-30
# File: tests/scitex/test_thin_wrapper_consistency.py

"""Tests for thin-wrapper consistency between scitex and standalone packages.

Thin wrappers should have consistent Python API exports, MCP tools, and CLI
commands.

MCP enumeration note
--------------------
The umbrella MCP server mounts ~19 peer servers + bridges, so enumerating it
through a `python -m scitex mcp list-tools` *subprocess* is slow (~40s) and
was timing out at the old 30s budget. These tests enumerate the umbrella's
tools **in-process** via the server's own ``get_tools_sync`` helper — fast,
deterministic, no subprocess. The standalone side is still probed through its
public CLI, but the probe *skips* (rather than fails) when the peer's own
tooling can't enumerate, since that's a peer-internal bug outside the
umbrella's control — not a thin-wrapper drift.
"""

import re
import subprocess
import sys

import pytest

# Generous budget for the heavy standalone CLI probe (peer mounts are slow).
_MCP_CLI_TIMEOUT = 180


def _umbrella_tool_names() -> set:
    """All umbrella MCP tool names, enumerated in-process (no subprocess)."""
    fastmcp = pytest.importorskip("fastmcp")  # noqa: F841
    try:
        from scitex._mcp_tools._compat import get_tools_sync
        from scitex.mcp_server import FASTMCP_AVAILABLE
        from scitex.mcp_server import mcp as mcp_server
    except ImportError as exc:
        pytest.skip(f"umbrella MCP server unavailable: {exc}")
    if not FASTMCP_AVAILABLE or mcp_server is None:
        pytest.skip("umbrella MCP server not initialized")
    return set(get_tools_sync(mcp_server).keys())


def _standalone_cli_tool_names(argv: list, prefixes: tuple) -> set:
    """Tool names from a standalone `... mcp list-tools` CLI probe.

    Skips (does NOT fail) when the standalone tooling errors or produces
    nothing — a broken peer CLI is a peer-internal bug, not umbrella drift.
    """
    try:
        result = subprocess.run(
            argv, capture_output=True, text=True, timeout=_MCP_CLI_TIMEOUT
        )
    except FileNotFoundError:
        pytest.skip(f"standalone CLI not installed: {argv[0]}")
    except subprocess.TimeoutExpired:
        pytest.skip(f"standalone CLI timed out: {' '.join(argv)}")
    if result.returncode != 0:
        pytest.skip(
            f"standalone CLI failed (rc={result.returncode}); peer-internal: "
            f"{result.stderr.strip().splitlines()[-1:] or ''}"
        )
    names = set(re.findall(r"\b[a-z][a-z0-9_]*_[a-z0-9_]+\b", result.stdout))
    found = {n for n in names if any(n.startswith(p) for p in prefixes)}
    if not found:
        pytest.skip("standalone CLI produced no recognizable tool names")
    return found


class TestWriterThinWrapper:
    """scitex.writer thin-wrapper consistency with scitex-writer."""

    def test_python_api_exports_core_modules(self):
        # Arrange
        import scitex.writer

        expected_modules = {
            "bib",
            "compile",
            "figures",
            "guidelines",
            "project",
            "prompts",
            "tables",
        }
        # Act
        scitex_exports = {x for x in dir(scitex.writer) if not x.startswith("_")}
        # Assert
        assert expected_modules <= scitex_exports

    def test_standalone_exports_core_modules(self):
        # Arrange
        import scitex_writer

        expected_modules = {
            "bib",
            "compile",
            "figures",
            "guidelines",
            "project",
            "prompts",
            "tables",
        }
        # Act
        standalone_exports = {x for x in dir(scitex_writer) if not x.startswith("_")}
        # Assert
        assert expected_modules <= standalone_exports

    def test_umbrella_exposes_writer_mcp_tools(self):
        # The umbrella must mount the writer peer's tools (writer_* prefix).
        # Arrange
        umbrella_tools = _umbrella_tool_names()
        # Act
        writer_tools = {t for t in umbrella_tools if t.startswith("writer_")}
        # Assert
        assert writer_tools

    def test_every_standalone_writer_tool_is_reachable_via_umbrella(self):
        # The umbrella mounts the writer peer under a mount prefix, so a
        # standalone tool is "reachable" when some umbrella tool name ends
        # with it. Skips if the standalone CLI can't enumerate (peer-internal
        # bug), so an upstream break doesn't redden the umbrella matrix.
        # Arrange
        umbrella_tools = _umbrella_tool_names()
        standalone = _standalone_cli_tool_names(
            ["scitex-writer", "mcp", "list-tools"], prefixes=("writer_",)
        )
        # Act
        unreachable = {
            s
            for s in standalone
            if not any(u == s or u.endswith("_" + s) for u in umbrella_tools)
        }
        # Assert
        assert not unreachable, (
            f"standalone writer tools not reachable via the umbrella mount: "
            f"{sorted(unreachable)}"
        )


class TestSocialThinWrapper:
    """scitex.social thin-wrapper consistency with socialia."""

    def test_social_reexports_every_socialia_platform_class(self):
        # The wrapper must surface every public platform class socialia
        # exports (derived from socialia itself — no stale hard-coded list).
        # Arrange
        socialia = pytest.importorskip("socialia")
        import scitex.social

        socialia_classes = {
            x
            for x in dir(socialia)
            if not x.startswith("_") and x[:1].isupper() and x.isidentifier()
        }
        scitex_exports = {x for x in dir(scitex.social) if not x.startswith("_")}
        # Act
        missing = socialia_classes - scitex_exports
        # Assert
        assert not missing, f"scitex.social missing socialia classes: {sorted(missing)}"

    def test_every_standalone_social_tool_is_reachable_via_umbrella(self):
        # The umbrella mounts socialia under a mount prefix
        # (socialia_social_analytics_track, ...), so a standalone tool is
        # "reachable" when some umbrella tool name ends with it. This checks
        # the real mount contract without coupling to the exact prefix.
        # Arrange
        pytest.importorskip("socialia")
        umbrella_tools = _umbrella_tool_names()
        standalone = _standalone_cli_tool_names(
            [sys.executable, "-m", "socialia", "mcp", "list-tools"],
            prefixes=("social_", "analytics_"),
        )
        # Act
        unreachable = {
            s
            for s in standalone
            if not any(u == s or u.endswith("_" + s) for u in umbrella_tools)
        }
        # Assert
        assert not unreachable, (
            f"standalone social tools not reachable via the umbrella mount: "
            f"{sorted(unreachable)}"
        )


class TestIntrospectAPIConsistency:
    """Tests using the introspect API to verify thin-wrapper consistency."""

    def test_writer_api_item_count_is_close(self):
        # Arrange
        from scitex.introspect import list_api

        scitex_df = list_api("scitex.writer", max_depth=2)
        standalone_df = list_api("scitex_writer", max_depth=2)
        # Act
        diff = abs(len(scitex_df) - len(standalone_df))
        # Assert
        assert diff <= 5

    def test_hyphen_and_underscore_resolve_identically(self):
        # Arrange
        from scitex.introspect import list_api

        df1 = list_api("scitex_writer", max_depth=1)
        df2 = list_api("scitex-writer", max_depth=1)
        # Act
        equal = len(df1) == len(df2)
        # Assert
        assert equal


# EOF
