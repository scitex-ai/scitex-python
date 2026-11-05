#!/usr/bin/env python3
"""Installed declaration projection for the umbrella ``scitex`` CLI.

Dev resolves installed ownership and CLI-specific declines without imports.
The registry supplies migration/naming policy, never fabricated capabilities.
Deliberate umbrella adapters preserve actual workflows; legacy console targets
use the exact declared target at invocation time. Discovery calls no provider.

Pulled out of ``scitex/cli/main.py`` to keep that orchestrator file
under the project's 512-line cap.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

# Spec shape: (module_path_or_candidates, attr_name, short_help).
# - module_path_or_candidates is either a single dotted module path (str)
#   OR a tuple of (module_path, attr_name) candidates. The LazyGroup
#   loader walks the tuple at invocation time and returns the first one
#   that imports cleanly. Storing candidates instead of probing them at
#   registration is what keeps the umbrella `scitex` CLI startup fast —
#   eagerly importing every peer's `_cli._main` at registration time
#   added ~45 s of cold-start latency across ~60 ecosystem peers.
LazySpec = tuple[object, str, str]


@dataclass(frozen=True)
class PeerCliTarget:
    """Metadata-qualified target; only these may use a console adapter."""

    candidates: tuple[tuple[str, str], ...]
    distribution: str
    target: str
    console_script: str | None

    def __iter__(self):
        return iter(self.candidates)


# Hidden migration routes reuse Dev's native alias helper. Canonical products
# stay at root; developer workflows move under dev. The normal metadata views
# never advertise these routes, and a reserved name cannot recreate an alias.
DEPRECATED_ALIASES: dict[str, tuple[object, str]] = {
    "notify": ("notification", "3.0"),
    "verify": ("clew", "3.0"),
    "events": ("event", "3.0"),
    "socialia": ("social", "3.0"),
    "todo": ("cards", "3.0"),
    "tunnel": (("ssh", "tunnel"), "3.0"),
    "app": (("sdk", "app"), "3.0"),
    "ui": (("sdk", "ui"), "3.0"),
    **{
        name: (("dev", name), "3.0")
        for name in (
            "audit",
            "completion",
            "introspect",
            "linter",
            "list-python-apis",
            "pkg",
            "skills",
            "capture",
            "security",
            "newb",
            "resource",
            "template",
            "git",
            "benchmark",
        )
    },
}

# Python identity aliases such as scitex.plt remain public Python facades.
# A separate CLI alias is mounted only if its installed ownership/delegation
# is actually declared and eligible; Python identity alone is insufficient.

# Help blurbs for scitex-internal subcommands AND fallback one-liners
# for registry peers whose package metadata is unavailable in the
# current environment (peer not installed -> importlib.metadata fails).
# Without a fallback the root help degraded to the bare subcommand name
# ("dataset   dataset"). One-liners are sourced from each package's own
# pyproject `description` (what metadata Summary would return), trimmed
# to fit the help column.
_FALLBACK_HELP: dict[str, str] = {
    # scitex-internal wrappers (no peer in the registry)
    "dev": "Developer tools, audits, package checks, skills, and completion.",
    "sdk": "SDK for standalone research apps and SciTeX Hub plugins.",
    "audit": "Security auditing tools.",
    "capture": "Screenshot capture tools.",
    "completion": "Shell tab-completion management (install, status).",
    "convert": "File format conversion.",
    "config": "Inspect and configure SciTeX paths and settings.",
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
    "ui": "Shared UI shell, components, and application tooling.",
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


# Existing umbrella-owned workflows are deliberate adapters, not generic peer
# discovery. Merely adding a file must not create a new public root command.
_UMBRELLA_WRAPPERS = frozenset(
    {
        "browser",
        "config",
        "convert",
        "dev",
        "docs",
        "event",
        "mcp",
        "repro",
        "resource",
        "social",
        "template",
        "tex",
        "web",
        "writer",
    }
)
# Require the actual installed domain owner even for call-time imports. An
# umbrella wrapper file alone does not establish a usable optional workflow.
# An absent native CLI declaration still provides installed-distribution proof:
# Root composes the Python-only events provider without inventing a leaf CLI.
_WRAPPER_OWNERS = {"web": "scitex-web", "event": "scitex-events"}

DEV_COMMANDS = frozenset(
    {
        "audit",
        "completion",
        "introspect",
        "linter",
        "list-python-apis",
        "pkg",
        "skills",
    }
)
DEV_PEERS = frozenset(
    {"capture", "security", "newb", "resource", "template", "git", "benchmark"}
)


# Actual operation delegation, not ownership inferred from a command spelling.
# Config/convert/pkg/completion/mcp are Root-owned compositions over libraries.
_WORKFLOW_OWNERS = {
    "browser": "scitex-browser",
    "dev": "scitex-dev",
    "docs": "scitex-dev",
    "event": "scitex-events",
    "repro": "scitex-repro",
    "resource": "scitex-resource",
    "social": "socialia",
    "template": "scitex-template",
    "tex": "scitex-tex",
    "web": "scitex-web",
    "writer": "scitex-writer",
    "audit": "scitex-audit",
    "introspect": "scitex-introspect",
    "list-python-apis": "scitex-introspect",
    "linter": "scitex-dev",
    "skills": "scitex-dev",
}


def _native_candidate(row, retired):
    return bool(
        row.name
        and row.target
        and row.status in {"declared", "legacy_unknown"}
        and row.distribution not in retired
        and not (row.name in DEPRECATED_ALIASES and row.name not in DEV_PEERS)
        and row.name not in DEV_COMMANDS
        and row.name != "dev"
    )


def workflow_enabled(name, snapshot):
    """Require Root's composition preference and any actual domain delegate."""
    return snapshot.allows("scitex") and snapshot.allows(
        _WORKFLOW_OWNERS.get(name, "scitex")
    )


