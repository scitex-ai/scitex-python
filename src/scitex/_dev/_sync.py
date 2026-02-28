#!/usr/bin/env python3
# Timestamp: 2026-02-24
# File: scitex/_dev/_sync.py

"""Ecosystem package sync across local and remote hosts.

Safety model (like bulk_rename):
  - All operations default to dry_run=True (preview only).
  - Pass confirm=True to actually execute.
  - CLI requires --confirm flag.
  - MCP tool requires confirm=True parameter.
"""

from __future__ import annotations

import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from ._config import DevConfig, HostConfig, get_enabled_hosts, load_config

# ---------------------------------------------------------------------------
# SSH helpers
# ---------------------------------------------------------------------------


def _build_ssh_args(host: HostConfig) -> list[str]:
    """Build SSH command prefix for a host."""
    args = ["ssh"]
    if host.ssh_key:
        args.extend(["-i", host.ssh_key])
    if host.port != 22:
        args.extend(["-p", str(host.port)])
    args.extend(
        [
            "-o",
            "BatchMode=yes",
            "-o",
            "StrictHostKeyChecking=accept-new",
            "-o",
            "ConnectTimeout=10",
        ]
    )
    args.append(f"{host.user}@{host.hostname}")
    return args


def _get_host_packages(host: HostConfig, config: DevConfig) -> list[tuple[str, str]]:
    """Get (package_name, remote_dir_name) pairs for a host.

    Uses host.packages if set, otherwise all ecosystem packages.
    Returns tuples of (pypi_name, directory_name) where directory_name
    is the local_path basename (e.g., 'scitex-python' for scitex).
    """
    pkg_map = {p.name: p for p in config.packages}

    names = host.packages if host.packages else [p.name for p in config.packages]
    result = []
    for name in names:
        pkg = pkg_map.get(name)
        if pkg and pkg.local_path:
            dir_name = Path(pkg.local_path).expanduser().name
            result.append((name, dir_name))
    return result


def _build_sync_commands(
    host: HostConfig, dir_name: str, stash: bool, install: bool
) -> list[str]:
    """Build the shell commands that would be run for a package."""
    base = f"{host.remote_base}/{dir_name}"
    cmds = [f"cd {base}"]
    if stash:
        cmds.append("git stash")
    cmds.append("git pull")
    if install:
        cmds.append(f"{host.pip_bin} install -e . -q")
    if stash:
        cmds.append("git stash pop 2>/dev/null || true")
    return cmds


def _sync_one_package(
    host: HostConfig, dir_name: str, stash: bool, install: bool
) -> dict[str, Any]:
    """Sync a single package on a remote host."""
    cmds = _build_sync_commands(host, dir_name, stash, install)
    remote_cmd = " && ".join(cmds)

    ssh_args = _build_ssh_args(host)
    ssh_args.append(remote_cmd)

    try:
        result = subprocess.run(ssh_args, capture_output=True, text=True, timeout=120)
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if result.returncode == 0:
            return {"status": "ok", "output": stdout}
        return {
            "status": "error",
            "output": stdout,
            "error": stderr or f"exit code {result.returncode}",
        }
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "error": "SSH command timed out (120s)"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


# ---------------------------------------------------------------------------
# Public API — all default to dry_run=True (safe preview)
# ---------------------------------------------------------------------------


def sync_host(
    host: HostConfig,
    packages: list[str] | None = None,
    stash: bool = True,
    install: bool = True,
    confirm: bool = False,
    config: DevConfig | None = None,
) -> dict[str, Any]:
    """Sync packages to a remote host via SSH.

    Safety: defaults to preview only. Pass confirm=True to execute.

    Steps per package: git stash, git pull, pip install -e ., git stash pop.

    Parameters
    ----------
    host : HostConfig
        Target host configuration.
    packages : list[str] | None
        Package names to sync. None = use host's configured packages.
    stash : bool
        Git stash before pull (default True).
    install : bool
        Pip install after pull (default True).
    confirm : bool
        If False (default), preview only (dry run).
        If True, execute the sync operation.
    config : DevConfig | None
        Configuration. Loaded from default if None.

    Returns
    -------
    dict
        Per-package results: {package: {status, commands|output, error}}.
    """
    if config is None:
        config = load_config()

    host_pkgs = _get_host_packages(host, config)
    if packages:
        host_pkgs = [(n, d) for n, d in host_pkgs if n in packages]

    if not confirm:
        return {
            name: {
                "status": "dry_run",
                "commands": _build_sync_commands(host, dir_name, stash, install),
            }
            for name, dir_name in host_pkgs
        }

    # Parallel package sync within a single host
    results: dict[str, Any] = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(_sync_one_package, host, dir_name, stash, install): name
            for name, dir_name in host_pkgs
        }
        for future in as_completed(futures):
            name = futures[future]
            try:
                results[name] = future.result()
            except Exception as e:
                results[name] = {"status": "error", "error": str(e)}
    return results


