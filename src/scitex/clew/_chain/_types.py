#!/usr/bin/env python3
# Timestamp: "2026-02-01 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/clew/_chain/_types.py
"""Verification dataclasses and enumerations."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple


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


# EOF
