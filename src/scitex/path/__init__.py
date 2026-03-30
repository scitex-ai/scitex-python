#!/usr/bin/env python3
# File: src/scitex/path/__init__.py
"""SciTeX path module — delegates to scitex-path (single source of truth)."""

from scitex_path import (
    clean,
    create_relative_symlink,
    find_dir,
    find_file,
    find_git_root,
    find_latest,
    fix_broken_symlinks,
    get_data_path_from_a_package,
    get_spath,
    get_this_path,
    getsize,
    increment_version,
    is_symlink,
    list_symlinks,
    mk_spath,
    readlink,
    resolve_symlinks,
    split,
    symlink,
    this_path,
    unlink_symlink,
)

__all__ = [
    "clean",
    "create_relative_symlink",
    "find_dir",
    "find_file",
    "find_git_root",
    "find_latest",
    "fix_broken_symlinks",
    "get_data_path_from_a_package",
    "get_spath",
    "get_this_path",
    "getsize",
    "increment_version",
    "is_symlink",
    "list_symlinks",
    "mk_spath",
    "readlink",
    "resolve_symlinks",
    "split",
    "symlink",
    "this_path",
    "unlink_symlink",
]

# EOF