def sync_all(
    hosts: list[str] | None = None,
    packages: list[str] | None = None,
    stash: bool = True,
    install: bool = True,
    confirm: bool = False,
    config: DevConfig | None = None,
) -> dict[str, Any]:
    """Sync packages across all enabled hosts.

    Safety: defaults to preview only. Pass confirm=True to execute.
    Parallel: hosts are synced concurrently by default.

    Parameters
    ----------
    hosts : list[str] | None
        Host names to sync. None = all enabled hosts.
    packages : list[str] | None
        Package names. None = host-specific defaults.
    stash : bool
        Git stash before pull.
    install : bool
        Pip install after pull.
    confirm : bool
        If False (default), preview only (dry run).
        If True, execute the sync operation.
    config : DevConfig | None
        Configuration.

    Returns
    -------
    dict
        {host_name: {package: result}}.
    """
    if config is None:
        config = load_config()

    enabled = get_enabled_hosts(config)
    if hosts:
        enabled = [h for h in enabled if h.name in hosts]

    if not confirm:
        # Dry-run: no SSH needed, compute locally
        return {
            host.name: sync_host(
                host,
                packages=packages,
                stash=stash,
                install=install,
                confirm=False,
                config=config,
            )
            for host in enabled
        }

    # Execute: parallel across hosts
    results: dict[str, Any] = {}
    with ThreadPoolExecutor(max_workers=len(enabled) or 1) as executor:
        futures = {
            executor.submit(
                sync_host,
                host,
                packages=packages,
                stash=stash,
                install=install,
                confirm=True,
                config=config,
            ): host.name
            for host in enabled
        }
        for future in as_completed(futures):
            host_name = futures[future]
            try:
                results[host_name] = future.result()
            except Exception as e:
                results[host_name] = {"error": str(e)}
    return results


def sync_local(
    packages: list[str] | None = None,
    confirm: bool = False,
    config: DevConfig | None = None,
) -> dict[str, Any]:
    """Install all local editable packages.

    Safety: defaults to preview only. Pass confirm=True to execute.

    Parameters
    ----------
    packages : list[str] | None
        Package names. None = all configured packages.
    confirm : bool
        If False (default), preview only.
        If True, execute pip install -e.
    config : DevConfig | None
        Configuration.

    Returns
    -------
    dict
        {package: {status, output|commands}}.
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

        if not confirm:
            results[pkg.name] = {
                "status": "dry_run",
                "commands": ["pip", "install", "-e", str(path), "-q"],
            }
            continue

        try:
            result = subprocess.run(
                ["pip", "install", "-e", str(path), "-q"],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0:
                results[pkg.name] = {"status": "ok", "output": result.stdout.strip()}
            else:
                results[pkg.name] = {
                    "status": "error",
                    "error": result.stderr.strip(),
                }
        except Exception as e:
            results[pkg.name] = {"status": "error", "error": str(e)}
    return results


def sync_tags(
    packages: list[str] | None = None,
    confirm: bool = False,
    config: DevConfig | None = None,
) -> dict[str, Any]:
    """Push local tags for all packages to origin.

    Safety: defaults to preview only. Pass confirm=True to execute.

    Parameters
    ----------
    packages : list[str] | None
        Package names. None = all configured packages.
    confirm : bool
        If False (default), preview only.
        If True, execute git push --tags.
    config : DevConfig | None
        Configuration.

    Returns
    -------
    dict
        {package: {status, tag, output|commands}}.
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

        # Get latest tag (always safe to check)
        try:
            tag_result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                capture_output=True,
                text=True,
                cwd=str(path),
                timeout=10,
            )
            tag = tag_result.stdout.strip() if tag_result.returncode == 0 else None
        except Exception:
            tag = None

        if not confirm:
            results[pkg.name] = {
                "status": "dry_run",
                "tag": tag,
                "commands": ["git", "push", "origin", "--tags"],
            }
            continue

        try:
            push_result = subprocess.run(
                ["git", "push", "origin", "--tags"],
                capture_output=True,
                text=True,
                cwd=str(path),
                timeout=30,
            )
            if push_result.returncode == 0:
                results[pkg.name] = {
                    "status": "ok",
                    "tag": tag,
                    "output": push_result.stderr.strip(),  # git push outputs to stderr
                }
            else:
                results[pkg.name] = {
                    "status": "error",
                    "tag": tag,
                    "error": push_result.stderr.strip(),
                }
        except Exception as e:
            results[pkg.name] = {"status": "error", "error": str(e)}
    return results


# EOF
