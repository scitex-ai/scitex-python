#!/usr/bin/env python3
# File: src/scitex/repro/__init__.py
"""SciTeX repro module — delegates to scitex-repro (single source of truth).

Provides tools for reproducible scientific computing:
- Random state management (RandomStateManager)
- ID generation (gen_ID)
- Timestamp generation (gen_timestamp)
- Array hashing (hash_array)
"""

from scitex_repro import (
    RandomStateManager,
    gen_ID,
    gen_id,
    gen_timestamp,
    get,
    hash_array,
    reset,
    timestamp,
)


# Legacy function for backward compatibility (user-confirmed fallback)
def fix_seeds(
    seed=42,
    os=True,
    random=True,
    np=True,
    torch=True,
    tf=False,
    jax=False,
    verbose=False,
    **kwargs,
):
    """
    Deprecated: Use stx.repro.RandomStateManager instead.

    This function maintains backward compatibility with the old fix_seeds API.
    """
    import warnings

    warnings.warn(
        "fix_seeds is deprecated. Use stx.repro.RandomStateManager instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    # Create RandomStateManager with seed and verbose
    # It automatically handles all available modules
    return RandomStateManager(seed=seed, verbose=verbose)


__all__ = [
    # ID and timestamp utilities
    "gen_ID",
    "gen_id",
    "gen_timestamp",
    "timestamp",
    # Hash utilities
    "hash_array",
    # Random state management
    "RandomStateManager",
    "get",
    "reset",
    # Legacy (deprecated)
    "fix_seeds",
]

# EOF
