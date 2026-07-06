#!/usr/bin/env python3
# Timestamp: 2026-05-31
# File: src/scitex/_mcp/__init__.py
"""Single registry-mounting entrypoint for the SciTeX umbrella MCP server.

This module is the umbrella's entire MCP surface. It is a *thin coordinator*:

1. Build one unified FastMCP server.
2. Registry-mount EVERY non-archived, non-umbrella peer's FastMCP instance
   (single source of truth: ``scitex_dev._ecosystem._core.ECOSYSTEM``),
   under a brand-prefixed namespace, with the historical tool-name renames.
   New tools added to a peer's ``_mcp_server`` propagate automatically — no
   umbrella-side maintenance.
3. Skip optional peers that aren't installed (graceful).
4. Fold in the umbrella-only inline tools (``scitex._mcp._umbrella_tools``)
   and the peer surfaces that need brand/name adjustment
   (``scitex._mcp._peer_extras``), plus the umbrella documentation resources.

There is no per-peer "register_<pkg>_tools" bridge layer anymore — that was
an anti-pattern. The registry loop replaces it.

Usage:
    scitex serve                          # stdio (Claude Desktop)
    scitex serve -t sse --port 8085       # SSE (remote via SSH)
    scitex serve -t http --port 8085      # HTTP (streamable)
"""

from __future__ import annotations

import importlib
import logging
import os
import threading
import time
import warnings
from typing import Iterable

# Load environment variables from SCITEX_ENV_SRC early.
from scitex.helpers import load_scitex_env

load_scitex_env()

from scitex_dev import try_import_optional

from ._compat import get_tools_sync, mounted_namespaces, safe_mount

logger = logging.getLogger(__name__)

FastMCP = try_import_optional("fastmcp", "FastMCP", pkg="scitex")
FASTMCP_AVAILABLE = FastMCP is not None

# Suppress httplib2 deprecation warnings from system pyparsing (old API).
# Must be AFTER fastmcp import (fastmcp.__init__ resets the filter) and
# BEFORE register_all_tools (which imports socialia -> google.auth -> httplib2).
warnings.filterwarnings(
    "ignore", category=DeprecationWarning, message=".*deprecated.*use.*"
)

__all__ = [
    "mcp",
    "run_server",
    "main",
    "register_all_tools",
    "safe_mount",
    "get_tools_sync",
    "mounted_namespaces",
    "FASTMCP_AVAILABLE",
]

# Canonical places a FastMCP instance might live inside a peer package.
_MCP_PATH_CANDIDATES = (
    "_mcp_server",
    "mcp_server",
    "_mcp.server",
    "mcp.server",
    "_server",
    "_mcp._server",
)
_MCP_ATTR_CANDIDATES = ("mcp", "server", "app")

# Categories the umbrella does NOT mount.
_SKIP_CATEGORIES = frozenset({"umbrella", "template"})

# Namespace overrides — registry's ``umbrella_subcommand`` may differ from
# the prefix consumers already know. Apply these renames so existing tool
# names (``crossref_search``, not ``crossref-local_search``) survive.
_NAMESPACE_ALIASES: dict[str, str] = {
    "crossref-local": "crossref",
    "openalex-local": "openalex",
    "agent-container": "agent_container",
}

# Per-peer resolve budget. Importing ONE peer's ``_mcp_server`` can hang at
# init (real case: scitex-todo's store-wedge stalls 20s+ at mcp-start). Since
# the umbrella fronts ~33 packages, a naive sequential resolve lets one hung
# peer darken EVERY peer's tools. We bound each peer's resolve and skip any
# that overruns. Override via ``SCITEX_MCP_PEER_TIMEOUT`` (seconds).
_DEFAULT_PEER_TIMEOUT = 8.0


def _peer_timeout() -> float:
    """Per-peer resolve budget in seconds (``SCITEX_MCP_PEER_TIMEOUT`` env)."""
    raw = os.environ.get("SCITEX_MCP_PEER_TIMEOUT")
    if raw is None:
        return _DEFAULT_PEER_TIMEOUT
    try:
        val = float(raw)
    except (TypeError, ValueError):
        logger.warning(
            "invalid SCITEX_MCP_PEER_TIMEOUT=%r — using default %.1fs",
            raw,
            _DEFAULT_PEER_TIMEOUT,
        )
        return _DEFAULT_PEER_TIMEOUT
    return val if val > 0 else _DEFAULT_PEER_TIMEOUT


def _env_gate_key(namespace: str) -> str:
    """Return the SCITEX_MCP_USE_<NS> env-var name for a namespace."""
    return "SCITEX_MCP_USE_" + namespace.upper().replace("-", "_")


def _is_enabled(namespace: str) -> bool:
    """Honour ``SCITEX_MCP_USE_<NS>=0`` to skip a peer mount."""
    return os.environ.get(_env_gate_key(namespace), "1") != "0"


