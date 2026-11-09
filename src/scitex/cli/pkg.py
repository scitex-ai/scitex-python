#!/usr/bin/env python3
"""SciTeX package-management CLI (``scitex-pkg``).

The ``validate`` subcommand checks virtualenv drift. It inspects a default list of
``scitex-*`` packages (overridable via env / config), checks that
each one has installed distribution metadata *and* is importable, and optionally
re-installs the package from a local editable checkout when drift
is detected.

Use ``scitex dev pkg validate`` or the standalone ``scitex-pkg validate``.
The older ``audit`` invocation remains a hidden compatibility route.

Exit codes (with ``--quiet``):
    0 = all packages ok
    1 = one or more packages in ``drift`` or ``missing`` state
    2 = auto-fix attempted but failed
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from importlib.metadata import PackageNotFoundError, version as distribution_version
from pathlib import Path
from typing import Optional

import click
from scitex_dev.ecosystem import deprecated_alias

# ---------------------------------------------------------------------------
# Target package set
# ---------------------------------------------------------------------------
# Keep the existing default targets ordered —
# users reading the terminal output benefit from a stable order.
DEFAULT_TARGET_PACKAGES: tuple[str, ...] = (
    "scitex",
    "scitex-orochi",
    "scitex-agent-container",
    "scitex-clew",
    "scitex-cloud",
)

# Map distribution name -> python import name. pip installs use dashes,
# python imports use underscores.
_IMPORT_NAME_OVERRIDES: dict[str, str] = {
    "scitex": "scitex",
    "scitex-orochi": "scitex_orochi",
    "scitex-agent-container": "scitex_agent_container",
    "scitex-clew": "scitex_clew",
    "scitex-cloud": "scitex_cloud",
}


def _import_name(pkg: str) -> str:
    """Return the python import name for a distribution ``pkg``."""
    if pkg in _IMPORT_NAME_OVERRIDES:
        return _IMPORT_NAME_OVERRIDES[pkg]
    return pkg.replace("-", "_")


def _repo_path_for(pkg: str) -> Path:
    """Default local repo path used by ``--auto-fix``.

    Convention: ``~/proj/<pkg>`` — matches the fleet's standard
    ``~/proj`` checkout root. Override by placing a same-named
    directory under ``$SCITEX_PROJ_ROOT`` if the env var is set.
    """
    root = os.environ.get("SCITEX_PROJ_ROOT")
    base = Path(root).expanduser() if root else Path.home() / "proj"
    # Special-case: the core package lives at ``scitex-python``
    if pkg == "scitex":
        candidates = [base / "scitex-python", base / "scitex"]
    else:
        candidates = [base / pkg]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    # Return the first candidate even if missing — caller checks .exists()
    return candidates[0]


def _extra_packages_from_env() -> list[str]:
    """Return additional packages from ``SCITEX_PKG_AUDIT_EXTRA`` env var.

    The value is a comma- or whitespace-separated list. Duplicates of
    packages already in the default list are filtered out upstream.
    """
    raw = os.environ.get("SCITEX_PKG_AUDIT_EXTRA", "").strip()
    if not raw:
        return []
    parts: list[str] = []
    for chunk in raw.replace(",", " ").split():
        chunk = chunk.strip()
        if chunk:
            parts.append(chunk)
    return parts


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------
@dataclass
class PackageAuditResult:
    """Outcome of auditing a single package.

    Attributes
    ----------
    pkg : str
        The distribution name, e.g. ``scitex-orochi``.
    status : str
        One of ``ok``, ``drift``, ``missing``.
    repo_path : Optional[str]
        Resolved local repo path (if any).
    version : Optional[str]
        Version from this interpreter's installed distribution metadata (if any).
    import_ok : bool
        Whether ``python -c 'import <pkg>'`` succeeded.
    fix_attempted : bool
        Whether ``--auto-fix`` actually ran ``pip install -e``.
    fix_result : Optional[str]
        One of ``succeeded``, ``failed``, or ``None`` if not attempted.
    error : Optional[str]
        Short error message captured when available.
    """

    pkg: str
    status: str
    repo_path: Optional[str] = None
    version: Optional[str] = None
    import_ok: bool = False
    fix_attempted: bool = False
    fix_result: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        """Return a plain-dict representation for JSON serialisation."""
        return asdict(self)


# ---------------------------------------------------------------------------
# Core audit primitives (wrap subprocess so tests can patch them)
# ---------------------------------------------------------------------------
def _installed_version(pkg: str) -> Optional[str]:
    """Read this interpreter's distribution metadata without requiring pip."""
    try:
        return distribution_version(pkg)
    except PackageNotFoundError:
        return None


