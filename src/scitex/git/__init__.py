#!/usr/bin/env python3
# File: /home/ywatanabe/proj/scitex-code/src/scitex/git/__init__.py

"""
Git operations and utilities.
"""

from ._branch import git_branch_rename, git_checkout_new_branch
from ._clone import clone_repo, git_init
from ._commit import git_add_all, git_commit
from ._init import create_child_git, find_parent_git, init_git_repo, remove_child_git
from ._remote import get_head_hash, get_remote_url, is_cloned_from, ls_remote
from ._retry import git_retry
from ._workflow import setup_branches

__all__ = [
    "init_git_repo",
    "find_parent_git",
    "create_child_git",
    "remove_child_git",
    "clone_repo",
    "git_init",
    "git_add_all",
    "git_commit",
    "git_branch_rename",
    "git_checkout_new_branch",
    "get_remote_url",
    "is_cloned_from",
    "ls_remote",
    "get_head_hash",
    "setup_branches",
    "git_retry",
]

# EOF
