#!/usr/bin/env python3
# Timestamp: 2026-02-14
# File: scitex/_dev/_rename/_config.py

"""Configuration dataclasses for bulk rename operations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RenameConfig:
    """Configuration for bulk rename operations."""

    pattern: str
    replacement: str
    directory: str = "."
    dry_run: bool = True
    django_safe: bool = True
    create_backup: bool = False
    # PATH-level filtering
    path_includes: str = (
        "py,txt,sh,md,yaml,toml,cfg,ini,json,html,css,ts,js,tsx,jsx,scss,less,svg,xml"
    )
    path_excludes: str = "__pycache__,staticfiles,node_modules,.git,venv,.venv"
    path_must_excludes: str = ".old,old,legacy,archive,backup,.backup,migrations"
    # SRC-level filtering
    src_excludes: str = "db_table=,related_name=,table=,name=,old_name=,new_name="
    src_must_excludes: str = ""
    extra_excludes: list[str] = field(default_factory=list)


@dataclass
class RenameResult:
    """Result of a bulk rename operation."""

    dry_run: bool
    pattern: str
    replacement: str
    directory: str
    contents: list[dict[str, Any]]
    symlink_targets: list[dict[str, Any]]
    symlink_names: list[dict[str, Any]]
    file_names: list[dict[str, Any]]
    dir_names: list[dict[str, Any]]
    summary: dict[str, Any]
    collisions: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None


# EOF
