#!/usr/bin/env python3
# Timestamp: "2026-02-01 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/clew/_chain/_chain_ops.py
"""Chain and status verification operations."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Union

from .._db import get_db
from ._types import ChainVerification, VerificationStatus
from ._verify_ops import verify_run


def verify_chain(
    target: Union[str, Path],
) -> ChainVerification:
    """Verify the dependency chain for a target file.

    Traces back through all sessions that produced this file
    and verifies each one.

    Parameters
    ----------
    target : str or Path
        Target file to trace

    Returns
    -------
    ChainVerification
        Verification result for the entire chain
    """
    db = get_db()
    target = str(Path(target).resolve())

    # Find session that produced this output
    sessions = db.find_session_by_file(target, role="output")
    if not sessions:
        return ChainVerification(
            target_file=target,
            runs=[],
            status=VerificationStatus.UNKNOWN,
        )

    # Get the most recent session
    session_id = sessions[0]

    # Build chain by following parent_session links
    chain = db.get_chain(session_id)

    # Verify each run in the chain
    run_verifications = []
    for sid in chain:
        run_verifications.append(verify_run(sid))

    # Determine overall status
    if all(r.is_verified for r in run_verifications):
        status = VerificationStatus.VERIFIED
    elif any(r.status == VerificationStatus.MISMATCH for r in run_verifications):
        status = VerificationStatus.MISMATCH
    elif any(r.status == VerificationStatus.MISSING for r in run_verifications):
        status = VerificationStatus.MISSING
    else:
        status = VerificationStatus.UNKNOWN

    return ChainVerification(
        target_file=target,
        runs=run_verifications,
        status=status,
    )


def get_status() -> Dict[str, Any]:
    """Get verification status for all runs (like git status).

    Returns
    -------
    dict
        Summary of verification status
    """
    db = get_db()
    runs = db.list_runs(limit=1000)

    verified = []
    mismatched = []
    missing = []

    for run in runs:
        session_id = run["session_id"]
        verification = verify_run(session_id)

        if verification.is_verified:
            verified.append(session_id)
        elif verification.mismatched_files:
            mismatched.append(
                {
                    "session_id": session_id,
                    "files": [f.path for f in verification.mismatched_files],
                }
            )
        elif verification.missing_files:
            missing.append(
                {
                    "session_id": session_id,
                    "files": [f.path for f in verification.missing_files],
                }
            )

    return {
        "verified_count": len(verified),
        "mismatch_count": len(mismatched),
        "missing_count": len(missing),
        "mismatched": mismatched,
        "missing": missing,
    }


# EOF
