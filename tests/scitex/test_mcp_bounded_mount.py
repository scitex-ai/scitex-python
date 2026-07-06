#!/usr/bin/env python3
# Timestamp: 2026-07-07
# File: tests/scitex/test_mcp_bounded_mount.py
"""Bounded, non-blocking per-peer mount for the umbrella MCP aggregator.

The single ``scitex serve`` aggregator fronts ~33 packages' MCP tools by
importing each peer's ``_mcp_server`` and mounting its FastMCP instance. If
ONE peer's import HANGS at init (real case: scitex-todo's store-wedge stalls
20s+ at mcp-start), a naive sequential resolve blocks the whole aggregator
load and darkens EVERY peer's tools — the failure concentrates 33x.

These tests prove the hardening: each peer's resolve runs in a bounded daemon
thread, so a hung peer degrades to "that peer's tools missing" and never to
"aggregator hangs". Real fixture peers (packages written to disk + imported)
are driven through the real code path via the injectable ``iter_registry`` /
``peer_timeout`` parameters — no mocks, no ``monkeypatch``.
"""

from __future__ import annotations

import logging
import os
import sys
import textwrap
from collections import namedtuple
from pathlib import Path
from time import monotonic
from types import SimpleNamespace

import pytest

fastmcp = pytest.importorskip("fastmcp")

from scitex import _mcp as umbrella  # noqa: E402

# --------------------------------------------------------------------------- #
# Fixture-peer bodies (written to disk, imported for real).
# --------------------------------------------------------------------------- #

_FAST_PEER = """
from fastmcp import FastMCP

mcp = FastMCP(name="{name}")


@mcp.tool()
def ping() -> str:
    return "pong"
"""

_HUNG_PEER = """
# Simulates a peer whose _mcp_server import wedges at init (store-wedge etc.).
import time

time.sleep(30)

from fastmcp import FastMCP  # never reached within the resolve budget

mcp = FastMCP(name="{name}")
"""

_INFINITE_PEER = """
# Simulates the REAL store-wedge shape: an import that blocks INDEFINITELY on a
# lock/IO (here an Event that is never set), not a bounded sleep. The bounded
# resolve must still return promptly and skip this peer.
import threading

threading.Event().wait()

from fastmcp import FastMCP  # never reached

mcp = FastMCP(name="{name}")
"""

_RAISING_PEER = """
raise ImportError("{name}: simulated precondition failure at import")
"""

_EXITING_PEER = """
# SystemExit is a BaseException; it must be caught and treated as a skip,
# never allowed to kill the aggregator.
import sys

sys.exit(3)
"""


class _ListHandler(logging.Handler):
    """Hand-rolled log sink — collects records so tests can assert on them."""

    def __init__(self, records: list) -> None:
        super().__init__()
        self._records = records

    def emit(self, record: logging.LogRecord) -> None:
        self._records.append(record)


def _write_peer(root: Path, name: str, body_template: str) -> None:
    pkg = root / name
    pkg.mkdir()
    (pkg / "__init__.py").write_text("")
    (pkg / "_mcp_server.py").write_text(
        textwrap.dedent(body_template).format(name=name)
    )


def _purge_modules(*names: str) -> None:
    for name in names:
        for mod in list(sys.modules):
            if mod == name or mod.startswith(name + "."):
                del sys.modules[mod]


_Resolve = namedtuple("_Resolve", "elapsed resolved skipped")


# --------------------------------------------------------------------------- #
# _resolve_peers_bounded — the primitive that must never hang.
#   Fixture runs the bounded resolve ONCE; each test asserts one fact.
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="module")
def bounded_resolve(tmp_path_factory):
    root = tmp_path_factory.mktemp("bounded_resolve")
    _write_peer(root, "bmfastpeer", _FAST_PEER)
    _write_peer(root, "bmhungpeer", _HUNG_PEER)
    sys.path.insert(0, str(root))
    try:
        peers = [("bmfastpeer", "fastns"), ("bmhungpeer", "hungns")]
        start = monotonic()
        resolved, skipped = umbrella._resolve_peers_bounded(peers, 1.0)
        elapsed = monotonic() - start
        yield _Resolve(elapsed, dict(resolved), dict(skipped))
    finally:
        sys.path.remove(str(root))
        _purge_modules("bmfastpeer", "bmhungpeer")


