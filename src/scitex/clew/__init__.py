#!/usr/bin/env python3
# Timestamp: "2026-02-01 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/verify/__init__.py
"""
SciTeX Clew Module - Hash-based verification for reproducible science.

This module provides tools to track, verify, and visualize the reproducibility
of scientific computations through cryptographic hashing.

Core Concepts
-------------
- **Run**: A single execution of a script with tracked inputs/outputs
- **Hash**: SHA256 fingerprint of files to detect changes
- **Chain**: Dependency links between runs (parent → child)
- **Verification**: Comparing stored hashes with current file states

Verification Levels
-------------------
- **verified-by-cache** (✓): Fast comparison of stored vs current hashes
- **verified-by-rerun** (✓✓): Full re-execution and comparison (slower, more thorough)

Examples
--------
>>> import scitex as stx

>>> # Automatic tracking via @stx.session + stx.io
>>> @stx.session
... def main():
...     data = stx.io.load("input.csv")   # Auto-tracked as input
...     result = process(data)
...     stx.io.save(result, "output.png") # Auto-tracked as output

>>> # Manual verification
>>> stx.clew.status()                     # Show changed files
>>> stx.clew.run("session_id")            # Verify specific run
>>> stx.clew.chain("output.png")          # Trace back to source

CLI Commands
------------
- ``scitex clew list`` - List all runs with verification status
- ``scitex clew run <id>`` - Verify specific run
- ``scitex clew chain <file>`` - Trace dependencies back to source
- ``scitex clew status`` - Show changed items (git status-like)

MCP Tools
---------
- ``verify_list`` - List runs
- ``verify_run`` - Verify specific run
- ``verify_chain`` - Trace chain
- ``verify_status`` - Show changes
"""

from __future__ import annotations

# Chain verification
from ._chain import (
    ChainVerification,
    DAGVerification,
    FileVerification,
    RunVerification,
    VerificationLevel,
    VerificationStatus,
    get_status,
    verify_chain,
    verify_file,
    verify_run,
)

# Claims
from ._claim import (
    Claim,
    add_claim,
    format_claims,
    list_claims,
    verify_claim,
    verify_claims_dag,
)

# DAG verification
from ._dag import verify_dag

# Database
from ._db import VerificationDB, get_db, set_db

# Examples
from ._examples import init_examples

# Hash utilities
from ._hash import combine_hashes, hash_directory, hash_file, hash_files, verify_hash

# Integration hooks
from ._integration import on_io_load, on_io_save, on_session_close, on_session_start

# Registry client
from ._registry import ClewRegistry, get_registry

# Rerun verification (separate module to avoid circular imports)
from ._rerun import verify_by_rerun, verify_run_from_scratch

# Stamping
from ._stamp import Stamp, check_stamp, list_stamps, stamp

# Tracker
from ._tracker import (
    SessionTracker,
    get_tracker,
    set_tracker,
    start_tracking,
    stop_tracking,
)

# Visualization
from ._visualize import (
    format_chain_verification,
    format_list,
    format_run_detailed,
    format_run_verification,
    format_status,
    generate_html_dag,
    generate_mermaid_dag,
    print_verification_summary,
    render_dag,
)


# Convenience functions at module level
def list_runs(limit: int = 100, status: str = None):
    """List tracked runs."""
    db = get_db()
    return db.list_runs(status=status, limit=limit)


def status():
    """Get verification status summary (like git status)."""
    return get_status()


def run(session_id: str, from_scratch: bool = False):
    """Verify a specific run.

    Parameters
    ----------
    session_id : str
        Session identifier
    from_scratch : bool, optional
        If True, re-execute the script and verify outputs (slow but thorough).
        If False, only compare hashes (fast).
    """
    if from_scratch:
        return verify_run_from_scratch(session_id)
    return verify_run(session_id)


def chain(target: str):
    """Verify the chain for a target file."""
    return verify_chain(target)


def stats():
    """Get database statistics."""
    db = get_db()
    return db.stats()


def dag(targets=None, claims=False):
    """Verify the DAG for multiple targets or all claims."""
    if claims:
        return verify_claims_dag()
    return verify_dag(targets or [])


def register(hash_value: str, source_type: str = "manual", **kwargs):
    """Register a hash with the remote Clew Registry on scitex.ai.

    Parameters
    ----------
    hash_value : str
        The hash to register (SHA256, up to 64 chars).
    source_type : str
        One of: session, file, stamp, manual.
    **kwargs
        Additional arguments passed to ClewRegistry.register().
    """
    return get_registry().register(hash_value, source_type=source_type, **kwargs)


def verify_remote(hash_value: str):
    """Verify a hash against the remote Clew Registry.

    Parameters
    ----------
    hash_value : str
        The hash to verify.

    Returns
    -------
    dict
        {registered: bool, registrations: [...]}
    """
    return get_registry().verify(hash_value)


__all__ = [
    # Hash utilities
    "hash_file",
    "hash_files",
    "hash_directory",
    "combine_hashes",
    "verify_hash",
    # Database
    "VerificationDB",
    "get_db",
    "set_db",
    # Tracker
    "SessionTracker",
    "get_tracker",
    "set_tracker",
    "start_tracking",
    "stop_tracking",
    # Chain verification
    "VerificationStatus",
    "VerificationLevel",
    "FileVerification",
    "RunVerification",
    "ChainVerification",
    "DAGVerification",
    "verify_file",
    "verify_run",
    "verify_by_rerun",
    "verify_run_from_scratch",  # backward compat alias
    "verify_chain",
    "verify_dag",
    "get_status",
    # Claims
    "Claim",
    "add_claim",
    "list_claims",
    "verify_claim",
    "verify_claims_dag",
    "format_claims",
    # Visualization
    "format_run_verification",
    "format_run_detailed",
    "format_chain_verification",
    "format_status",
    "format_list",
    "generate_mermaid_dag",
    "generate_html_dag",
    "render_dag",
    "print_verification_summary",
    # Convenience functions
    "list_runs",
    "status",
    "run",
    "chain",
    "stats",
    "dag",
    # Integration hooks
    "on_session_start",
    "on_session_close",
    "on_io_load",
    "on_io_save",
    # Registry
    "ClewRegistry",
    "get_registry",
    "register",
    "verify_remote",
    # Stamping
    "Stamp",
    "stamp",
    "check_stamp",
    "list_stamps",
    # Examples
    "init_examples",
]


# EOF
