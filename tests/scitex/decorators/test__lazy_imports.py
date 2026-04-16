#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: tests/scitex/decorators/test__lazy_imports.py

"""Regression tests for the joblib eager-import leak (todo#442).

The bug: pre-fix, ``import scitex.decorators`` (and the transitive
``import scitex.io`` chain) raised ``ModuleNotFoundError: No module
named 'joblib'`` whenever joblib wasn't installed in the venv, because
``_cache_disk.py`` and ``_cache_disk_async.py`` had top-level
``from joblib import Memory as _Memory``.

The fix: joblib is lazy-imported inside ``cache_disk()`` /
``cache_disk_async()`` function bodies only. ``import scitex.decorators``
must succeed without joblib; only constructing the decorator (= calling
it on a target function) requires joblib.

Same class of bug as #441 (flask), #279 (bs4), #443 (matplotlib).

This test file is intentionally separate from ``test__cache_disk.py``
because the latter eager-imports ``joblib.Memory`` for legacy tests and
gets skipped wholesale on no-joblib venvs — defeating the regression
guard. The tests below run unconditionally and only inspect module
source for the offending top-level import lines.
"""

from __future__ import annotations

import inspect


def test_cache_disk_module_has_no_top_level_joblib_import():
    """``_cache_disk.py`` must not import joblib at module scope."""
    from scitex.decorators import _cache_disk as mod

    src = inspect.getsource(mod)
    for lineno, line in enumerate(src.splitlines(), 1):
        if line.startswith("from joblib") or line.startswith("import joblib"):
            raise AssertionError(
                f"Top-level joblib import re-introduced in _cache_disk.py "
                f"at line {lineno}: {line!r}.\n"
                "Lazy-import inside cache_disk() is required to keep "
                "`import scitex.decorators` working on venvs without "
                "joblib (todo#442)."
            )


def test_cache_disk_async_module_has_no_top_level_joblib_import():
    """``_cache_disk_async.py`` must not import joblib at module scope."""
    from scitex.decorators import _cache_disk_async as mod

    src = inspect.getsource(mod)
    for lineno, line in enumerate(src.splitlines(), 1):
        if line.startswith("from joblib") or line.startswith("import joblib"):
            raise AssertionError(
                f"Top-level joblib import re-introduced in "
                f"_cache_disk_async.py at line {lineno}: {line!r}.\n"
                "Lazy-import inside cache_disk_async() is required "
                "(todo#442)."
            )


def test_import_scitex_decorators_does_not_require_joblib():
    """The package ``scitex.decorators`` must import without joblib.

    This is the contract surfaced by todo#442. We assert by inspection
    on the decorator source files (above) rather than runtime mocking,
    because pytest's import system does not let us cleanly re-import
    a module that the test runner has already loaded earlier in the
    session. Source inspection is a sufficient regression guard: if
    no top-level joblib import exists in either file, the contract
    holds at import time.
    """
    # Sanity: importing the package itself must not raise. (It may have
    # already been imported in an earlier test; that's fine.)
    import scitex.decorators  # noqa: F401


# EOF
