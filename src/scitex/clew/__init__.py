#!/usr/bin/env python3
"""
SciTeX Clew — Hash-based verification for reproducible science.

Thin re-export layer. All code lives in the standalone ``scitex-clew`` package.
Integration hooks (on_session_start, on_io_save, …) are added here.

Public API (19 functions)::

    stx.clew.status()                  # git-status-like overview
    stx.clew.run(session_id)           # verify one run (hash check)
    stx.clew.chain(target_file)        # trace file → source chain
    stx.clew.dag(targets)              # verify full DAG
    stx.clew.rerun(target)             # re-execute & compare (sandbox)
    stx.clew.rerun_dag(targets)        # rerun full DAG in topo order
    stx.clew.rerun_claims()            # rerun all claim-backing sessions
    stx.clew.list_runs(limit=100)      # list tracked runs
    stx.clew.stats()                   # database statistics
    stx.clew.add_claim(...)            # register manuscript assertion
    stx.clew.list_claims(...)          # list registered claims
    stx.clew.verify_claim(...)         # verify a specific claim
    stx.clew.stamp(...)                # create temporal proof
    stx.clew.list_stamps(...)          # list stamps
    stx.clew.check_stamp(...)          # verify a stamp
    stx.clew.hash_file(path)           # SHA256 of a file
    stx.clew.hash_directory(path)      # SHA256 of all files in dir
    stx.clew.mermaid(...)              # generate Mermaid DAG diagram
    stx.clew.init_examples(dest)       # scaffold example pipeline
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Re-export everything from the standalone scitex-clew package
# ---------------------------------------------------------------------------
from scitex_clew import *  # noqa: F401,F403  — 19 public names

# Backward-compat names (not in __all__, but accessible as attributes)
from scitex_clew import (  # noqa: F401
    ChainVerification,
    Claim,
    ClewRegistry,
    DAGVerification,
    FileVerification,
    RunVerification,
    SessionTracker,
    Stamp,
    VerificationDB,
    VerificationLevel,
    VerificationStatus,
    __all__,  # noqa: F401
    combine_hashes,
    format_chain_verification,
    format_claims,
    format_list,
    format_run_detailed,
    format_run_verification,
    format_status,
    generate_html_dag,
    generate_mermaid_dag,
    get_db,
    get_registry,
    get_status,
    get_tracker,
    hash_files,
    print_verification_summary,
    render_dag,
    set_db,
    set_tracker,
    start_tracking,
    stop_tracking,
    verify_by_rerun,
    verify_chain,
    verify_claims_dag,
    verify_dag,
    verify_file,
    verify_hash,
    verify_run,
    verify_run_from_scratch,
)

# ---------------------------------------------------------------------------
# Integration hooks (scitex-specific glue, NOT in standalone package)
# ---------------------------------------------------------------------------
from ._integration import (  # noqa: F401
    on_io_load,
    on_io_save,
    on_session_close,
    on_session_start,
)


# EOF
