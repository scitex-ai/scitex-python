#!/usr/bin/env python3
"""Container version management: list, switch, rollback, deploy, cleanup."""

from __future__ import annotations

import logging
import re
import subprocess
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("scitex")

_VERSION_RE = re.compile(r"^scitex-v(.+)\.sif$")
_BASE_RE = re.compile(r"^scitex-base-v(\d+)\.sif$")


def _human_size(nbytes: int) -> str:
    """Convert bytes to human-readable size.

    Parameters
    ----------
    nbytes : int
        Number of bytes.

    Returns
    -------
    str
        Human-readable size string (e.g. "1.2 GB").
    """
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(nbytes) < 1024:
            return f"{nbytes:.1f} {unit}"
        nbytes /= 1024
    return f"{nbytes:.1f} PB"


def _parse_version(path: Path) -> str | None:
    """Extract version string from a scitex-v*.sif filename.

    Parameters
    ----------
    path : Path
        Path to the SIF file.

    Returns
    -------
    str or None
        Version string if matched, else None.
    """
    m = _VERSION_RE.match(path.name)
    return m.group(1) if m else None


def _versioned_sifs(containers_dir: Path) -> list[Path]:
    """Return scitex-v*.sif paths sorted by modification time (newest first).

    Parameters
    ----------
    containers_dir : Path
        Directory containing SIF files.

    Returns
    -------
    list[Path]
        Sorted list of versioned SIF paths.
    """
    sifs = [
        p
        for p in containers_dir.glob("scitex-v*.sif")
        if _VERSION_RE.match(p.name) and p.is_file()
    ]
    sifs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return sifs


def list_versions(containers_dir: Path) -> list[dict]:
    """List all versioned SIFs with metadata.

    Parameters
    ----------
    containers_dir : Path
        Directory containing SIF files.

    Returns
    -------
    list[dict]
        Each dict contains keys: version, path, size, date, active.
        Sorted by modification time (newest first).
    """
    containers_dir = Path(containers_dir)
    active = get_active_version(containers_dir)
    results = []

    for sif in _versioned_sifs(containers_dir):
        version = _parse_version(sif)
        if version is None:
            continue
        stat = sif.stat()
        results.append(
            {
                "version": version,
                "path": str(sif),
                "size": _human_size(stat.st_size),
                "date": datetime.fromtimestamp(stat.st_mtime).strftime(
                    "%Y-%m-%d %H:%M"
                ),
                "active": version == active,
            }
        )

    return results


def get_active_version(containers_dir: Path) -> str | None:
    """Read current.sif symlink to determine active version.

    Parameters
    ----------
    containers_dir : Path
        Directory containing the current.sif symlink.

    Returns
    -------
    str or None
        Version string of the active SIF, or None if no symlink exists
        or it does not point to a valid versioned SIF.
    """
    containers_dir = Path(containers_dir)
    link = containers_dir / "current.sif"

    if not link.is_symlink():
        return None

    target = link.resolve()
    return _parse_version(target)


