#!/usr/bin/env python3
# Timestamp: 2026-02-26
# File: scitex/_dev/_sync_remote.py

"""Reverse sync operations: remote → local.

Complements _sync.py (local → remote) with:
  - remote_diff(): Show uncommitted changes on remote hosts
  - remote_commit(): Commit + push dirty changes on remote hosts
  - pull_local(): Pull origin → local repos

Safety model (same as _sync.py):
  - All mutating operations default to confirm=False (preview only).
  - Pass confirm=True to actually execute.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from ._config import DevConfig, HostConfig, get_enabled_hosts, load_config
from ._sync import _build_ssh_args, _get_host_packages

# ---------------------------------------------------------------------------
# SSH helper (filters X11 noise)
# ---------------------------------------------------------------------------


def _run_ssh(host: HostConfig, remote_cmd: str, timeout: int = 120) -> dict[str, Any]:
    """Run a single SSH command and return structured result."""
    ssh_args = _build_ssh_args(host)
    ssh_args.append(remote_cmd)
    try:
        result = subprocess.run(
            ssh_args, capture_output=True, text=True, timeout=timeout
        )
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        stderr_lines = [
            line for line in stderr.splitlines() if "X11 forwarding" not in line
        ]
        stderr = "\n".join(stderr_lines).strip()
        if result.returncode == 0:
            return {"status": "ok", "output": stdout, "stderr": stderr}
        return {
            "status": "error",
            "output": stdout,
            "error": stderr or f"exit code {result.returncode}",
        }
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "error": f"SSH command timed out ({timeout}s)"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def remote_diff(
    host: str | None = None,
    packages: list[str] | None = None,
    config: DevConfig | None = None,
) -> dict[str, Any]:
    """Show git diff on remote host(s). Read-only operation.

    Parameters
    ----------
    host : str | None
        Host name. None = first enabled host.
    packages : list[str] | None
        Package names. None = host-configured defaults.
    config : DevConfig | None
        Configuration.

    Returns
    -------
    dict
        {host_name: {package: {status, files, diff_stat, diff}}}.
    """
    if config is None:
        config = load_config()

    enabled = get_enabled_hosts(config)
    if host:
        enabled = [h for h in enabled if h.name == host]
    if not enabled:
        return {"error": f"Host '{host}' not found or not enabled"}

    results: dict[str, Any] = {}
    for h in enabled:
        host_pkgs = _get_host_packages(h, config)
        if packages:
            host_pkgs = [(n, d) for n, d in host_pkgs if n in packages]

        pkg_results: dict[str, Any] = {}
        for name, dir_name in host_pkgs:
            base = f"{h.remote_base}/{dir_name}"
            cmd = (
                f"cd {base} && "
                f"echo '---STATUS---' && git status --short && "
                f"echo '---STAT---' && git diff --stat && "
                f"echo '---DIFF---' && git diff"
            )
            r = _run_ssh(h, cmd)
            if r["status"] == "ok":
                output = r["output"]
                parts = output.split("---DIFF---")
                header = parts[0] if parts else ""
                diff = parts[1].strip() if len(parts) > 1 else ""

                stat_parts = header.split("---STAT---")
                status_text = (
                    stat_parts[0].replace("---STATUS---", "").strip()
                    if stat_parts
                    else ""
                )
                stat_text = stat_parts[1].strip() if len(stat_parts) > 1 else ""

                pkg_results[name] = {
                    "status": "dirty" if status_text else "clean",
                    "files": status_text,
                    "diff_stat": stat_text,
                    "diff": diff,
                }
            else:
                pkg_results[name] = r
        results[h.name] = pkg_results
    return results


def remote_commit(
    host: str,
    packages: list[str] | None = None,
    message: str | None = None,
    push: bool = True,
    confirm: bool = False,
    config: DevConfig | None = None,
) -> dict[str, Any]:
    """Commit dirty changes on a remote host and optionally push to origin.

    Safety: defaults to preview only. Pass confirm=True to execute.

    Parameters
    ----------
    host : str
        Host name (required).
    packages : list[str] | None
        Package names. None = host-configured defaults.
    message : str | None
        Commit message. Auto-generated if not provided.
    push : bool
        Push to origin after commit (default True).
    confirm : bool
        If False (default), preview only (dry run).
    config : DevConfig | None
        Configuration.

    Returns
    -------
    dict
        {package: {status, commands|output}}.
    """
    if config is None:
        config = load_config()

    enabled = get_enabled_hosts(config)
    target = next((h for h in enabled if h.name == host), None)
    if target is None:
        return {"error": f"Host '{host}' not found or not enabled"}

    host_pkgs = _get_host_packages(target, config)
    if packages:
        host_pkgs = [(n, d) for n, d in host_pkgs if n in packages]

    results: dict[str, Any] = {}
    for name, dir_name in host_pkgs:
        base = f"{target.remote_base}/{dir_name}"

        if not confirm:
            cmd = f"cd {base} && git status --short"
            r = _run_ssh(target, cmd)
            dirty_files = r.get("output", "").strip() if r["status"] == "ok" else ""
            if not dirty_files:
                results[name] = {"status": "clean", "message": "nothing to commit"}
                continue

            msg = message or f"chore({name}): sync from {host}"
            commit_cmds = [f"cd {base}", "git add -A", f'git commit -m "{msg}"']
            if push:
                commit_cmds.append("git push origin $(git rev-parse --abbrev-ref HEAD)")
            results[name] = {
                "status": "dry_run",
                "dirty_files": dirty_files,
                "commands": commit_cmds,
            }
            continue

        # Execute: check if dirty first
        status_r = _run_ssh(target, f"cd {base} && git status --short")
        dirty = status_r.get("output", "").strip() if status_r["status"] == "ok" else ""
        if not dirty:
            results[name] = {"status": "clean", "message": "nothing to commit"}
            continue

        msg = message or f"chore({name}): sync from {host}"
        cmds = [f"cd {base}", "git add -A", f'git commit -m "{msg}"']
        if push:
            cmds.append("git push origin $(git rev-parse --abbrev-ref HEAD)")
        results[name] = _run_ssh(target, " && ".join(cmds))

    return results


def pull_local(
    packages: list[str] | None = None,
    confirm: bool = False,
    stash: bool = True,
    config: DevConfig | None = None,
) -> dict[str, Any]:
    """Pull latest from origin to local repos.

    Safety: defaults to preview only. Pass confirm=True to execute.

    Parameters
    ----------
    packages : list[str] | None
        Package names. None = all configured packages.
    confirm : bool
        If False (default), preview only.
    stash : bool
        If True (default), stash local changes before pull and pop after.
        If False and repo is dirty, pull proceeds as-is (may fail).
    config : DevConfig | None
        Configuration.

    Returns
    -------
    dict
        {package: {status, output|commands, stashed}}.
    """
    if config is None:
        config = load_config()

    targets = config.packages
    if packages:
        targets = [p for p in targets if p.name in packages]

    results: dict[str, Any] = {}
    for pkg in targets:
        if not pkg.local_path:
            continue

        path = Path(pkg.local_path).expanduser()
        if not path.exists():
            results[pkg.name] = {"status": "skipped", "error": f"{path} not found"}
            continue

        # Check if repo is dirty
        status_result = subprocess.run(
            ["git", "-C", str(path), "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        is_dirty = bool(status_result.stdout.strip())

        if not confirm:
            entry: dict[str, Any] = {
                "status": "dry_run",
                "commands": ["git", "-C", str(path), "pull", "origin"],
            }
            if is_dirty:
                entry["dirty"] = True
                if stash:
                    entry["note"] = "repo is dirty; would stash before pull"
            results[pkg.name] = entry
            continue

        try:
            did_stash = False
            if is_dirty and stash:
                stash_result = subprocess.run(
                    ["git", "-C", str(path), "stash"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if stash_result.returncode != 0:
                    results[pkg.name] = {
                        "status": "error",
                        "error": stash_result.stderr.strip() or "git stash failed",
                        "stashed": False,
                    }
                    continue
                did_stash = True

            result = subprocess.run(
                ["git", "-C", str(path), "pull", "origin"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            stderr_lines = [
                line for line in stderr.splitlines() if "X11 forwarding" not in line
            ]
            stderr = "\n".join(stderr_lines).strip()

            if did_stash:
                pop_result = subprocess.run(
                    ["git", "-C", str(path), "stash", "pop"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if pop_result.returncode != 0:
                    results[pkg.name] = {
                        "status": "stash_conflict",
                        "output": stdout or stderr,
                        "stashed": True,
                        "error": pop_result.stderr.strip()
                        or "git stash pop failed; resolve conflicts manually",
                    }
                    continue

            if result.returncode == 0:
                results[pkg.name] = {
                    "status": "ok",
                    "output": stdout or stderr,
                    "stashed": did_stash,
                }
            else:
                results[pkg.name] = {
                    "status": "error",
                    "error": stderr or f"exit code {result.returncode}",
                    "stashed": did_stash,
                }
        except Exception as e:
            results[pkg.name] = {"status": "error", "error": str(e)}
    return results


# EOF
