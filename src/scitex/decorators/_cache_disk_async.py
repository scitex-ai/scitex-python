#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-09 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/decorators/_cache_disk_async.py
# ----------------------------------------
from __future__ import annotations

import os

__FILE__ = "./src/scitex/decorators/_cache_disk_async.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""Async disk caching decorator using joblib.Memory."""

import asyncio
import functools

from scitex.config import get_paths


def cache_disk_async(func):
    """Disk caching decorator for async functions.

    joblib is lazy-imported inside the decorator body so that ``import
    scitex.decorators`` does not fail on venvs without joblib (todo#442,
    same class as #441 / #279). Without this, the eager top-level
    ``from joblib import Memory`` propagates ``ModuleNotFoundError`` up
    the ``scitex.io`` import chain and breaks unrelated callers.

    Usage:
        @cache_disk_async
        async def expensive_async_function(x):
            await asyncio.sleep(1)
            return x ** 2
    """
    cache_dir = str(get_paths().function_cache)
    from joblib import Memory as _Memory  # lazy: see todo#442

    memory = _Memory(cache_dir, verbose=0)

    # Create sync wrapper for joblib
    def sync_wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    cached_sync = memory.cache(sync_wrapper)

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        # Run cached sync version in executor to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: cached_sync(*args, **kwargs))
        return result

    return async_wrapper


# EOF