def _python_import_ok(import_name: str) -> tuple[bool, Optional[str]]:
    """Run ``python -c 'import <name>'`` in a subprocess.

    Returns ``(ok, error_message)``. A clean subprocess is used so a
    failing import of a sibling package doesn't poison the auditor's
    own process.
    """
    try:
        proc = subprocess.run(
            [sys.executable, "-c", f"import {import_name}"],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (subprocess.SubprocessError, OSError) as exc:
        return False, str(exc)
    if proc.returncode == 0:
        return True, None
    err = (proc.stderr or proc.stdout or "").strip()
    # Keep error short — last non-empty line is usually the exception
    last_line = err.splitlines()[-1] if err else ""
    return False, last_line or None


def _pip_install_editable(repo_path: Path) -> tuple[bool, Optional[str]]:
    """Attempt ``pip install -e <repo_path>``. Returns ``(ok, error)``."""
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", str(repo_path)],
            capture_output=True,
            text=True,
            timeout=600,
        )
    except (subprocess.SubprocessError, OSError) as exc:
        return False, str(exc)
    if proc.returncode == 0:
        return True, None
    err = (proc.stderr or proc.stdout or "").strip()
    last_line = err.splitlines()[-1] if err else ""
    return False, last_line or f"pip exited {proc.returncode}"


# ---------------------------------------------------------------------------
# Per-package audit
# ---------------------------------------------------------------------------
def audit_package(pkg: str, auto_fix: bool = False) -> PackageAuditResult:
    """Audit a single package and return a ``PackageAuditResult``.

    The algorithm:
      1. Distribution metadata establishes the installed version.
      2. ``python -c 'import <pkg>'`` — establishes "it actually works".
      3. If both pass → ``ok``.
         If metadata-only → ``drift`` (e.g. editable install that lost its src).
         If neither → ``missing``.
      4. If ``auto_fix`` and a local repo path exists, run
         ``pip install -e <repo_path>`` then re-verify the import.
    """
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?", pkg):
        return PackageAuditResult(pkg=pkg, status="missing", error="Invalid distribution name")
    import_name = _import_name(pkg)
    repo_path = _repo_path_for(pkg)
    repo_path_str = str(repo_path) if repo_path.exists() else None

    version = _installed_version(pkg)
    import_ok, import_err = _python_import_ok(import_name)

    if version and import_ok:
        status = "ok"
        error = None
    elif version and not import_ok:
        status = "drift"
        error = import_err
    else:
        status = "missing"
        error = import_err

    result = PackageAuditResult(
        pkg=pkg,
        status=status,
        repo_path=repo_path_str,
        version=version,
        import_ok=import_ok,
        error=error,
    )

    if auto_fix and status != "ok" and repo_path_str:
        result.fix_attempted = True
        ok, err = _pip_install_editable(repo_path)
        if ok:
            # Re-verify import now that pip has (re)installed.
            import_ok_after, import_err_after = _python_import_ok(import_name)
            if import_ok_after:
                result.fix_result = "succeeded"
                result.status = "ok"
                result.import_ok = True
                result.error = None
                result.version = _installed_version(pkg) or result.version
            else:
                result.fix_result = "failed"
                result.error = import_err_after or "import still fails after reinstall"
        else:
            result.fix_result = "failed"
            result.error = err

    return result


