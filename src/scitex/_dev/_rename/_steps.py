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
from ._io import (
    mkdir as _mkdir,
)
from ._io import (
    rename_path as _rename_path,
)
from ._io import (
    rmdir as _rmdir,
)
from ._io import (
    symlink_to as _symlink_to,
)
from ._io import (
    unlink_path as _unlink_path,
)
from ._io import (
    write_text as _write_text,
)


def _should_skip(item_id: str, skip_ids: list[str]) -> bool:
    """Check whether an item should be skipped based on skip_ids."""
    return item_id in skip_ids


def rename_file_contents(config: RenameConfig, directory: str) -> list[dict[str, Any]]:
    """Step 0: Replace pattern in file contents."""
    files = find_matching_files(directory, config, need_content_match=True)
    results = []

    for i, file_path in enumerate(files):
        file_id = f"c-{i:03d}"

        try:
            content = file_path.read_text(errors="replace")
        except (OSError, UnicodeDecodeError):
            continue

        # Skip entire file if file-level ID is in skip_ids
        skip_entire_file = _should_skip(file_id, config.skip_ids)

        lines = content.split("\n")
        matches = 0
        protected = 0
        new_lines = []
        line_details: list[dict[str, Any]] = []

        for line_num, line in enumerate(lines, 1):
            if config.pattern in line:
                line_id = f"{file_id}-L{line_num}"
                skip_this_line = skip_entire_file or _should_skip(
                    line_id, config.skip_ids
                )

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
                    if config.dry_run and len(line_details) < 20:
                        line_details.append(
                            {
                                "id": line_id,
                                "line_num": line_num,
                                "action": "protect",
                                "before": line,
                                "after": line,
                            }
                        )
                elif skip_this_line:
                    # Skipped by skip_ids -- keep original line
                    new_lines.append(line)
                    if config.dry_run and len(line_details) < 20:
                        line_details.append(
                            {
                                "id": line_id,
                                "line_num": line_num,
                                "action": "skip",
                                "before": line,
                                "after": line,
                            }
                        )
                else:
                    matches += line.count(config.pattern)
                    replaced = line.replace(config.pattern, config.replacement)
                    new_lines.append(replaced)
                    if config.dry_run and len(line_details) < 20:
                        line_details.append(
                            {
                                "id": line_id,
                                "line_num": line_num,
                                "action": "replace",
                                "before": line,
                                "after": replaced,
                            }
                        )
            else:
                new_lines.append(line)

        if matches > 0:
            if not config.dry_run and not skip_entire_file:
                _write_text(file_path, "\n".join(new_lines), config.use_sudo)

            entry: dict[str, Any] = {
                "id": file_id,
                "file": str(file_path),
                "matches": matches,
                "protected": protected,
            }
            if config.dry_run:
                entry["lines"] = line_details

            results.append(entry)

    return results


def update_symlink_targets(
    config: RenameConfig, directory: str
) -> list[dict[str, Any]]:
    """Step 1: Update symlink targets to point to future paths."""
    root = Path(directory)
    results = []
    idx = 0

    for path in sorted(root.rglob("*")):
        if not path.is_symlink():
            continue
        if should_exclude_path(path, config):
            continue

        target = os.readlink(str(path))
        if config.pattern in target:
            item_id = f"st-{idx:03d}"
            new_target = target.replace(config.pattern, config.replacement)

            if not config.dry_run and not _should_skip(item_id, config.skip_ids):
                _unlink_path(path, config.use_sudo)
                _symlink_to(path, new_target, config.use_sudo)

            results.append(
                {
                    "id": item_id,
                    "link": str(path),
                    "old_target": target,
                    "new_target": new_target,
                }
            )
            idx += 1

    return results


def rename_symlink_names(config: RenameConfig, directory: str) -> list[dict[str, Any]]:
    """Step 2: Rename symlink basenames."""
    root = Path(directory)
    results = []
    idx = 0

    for path in sorted(root.rglob("*")):
        if not path.is_symlink():
            continue
        if should_exclude_path(path, config):
            continue

        name = path.name
        if config.pattern in name:
            item_id = f"sn-{idx:03d}"
            new_name = name.replace(config.pattern, config.replacement)
            new_path = path.parent / new_name
            target_exists = new_path.exists() and new_path != path

            if not config.dry_run and not _should_skip(item_id, config.skip_ids):
                _rename_path(path, new_path, config.use_sudo)

            results.append(
                {
                    "id": item_id,
                    "old_name": str(path),
                    "new_name": str(new_path),
                    "target_exists": target_exists,
                }
            )
            idx += 1

    return results


def rename_file_names(config: RenameConfig, directory: str) -> list[dict[str, Any]]:
    """Step 3: Rename file basenames."""
    files = find_matching_files(directory, config)
    results = []
    idx = 0

    for file_path in files:
        name = file_path.name
        if config.pattern in name:
            item_id = f"f-{idx:03d}"
            new_name = name.replace(config.pattern, config.replacement)
            new_path = file_path.parent / new_name
            target_exists = new_path.exists() and new_path != file_path

            if not config.dry_run and not _should_skip(item_id, config.skip_ids):
                _rename_path(file_path, new_path, config.use_sudo)

            results.append(
                {
                    "id": item_id,
                    "old_path": str(file_path),
                    "new_path": str(new_path),
                    "target_exists": target_exists,
                }
            )
            idx += 1

    return results


def _merge_directory(src: Path, dst: Path, use_sudo: bool = False) -> int:
    """Move all children from src into dst, then remove empty src.

    Returns number of items moved.
    """
    moved = 0
    for child in list(src.iterdir()):
        target = dst / child.name
        if child.is_dir() and target.is_dir():
            moved += _merge_directory(child, target, use_sudo)
        else:
            if target.exists():
                _unlink_path(target, use_sudo)
            _rename_path(child, target, use_sudo)
            moved += 1
    # Remove src if now empty
    if src.exists() and not any(src.iterdir()):
        _rmdir(src, use_sudo)
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

    for idx, dir_path in enumerate(dirs):
        item_id = f"d-{idx:03d}"

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

        if not config.dry_run and not _should_skip(item_id, config.skip_ids):
            _mkdir(new_path.parent, parents=True, use_sudo=config.use_sudo)
            if target_exists:
                _merge_directory(dir_path, new_path, config.use_sudo)
            else:
                _rename_path(dir_path, new_path, config.use_sudo)

        results.append(
            {
                "id": item_id,
                "old_path": str(dir_path),
                "new_path": str(new_path),
                "target_exists": target_exists,
                "merged": target_exists,
            }
        )

    return results


# EOF