def test_bounded_resolve_does_not_hang(bounded_resolve):
    # Arrange
    outcome = bounded_resolve
    # Act
    elapsed = outcome.elapsed
    # Assert — bounded by ~timeout (1s), nowhere near the hung peer's 30s sleep.
    assert elapsed < 6.0


def test_bounded_resolve_reports_hung_peer_skipped(bounded_resolve):
    # Arrange
    outcome = bounded_resolve
    # Act
    skipped = outcome.skipped
    # Assert
    assert "hungns" in skipped


def test_bounded_resolve_hung_reason_is_timeout(bounded_resolve):
    # Arrange
    outcome = bounded_resolve
    # Act
    reason = outcome.skipped.get("hungns", "")
    # Assert
    assert "timed out" in reason


def test_bounded_resolve_keeps_fast_peer(bounded_resolve):
    # Arrange
    outcome = bounded_resolve
    # Act
    resolved = outcome.resolved
    # Assert
    assert "fastns" in resolved


def test_bounded_resolve_fast_peer_is_a_fastmcp(bounded_resolve):
    # Arrange
    outcome = bounded_resolve
    # Act
    peer = outcome.resolved.get("fastns")
    # Assert
    assert isinstance(peer, fastmcp.FastMCP)


def test_bounded_resolve_hung_peer_not_resolved(bounded_resolve):
    # Arrange
    outcome = bounded_resolve
    # Act
    resolved = outcome.resolved
    # Assert
    assert "hungns" not in resolved


# --------------------------------------------------------------------------- #
# A peer that ImportErrors at import resolves to None -> silently absent.
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="module")
def resolve_with_raising_peer(tmp_path_factory):
    root = tmp_path_factory.mktemp("resolve_raising")
    _write_peer(root, "bmraisepeer", _RAISING_PEER)
    _write_peer(root, "bmfastpeer2", _FAST_PEER)
    sys.path.insert(0, str(root))
    try:
        peers = [("bmraisepeer", "raisens"), ("bmfastpeer2", "fastns2")]
        resolved, skipped = umbrella._resolve_peers_bounded(peers, 5.0)
        yield SimpleNamespace(resolved=dict(resolved), skipped=dict(skipped))
    finally:
        sys.path.remove(str(root))
        _purge_modules("bmraisepeer", "bmfastpeer2")


def test_raising_peer_absent_from_resolved(resolve_with_raising_peer):
    # Arrange
    outcome = resolve_with_raising_peer
    # Act
    resolved = outcome.resolved
    # Assert
    assert "raisens" not in resolved


def test_raising_peer_does_not_block_fast_peer(resolve_with_raising_peer):
    # Arrange
    outcome = resolve_with_raising_peer
    # Act
    resolved = outcome.resolved
    # Assert
    assert "fastns2" in resolved


# --------------------------------------------------------------------------- #
# A peer that sys.exit()s at import (SystemExit is BaseException) is skipped.
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="module")
def resolve_with_exiting_peer(tmp_path_factory):
    root = tmp_path_factory.mktemp("resolve_exiting")
    _write_peer(root, "bmexitpeer", _EXITING_PEER)
    _write_peer(root, "bmfastpeer3", _FAST_PEER)
    sys.path.insert(0, str(root))
    try:
        peers = [("bmexitpeer", "exitns"), ("bmfastpeer3", "fastns3")]
        resolved, skipped = umbrella._resolve_peers_bounded(peers, 5.0)
        yield SimpleNamespace(resolved=dict(resolved), skipped=dict(skipped))
    finally:
        sys.path.remove(str(root))
        _purge_modules("bmexitpeer", "bmfastpeer3")


def test_exiting_peer_absent_from_resolved(resolve_with_exiting_peer):
    # Arrange
    outcome = resolve_with_exiting_peer
    # Act
    resolved = outcome.resolved
    # Assert
    assert "exitns" not in resolved


