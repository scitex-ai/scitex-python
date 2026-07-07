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

# Spec shape: (module_path_or_candidates, attr_name, short_help).
# - module_path_or_candidates is either a single dotted module path (str)
#   OR a tuple of (module_path, attr_name) candidates. The LazyGroup
#   loader walks the tuple at invocation time and returns the first one
#   that imports cleanly. Storing candidates instead of probing them at
#   registration is what keeps the umbrella `scitex` CLI startup fast —
#   eagerly importing every peer's `_cli._main` at registration time
#   added ~45 s of cold-start latency across ~60 ecosystem peers.
LazySpec = Tuple[object, str, str]

_REGISTRY_SKIP_CATEGORIES = frozenset({"umbrella", "template"})

# Duplicate namespaces retired 2026-07-07 (CLI-standardization slice 5).
# {old_name: (canonical_name, remove_in_version)}. The old names are
# NEVER registered as lazy subcommands; ``main.py`` re-adds them as
# hidden warn-phase deprecated aliases via scitex-dev's
# ``click_compat.deprecated_alias`` when that helper is importable
# (scitex-dev > 0.21.0). With an older scitex-dev the duplicates are
# simply excluded — canonical names only.
#
# Canonical picks (verified against the packages' own CLI names and the
# doctrine noun catalog):
#   notification — the package is scitex-notification; `notify` was an
#                  ad-hoc alias added here.
#   clew         — the package is scitex-clew; `verify` was an ad-hoc
#                  alias added here.
#   event        — singular noun-group doctrine; the `events` name came
#                  from the scitex-events peer, which ships NO CLI (all
#                  candidate probes fail), so `scitex events` was a dead
#                  entry in help.
#   social       — doctrine §5b brand table (socialia → `scitex social`);
#                  the bare `socialia` name leaked from the registry
#                  because the peer record has no umbrella_subcommand.
DEPRECATED_ALIASES: Dict[str, Tuple[str, str]] = {
    "notify": ("notification", "3.0"),
    "verify": ("clew", "3.0"),
    "events": ("event", "3.0"),
    "socialia": ("social", "3.0"),
}

# NOTE on figrecipe/plt: NOT a deprecated duplicate. `scitex plt` mounts
# the scitex-plt peer, a published identity-alias package for figrecipe
# (`scitex_plt is figrecipe` -> True), and doctrine §5b's brand table
# documents `scitex plt` as a figrecipe mount. Both names stay mounted;
# `figrecipe` is canonical and `plt` self-describes as the alias.

# Help blurbs for scitex-internal subcommands AND fallback one-liners
# for registry peers whose package metadata is unavailable in the
# current environment (peer not installed -> importlib.metadata fails).
# Without a fallback the root help degraded to the bare subcommand name
# ("dataset   dataset"). One-liners are sourced from each package's own
# pyproject `description` (what metadata Summary would return), trimmed
# to fit the help column.
_FALLBACK_HELP: Dict[str, str] = {
    # scitex-internal wrappers (no peer in the registry)
    "audit": "Security auditing tools.",
    "capture": "Screenshot capture tools.",
    "completion": "Shell tab-completion management (install, status).",
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
    "social": "Social media management (post, feed, analytics) via socialia.",
    "template": "Project template cloner + code snippet library.",
    "tex": "LaTeX tools.",
    "web": "Web utilities.",
    # registry peers (fallback when the peer is not installed)
    "app": "SciTeX App SDK — write-once interface for local + cloud apps.",
    "audio": "Text-to-speech with multiple backends for scientific work.",
    "browser": "Browser automation for scholarly paper access.",
    "clew": "Verifiable knowledge graph for scientific experiments.",
    "crossref-local": "Local CrossRef database (167M+ works) with full-text search.",
    "dataset": "Multi-domain dataset fetcher (OpenNeuro, DANDI, PhysioNet, GEO, ...).",
    "datetime": "Datetime helpers (linspace, normalize_timestamp, format helpers).",
    "decorators": "Decorator library (numpy_fn/torch_fn/pandas_fn, caching, batching).",
    "dsp": "Digital signal processing (PAC, Hilbert, wavelet, filters).",
    "figrecipe": "Reproducible matplotlib wrapper with mm-precision layouts.",
    "git": "Git + GitHub Actions utilities (clone, branch, commit, gh secrets).",
    "hpc": "Generic SLURM dispatch (srun, sbatch, sync, poll, fetch).",
    "hub": "Deployment and management CLI for SciTeX Hub.",
    "io": "Universal scientific data I/O with plugin registry.",
    "linalg": "Small linear-algebra helpers (distance, geometric median, cosine).",
    "linter": "DEPRECATED shim re-exporting scitex-dev's linter.",
    "math": "Mathematical utilities (parity helpers, etc.).",
    "ml": "Machine learning, classification, and training utilities.",
    "newb": "Fresh-agent doc smoke-tests — checks your docs actually work.",
    "nn": "Neural network building blocks (BNet, Hilbert, PAC, wavelet).",
    "openalex-local": "Local OpenAlex database (284M+ works) with semantic search.",
    "orochi": "Agent communication hub for the SciTeX ecosystem.",
    "plt": "SciTeX plotting (published alias for figrecipe).",
    "repl": "Interactive REPL helpers (embed / less / paste).",
    "scholar": "Scientific paper search, enrichment, download, and management.",
    "seizure-metrics": "Metrics for epileptic seizure detection and forecasting.",
    "sh": "Safe subprocess wrapper (list-only, no shell injection).",
    "ssh": "SSH primitives (exec/copy/attach/tunnel; per-host allowlist).",
    "tunnel": "SSH tunnel management for SciTeX services.",
    "writer": "LaTeX manuscript compilation system for scientific documents.",
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
    ("_cli_main", "cli"),  # scitex-scholar (entry point scitex_scholar._cli_main:cli)
)


