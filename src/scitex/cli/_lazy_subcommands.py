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


def build_lazy_subcommands(cli_dir: str) -> Dict[str, LazySpec]:
    """Build the umbrella's lazy-subcommand dict.

    ``cli_dir`` is the on-disk directory holding the ``scitex.cli.*``
    wrapper modules — passed in so this builder stays import-cycle-free.
    """
    out: Dict[str, LazySpec] = {}
    have_wrapper = _wrapper_inventory(cli_dir)

    # 1. Registry-derived entries.
    try:
        from scitex_dev._ecosystem._core import ECOSYSTEM
    except ImportError:
        ECOSYSTEM = {}

    for pip_name, info in ECOSYSTEM.items():
        if info.get("archived"):
            continue
        if info.get("category") in _REGISTRY_SKIP_CATEGORIES:
            continue
        sub = info.get("umbrella_subcommand", pip_name.removeprefix("scitex-"))
        attr = sub.replace("-", "_")
        if attr not in have_wrapper:
            continue
        help_text = _registry_subcommand_help(info.get("import_name", "")) or sub
        out[sub] = (f"scitex.cli.{attr}", attr, help_text)

    # 2. scitex-internal wrappers (no peer in the registry).
    registered_attrs = {spec[1] for spec in out.values()}
    for attr in have_wrapper:
        if attr in registered_attrs:
            continue
        sub = attr.replace("_", "-")
        out.setdefault(sub, (f"scitex.cli.{attr}", attr, _INTERNAL_HELP.get(sub, sub)))

    # 3. Non-conventional overrides (peers whose CLI lives outside scitex.cli).
    out["app"] = ("scitex_app._cli._app", "app", "Create and manage SciTeX apps.")

    # 4. Aliases.
    if "notification" in out:
        out["notify"] = out["notification"]
    if "clew" in out:
        out["verify"] = out["clew"]

    return out


# EOF