def _resolve_peer_mcp(import_name: str):
    """Try every canonical location for a peer's FastMCP instance."""
    try:
        from fastmcp import FastMCP as _FastMCP
    except ImportError:
        return None

    for sub in _MCP_PATH_CANDIDATES:
        try:
            mod = importlib.import_module(f"{import_name}.{sub}")
        except BaseException:
            # BaseException: some peers ``sys.exit(1)`` at import if their
            # preconditions fail; SystemExit must not kill the umbrella.
            continue
        for attr in _MCP_ATTR_CANDIDATES:
            obj = getattr(mod, attr, None)
            if isinstance(obj, _FastMCP):
                return obj
    return None


def _iter_registry() -> Iterable[tuple[str, str, str]]:
    """Yield ``(pip_name, import_name, namespace)`` for every mountable peer."""
    try:
        from scitex_dev._ecosystem._core import ECOSYSTEM
    except ImportError:
        logger.warning("scitex-dev not installed — peer MCP auto-mount disabled.")
        return

    for pip_name, info in ECOSYSTEM.items():
        if info.get("archived"):
            continue
        if info.get("category") in _SKIP_CATEGORIES:
            continue
        import_name = info.get("import_name")
        if not import_name:
            continue
        namespace = info.get("umbrella_subcommand", pip_name.removeprefix("scitex-"))
        namespace = _NAMESPACE_ALIASES.get(namespace, namespace)
        yield pip_name, import_name, namespace


def _resolve_peers_bounded(
    peers: list[tuple[str, str]], timeout: float
) -> tuple[list[tuple[str, object]], list[tuple[str, str]]]:
    """Resolve each peer's FastMCP concurrently under a bounded time budget.

    Each ``(import_name, namespace)`` is resolved in its own **daemon** thread
    so that a peer whose ``_mcp_server`` import HANGS cannot (a) block the
    other peers' resolution nor (b) block interpreter exit. All threads start
    at once and are joined against a single shared deadline, so total wall time
    is ~``max(peer resolve)`` bounded by ``timeout`` — never the sum.

    Returns ``(resolved, skipped)`` where:
      * ``resolved`` is ``[(namespace, peer_mcp), ...]`` in registry order for
        peers that produced a FastMCP instance, and
      * ``skipped`` is ``[(namespace, reason), ...]`` for peers that timed out
        (hung import) or raised during resolve.

    Peers that resolve cleanly to ``None`` (no FastMCP found — an optional peer
    that isn't installed) are silently omitted from both, matching the prior
    behavior of the sequential loop.
    """
    results: dict[str, object] = {}
    errors: dict[str, BaseException] = {}

    def _worker(import_name: str, namespace: str) -> None:
        try:
            results[namespace] = _resolve_peer_mcp(import_name)
        except BaseException as exc:  # noqa: BLE001 — surfaced by caller
            # BaseException: a peer may ``sys.exit()`` at import; that must be
            # recorded as a skip, never propagate out of the daemon thread.
            errors[namespace] = exc

    threads: list[tuple[str, threading.Thread]] = []
    for import_name, namespace in peers:
        t = threading.Thread(
            target=_worker,
            args=(import_name, namespace),
            name=f"scitex-mcp-resolve-{namespace}",
            daemon=True,
        )
        threads.append((namespace, t))
        t.start()

    deadline = time.monotonic() + timeout
    for _namespace, t in threads:
        remaining = deadline - time.monotonic()
        if remaining > 0:
            t.join(remaining)

    resolved: list[tuple[str, object]] = []
    skipped: list[tuple[str, str]] = []
    for namespace, t in threads:
        if t.is_alive():
            skipped.append(
                (namespace, f"resolve timed out after {timeout:.1f}s (hung import)")
            )
        elif namespace in errors:
            skipped.append((namespace, f"resolve raised {errors[namespace]!r}"))
        elif results.get(namespace) is not None:
            resolved.append((namespace, results[namespace]))
    return resolved, skipped


