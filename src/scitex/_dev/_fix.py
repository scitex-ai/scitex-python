#!/usr/bin/env python3
# Timestamp: 2026-03-11
# File: scitex/_dev/_fix.py

"""Detect and fix version mismatches across the ecosystem.

Combines detection (list_versions) with sync (sync_local + sync_all)
into a single command.

Safety model: defaults to dry_run (confirm=False).
"""

from __future__ import annotations

from typing import Any

from ._config import DevConfig, load_config
from ._sync import sync_all, sync_local
from ._versions import get_mismatches


def fix_mismatches(
    hosts: list[str] | None = None,
    packages: list[str] | None = None,
    local: bool = True,
    remote: bool = True,
    confirm: bool = False,
    config: DevConfig | None = None,
) -> dict[str, Any]:
    """Detect version mismatches and fix them.

    Safety: defaults to preview only. Pass confirm=True to execute.

    Parameters
    ----------
    hosts : list[str] | None
        Host names to fix. None = all enabled hosts.
    packages : list[str] | None
        Package names. None = all with mismatches.
    local : bool
        Fix local mismatches (pip install -e .).
    remote : bool
        Fix remote mismatches (git pull + pip install on hosts).
    confirm : bool
        If False (default), preview only.
        If True, execute fixes.
    config : DevConfig | None
        Configuration.

    Returns
    -------
    dict
        {detected, local_fixes, remote_fixes, summary}
    """
    if config is None:
        config = load_config()

    mismatches = get_mismatches(packages)
    mismatch_names = list(mismatches.keys()) if not packages else packages

    result: dict[str, Any] = {
        "detected": {
            pkg: {"status": info.get("status"), "issues": info.get("issues", [])}
            for pkg, info in mismatches.items()
        },
        "local_fixes": {},
        "remote_fixes": {},
        "summary": {"detected": len(mismatches), "local_fixed": 0, "remote_fixed": 0},
    }

    if not mismatch_names:
        return result

    # Fix local: pip install -e . where installed != toml
    if local:
        local_to_fix = _find_local_mismatches(mismatches)
        if local_to_fix:
            result["local_fixes"] = sync_local(
                packages=local_to_fix, confirm=confirm, config=config
            )
            if confirm:
                result["summary"]["local_fixed"] = sum(
                    1 for r in result["local_fixes"].values() if r.get("status") == "ok"
                )

    # Fix remote: git pull + pip install on hosts
    if remote:
        result["remote_fixes"] = sync_all(
            hosts=hosts,
            packages=mismatch_names,
            stash=True,
            install=True,
            confirm=confirm,
            config=config,
        )
        if confirm:
            for host_results in result["remote_fixes"].values():
                if isinstance(host_results, dict):
                    result["summary"]["remote_fixed"] += sum(
                        1
                        for r in host_results.values()
                        if isinstance(r, dict) and r.get("status") == "ok"
                    )

    return result


def _find_local_mismatches(mismatches: dict[str, Any]) -> list[str]:
    """Extract package names where local installed != toml version."""
    to_fix = []
    for pkg, info in mismatches.items():
        lv = info.get("local", {})
        toml = lv.get("pyproject_toml")
        installed = lv.get("installed")
        if toml and installed and toml != installed:
            to_fix.append(pkg)
        elif toml and not installed:
            to_fix.append(pkg)
    return to_fix


# EOF
