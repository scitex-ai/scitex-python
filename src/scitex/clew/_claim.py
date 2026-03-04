#!/usr/bin/env python3
# Timestamp: "2026-02-09 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/verify/_claim.py
"""Claim layer — link paper assertions to verification chain.

Claims represent specific assertions in manuscripts (statistics, figures,
tables) that can be traced back through the verification chain to source data.

Five claim types:
  - statistic: A numerical result (p-value, effect size, etc.)
  - figure:    A figure reference linked to a recipe/image
  - table:     A table reference linked to source CSV
  - text:      A textual assertion linked to computational output
  - value:     A specific computed value (count, percentage, etc.)
"""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ._db import get_db

# Canonical claim types
CLAIM_TYPES = ("statistic", "figure", "table", "text", "value")


@dataclass
class Claim:
    """A traceable assertion in a manuscript."""

    claim_id: str
    file_path: str
    line_number: Optional[int]
    claim_type: str
    claim_value: Optional[str]
    source_session: Optional[str]
    source_file: Optional[str]
    source_hash: Optional[str]
    registered_at: Optional[str] = None
    verified_at: Optional[str] = None
    status: str = "registered"

    @property
    def location(self) -> str:
        """Human-readable location string."""
        if self.line_number:
            return f"{self.file_path}:L{self.line_number}"
        return self.file_path

    def to_dict(self) -> Dict:
        return {
            "claim_id": self.claim_id,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "claim_type": self.claim_type,
            "claim_value": self.claim_value,
            "source_session": self.source_session,
            "source_file": self.source_file,
            "source_hash": self.source_hash,
            "registered_at": self.registered_at,
            "verified_at": self.verified_at,
            "status": self.status,
        }


def migrate_add_claims_table(db_path: Path) -> None:
    """Create claims table if not present. Safe to call multiple times."""
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS claims (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                claim_id TEXT UNIQUE NOT NULL,
                file_path TEXT NOT NULL,
                line_number INTEGER,
                claim_type TEXT NOT NULL,
                claim_value TEXT,
                source_session TEXT,
                source_file TEXT,
                source_hash TEXT,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                verified_at TIMESTAMP,
                status TEXT DEFAULT 'registered'
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_claims_file ON claims(file_path)")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_claims_source ON claims(source_file)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_claims_session ON claims(source_session)"
        )
        conn.commit()
    finally:
        conn.close()


def _generate_claim_id(
    file_path: str, line_number: Optional[int], claim_type: str
) -> str:
    """Generate a deterministic claim ID."""
    loc = f"{file_path}:L{line_number}" if line_number else file_path
    import hashlib

    h = hashlib.sha256(f"{loc}:{claim_type}".encode()).hexdigest()[:12]
    return f"claim_{h}"


