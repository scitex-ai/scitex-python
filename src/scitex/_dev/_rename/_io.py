#!/usr/bin/env python3
# Timestamp: 2026-03-09
# File: scitex/_dev/_rename/_io.py

"""I/O helpers for bulk rename — with optional sudo escalation."""

from __future__ import annotations

import subprocess
from pathlib import Path

# Module-level sudo password cache (not serialized to output)
_sudo_password: str | None = None


def set_sudo_password(password: str | None) -> None:
    """Set the sudo password for non-interactive sudo -S calls."""
    global _sudo_password
    _sudo_password = password


def _sudo_run(cmd: list[str], input_data: bytes | None = None) -> None:
    """Run a command with sudo -S, piping password via stdin."""
    sudo_cmd = ["sudo", "-S"] + cmd
    stdin_data = input_data
    if _sudo_password:
        pw_bytes = (_sudo_password + "\n").encode()
        stdin_data = pw_bytes + (input_data or b"")
    subprocess.run(
        sudo_cmd,
        input=stdin_data,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )


def write_text(path: Path, content: str, use_sudo: bool = False) -> None:
    """Write text to file, optionally via sudo."""
    if not use_sudo:
        path.write_text(content)
        return
    _sudo_run(["tee", str(path)], input_data=content.encode())


def rename_path(src: Path, dst: Path, use_sudo: bool = False) -> None:
    """Rename (move) a path, optionally via sudo."""
    if not use_sudo:
        src.rename(dst)
        return
    _sudo_run(["mv", str(src), str(dst)])


def unlink_path(path: Path, use_sudo: bool = False) -> None:
    """Remove a file or symlink, optionally via sudo."""
    if not use_sudo:
        path.unlink()
        return
    _sudo_run(["rm", str(path)])


def mkdir(path: Path, parents: bool = False, use_sudo: bool = False) -> None:
    """Create directory, optionally via sudo."""
    if not use_sudo:
        path.mkdir(parents=parents, exist_ok=True)
        return
    cmd = ["mkdir"]
    if parents:
        cmd.append("-p")
    cmd.append(str(path))
    _sudo_run(cmd)


def rmdir(path: Path, use_sudo: bool = False) -> None:
    """Remove empty directory, optionally via sudo."""
    if not use_sudo:
        path.rmdir()
        return
    _sudo_run(["rmdir", str(path)])


def symlink_to(link: Path, target: str, use_sudo: bool = False) -> None:
    """Create a symlink, optionally via sudo."""
    if not use_sudo:
        link.symlink_to(target)
        return
    _sudo_run(["ln", "-s", target, str(link)])


# EOF
