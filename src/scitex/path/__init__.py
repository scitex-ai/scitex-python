#!/usr/bin/env python3
"""SciTeX path module — delegates to scitex-path."""

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