def test_exiting_peer_does_not_block_fast_peer(resolve_with_exiting_peer):
    # Arrange
    outcome = resolve_with_exiting_peer
    # Act
    resolved = outcome.resolved
    # Assert
    assert "fastns3" in resolved


# --------------------------------------------------------------------------- #
# A peer whose import blocks INDEFINITELY (Event.wait, never set) — the real
# store-wedge shape — must still be bounded + skipped, not hang forever.
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="module")
def resolve_with_infinite_peer(tmp_path_factory):
    root = tmp_path_factory.mktemp("resolve_infinite")
    _write_peer(root, "bminfpeer", _INFINITE_PEER)
    _write_peer(root, "bmfastpeer4", _FAST_PEER)
    sys.path.insert(0, str(root))
    try:
        # Fast peer first, then the infinite one — proves the wedged peer is
        # abandoned after the budget and never blocks the run.
        peers = [("bmfastpeer4", "fastns4"), ("bminfpeer", "infns")]
        start = monotonic()
        resolved, skipped = umbrella._resolve_peers_bounded(peers, 1.0)
        elapsed = monotonic() - start
        yield SimpleNamespace(
            elapsed=elapsed, resolved=dict(resolved), skipped=dict(skipped)
        )
    finally:
        sys.path.remove(str(root))
        _purge_modules("bminfpeer", "bmfastpeer4")


def test_infinite_peer_does_not_hang(resolve_with_infinite_peer):
    # Arrange
    outcome = resolve_with_infinite_peer
    # Act
    elapsed = outcome.elapsed
    # Assert — bounded by ~timeout (1s) even though the import never returns.
    assert elapsed < 6.0


def test_infinite_peer_is_skipped(resolve_with_infinite_peer):
    # Arrange
    outcome = resolve_with_infinite_peer
    # Act
    skipped = outcome.skipped
    # Assert
    assert "infns" in skipped


def test_infinite_peer_does_not_block_fast_peer(resolve_with_infinite_peer):
    # Arrange
    outcome = resolve_with_infinite_peer
    # Act
    resolved = outcome.resolved
    # Assert
    assert "fastns4" in resolved


# --------------------------------------------------------------------------- #
# register_all_tools — full path, hung peer injected via iter_registry.
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="module")
def register_outcome(tmp_path_factory):
    from scitex._mcp import mounted_namespaces

    root = tmp_path_factory.mktemp("register_bounded")
    _write_peer(root, "regfastpeer", _FAST_PEER)
    _write_peer(root, "reghungpeer", _HUNG_PEER)
    sys.path.insert(0, str(root))

    records: list = []
    handler = _ListHandler(records)
    lg = logging.getLogger(umbrella.__name__)
    lg.addHandler(handler)
    prev_level = lg.level
    lg.setLevel(logging.WARNING)

    def fake_iter_registry():
        yield ("regfast-pip", "regfastpeer", "regfastns")
        yield ("reghung-pip", "reghungpeer", "reghungns")

    probe = fastmcp.FastMCP(name="probe-bounded")
    try:
        start = monotonic()
        umbrella.register_all_tools(
            probe, iter_registry=fake_iter_registry, peer_timeout=1.0
        )
        elapsed = monotonic() - start
        warnings_text = "\n".join(
            r.getMessage() for r in records if r.levelno >= logging.WARNING
        )
        yield SimpleNamespace(
            elapsed=elapsed,
            prefixes=mounted_namespaces(probe),
            warnings=warnings_text,
        )
    finally:
        lg.removeHandler(handler)
        lg.setLevel(prev_level)
        sys.path.remove(str(root))
        _purge_modules("regfastpeer", "reghungpeer")


def test_register_all_tools_does_not_hang(register_outcome):
    # Arrange
    outcome = register_outcome
    # Act
    elapsed = outcome.elapsed
    # Assert — without the fix a 30s-sleep peer would make this ~30s+.
    assert elapsed < 20.0


def test_register_all_tools_skips_hung_peer(register_outcome):
    # Arrange
    outcome = register_outcome
    # Act
    prefixes = outcome.prefixes
    # Assert
    assert "reghungns" not in prefixes