def _status_emoji(status: str) -> str:
    """Return a non-ANSI emoji badge for ``status`` (used in text output)."""
    return {
        "ok": "OK",
        "drift": "DRIFT",
        "missing": "MISSING",
    }.get(status, status.upper())


def _status_color(status: str) -> str:
    return {
        "ok": "green",
        "drift": "yellow",
        "missing": "red",
    }.get(status, "white")


# ---------------------------------------------------------------------------
# Click CLI
# ---------------------------------------------------------------------------
@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def pkg():
    """SciTeX package-management CLI.

    \b
    Subcommands:
      validate    Check installed scitex-* packages for venv drift.
    """


@pkg.command(name="validate")
@click.option(
    "--auto-fix",
    is_flag=True,
    help="Attempt to re-install from the local repo when drift is detected.",
)
@click.option(
    "--host",
    type=str,
    default=None,
    help="Audit a specific remote host via SSH (not yet implemented).",
)
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Emit NDJSON — one JSON object per package, one per line.",
)
@click.option(
    "--quiet",
    is_flag=True,
    help="Suppress human output. Exit code reflects outcome.",
)
@click.option(
    "--pkg",
    "single_pkg",
    type=str,
    default=None,
    help="Audit only one package (distribution name).",
)
def audit(auto_fix, host, as_json, quiet, single_pkg):
    """Audit installed scitex-* packages for venv drift.

    \b
    Examples:
      scitex dev pkg validate                     # human text, read-only
      scitex dev pkg validate --auto-fix          # repair any drift found
      scitex dev pkg validate --json              # NDJSON output
      scitex dev pkg validate --pkg scitex        # validate one package
      scitex dev pkg validate --auto-fix --quiet  # exit code only
    """
    # --host is a stub; remote audit lives in a future iteration so the
    # orochi-cron entry on mgr-pkg stays simple.
    if host:
        msg = f"remote audit not implemented (requested --host {host})"
        if as_json:
            click.echo(json.dumps({"error": msg, "host": host}))
        elif not quiet:
            click.secho(msg, fg="yellow", err=True)
        sys.exit(2)

    if single_pkg:
        targets: list[str] = [single_pkg]
    else:
        # De-duplicate while preserving order.
        seen: set[str] = set()
        targets = []
        for name in list(DEFAULT_TARGET_PACKAGES) + _extra_packages_from_env():
            if name not in seen:
                seen.add(name)
                targets.append(name)

    results: list[PackageAuditResult] = []
    for name in targets:
        result = audit_package(name, auto_fix=auto_fix)
        results.append(result)
        if as_json:
            click.echo(json.dumps(result.to_dict(), sort_keys=True))
        elif not quiet:
            badge = click.style(
                _status_emoji(result.status),
                fg=_status_color(result.status),
                bold=True,
            )
            version_str = f" v{result.version}" if result.version else ""
            fix_note = ""
            if result.fix_attempted:
                fix_note = f" [fix:{result.fix_result}]"
            error_note = f" — {result.error}" if result.error and result.status != "ok" else ""
            click.echo(f"  {badge:20s} {result.pkg}{version_str}{fix_note}{error_note}")

    # Exit-code semantics
    any_non_ok = any(r.status != "ok" for r in results)
    any_fix_failed = any(
        r.fix_attempted and r.fix_result == "failed" for r in results
    )
    if any_fix_failed:
        sys.exit(2)
    if any_non_ok:
        sys.exit(1)
    sys.exit(0)


deprecated_alias(pkg, "audit", target="validate", remove_in="3.0")


# Allow ``python -m scitex.cli.pkg`` for quick manual runs
if __name__ == "__main__":
    pkg()

# EOF
