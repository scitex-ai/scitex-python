#!/usr/bin/env python3
# Timestamp: 2026-02-14
# File: scitex/_dev/_rename/_filters.py

"""Filtering logic for bulk rename operations (PATH and SRC level)."""

from __future__ import annotations

import re
from pathlib import Path

from ._config import RenameConfig


def parse_csv_config(value: str) -> list[str]:
    """Parse comma-separated config string into list."""
    return [v.strip() for v in value.split(",") if v.strip()]


def should_exclude_path(path: Path, config: RenameConfig) -> bool:
    """Check if a path should be excluded based on config."""
    path_str = str(path)
    parts = path.parts

    # Must-excludes (strongest) - exact directory name match
    for exc in parse_csv_config(config.path_must_excludes):
        if exc in parts:
            return True

    # Standard excludes - exact directory name match
    for exc in parse_csv_config(config.path_excludes):
        if exc in parts:
            return True

    # Extra excludes from user
    for exc in config.extra_excludes:
        if exc in path_str:
            return True

    return False


def matches_include_extensions(path: Path, config: RenameConfig) -> bool:
    """Check if file extension matches include list."""
    includes = parse_csv_config(config.path_includes)
    if not includes:
        return True

    suffix = path.suffix.lstrip(".")
    name = path.name

    for inc in includes:
        if suffix == inc:
            return True
        if inc.startswith(".") and name.startswith(inc):
            return True
        if "*" in inc:
            import fnmatch

            if fnmatch.fnmatch(name, inc):
                return True

    return False


def find_matching_files(
    directory: str, config: RenameConfig, need_content_match: bool = False
) -> list[Path]:
    """Find files matching the filtering criteria."""
    root = Path(directory)
    matching = []

    for path in root.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        if should_exclude_path(path, config):
            continue
        if not matches_include_extensions(path, config):
            continue
        if need_content_match:
            try:
                content = path.read_text(errors="replace")
                if config.pattern not in content:
                    continue
            except (OSError, UnicodeDecodeError):
                continue
        matching.append(path)

    return matching


def is_django_protected_line(line: str, pattern: str) -> bool:
    """Check if a line should be protected in Django-safe mode."""
    if re.search(r"db_table\s*=\s*['\"]", line):
        return True
    if re.search(r"(old_name|new_name)\s*=\s*['\"]", line):
        return True
    if re.search(r"related_name\s*=\s*['\"]", line):
        return True
    if re.search(r"objects\s*=\s*.*Manager", line):
        return True
    settings_patterns = (
        "INSTALLED_APPS",
        "DATABASES",
        "CACHES",
        "SECRET_KEY",
        "DEBUG",
        "ALLOWED_HOSTS",
        "MIDDLEWARE",
        "TEMPLATES",
    )
    stripped = line.lstrip()
    for sp in settings_patterns:
        if stripped.startswith(sp):
            return True
    if re.search(r"(django|Django).*\d+\.\d+", line):
        return True
    return False


def is_src_excluded(line: str, config: RenameConfig) -> bool:
    """Check if a line matches SRC-level exclusion patterns."""
    for exc in parse_csv_config(config.src_must_excludes):
        if exc in line:
            return True
    for exc in parse_csv_config(config.src_excludes):
        if exc in line:
            return True
    return False


# EOF