def reserved_cli_names(rows=None, *, snapshot=None, namespace="root"):
    """Reserve declarations and declined actual routes, never a guessed namespace."""
    if snapshot is None and rows is None:
        from ._exposure import load_cli_snapshot

        snapshot = load_cli_snapshot()
    if rows is None:
        rows = snapshot.rows
    blocked = {
        row.name
        for row in rows
        if row.name and row.status in {"none", "invalid", "ambiguous"}
    }
    if snapshot is not None:
        eligible = [
            row
            for row in rows
            if _native_candidate(row, snapshot.retired)
            and (namespace == "root" or row.name in DEV_PEERS)
        ]
        blocked.update(
            row.name for row in eligible if not snapshot.allows(row.distribution)
        )
        native_enabled = {
            row.name for row in eligible if snapshot.allows(row.distribution)
        }
        workflows = {*_UMBRELLA_WRAPPERS, *DEV_COMMANDS, "linter", "skills"}
        blocked.update(
            name
            for name in workflows
            if name not in native_enabled and not workflow_enabled(name, snapshot)
        )
    return blocked


def build_lazy_subcommands(
    cli_dir: str, *, namespace: str = "root", snapshot=None
) -> dict[str, LazySpec]:
    """Project installed CLI declarations; never invent a CLI from a registry row.

    The Dev reader owns metadata eligibility and explicit declines. Registry
    records supply retirement/name policy only. A named, existing umbrella
    adapter may implement a workflow without a standalone leaf console script.
    Explicit decline/invalid/ambiguous names remain reserved against adapters.
    """
    if namespace not in {"root", "dev"}:
        raise ValueError("CLI namespace must be root or dev")

    from ._exposure import load_cli_snapshot

    have_wrapper = _wrapper_inventory(cli_dir)
    out: dict[str, LazySpec] = {}
    snapshot = load_cli_snapshot() if snapshot is None else snapshot
    rows = snapshot.rows
    blocked = reserved_cli_names(rows, snapshot=snapshot, namespace=namespace)
    installed_owners = {row.distribution for row in rows}
    retired = snapshot.retired
    for row in rows:
        if not row.name or row.name in blocked or not row.target:
            continue
        if (
            row.status not in {"declared", "legacy_unknown"}
            or row.distribution in retired
        ):
            continue
        sub = row.name
        if (
            (sub in DEPRECATED_ALIASES and sub not in DEV_PEERS)
            or sub in DEV_COMMANDS
            or sub == "dev"
        ):
            continue
        module, _, attr = row.target.partition(":")
        if not module or not attr:
            continue
        help_text = _registry_subcommand_help(row.distribution) or _FALLBACK_HELP.get(
            sub, sub
        )
        # The shared reader proved this exact module belongs to the owner.
        # Do not probe alternate modules: namespace prefixes are not ownership.
        candidates = ((module, attr),)
        out[sub] = (
            PeerCliTarget(candidates, row.distribution, row.target, row.console_script),
            sub.replace("-", "_"),
            help_text,
        )

    for name in _UMBRELLA_WRAPPERS:
        if (
            name in blocked
            or name not in have_wrapper
            or not workflow_enabled(name, snapshot)
        ):
            continue
        owner = _WRAPPER_OWNERS.get(name)
        if owner is not None and owner not in installed_owners:
            continue
        # An explicit leaf target takes precedence over a legacy wrapper.
        explicit = any(r.name == name and r.status == "declared" for r in rows)
        # This exact owner still needs Root's filtered Dev composition,
        # rather than mounting the raw owner group and bypassing its scope.
        canonical_dev = name == "dev" and any(
            row.name == "dev"
            and row.status == "declared"
            and row.distribution == "scitex-dev"
            and row.target == "scitex_dev._cli:main"
            for row in rows
        )
        if explicit and not canonical_dev:
            continue
        out[name] = (f"scitex.cli.{name}", name, _FALLBACK_HELP.get(name, name))
    # Deprecated spellings are added only as hidden, lazy canonical aliases.
    if namespace == "dev":
        return {name: spec for name, spec in out.items() if name in DEV_PEERS}
    for name in (*DEPRECATED_ALIASES, *DEV_COMMANDS, *DEV_PEERS):
        out.pop(name, None)
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
_NON_CORE_CATEGORIES: tuple[tuple[str, frozenset], ...] = (
    ("Data & Sync", frozenset({"convert"})),
    (
        "Service",
        frozenset(
            {"agent-container", "container", "hub", "mcp", "orochi", "ssh", "tunnel"}
        ),
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
CATEGORY_ORDER: tuple[str, ...] = (
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