def add_claim(
    file_path: str,
    claim_type: str,
    line_number: Optional[int] = None,
    claim_value: Optional[str] = None,
    source_file: Optional[str] = None,
    source_session: Optional[str] = None,
) -> Claim:
    """Register a claim linking a manuscript assertion to the verification chain.

    Parameters
    ----------
    file_path : str
        Path to the manuscript file (e.g., paper.tex).
    claim_type : str
        One of: statistic, figure, table, text, value.
    line_number : int, optional
        Line number in the manuscript.
    claim_value : str, optional
        The asserted value (e.g., "p = 0.003").
    source_file : str, optional
        Path to the source file that produced this claim.
    source_session : str, optional
        Session ID that produced the source.

    Returns
    -------
    Claim
        The registered claim object.
    """
    if claim_type not in CLAIM_TYPES:
        raise ValueError(
            f"Invalid claim_type '{claim_type}'. Must be one of: {CLAIM_TYPES}"
        )

    file_path = str(Path(file_path).resolve())
    claim_id = _generate_claim_id(file_path, line_number, claim_type)

    # Compute source hash if source_file exists
    source_hash = None
    if source_file:
        source_file = str(Path(source_file).resolve())
        source_path = Path(source_file)
        if source_path.exists():
            from ._hash import hash_file

            source_hash = hash_file(source_path)

    # Auto-detect source session if not provided
    if source_file and not source_session:
        db = get_db()
        sessions = db.find_session_by_file(source_file, role="output")
        if sessions:
            source_session = sessions[0]

    claim = Claim(
        claim_id=claim_id,
        file_path=file_path,
        line_number=line_number,
        claim_type=claim_type,
        claim_value=claim_value,
        source_session=source_session,
        source_file=source_file,
        source_hash=source_hash,
    )

    # Store in database
    db = get_db()
    _ensure_claims_table(db)
    conn = sqlite3.connect(str(db.db_path))
    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO claims
                (claim_id, file_path, line_number, claim_type, claim_value,
                 source_session, source_file, source_hash, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'registered')
            """,
            (
                claim.claim_id,
                claim.file_path,
                claim.line_number,
                claim.claim_type,
                claim.claim_value,
                claim.source_session,
                claim.source_file,
                claim.source_hash,
            ),
        )
        conn.commit()
    finally:
        conn.close()

    return claim


def list_claims(
    file_path: Optional[str] = None,
    claim_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
) -> List[Claim]:
    """List registered claims with optional filters.

    Parameters
    ----------
    file_path : str, optional
        Filter by manuscript file path.
    claim_type : str, optional
        Filter by claim type.
    status : str, optional
        Filter by verification status.
    limit : int
        Maximum number of claims to return.

    Returns
    -------
    list of Claim
    """
    db = get_db()
    _ensure_claims_table(db)

    query = "SELECT * FROM claims WHERE 1=1"
    params = []

    if file_path:
        file_path = str(Path(file_path).resolve())
        query += " AND file_path = ?"
        params.append(file_path)
    if claim_type:
        query += " AND claim_type = ?"
        params.append(claim_type)
    if status:
        query += " AND status = ?"
        params.append(status)

    query += " ORDER BY file_path, line_number LIMIT ?"
    params.append(limit)

    conn = sqlite3.connect(str(db.db_path))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(query, params).fetchall()
        return [
            Claim(
                claim_id=row["claim_id"],
                file_path=row["file_path"],
                line_number=row["line_number"],
                claim_type=row["claim_type"],
                claim_value=row["claim_value"],
                source_session=row["source_session"],
                source_file=row["source_file"],
                source_hash=row["source_hash"],
                registered_at=row["registered_at"],
                verified_at=row["verified_at"],
                status=row["status"],
            )
            for row in rows
        ]
    finally:
        conn.close()


def verify_claim(claim_id_or_location: str) -> Dict:
    """Verify a specific claim by checking its source against the verification chain.

    Parameters
    ----------
    claim_id_or_location : str
        Either a claim_id or a location string like "paper.tex:L42".

    Returns
    -------
    dict
        Verification result with claim details and chain status.
    """
    db = get_db()
    _ensure_claims_table(db)

    claim = _resolve_claim(claim_id_or_location, db)
    if not claim:
        return {
            "status": "not_found",
            "message": f"No claim found for '{claim_id_or_location}'",
        }

    result = {
        "claim": claim.to_dict(),
        "source_verified": False,
        "chain_verified": False,
        "details": [],
    }

    # Check source file exists and hash matches
    if claim.source_file:
        source_path = Path(claim.source_file)
        if not source_path.exists():
            result["details"].append(f"Source file missing: {claim.source_file}")
            _update_claim_status(claim.claim_id, "missing", db)
            result["claim"]["status"] = "missing"
            return result

        from ._hash import hash_file

        current_hash = hash_file(source_path)
        if (
            claim.source_hash
            and current_hash[: len(claim.source_hash)]
            == claim.source_hash[: len(current_hash)]
        ):
            result["source_verified"] = True
            result["details"].append("Source file hash matches")
        else:
            result["details"].append(
                f"Source hash mismatch: stored={claim.source_hash}, current={current_hash}"
            )
            _update_claim_status(claim.claim_id, "mismatch", db)
            result["claim"]["status"] = "mismatch"
            return result

    # Verify the chain if we have a source file
    if claim.source_file:
        from ._chain import verify_chain

        try:
            chain = verify_chain(claim.source_file)
            result["chain_verified"] = chain.is_verified
            if chain.is_verified:
                result["details"].append(f"Chain verified ({len(chain.runs)} runs)")
            else:
                result["details"].append(
                    f"Chain verification failed ({len(chain.failed_runs)} failed runs)"
                )
        except Exception as e:
            result["details"].append(f"Chain verification error: {e}")

    # Update status
    if result["source_verified"] and result["chain_verified"]:
        _update_claim_status(claim.claim_id, "verified", db)
        result["claim"]["status"] = "verified"
    elif result["source_verified"]:
        _update_claim_status(claim.claim_id, "partial", db)
        result["claim"]["status"] = "partial"

    return result


def verify_claims_dag(
    file_path: Optional[str] = None,
    claim_type: Optional[str] = None,
) -> DAGVerification:
    """Build a unified DAG from all claims, tracing each back to its source.

    Parameters
    ----------
    file_path : str, optional
        Filter claims by manuscript file path.
    claim_type : str, optional
        Filter claims by type.

    Returns
    -------
    DAGVerification
        Unified verification result covering all claim source chains merged.
    """
    from ._chain import DAGVerification, VerificationStatus
    from ._dag import verify_dag

    claims = list_claims(file_path=file_path, claim_type=claim_type)

    # Collect unique source files from claims
    source_files = []
    for c in claims:
        if c.source_file and c.source_file not in source_files:
            source_files.append(c.source_file)

    if not source_files:
        return DAGVerification(
            target_files=[],
            runs=[],
            edges=[],
            status=VerificationStatus.UNKNOWN,
            topological_order=[],
        )

    return verify_dag(source_files)


def _resolve_claim(identifier: str, db) -> Optional[Claim]:
    """Resolve a claim by ID or location string."""
    conn = sqlite3.connect(str(db.db_path))
    conn.row_factory = sqlite3.Row
    try:
        # Try claim_id first
        row = conn.execute(
            "SELECT * FROM claims WHERE claim_id = ?", (identifier,)
        ).fetchone()

        if not row:
            # Try location format: file.tex:L42
            match = re.match(r"^(.+):L(\d+)$", identifier)
            if match:
                fpath = str(Path(match.group(1)).resolve())
                line = int(match.group(2))
                row = conn.execute(
                    "SELECT * FROM claims WHERE file_path = ? AND line_number = ?",
                    (fpath, line),
                ).fetchone()

        if not row:
            # Try file path only (returns first match)
            fpath = str(Path(identifier).resolve())
            row = conn.execute(
                "SELECT * FROM claims WHERE file_path = ? ORDER BY line_number LIMIT 1",
                (fpath,),
            ).fetchone()

        if row:
            return Claim(
                claim_id=row["claim_id"],
                file_path=row["file_path"],
                line_number=row["line_number"],
                claim_type=row["claim_type"],
                claim_value=row["claim_value"],
                source_session=row["source_session"],
                source_file=row["source_file"],
                source_hash=row["source_hash"],
                registered_at=row["registered_at"],
                verified_at=row["verified_at"],
                status=row["status"],
            )
        return None
    finally:
        conn.close()


def _update_claim_status(claim_id: str, status: str, db) -> None:
    """Update claim verification status."""
    conn = sqlite3.connect(str(db.db_path))
    try:
        conn.execute(
            "UPDATE claims SET status = ?, verified_at = ? WHERE claim_id = ?",
            (status, datetime.now().isoformat(), claim_id),
        )
        conn.commit()
    finally:
        conn.close()


def _ensure_claims_table(db) -> None:
    """Ensure the claims table exists (run migration)."""
    migrate_add_claims_table(db.db_path)


def format_claims(claims: List[Claim], verbose: bool = False) -> str:
    """Format claims list for terminal display."""
    if not claims:
        return "No claims registered."

    lines = []
    status_icons = {
        "registered": "\u25cb",  # ○
        "verified": "\u2713",  # ✓
        "mismatch": "\u2717",  # ✗
        "missing": "?",
        "partial": "~",
    }

    for c in claims:
        icon = status_icons.get(c.status, "?")
        loc = c.location
        val = f" = {c.claim_value}" if c.claim_value else ""
        lines.append(f"  {icon} [{c.claim_type}] {loc}{val}")
        if verbose and c.source_file:
            src = Path(c.source_file).name
            lines.append(
                f"      source: {src} (session: {c.source_session or 'unknown'})"
            )

    return "\n".join(lines)


__all__ = [
    "CLAIM_TYPES",
    "Claim",
    "add_claim",
    "list_claims",
    "verify_claim",
    "verify_claims_dag",
    "format_claims",
    "migrate_add_claims_table",
]
