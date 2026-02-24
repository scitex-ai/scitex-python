#!/usr/bin/env python3
# Timestamp: 2026-02-02
# File: scitex/_dev/_versions.py

"""Core version checking logic for the scitex ecosystem."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

from ._ecosystem import ECOSYSTEM, get_all_packages, get_local_path


def get_version_from_toml(path: Path) -> str | None:
    """Read version from pyproject.toml."""
    toml_path = path / "pyproject.toml"
    if not toml_path.exists():
        return None

    try:
        # Python 3.11+
        import tomllib

        with open(toml_path, "rb") as f:
            data = tomllib.load(f)
    except ImportError:
        try:
            import tomli

            with open(toml_path, "rb") as f:
                data = tomli.load(f)
        except ImportError:
            # Fallback: regex parse
            content = toml_path.read_text()
            match = re.search(
                r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE
            )
            return match.group(1) if match else None

    return data.get("project", {}).get("version")


def get_version_installed(package: str) -> str | None:
    """Get version from importlib.metadata."""
    try:
        from importlib.metadata import version

        return version(package)
    except Exception:
        return None


def get_git_latest_tag(path: Path) -> str | None:
    """Get latest git tag (version tags only)."""
    if not path.exists():
        return None

    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0", "--match", "v*"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass

    # Fallback: list all tags
    try:
        result = subprocess.run(
            ["git", "tag", "-l", "v*", "--sort=-v:refname"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split("\n")[0]
    except Exception:
        pass

    return None


def get_git_branch(path: Path) -> str | None:
    """Get current git branch."""
    if not path.exists():
        return None

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass

    return None


def get_git_status(path: Path) -> dict[str, Any] | None:
    """Get git worktree status (dirty/clean, ahead/behind remote).

    Returns
    -------
    dict or None
        Keys: dirty (bool), ahead (int), behind (int), short_hash (str).
        Returns None if path doesn't exist or is not a git repo.
    """
    if not path.exists():
        return None

    info: dict[str, Any] = {"dirty": False, "ahead": 0, "behind": 0, "short_hash": None}

    # Check if dirty (uncommitted changes)
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            info["dirty"] = bool(result.stdout.strip())
    except Exception:
        pass

    # Get short commit hash
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            info["short_hash"] = result.stdout.strip()
    except Exception:
        pass

    # Ahead/behind upstream
    try:
        result = subprocess.run(
            ["git", "rev-list", "--left-right", "--count", "HEAD...@{upstream}"],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split()
            if len(parts) == 2:
                info["ahead"] = int(parts[0])
                info["behind"] = int(parts[1])
    except Exception:
        pass

    return info


def get_pypi_version(package: str) -> str | None:
    """Fetch latest version from PyPI API."""
    try:
        import urllib.request

        url = f"https://pypi.org/pypi/{package}/json"
        with urllib.request.urlopen(url, timeout=5) as response:
            import json

            data = json.loads(response.read().decode())
            return data.get("info", {}).get("version")
    except Exception:
        return None


def _normalize_version(v: str | None) -> str | None:
    """Normalize version string (strip v prefix)."""
    if v is None:
        return None
    return v.lstrip("v")


def _pep440_equal(v1: str | None, v2: str | None) -> bool:
    """Compare two version strings using PEP 440 normalization.

    Treats e.g. '0.10.3-alpha' and '0.10.3a0' as equal.
    """
    if v1 is None or v2 is None:
        return v1 == v2
    from packaging.version import InvalidVersion, Version

    try:
        return Version(_normalize_version(v1)) == Version(_normalize_version(v2))
    except InvalidVersion:
        return _normalize_version(v1) == _normalize_version(v2)


def _compare_versions(v1: str | None, v2: str | None) -> int:
    """Compare two version strings. Returns -1, 0, or 1."""
    if v1 is None or v2 is None:
        return 0

    from packaging.version import Version

    try:
        ver1 = Version(_normalize_version(v1))
        ver2 = Version(_normalize_version(v2))
        if ver1 < ver2:
            return -1
        if ver1 > ver2:
            return 1
        return 0
    except Exception:
        # Fallback: string comparison
        return 0


def _determine_status(info: dict[str, Any]) -> tuple[str, list[str]]:
    """Determine version status and issues."""
    issues = []

    toml_ver = info.get("local", {}).get("pyproject_toml")
    installed_ver = info.get("local", {}).get("installed")
    tag_ver = _normalize_version(info.get("git", {}).get("latest_tag"))
    pypi_ver = info.get("remote", {}).get("pypi")

    # Check local consistency (PEP 440: '0.10.3-alpha' == '0.10.3a0')
    if toml_ver and installed_ver and not _pep440_equal(toml_ver, installed_ver):
        issues.append(f"pyproject.toml ({toml_ver}) != installed ({installed_ver})")

    # Check if toml matches tag
    if toml_ver and tag_ver and not _pep440_equal(toml_ver, tag_ver):
        issues.append(f"pyproject.toml ({toml_ver}) != git tag ({tag_ver})")

    # Check pypi status
    if toml_ver and pypi_ver:
        cmp = _compare_versions(toml_ver, pypi_ver)
        if cmp > 0:
            issues.append(f"local ({toml_ver}) > pypi ({pypi_ver}) - ready to release")
            return "unreleased", issues
        if cmp < 0:
            issues.append(f"local ({toml_ver}) < pypi ({pypi_ver}) - outdated")
            return "outdated", issues

    # Check git worktree status
    git_info = info.get("git", {})
    if git_info.get("dirty"):
        issues.append("uncommitted changes")
    ahead = git_info.get("ahead", 0)
    behind = git_info.get("behind", 0)
    if ahead:
        issues.append(f"{ahead} commit(s) ahead of remote")
    if behind:
        issues.append(f"{behind} commit(s) behind remote")

    if issues:
        return "mismatch", issues

    if not toml_ver:
        return "unavailable", ["package not found locally"]

    return "ok", []


def list_versions(packages: list[str] | None = None) -> dict[str, Any]:
    """List versions for all ecosystem packages.

    Parameters
    ----------
    packages : list[str] | None
        List of package names to check. If None, checks all ecosystem packages.

    Returns
    -------
    dict
        Version information for each package.
    """
    if packages is None:
        packages = get_all_packages()

    result = {}
    for pkg in packages:
        if pkg not in ECOSYSTEM:
            result[pkg] = {"status": "unknown", "issues": [f"'{pkg}' not in ecosystem"]}
            continue

        info: dict[str, Any] = {"local": {}, "git": {}, "remote": {}}
        local_path = get_local_path(pkg)
        pypi_name = ECOSYSTEM[pkg].get("pypi_name", pkg)

        # Local sources
        if local_path and local_path.exists():
            info["local"]["pyproject_toml"] = get_version_from_toml(local_path)
        info["local"]["installed"] = get_version_installed(pypi_name)

        # Git sources
        if local_path and local_path.exists():
            info["git"]["latest_tag"] = get_git_latest_tag(local_path)
            info["git"]["branch"] = get_git_branch(local_path)
            git_status = get_git_status(local_path)
            if git_status:
                info["git"]["dirty"] = git_status["dirty"]
                info["git"]["ahead"] = git_status["ahead"]
                info["git"]["behind"] = git_status["behind"]
                info["git"]["short_hash"] = git_status["short_hash"]

        # Remote sources
        info["remote"]["pypi"] = get_pypi_version(pypi_name)

        # Determine status
        status, issues = _determine_status(info)
        info["status"] = status
        info["issues"] = issues

        result[pkg] = info

    return result


def check_versions(packages: list[str] | None = None) -> dict[str, Any]:
    """Check version consistency and return detailed status.

    Parameters
    ----------
    packages : list[str] | None
        List of package names to check. If None, checks all ecosystem packages.

    Returns
    -------
    dict
        Detailed version check results with overall summary.
    """
    versions = list_versions(packages)

    summary = {
        "total": len(versions),
        "ok": 0,
        "mismatch": 0,
        "unreleased": 0,
        "outdated": 0,
        "unavailable": 0,
        "unknown": 0,
    }

    for _pkg, info in versions.items():
        status = info.get("status", "unknown")
        if status in summary:
            summary[status] += 1

    return {"packages": versions, "summary": summary}


# EOF
