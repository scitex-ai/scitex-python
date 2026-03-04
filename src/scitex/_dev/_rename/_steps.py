#!/usr/bin/env python3
# Timestamp: 2026-02-14
# File: scitex/_dev/_rename/_steps.py

"""Five-step execution order for bulk rename operations."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from ._config import RenameConfig
from ._filters import (
    find_matching_files,
    is_django_protected_line,
    is_src_excluded,
    should_exclude_path,
)


def rename_file_contents(config: RenameConfig, directory: str) -> list[dict[str, Any]]:
    """Step 0: Replace pattern in file contents."""
    files = find_matching_files(directory, config, need_content_match=True)
    results = []

    for file_path in files:
        try:
            content = file_path.read_text(errors="replace")
        except (OSError, UnicodeDecodeError):
            continue

        lines = content.split("\n")
        matches = 0
        protected = 0
        new_lines = []

        for line in lines:
            if config.pattern in line:
                should_protect = False
                if config.django_safe and is_django_protected_line(
                    line, config.pattern
                ):
                    should_protect = True
                if is_src_excluded(line, config):
                    should_protect = True

                if should_protect:
                    protected += 1
                    new_lines.append(line)
                else:
                    matches += line.count(config.pattern)
                    new_lines.append(line.replace(config.pattern, config.replacement))
            else:
                new_lines.append(line)

        if matches > 0:
            if not config.dry_run:
                file_path.write_text("\n".join(new_lines))

            results.append(
                {
                    "file": str(file_path),
                    "matches": matches,
                    "protected": protected,
                }
            )

    return results


def update_symlink_targets(
    config: RenameConfig, directory: str
) -> list[dict[str, Any]]:
    """Step 1: Update symlink targets to point to future paths."""
    root = Path(directory)
    results = []

    for path in root.rglob("*"):
        if not path.is_symlink():
            continue
        if should_exclude_path(path, config):
            continue

        target = os.readlink(str(path))
        if config.pattern in target:
            new_target = target.replace(config.pattern, config.replacement)

            if not config.dry_run:
                path.unlink()
                path.symlink_to(new_target)

            results.append(
                {
                    "link": str(path),
                    "old_target": target,
                    "new_target": new_target,
                }
            )

    return results


def rename_symlink_names(config: RenameConfig, directory: str) -> list[dict[str, Any]]:
    """Step 2: Rename symlink basenames."""
    root = Path(directory)
    results = []

    for path in root.rglob("*"):
        if not path.is_symlink():
            continue
        if should_exclude_path(path, config):
            continue

        name = path.name
        if config.pattern in name:
            new_name = name.replace(config.pattern, config.replacement)
            new_path = path.parent / new_name
            target_exists = new_path.exists() and new_path != path

            if not config.dry_run:
                path.rename(new_path)

            results.append(
                {
                    "old_name": str(path),
                    "new_name": str(new_path),
                    "target_exists": target_exists,
                }
            )

    return results


def rename_file_names(config: RenameConfig, directory: str) -> list[dict[str, Any]]:
    """Step 3: Rename file basenames."""
    files = find_matching_files(directory, config)
    results = []

    for file_path in files:
        name = file_path.name
        if config.pattern in name:
            new_name = name.replace(config.pattern, config.replacement)
            new_path = file_path.parent / new_name
            target_exists = new_path.exists() and new_path != file_path

            if not config.dry_run:
                file_path.rename(new_path)

            results.append(
                {
                    "old_path": str(file_path),
                    "new_path": str(new_path),
                    "target_exists": target_exists,
                }
            )

    return results


def _merge_directory(src: Path, dst: Path) -> int:
    """Move all children from src into dst, then remove empty src.

    Returns number of items moved.
    """
    moved = 0
    for child in list(src.iterdir()):
        target = dst / child.name
        if child.is_dir() and target.is_dir():
            moved += _merge_directory(child, target)
        else:
            if target.exists():
                target.unlink()
            child.rename(target)
            moved += 1
    # Remove src if now empty
    if src.exists() and not any(src.iterdir()):
        src.rmdir()
    return moved


def rename_directory_names(
    config: RenameConfig, directory: str
) -> list[dict[str, Any]]:
    """Step 4: Rename directories (deepest first).

    Matches pattern against both:
    - Leaf directory name (e.g., 'js')
    - Relative path from root (e.g., 'static/scholar_app/js')
    This enables patterns like 'scholar_app/js' to match path segments.

    When target directory exists, merges contents into it.
    """
    root = Path(directory)
    results = []

    dirs = []
    for path in root.rglob("*"):
        if path.is_dir() and not path.is_symlink():
            if should_exclude_path(path, config):
                continue
            rel_path = str(path.relative_to(root))
            if config.pattern in path.name or config.pattern in rel_path:
                dirs.append(path)

    dirs.sort(key=lambda p: len(p.parts), reverse=True)

    for dir_path in dirs:
        if not dir_path.exists():
            continue  # already moved by parent merge
        if config.pattern in dir_path.name:
            new_name = dir_path.name.replace(config.pattern, config.replacement)
            new_path = dir_path.parent / new_name
        else:
            rel = str(dir_path.relative_to(root))
            new_rel = rel.replace(config.pattern, config.replacement)
            new_path = root / new_rel
        target_exists = new_path.exists() and new_path != dir_path

        if not config.dry_run:
            new_path.parent.mkdir(parents=True, exist_ok=True)
            if target_exists:
                _merge_directory(dir_path, new_path)
            else:
                dir_path.rename(new_path)

        results.append(
            {
                "old_path": str(dir_path),
                "new_path": str(new_path),
                "target_exists": target_exists,
                "merged": target_exists,
            }
        )

    return results


# EOF