def test_register_all_tools_mounts_fast_peer(register_outcome):
    # Arrange
    outcome = register_outcome
    # Act
    prefixes = outcome.prefixes
    # Assert
    assert "regfastns" in prefixes


def test_register_all_tools_warns_naming_hung_peer(register_outcome):
    # Arrange
    outcome = register_outcome
    # Act
    warnings_text = outcome.warnings
    # Assert
    assert "reghungns" in warnings_text


def test_register_all_tools_warning_marks_unavailable(register_outcome):
    # Arrange
    outcome = register_outcome
    # Act
    warnings_text = outcome.warnings
    # Assert
    assert "unavailable" in warnings_text


# --------------------------------------------------------------------------- #
# SCITEX_MCP_USE_<NS>=0 env gate is preserved.
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="module")
def gate_outcome(tmp_path_factory):
    from scitex._mcp import mounted_namespaces

    root = tmp_path_factory.mktemp("gate_bounded")
    _write_peer(root, "gatefastA", _FAST_PEER)
    _write_peer(root, "gatefastB", _FAST_PEER)
    sys.path.insert(0, str(root))

    prev = os.environ.get("SCITEX_MCP_USE_GATENSB")
    os.environ["SCITEX_MCP_USE_GATENSB"] = "0"

    def fake_iter_registry():
        yield ("gateA-pip", "gatefastA", "gatensA")
        yield ("gateB-pip", "gatefastB", "gatensB")

    probe = fastmcp.FastMCP(name="probe-gate")
    try:
        umbrella.register_all_tools(
            probe, iter_registry=fake_iter_registry, peer_timeout=5.0
        )
        yield mounted_namespaces(probe)
    finally:
        if prev is None:
            os.environ.pop("SCITEX_MCP_USE_GATENSB", None)
        else:
            os.environ["SCITEX_MCP_USE_GATENSB"] = prev
        sys.path.remove(str(root))
        _purge_modules("gatefastA", "gatefastB")


def test_env_gate_keeps_enabled_peer(gate_outcome):
    # Arrange
    prefixes = gate_outcome
    # Act
    is_mounted = "gatensA" in prefixes
    # Assert
    assert is_mounted is True


def test_env_gate_drops_disabled_peer(gate_outcome):
    # Arrange
    prefixes = gate_outcome
    # Act
    is_mounted = "gatensB" in prefixes
    # Assert
    assert is_mounted is False


# --------------------------------------------------------------------------- #
# _peer_timeout — env-var parsing.
# --------------------------------------------------------------------------- #


@pytest.fixture
def peer_timeout_env():
    """Set/restore the real SCITEX_MCP_PEER_TIMEOUT env var (no monkeypatch)."""
    saved = os.environ.get("SCITEX_MCP_PEER_TIMEOUT")

    def _set(value):
        if value is None:
            os.environ.pop("SCITEX_MCP_PEER_TIMEOUT", None)
        else:
            os.environ["SCITEX_MCP_PEER_TIMEOUT"] = value

    yield _set

    if saved is None:
        os.environ.pop("SCITEX_MCP_PEER_TIMEOUT", None)
    else:
        os.environ["SCITEX_MCP_PEER_TIMEOUT"] = saved


def test_peer_timeout_default(peer_timeout_env):
    # Arrange
    peer_timeout_env(None)
    # Act
    value = umbrella._peer_timeout()
    # Assert
    assert value == umbrella._DEFAULT_PEER_TIMEOUT


def test_peer_timeout_override(peer_timeout_env):
    # Arrange
    peer_timeout_env("3.5")
    # Act
    value = umbrella._peer_timeout()
    # Assert
    assert value == 3.5


@pytest.mark.parametrize("bad", ["not-a-number", "0", "-4"])
def test_peer_timeout_invalid_falls_back(peer_timeout_env, bad):
    # Arrange
    peer_timeout_env(bad)
    # Act
    value = umbrella._peer_timeout()
    # Assert
    assert value == umbrella._DEFAULT_PEER_TIMEOUT


# EOF
