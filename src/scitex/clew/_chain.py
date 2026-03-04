#!/usr/bin/env python3
# Timestamp: "2026-02-01 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/verify/_chain.py
"""Dependency chain tracking and verification."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from ._db import get_db
from ._hash import hash_file


class VerificationStatus(Enum):
    """Verification status for a run or file."""

    VERIFIED = "verified"
    MISMATCH = "mismatch"
    MISSING = "missing"
    UNKNOWN = "unknown"


class VerificationLevel(Enum):
    """Level of verification performed.

    L1: CACHE     — Compare stored hashes vs current files (local only)
    L2: RERUN     — Re-execute pipeline and compare (local only)
    L3: REGISTERED — L2 + hash registered in Clew Registry with timestamp (scitex.ai)
    """

    CACHE = "cache"  # L1: Hash comparison only (fast)
    RERUN = "rerun"  # L2: Full re-execution (thorough)
    REGISTERED = "registered"  # L3: Registered with server-side timestamp


@dataclass
class FileVerification:
    """Verification result for a single file."""

    path: str
    role: str
    expected_hash: str
    current_hash: Optional[str]
    status: VerificationStatus

    @property
    def is_verified(self) -> bool:
        return self.status == VerificationStatus.VERIFIED


@dataclass
class RunVerification:
    """Verification result for a session run."""

    session_id: str
    script_path: Optional[str]
    status: VerificationStatus
    files: List[FileVerification]
    combined_hash_expected: Optional[str]
    combined_hash_current: Optional[str]
    level: VerificationLevel = VerificationLevel.CACHE

    @property
    def is_verified(self) -> bool:
        return self.status == VerificationStatus.VERIFIED

    @property
    def is_verified_from_scratch(self) -> bool:
        return self.is_verified and self.level == VerificationLevel.RERUN

    @property
    def inputs(self) -> List[FileVerification]:
        return [f for f in self.files if f.role == "input"]

    @property
    def outputs(self) -> List[FileVerification]:
        return [f for f in self.files if f.role == "output"]

    @property
    def mismatched_files(self) -> List[FileVerification]:
        return [f for f in self.files if f.status == VerificationStatus.MISMATCH]

    @property
    def missing_files(self) -> List[FileVerification]:
        return [f for f in self.files if f.status == VerificationStatus.MISSING]


@dataclass
class ChainVerification:
    """Verification result for a dependency chain."""

    target_file: str
    runs: List[RunVerification]
    status: VerificationStatus

    @property
    def is_verified(self) -> bool:
        return self.status == VerificationStatus.VERIFIED

    @property
    def failed_runs(self) -> List[RunVerification]:
        return [r for r in self.runs if not r.is_verified]


@dataclass
class DAGVerification:
    """Verification result for a multi-target DAG."""

    target_files: List[str]
    runs: List[RunVerification]
    edges: List[Tuple[str, str]]  # (parent_sid, child_sid)
    status: VerificationStatus
    topological_order: List[str]

    @property
    def is_verified(self) -> bool:
        return self.status == VerificationStatus.VERIFIED

    @property
    def failed_runs(self) -> List[RunVerification]:
        return [r for r in self.runs if not r.is_verified]


def verify_file(
    path: Union[str, Path],
    expected_hash: str,
    role: str = "unknown",
) -> FileVerification:
    """
    Verify a single file against expected hash.

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


def verify_run(
    target: str,
    propagate: bool = True,
) -> RunVerification:
    """
    Verify a session run by checking all file hashes.

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


def verify_chain(
    target: Union[str, Path],
) -> ChainVerification:
    """
    Verify the dependency chain for a target file.

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
    """
    Get verification status for all runs (like git status).

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
