#!/usr/bin/env python3
# Timestamp: 2026-02-14
# File: scitex/_dev/_rename/_core.py

"""Core orchestration for bulk rename operations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ._config import RenameConfig, RenameResult
from ._safety import check_directory_safety, create_backup, has_uncommitted_changes
from ._steps import (
    rename_directory_names,
    rename_file_contents,
    rename_file_names,
    rename_symlink_names,
    update_symlink_targets,
)


def _make_error_result(
    pattern: str, replacement: str, directory: str, error: str
) -> RenameResult:
    """Create an error RenameResult."""
    return RenameResult(
        dry_run=False,
        pattern=pattern,
        replacement=replacement,
        directory=directory,
        contents=[],
        symlink_targets=[],
        symlink_names=[],
        file_names=[],
        dir_names=[],
        summary={},
        error=error,
    )


def preview_rename(
    pattern: str,
    replacement: str,
    directory: str = ".",
    django_safe: bool = True,
    extra_excludes: list[str] | None = None,
    **kwargs: Any,
) -> RenameResult:
    """Preview rename changes without executing (dry run).

    Parameters
    ----------
    pattern : str
        Pattern to search for.
    replacement : str
        String to replace matches with.
    directory : str
        Target directory.
    django_safe : bool
        Enable Django-safe mode.
    extra_excludes : list of str, optional
        Additional exclude patterns.

    Returns
    -------
    RenameResult
        Preview of all changes that would be made.
    """
    config = RenameConfig(
        pattern=pattern,
        replacement=replacement,
        directory=directory,
        dry_run=True,
        django_safe=django_safe,
        extra_excludes=extra_excludes or [],
        **kwargs,
    )
    return bulk_rename(config)


def execute_rename(
    pattern: str,
    replacement: str,
    directory: str = ".",
    django_safe: bool = True,
    create_backup: bool = False,
    extra_excludes: list[str] | None = None,
    force: bool = False,
    **kwargs: Any,
) -> RenameResult:
    """Execute rename with safety checks.

    Checks for uncommitted git changes before proceeding.

    Parameters
    ----------
    pattern : str
        Pattern to search for.
    replacement : str
        String to replace matches with.
    directory : str
        Target directory.
    django_safe : bool
        Enable Django-safe mode.
    create_backup : bool
        Create backup before changes.
    extra_excludes : list of str, optional
        Additional exclude patterns.
    force : bool
        Skip uncommitted changes check (default False).

    Returns
    -------
    RenameResult
        Results of the rename operation.
    """
    if not force and has_uncommitted_changes(directory):
        return _make_error_result(
            pattern,
            replacement,
            directory,
            "Uncommitted changes detected. Commit or stash first.",
        )

    config = RenameConfig(
        pattern=pattern,
        replacement=replacement,
        directory=directory,
        dry_run=False,
        django_safe=django_safe,
        create_backup=create_backup,
        extra_excludes=extra_excludes or [],
        **kwargs,
    )
    return bulk_rename(config)


def bulk_rename(config: RenameConfig) -> RenameResult:
    """Execute bulk rename operation.

    Parameters
    ----------
    config : RenameConfig
        Configuration for the rename operation.

    Returns
    -------
    RenameResult
        Results including all changes made or previewed.
    """
    directory = str(Path(config.directory).resolve())

    # Safety: block dangerous directories and require git for live runs
    if not config.dry_run:
        safety_error = check_directory_safety(directory)
        if safety_error:
            return _make_error_result(
                config.pattern,
                config.replacement,
                directory,
                safety_error,
            )

    if config.create_backup and not config.dry_run:
        create_backup(directory, config.pattern, config.replacement)

    # Dry-run pass to detect collisions before any changes
    if not config.dry_run:
        dry_config = RenameConfig(
            pattern=config.pattern,
            replacement=config.replacement,
            directory=config.directory,
            dry_run=True,
            django_safe=config.django_safe,
            path_includes=config.path_includes,
            path_excludes=config.path_excludes,
            path_must_excludes=config.path_must_excludes,
            src_excludes=config.src_excludes,
            src_must_excludes=config.src_must_excludes,
            extra_excludes=config.extra_excludes,
        )
        preview = bulk_rename(dry_config)
        # Block file/symlink collisions; directory collisions are handled via merge
        non_dir_collisions = [
            c for c in preview.collisions if c.get("type") != "directory"
        ]
        if non_dir_collisions:
            return _make_error_result(
                config.pattern,
                config.replacement,
                directory,
                f"Collisions detected: {len(non_dir_collisions)} target(s) already exist. "
                "Run dry-run to inspect.",
            )

    # Execute in order (critical for path integrity)
    contents = rename_file_contents(config, directory)
    symlink_targets = update_symlink_targets(config, directory)
    symlink_names = rename_symlink_names(config, directory)
    file_names = rename_file_names(config, directory)
    dir_names = rename_directory_names(config, directory)

    # Collect collisions from path-renaming steps
    collisions = []
    for item in symlink_names:
        if item.get("target_exists"):
            collisions.append({"type": "symlink", "path": item["new_name"]})
    for item in file_names:
        if item.get("target_exists"):
            collisions.append({"type": "file", "path": item["new_path"]})
    for item in dir_names:
        if item.get("target_exists"):
            collisions.append({"type": "directory", "path": item["new_path"]})

    summary = {
        "content_files": len(contents),
        "content_matches": sum(c.get("matches", 0) for c in contents),
        "content_protected": sum(c.get("protected", 0) for c in contents),
        "symlink_targets_updated": len(symlink_targets),
        "symlinks_renamed": len(symlink_names),
        "files_renamed": len(file_names),
        "dirs_renamed": len(dir_names),
        "collisions": len(collisions),
    }

    return RenameResult(
        dry_run=config.dry_run,
        pattern=config.pattern,
        replacement=config.replacement,
        directory=directory,
        contents=contents,
        symlink_targets=symlink_targets,
        symlink_names=symlink_names,
        file_names=file_names,
        dir_names=dir_names,
        summary=summary,
        collisions=collisions,
    )


# EOF