def switch_version(
    version: str,
    containers_dir: Path,
    use_sudo: bool = False,
) -> None:
    """Atomically switch current.sif symlink to scitex-v{version}.sif.

    Uses ``ln -sf`` to create a temporary symlink, then ``mv -Tf`` for an
    atomic rename on the same filesystem.

    Parameters
    ----------
    version : str
        Target version string (e.g. "2.19.5").
    containers_dir : Path
        Directory containing SIF files.
    use_sudo : bool
        If True, run ln/mv via sudo (needed for /opt/scitex paths).

    Raises
    ------
    FileNotFoundError
        If the target SIF does not exist.
    RuntimeError
        If the symlink switch fails.
    """
    containers_dir = Path(containers_dir)
    target_name = f"scitex-v{version}.sif"
    target_path = containers_dir / target_name
    link_path = containers_dir / "current.sif"

    if not target_path.exists():
        raise FileNotFoundError(f"Version {version} not found: {target_path}")

    # Temporary symlink name in the same directory (same filesystem)
    tmp_link = containers_dir / f".current.sif.tmp.{id(version)}"

    prefix = ["sudo"] if use_sudo else []

    try:
        # Create temp symlink pointing at target
        subprocess.run(
            [*prefix, "ln", "-sf", target_name, str(tmp_link)],
            check=True,
        )
        # Atomic rename over the real symlink
        subprocess.run(
            [*prefix, "mv", "-Tf", str(tmp_link), str(link_path)],
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        # Clean up temp link on failure
        tmp_link.unlink(missing_ok=True)
        raise RuntimeError(f"Failed to switch to version {version}: {exc}") from exc

    logger.info("Switched to version %s", version)


def rollback(
    containers_dir: Path,
    use_sudo: bool = False,
) -> str:
    """Switch to the version before the current one (by modification time).

    Parameters
    ----------
    containers_dir : Path
        Directory containing SIF files.
    use_sudo : bool
        If True, run symlink commands via sudo.

    Returns
    -------
    str
        Version string that is now active after rollback.

    Raises
    ------
    RuntimeError
        If there is no current version or no previous version to roll back to.
    """
    containers_dir = Path(containers_dir)
    active = get_active_version(containers_dir)

    if active is None:
        raise RuntimeError("No active version found; cannot rollback")

    sifs = _versioned_sifs(containers_dir)
    versions = [_parse_version(s) for s in sifs]

    try:
        idx = versions.index(active)
    except ValueError:
        raise RuntimeError(f"Active version {active} not found in directory")

    if idx + 1 >= len(versions):
        raise RuntimeError(
            f"No older version available to roll back to (current: {active})"
        )

    previous = versions[idx + 1]
    logger.info("Rolling back from %s to %s", active, previous)
    switch_version(previous, containers_dir, use_sudo=use_sudo)
    return previous


def deploy(
    source_dir: Path,
    target_dir: Path = Path("/opt/scitex/singularity"),
) -> None:
    """Copy active SIF and base SIF to target directory.

    Copies the currently active ``scitex-v*.sif`` and the latest
    ``scitex-base-v*.sif`` to *target_dir*, then recreates the
    ``current.sif`` symlink there. Uses sudo for the copy.

    Parameters
    ----------
    source_dir : Path
        Directory containing the built SIF files.
    target_dir : Path
        Deployment target directory (default: /opt/scitex/singularity).

    Raises
    ------
    RuntimeError
        If no active version is set or copy fails.
    FileNotFoundError
        If the active SIF or base SIF is missing.
    """
    source_dir = Path(source_dir)
    target_dir = Path(target_dir)

    active = get_active_version(source_dir)
    if active is None:
        raise RuntimeError("No active version in source directory")

    active_sif = source_dir / f"scitex-v{active}.sif"
    if not active_sif.exists():
        raise FileNotFoundError(f"Active SIF not found: {active_sif}")

    # Find latest base SIF by modification time
    base_sifs = sorted(
        (p for p in source_dir.glob("scitex-base-v*.sif") if p.is_file()),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    # Ensure target directory exists
    subprocess.run(
        ["sudo", "mkdir", "-p", str(target_dir)],
        check=True,
    )

    # Copy active SIF
    logger.info("Deploying %s to %s", active_sif.name, target_dir)
    subprocess.run(
        ["sudo", "cp", str(active_sif), str(target_dir / active_sif.name)],
        check=True,
    )

    # Copy base SIF if available
    if base_sifs:
        base_sif = base_sifs[0]
        logger.info("Deploying %s to %s", base_sif.name, target_dir)
        subprocess.run(
            ["sudo", "cp", str(base_sif), str(target_dir / base_sif.name)],
            check=True,
        )

    # Recreate symlink at target
    switch_version(active, target_dir, use_sudo=True)
    logger.info("Deploy complete: version %s", active)


def cleanup(
    containers_dir: Path,
    keep: int = 3,
) -> list[Path]:
    """Remove old scitex-v*.sif files, keeping the N most recent.

    Never removes the active version (current.sif target) or any
    ``scitex-base-v*.sif`` base images.

    Parameters
    ----------
    containers_dir : Path
        Directory containing SIF files.
    keep : int
        Number of most-recent versioned SIFs to keep (default: 3).

    Returns
    -------
    list[Path]
        Paths of removed SIF files.
    """
    containers_dir = Path(containers_dir)
    active = get_active_version(containers_dir)
    sifs = _versioned_sifs(containers_dir)  # newest first
    removed: list[Path] = []

    protected = set()
    if active is not None:
        protected.add(f"scitex-v{active}.sif")

    # Keep the top N by modification time
    kept = 0
    for sif in sifs:
        version = _parse_version(sif)
        if version is None:
            continue

        if sif.name in protected:
            # Active version is always kept and does not count toward limit
            continue

        if kept < keep:
            kept += 1
            continue

        # Remove
        logger.info("Removing old SIF: %s", sif.name)
        sif.unlink()
        removed.append(sif)

    return removed


# EOF