def _peer_cli_candidates(import_name: str) -> tuple[tuple[str, str], ...]:
    """Return candidate ``(module_path, attr_name)`` pairs for the peer's main click group.

    Does NOT import — that's left to the LazyGroup loader at invocation
    time. Returning the candidate list at registration keeps umbrella
    startup fast (importing every peer's ``_cli._main`` at registration
    added ~45 s across ~60 peers).
    """
    return tuple((f"{import_name}.{sub}", attr) for sub, attr in _PEER_CLI_PROBES)


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
        # Register the peer's candidate locations WITHOUT importing.
        # LazyGroup._load_lazy walks the candidates at invocation time
        # and returns the first one that resolves. An on-disk wrapper
        # file in scitex/cli/<short>.py acts as an explicit override.
        help_text = _registry_subcommand_help(imp) or _FALLBACK_HELP.get(sub) or sub
        if attr in have_wrapper:
            out[sub] = (f"scitex.cli.{attr}", attr, help_text)
        else:
            out[sub] = (_peer_cli_candidates(imp), attr, help_text)

    # 2. scitex-internal wrappers (no peer in the registry).
    registered_attrs = {
        spec[1]
        for spec in out.values()
        if isinstance(spec[0], str) and spec[0].startswith("scitex.cli.")
    }
    for attr in have_wrapper:
        if attr in registered_attrs:
            continue
        sub = attr.replace("_", "-")
        out.setdefault(sub, (f"scitex.cli.{attr}", attr, _FALLBACK_HELP.get(sub, sub)))

    # 3. Retired duplicate namespaces (see DEPRECATED_ALIASES above).
    # main.py re-adds them as hidden warn-phase deprecated aliases when
    # scitex-dev's click_compat is importable.
    for old_name in DEPRECATED_ALIASES:
        out.pop(old_name, None)

    return out


# Fixed, ordered help categories per doctrine §4a (10a_command-categories
# .md): Core / Data & Sync / Service / Diagnostics / Introspection /
# Shell / Other. Header names and order are canonical ecosystem-wide;
# `Other` is the catch-all and must be empty at audit-clean, so every
# mounted subcommand is explicitly assigned here. `Core` is the implicit
# default for anything not listed below — the umbrella's Core is "every
# re-exported domain package", which grows with the registry, so listing
# the non-Core minority keeps this table maintainable and keeps new
# registry peers out of `Other`.
_NON_CORE_CATEGORIES: Tuple[Tuple[str, frozenset], ...] = (
    ("Data & Sync", frozenset({"convert"})),
    (
        "Service",
        frozenset({"agent-container", "container", "hub", "mcp", "orochi", "ssh", "tunnel"}),
    ),
    (
        "Diagnostics",
        frozenset({"audit", "benchmark", "linter", "pkg", "resource", "security"}),
    ),
    (
        "Introspection",
        frozenset({"dev", "docs", "introspect", "list-python-apis", "skills"}),
    ),
    ("Shell", frozenset({"completion", "repl"})),
)

# Canonical render order (§4a). Empty categories are omitted at render.
CATEGORY_ORDER: Tuple[str, ...] = (
    "Core",
    "Data & Sync",
    "Service",
    "Diagnostics",
    "Introspection",
    "Shell",
    "Other",
)


def command_category(name: str) -> str:
    """Return the §4a help category for a top-level subcommand name."""
    for category, names in _NON_CORE_CATEGORIES:
        if name in names:
            return category
    return "Core"


# EOF
