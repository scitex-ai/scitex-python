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
import sys
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

# Umbrella commands renamed to the noun/verb CLI convention (2026-11-19).
# {mounted_name: ((new_name, attr_in_the_same_module), ...)}. The new names
# are mounted from the same wrapper module; ``main.py`` keeps each old
# name working as a hidden alias that prints a deprecation note.
#   audit      — a verb group; split into the leaf `audit-security [PATH]`
#                and the noun group `audit-tool {status,install}`.
#   introspect — a verb group; renamed to the noun `introspection`.
#   convert    — a verb group over .stx bundle files; renamed to `bundle`.
RENAMED_MOUNTS: Dict[str, Tuple[Tuple[str, str], ...]] = {
    "audit": (("audit-security", "audit_security"), ("audit-tool", "audit_tool")),
    "introspect": (("introspection", "introspect"),),
    "convert": (("bundle", "convert"),),
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
    "audit-security": "Run security tools (Bandit, ShellCheck, pip-audit, GitHub).",
    "audit-tool": "Check and install the tools audit-security runs.",
    "bundle": "Convert and validate SciTeX bundle files (.figz/.pltz -> .stx).",
    "capture": "Screenshot capture tools.",
    "completion": "Shell tab-completion management (install, status).",
    "docs": "Browse and search SciTeX documentation.",
    "event": "Event bus for async task results.",
    "introspection": "Code introspection tools.",
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
    ("_cli", "cli"),  # crossref-local, openalex-local (`main` is a plain function)
    ("cli", "cli"),  # crossref-local, openalex-local (legacy module path)
    ("cli", "main_group"),  # scitex-msword
)


# Published identity-alias packages: the alias imports as its target
# (`scitex_plt is figrecipe`), so its CLI modules live in the target's tree.
_IDENTITY_ALIASES: Dict[str, str] = {"scitex_plt": "figrecipe"}


def _locate_without_importing(top: str):
    """Find the spec of top-level package ``top`` without executing it.

    ``importlib.util.find_spec`` is not safe here: `import scitex` registers
    peers in ``sys.modules`` behind a ``LazyLoader``, and ``util.find_spec``
    reads ``sys.modules[top].__spec__``, which executes the peer's whole body
    (a peer importing torch at import time then recursed through torch's
    inspect-based op registration and broke `scitex --help`). Asking the
    meta-path finders directly never consults ``sys.modules``.
    """
    for finder in sys.meta_path:
        find_spec = getattr(finder, "find_spec", None)
        if find_spec is None:
            continue
        spec = find_spec(top, None)
        if spec is not None:
            return spec
    return None


def _peer_cli_present(candidates: tuple[tuple[str, str], ...]) -> bool:
    """Return True when the peer is installed AND ships a probed CLI module.

    Imports nothing: ``find_spec`` on a top-level name only locates the
    package, and the candidate submodules are checked as files on disk.
    A peer that is not installed, or installed without any CLI module
    (scitex-str, scitex-session, ...), must not be advertised: its name
    would resolve to no command, which `scitex --help` lists but click
    then rejects, and which scitex-dev's CLI audit refuses as incomplete
    public command discovery (§1a, ``missing-command``).
    """
    top = candidates[0][0].split(".", 1)[0]
    top = _IDENTITY_ALIASES.get(top, top)
    try:
        spec = _locate_without_importing(top)
    except (ImportError, ValueError):
        return False
    if spec is None or not spec.submodule_search_locations:
        return False
    for module_path, _attr in candidates:
        parts = module_path.split(".")[1:]
        for base in spec.submodule_search_locations:
            path = os.path.join(base, *parts)
            if os.path.isfile(path + ".py") or os.path.isfile(
                os.path.join(path, "__init__.py")
            ):
                return True
    return False


def _peer_installed(import_name: str) -> bool:
    """Return True when the peer's top-level package is importable (no import)."""
    try:
        return _locate_without_importing(import_name) is not None
    except (ImportError, ValueError):
        return False


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
    peer_wrappers: set[str] = set()

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
        # Only advertise what can resolve (see _peer_cli_present): a wrapper
        # override needs its peer installed, a direct mount needs the peer's
        # CLI module on disk. Unavailable peers stay out of help instead of
        # being listed and then rejected as "No such command".
        help_text = _registry_subcommand_help(imp) or _FALLBACK_HELP.get(sub) or sub
        if attr in have_wrapper:
            peer_wrappers.add(attr)
            if _peer_installed(imp):
                out[sub] = (f"scitex.cli.{attr}", attr, help_text)
        else:
            candidates = _peer_cli_candidates(imp)
            if _peer_cli_present(candidates):
                out[sub] = (candidates, attr, help_text)

    # 2. scitex-internal wrappers (no peer in the registry).
    registered_attrs = {
        spec[1]
        for spec in out.values()
        if isinstance(spec[0], str) and spec[0].startswith("scitex.cli.")
    }
    for attr in have_wrapper:
        # A peer's override wrapper skipped in step 1 (peer not installed)
        # must not come back here as if it were scitex-internal.
        if attr in registered_attrs or attr in peer_wrappers:
            continue
        sub = attr.replace("_", "-")
        out.setdefault(sub, (f"scitex.cli.{attr}", attr, _FALLBACK_HELP.get(sub, sub)))

    # 3. Renamed umbrella commands (see RENAMED_MOUNTS above): mount the
    # new names from the same module; main.py aliases the old names.
    for old_name, new_mounts in RENAMED_MOUNTS.items():
        spec = out.pop(old_name, None)
        if spec is None:
            continue
        for new_name, new_attr in new_mounts:
            out[new_name] = (spec[0], new_attr, _FALLBACK_HELP.get(new_name, spec[2]))

    # 4. Retired duplicate namespaces (see DEPRECATED_ALIASES above).
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
    ("Data & Sync", frozenset({"bundle"})),
    (
        "Service",
        frozenset(
            {"agent-container", "container", "hub", "mcp", "orochi", "ssh", "tunnel"}
        ),
    ),
    (
        "Diagnostics",
        frozenset(
            {
                "audit-security",
                "audit-tool",
                "benchmark",
                "linter",
                "pkg",
                "resource",
                "security",
            }
        ),
    ),
    (
        "Introspection",
        frozenset({"dev", "docs", "introspection", "list-python-apis", "skills"}),
    ),
    (
        "Shell",
        frozenset(
            {
                "completion",
                "install-shell-completion",
                "print-shell-completion",
                "repl",
            }
        ),
    ),
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
