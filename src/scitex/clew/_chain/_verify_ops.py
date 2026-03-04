#!/usr/bin/env python3
# Timestamp: "2026-02-01 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/clew/_chain/_verify_ops.py
"""Core file and run verification logic."""

from __future__ import annotations

from pathlib import Path
from typing import Union

from .._db import get_db
from .._hash import hash_file
from ._types import (
    FileVerification,
    RunVerification,
    VerificationStatus,
)


def verify_file(
    path: Union[str, Path],
    expected_hash: str,
    role: str = "unknown",
) -> FileVerification:
    """Verify a single file against expected hash.

    Parameters
    ----------
    path : str or Path
        Path to the file
    expected_hash : str
        Expected hash value
    role : str, optional
        Role of the file (input, output, script)

    Returns
    -------
    FileVerification
        Verification result
    """
    path = Path(path)
    path_str = str(path)

    if not path.exists():
        return FileVerification(
            path=path_str,
            role=role,
            expected_hash=expected_hash,
            current_hash=None,
            status=VerificationStatus.MISSING,
        )

    current_hash = hash_file(path)

    # Compare only the length of expected_hash
    matches = current_hash[: len(expected_hash)] == expected_hash

    return FileVerification(
        path=path_str,
        role=role,
        expected_hash=expected_hash,
        current_hash=current_hash,
        status=VerificationStatus.VERIFIED if matches else VerificationStatus.MISMATCH,
    )


def _resolve_target(db, target: str) -> str | None:
    """Resolve target (session_id, script path, or artifact path) to session_id."""
    # Try as session_id
    if db.get_run(target):
        return target

    # Resolve to absolute path
    resolved = str(Path(target).resolve())

    # Try as script path
    for run in db.list_runs(limit=100):
        if run.get("script_path") == resolved:
            return run["session_id"]

    # Try as artifact (output) path
    sessions = db.find_session_by_file(resolved, role="output")
    return sessions[0] if sessions else None


def verify_run(
    target: str,
    propagate: bool = True,
) -> RunVerification:
    """Verify a session run by checking all file hashes.

    Parameters
    ----------
    target : str
        Session ID, script path, or artifact path
    propagate : bool
        If True, mark as failed if any upstream input has failed verification

    Returns
    -------
    RunVerification
        Verification result
    """
    db = get_db()

    # Resolve target to session_id
    session_id = _resolve_target(db, target)
    if not session_id:
        return RunVerification(
            session_id=target,
            script_path=None,
            status=VerificationStatus.UNKNOWN,
            files=[],
            combined_hash_expected=None,
            combined_hash_current=None,
        )

    # Get run info
    run_info = db.get_run(session_id)
    if not run_info:
        return RunVerification(
            session_id=session_id,
            script_path=None,
            status=VerificationStatus.UNKNOWN,
            files=[],
            combined_hash_expected=None,
            combined_hash_current=None,
        )

    # Get all file hashes
    input_hashes = db.get_file_hashes(session_id, role="input")
    output_hashes = db.get_file_hashes(session_id, role="output")

    # Verify each file
    file_verifications = []
    upstream_failed = False

    for path, expected in input_hashes.items():
        fv = verify_file(path, expected, role="input")
        file_verifications.append(fv)

        # Check if upstream session that produced this input has failed
        if propagate and not fv.is_verified:
            upstream_failed = True

    for path, expected in output_hashes.items():
        file_verifications.append(verify_file(path, expected, role="output"))

    # Verify script if present
    if run_info.get("script_path") and run_info.get("script_hash"):
        script_verification = verify_file(
            run_info["script_path"],
            run_info["script_hash"],
            role="script",
        )
        file_verifications.append(script_verification)

    # Determine overall status (upstream failure propagates)
    if upstream_failed:
        status = VerificationStatus.MISMATCH
    elif all(f.is_verified for f in file_verifications):
        status = VerificationStatus.VERIFIED
    elif any(f.status == VerificationStatus.MISMATCH for f in file_verifications):
        status = VerificationStatus.MISMATCH
    elif any(f.status == VerificationStatus.MISSING for f in file_verifications):
        status = VerificationStatus.MISSING
    else:
        status = VerificationStatus.UNKNOWN

    return RunVerification(
        session_id=session_id,
        script_path=run_info.get("script_path"),
        status=status,
        files=file_verifications,
        combined_hash_expected=run_info.get("combined_hash"),
        combined_hash_current=None,
    )


# EOF