def register_all_tools(mcp, *, iter_registry=None, peer_timeout=None) -> None:
    """Mount every peer's FastMCP onto the umbrella, then fold in extras.

    Order:
      1. Registry-driven ``safe_mount`` of each peer's FastMCP instance. Each
         peer's *resolve* (its ``_mcp_server`` import) runs concurrently under
         a bounded timeout (``SCITEX_MCP_PEER_TIMEOUT``, default 8s); a hung
         peer is SKIPPED with a warning so it can't darken the aggregator.
      2. Peer surfaces needing brand/name adjustment (figrecipe plt_stx,
         socialia social_*, linter, optional cloud mount).
      3. Umbrella-only inline tools (no peer owns them).

    Each peer is gated by ``SCITEX_MCP_USE_<NAMESPACE>=0`` (default enabled).

    Args:
        mcp: the umbrella FastMCP server to mount onto.
        iter_registry: injectable ``() -> Iterable[(pip, import_name, ns)]``
            source of peers; defaults to :func:`_iter_registry` (the ecosystem
            registry). Exposed for tests so they can drive the real code path
            with hand-rolled fixture peers instead of patching module globals.
        peer_timeout: injectable per-peer resolve budget in seconds; defaults
            to :func:`_peer_timeout` (the ``SCITEX_MCP_PEER_TIMEOUT`` env var).
    """
    iter_registry = iter_registry if iter_registry is not None else _iter_registry
    timeout = peer_timeout if peer_timeout is not None else _peer_timeout()
    mounted: set[str] = set()

    peers = [
        (import_name, namespace)
        for _pip, import_name, namespace in iter_registry()
        if _is_enabled(namespace)
    ]

    resolved, skipped = _resolve_peers_bounded(peers, timeout)

    for namespace, reason in skipped:
        logger.warning(
            "MCP peer %r %s — its tools will be unavailable this session",
            namespace,
            reason,
        )

    # Mount on the MAIN thread. The slow, hang-prone part is the peer IMPORT
    # (bounded above); the mount itself is fast and mutates shared parent-server
    # state, so it stays single-threaded here to avoid concurrent-mutation races.
    for namespace, peer_mcp in resolved:
        try:
            safe_mount(mcp, peer_mcp, namespace=namespace)
            mounted.add(namespace)
        except Exception as exc:  # noqa: BLE001 — diagnostic, never fatal
            logger.warning("MCP mount failed for %r: %s", namespace, exc)

    from ._peer_extras import register_peer_extras
    from ._umbrella_tools import register_umbrella_tools

    register_peer_extras(mcp)
    register_umbrella_tools(mcp)

    if mounted:
        logger.info(
            "MCP umbrella mounted %d peer servers: %s",
            len(mounted),
            ", ".join(sorted(mounted)),
        )


_INSTRUCTIONS = """\
SciTeX: Python Framework for Scientific Research Automation (https://scitex.ai)

IMPORTANT: When writing Python for data analysis, visualization, or research,
ALWAYS use `import scitex as stx` and leverage these core patterns:

### @stx.session - Reproducible Experiment Tracking
```python
import scitex as stx

@stx.session
def main(param1="default", CONFIG=stx.INJECTED, plt=stx.INJECTED,
         logger=stx.INJECTED):
    \"\"\"Docstring becomes --help description.\"\"\"
    stx.io.save(results, "results.csv")
    return 0
```

### stx.io - Universal File I/O (30+ formats)
```python
stx.io.save(df, "data.csv"); stx.io.save(fig, "plot.png")  # +auto CSV
data = stx.io.load("data.csv")
```

### stx.plt - Publication-Ready Figures (Auto CSV Export)
```python
fig, ax = stx.plt.subplots()
ax.plot_line(x, y); ax.set_xyt("X", "Y", "Title")
stx.io.save(fig, "plot.png")  # plot.png + plot.csv
```

### stx.stats - Publication Statistics (23 tests)
```python
result = stx.stats.test_ttest_ind(g1, g2, return_as="dataframe")
```

## MCP Resources (Read for detailed docs):
- scitex://cheatsheet, scitex://session-tree, scitex://io-formats
- scitex://module/{io,plt,stats,scholar,session}
- scitex://plt-figrecipe

Use introspect_* tools to explore the API: introspect_dir("scitex.stats")
"""


if FASTMCP_AVAILABLE:
    mcp = FastMCP(name="scitex", instructions=_INSTRUCTIONS)

    register_all_tools(mcp)

    # Annotate tools with the standardized Result envelope schema.
    try:
        from scitex_dev.types import RESULT_SCHEMA

        for tool in get_tools_sync(mcp).values():
            if getattr(tool, "output_schema", None) is None:
                tool.output_schema = RESULT_SCHEMA
    except Exception:
        pass  # Non-critical: schema annotation is informational.

    from ._resources import register_resources

    register_resources(mcp)
else:
    mcp = None


def run_server(
    transport: str = "stdio",
    host: str = "0.0.0.0",
    port: int = 8085,
):
    """Run the unified MCP server with transport selection."""
    if not FASTMCP_AVAILABLE:
        import sys

        print("=" * 60)
        print("Requires 'fastmcp' package: pip install fastmcp")
        print("=" * 60)
        sys.exit(1)

    if transport == "stdio":
        mcp.run(transport="stdio")
    elif transport == "sse":
        print(f"Starting scitex MCP (SSE) on {host}:{port}")
        print(f"Remote: ssh -R {port}:localhost:{port} remote-host")
        mcp.run(transport="sse", host=host, port=port)
    elif transport == "http":
        print(f"Starting scitex MCP (HTTP) on {host}:{port}")
        mcp.run(transport="streamable-http", host=host, port=port)
    else:
        raise ValueError(f"Unknown transport: {transport}")


def main():
    """Entry point for the ``scitex-mcp-server`` console script."""
    run_server(transport="stdio")


if __name__ == "__main__":
    main()

# EOF
