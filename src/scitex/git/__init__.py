"""SciTeX git — thin compatibility shim for scitex-git.

Every public name that used to live in ``scitex.git`` now lives in the
standalone ``scitex-git`` package (module ``scitex_git``). This file
aliases ``scitex.git`` to ``scitex_git`` via ``sys.modules`` so every
previous import path keeps resolving (``scitex.git is scitex_git``).

Public API:
    Init / discovery: init_git_repo, find_parent_git, create_child_git, remove_child_git
    Clone / init:     clone_repo, git_init
    Stage / commit:   git_add_all, git_commit
    Branch ops:       git_branch_rename, git_checkout_new_branch, setup_branches
    Remote helpers:   get_remote_url, is_cloned_from, ls_remote, get_head_hash
    Retry decorator:  git_retry

Install: ``pip install scitex[git]``  (or ``pip install scitex-git``).
See: https://github.com/ywatanabe1989/scitex-git
"""

import sys as _sys

try:
    import scitex_git as _real
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "scitex.git requires the 'scitex-git' package. "
        "Install with: pip install scitex[git]  (or: pip install scitex-git)"
    ) from _e

_sys.modules[__name__] = _real
