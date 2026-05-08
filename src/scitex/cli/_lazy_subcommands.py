#!/usr/bin/env python3
"""Registry-driven lazy-subcommand wiring for the umbrella ``scitex`` CLI.

Single source of truth: the scitex-dev ecosystem registry
(``scitex_dev._ecosystem._core.ECOSYSTEM``). Every peer with
``umbrella_subcommand=X`` is expected to ship an umbrella-side click
group at ``scitex.cli.<X>:<X>`` (X with underscores for hyphenated
names). The builder iterates the registry, filters to subcommands
whose wrapper file actually exists in ``scitex/cli/``, and merges in
non-conventional overrides + aliases.

Pulled out of ``scitex/cli/main.py`` to keep that orchestrator file
under the project's 512-line cap.
"""

from __future__ import annotations

import os
from typing import Dict, Tuple

LazySpec = Tuple[str, str, str]  # (module_path, attr_name, short_help)

_REGISTRY_SKIP_CATEGORIES = frozenset({"umbrella", "template"})

# Help blurbs for scitex-internal subcommands (no corresponding peer in
# the registry). Anything not listed falls through to the bare name.
_INTERNAL_HELP: Dict[str, str] = {
    "audit": "Security auditing tools.",
    "capture": "Screenshot capture tools.",
    "convert": "File format conversion.",
    "docs": "Browse and search SciTeX documentation.",
    "event": "Event bus for async task results.",
    "introspect": "Code introspection tools.",
    "mcp": "MCP server management.",
    "notebook": "Jupyter notebook tools.",
    "notification": "Notification and alerting tools.",
    "pkg": "Package management (venv drift audit).",
    "resource": "Resource management.",
    "security": "Security scanning tools.",
    "skills": "Browse skills across the ecosystem.",
    "tex": "LaTeX tools.",
    "web": "Web utilities.",
}


def _registry_subcommand_help(import_name: str) -> str:
    """Best-effort short help drawn from the peer's package metadata Summary."""
    try:
        from importlib.metadata import metadata

        meta = metadata(import_name.replace("_", "-"))
        # PackageMetadata is a Message-like object; .get() works in py3.10+.
        return str(meta.get("Summary") or "")
    except Exception:
        return ""


def _wrapper_inventory(cli_dir: str) -> set[str]:
    """Return the set of attr-names whose ``scitex.cli.<attr>.py`` exists."""
    return {
        f[:-3]
        for f in os.listdir(cli_dir)
        if f.endswith(".py") and not f.startswith("_") and f != "main.py"
    }


# Conventional locations a peer might publish its main click group at.
# Probed in order; first hit wins. Keeps the umbrella registry-driven
# even when peers don't follow a single canonical layout.
_PEER_CLI_PROBES: tuple[tuple[str, str], ...] = (
    ("_cli._main", "main"),  # scitex-io, scitex-clew, scitex-plt, scitex-ssh, …
    ("_cli", "main"),  # scitex-dataset, scitex-audio, scitex-cloud, …
    ("cli", "main"),  # scitex-capture, scitex-security, scitex-agent-container
    ("_cli._app", "app"),  # scitex-app
)


def _probe_peer_cli(import_name: str) -> tuple[str, str] | None:
    """Find the peer's main click group.

    Returns ``(module_path, attr_name)`` or ``None`` if the peer ships no
    discoverable CLI. Imports the candidate module to verify the attr
    exists (lazy callers should still wrap loading in try/except since
    optional deps may be missing).
    """
    import importlib

    for sub_path, attr in _PEER_CLI_PROBES:
        full = f"{import_name}.{sub_path}"
        try:
            mod = importlib.import_module(full)
        except ImportError:
            continue
        if hasattr(mod, attr):
            return full, attr
    return None


def build_lazy_subcommands(cli_dir: str) -> Dict[str, LazySpec]:
    """Build the umbrella's lazy-subcommand dict.

    Pure registry-driven: for every non-archived non-template peer in
    ``ECOSYSTEM``, probe the peer's import name for a ``main``/``app``
    click group at one of the conventional sub-paths and register it
    directly as ``scitex <short>``. No per-peer wrapper file in
    ``scitex/cli/<short>.py`` is required (or wanted) — the umbrella
    ships zero hand-wired peer dispatchers.

    Falls back to the on-disk wrapper inventory only for scitex-internal
    subcommands that aren't peers (audit, capture, convert, docs, etc.)
    and for any peer that was missed by the probe (the wrapper acts as
    an explicit override).
    """
    out: Dict[str, LazySpec] = {}
    have_wrapper = _wrapper_inventory(cli_dir)

    # 1. Registry-driven peer dispatch (no per-peer wrapper file needed).
    try:
        from scitex_dev._ecosystem._core import ECOSYSTEM
    except ImportError:
        ECOSYSTEM = {}

    for pip_name, info in ECOSYSTEM.items():
        if info.get("archived"):
            continue
        if info.get("category") in _REGISTRY_SKIP_CATEGORIES:
            continue
        imp = info.get("import_name") or ""
        if not imp:
            continue
        sub = info.get("umbrella_subcommand", pip_name.removeprefix("scitex-"))
        attr = sub.replace("-", "_")
        # Probe the peer's main click group at one of the conventional
        # locations; this is the canonical path. An on-disk wrapper file
        # in scitex/cli/<short>.py is only consulted as a fallback when
        # the probe doesn't find anything (kept as an escape hatch for
        # peers that don't yet expose a click group).
        probe = _probe_peer_cli(imp)
        if probe is not None:
            module_path, attr_name = probe
            help_text = _registry_subcommand_help(imp) or _INTERNAL_HELP.get(sub) or sub
            out[sub] = (module_path, attr_name, help_text)
            continue
        if attr in have_wrapper:
            help_text = _registry_subcommand_help(imp) or _INTERNAL_HELP.get(sub) or sub
            out[sub] = (f"scitex.cli.{attr}", attr, help_text)

    # 2. scitex-internal wrappers (no peer in the registry).
    registered_attrs = {
        spec[1] for spec in out.values() if spec[0].startswith("scitex.cli.")
    }
    for attr in have_wrapper:
        if attr in registered_attrs:
            continue
        sub = attr.replace("_", "-")
        out.setdefault(sub, (f"scitex.cli.{attr}", attr, _INTERNAL_HELP.get(sub, sub)))

    # 3. Aliases.
    if "notification" in out:
        out["notify"] = out["notification"]
    if "clew" in out:
        out["verify"] = out["clew"]

    return out


# EOF
