#!/usr/bin/env python3
# Timestamp: "2026-02-01 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/clew/__init__.py
"""
SciTeX Clew — Hash-based verification for reproducible science.

Public API (19 functions)::

    # Verification
    stx.clew.status()                  # git-status-like overview
    stx.clew.run(session_id)           # verify one run (hash check)
    stx.clew.chain(target_file)        # trace file → source chain
    stx.clew.dag(targets)              # verify full DAG
    stx.clew.rerun(target)             # re-execute & compare (sandbox)
    stx.clew.rerun_dag(targets)        # rerun full DAG in topo order
    stx.clew.rerun_claims()            # rerun all claim-backing sessions
    stx.clew.list_runs(limit=100)      # list tracked runs
    stx.clew.stats()                   # database statistics

    # Claims
    stx.clew.add_claim(...)            # register manuscript assertion
    stx.clew.list_claims(...)          # list registered claims
    stx.clew.verify_claim(...)         # verify a specific claim

    # Stamping
    stx.clew.stamp(...)                # create temporal proof
    stx.clew.list_stamps(...)          # list stamps
    stx.clew.check_stamp(...)          # verify a stamp

    # Hashing
    stx.clew.hash_file(path)           # SHA256 of a file
    stx.clew.hash_directory(path)      # SHA256 of all files in dir

    # Visualization
    stx.clew.mermaid(...)              # generate Mermaid DAG diagram

    # Examples
    stx.clew.init_examples(dest)       # scaffold example pipeline
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Internal imports (hidden from public API, still importable via full path)
# ---------------------------------------------------------------------------
from ._chain import (
    ChainVerification as _ChainVerification,
)
from ._chain import (
    DAGVerification as _DAGVerification,
)
from ._chain import (
    FileVerification as _FileVerification,
)
from ._chain import (
    RunVerification as _RunVerification,
)
from ._chain import (
    VerificationLevel as _VerificationLevel,
)
from ._chain import (
    VerificationStatus as _VerificationStatus,
)
from ._chain import (
    get_status as _get_status,
)
from ._chain import (
    verify_chain as _verify_chain,
)
from ._chain import (
    verify_file as _verify_file,
)
from ._chain import (
    verify_run as _verify_run,
)
from ._claim import (
    Claim as _Claim,
)
from ._claim import (
    add_claim,
    list_claims,
    verify_claim,
)
from ._claim import (
    format_claims as _format_claims,
)
from ._claim import (
    verify_claims_dag as _verify_claims_dag,
)
from ._dag import verify_dag as _verify_dag
from ._db import VerificationDB as _VerificationDB
from ._db import get_db as _get_db
from ._db import set_db as _set_db
from ._examples import init_examples
from ._hash import (
    combine_hashes as _combine_hashes,
)
from ._hash import (
    hash_directory,
    hash_file,
)
from ._hash import (
    hash_files as _hash_files,
)
from ._hash import (
    verify_hash as _verify_hash,
)
from ._integration import (
    on_io_load as _on_io_load,
)
from ._integration import (
    on_io_save as _on_io_save,
)
from ._integration import (
    on_session_close as _on_session_close,
)
from ._integration import (
    on_session_start as _on_session_start,
)
from ._registry import ClewRegistry as _ClewRegistry
from ._registry import get_registry as _get_registry
from ._rerun import rerun_claims, rerun_dag
from ._rerun import verify_by_rerun as _verify_by_rerun
from ._stamp import Stamp as _Stamp
from ._stamp import check_stamp, list_stamps, stamp
from ._tracker import (
    SessionTracker as _SessionTracker,
)
from ._tracker import (
    get_tracker as _get_tracker,
)
from ._tracker import (
    set_tracker as _set_tracker,
)
from ._tracker import (
    start_tracking as _start_tracking,
)
from ._tracker import (
    stop_tracking as _stop_tracking,
)
from ._visualize import (
    format_chain_verification as _format_chain_verification,
)
from ._visualize import (
    format_list as _format_list,
)
from ._visualize import (
    format_run_detailed as _format_run_detailed,
)
from ._visualize import (
    format_run_verification as _format_run_verification,
)
from ._visualize import (
    format_status as _format_status,
)
from ._visualize import (
    generate_html_dag as _generate_html_dag,
)
from ._visualize import (
    generate_mermaid_dag as _generate_mermaid_dag,
)
from ._visualize import (
    print_verification_summary as _print_verification_summary,
)
from ._visualize import (
    render_dag as _render_dag,
)


# ---------------------------------------------------------------------------
# Public convenience API
# ---------------------------------------------------------------------------
def list_runs(limit: int = 100, status: str = None):
    """List tracked runs."""
    db = _get_db()
    return db.list_runs(status=status, limit=limit)


def status():
    """Get verification status summary (like git status)."""
    return _get_status()


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
        return _verify_by_rerun(session_id)
    return _verify_run(session_id)


def chain(target: str):
    """Verify the dependency chain for a target file."""
    return _verify_chain(target)


def stats():
    """Get database statistics."""
    db = _get_db()
    return db.stats()


def dag(targets=None, claims=False):
    """Verify the DAG for multiple targets or all claims."""
    if claims:
        return _verify_claims_dag()
    return _verify_dag(targets or [])


def rerun(target, timeout: int = 300, cleanup: bool = True):
    """Re-execute a session in a sandbox and compare outputs.

    Parameters
    ----------
    target : str or list[str]
        Session ID, script path, or artifact path.
    timeout : int, optional
        Maximum execution time in seconds (default: 300).
    cleanup : bool, optional
        Remove sandbox outputs after verification (default: True).
    """
    return _verify_by_rerun(target, timeout=timeout, cleanup=cleanup)


def mermaid(
    session_id=None,
    target_file=None,
    target_files=None,
    claims=False,
    **kwargs,
):
    """Generate a Mermaid DAG diagram.

    Parameters
    ----------
    session_id : str, optional
        Start from this session.
    target_file : str, optional
        Start from the session that produced this file.
    target_files : list of str, optional
        Multiple target files (multi-target DAG).
    claims : bool, optional
        If True, build DAG from all registered claims.
    """
    return _generate_mermaid_dag(
        session_id=session_id,
        target_file=target_file,
        target_files=target_files,
        claims=claims,
        **kwargs,
    )


# ---------------------------------------------------------------------------
# Backward compatibility: keep old names accessible as attributes
# ---------------------------------------------------------------------------
# These are NOT in __all__ but can still be used via stx.clew.verify_run etc.
get_db = _get_db
set_db = _set_db
verify_run = _verify_run
verify_chain = _verify_chain
verify_dag = _verify_dag
verify_file = _verify_file
verify_by_rerun = _verify_by_rerun
verify_claims_dag = _verify_claims_dag
get_status = _get_status
generate_mermaid_dag = _generate_mermaid_dag
on_session_start = _on_session_start
on_session_close = _on_session_close
on_io_load = _on_io_load
on_io_save = _on_io_save
get_tracker = _get_tracker
set_tracker = _set_tracker
start_tracking = _start_tracking
stop_tracking = _stop_tracking
get_registry = _get_registry
format_claims = _format_claims
format_status = _format_status
format_list = _format_list
format_run_verification = _format_run_verification
format_run_detailed = _format_run_detailed
format_chain_verification = _format_chain_verification
print_verification_summary = _print_verification_summary
generate_html_dag = _generate_html_dag
render_dag = _render_dag
combine_hashes = _combine_hashes
hash_files = _hash_files
verify_hash = _verify_hash
register = lambda hash_value, source_type="manual", **kw: _get_registry().register(  # noqa: E731
    hash_value, source_type=source_type, **kw
)
verify_remote = lambda hash_value: _get_registry().verify(hash_value)  # noqa: E731

# Backward compat: class/type names
VerificationDB = _VerificationDB
SessionTracker = _SessionTracker
ClewRegistry = _ClewRegistry
VerificationStatus = _VerificationStatus
VerificationLevel = _VerificationLevel
FileVerification = _FileVerification
RunVerification = _RunVerification
ChainVerification = _ChainVerification
DAGVerification = _DAGVerification
Claim = _Claim
Stamp = _Stamp
verify_run_from_scratch = _verify_by_rerun


# ---------------------------------------------------------------------------
# Public API — only these 19 names show in dir() and tab-completion
# ---------------------------------------------------------------------------
__all__ = [
    # Verification
    "status",
    "run",
    "chain",
    "dag",
    "rerun",
    "rerun_dag",
    "rerun_claims",
    "list_runs",
    "stats",
    # Claims
    "add_claim",
    "list_claims",
    "verify_claim",
    # Stamping
    "stamp",
    "list_stamps",
    "check_stamp",
    # Hashing
    "hash_file",
    "hash_directory",
    # Visualization
    "mermaid",
    # Examples
    "init_examples",
]


# EOF
