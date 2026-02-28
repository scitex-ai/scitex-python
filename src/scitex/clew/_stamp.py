#!/usr/bin/env python3
# Timestamp: "2026-02-09 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/verify/_stamp.py
"""External hash timestamping for temporal integrity.

Provides independent temporal proof that a verification chain was consistent
at a specific point in time. Only hashes are transmitted — never actual data.

Backends (increasing trust level):
  - file:    Local JSON file with timestamp (development/testing)
  - rfc3161: RFC 3161 Timestamping Authority (production standard)
  - zenodo:  Zenodo deposit with DOI (archival, citable)
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from ._db import get_db

STAMP_BACKENDS = ("file", "rfc3161", "zenodo", "scitex_cloud")


@dataclass
class Stamp:
    """A temporal proof record."""

    stamp_id: str
    root_hash: str
    timestamp: str
    backend: str
    service_url: Optional[str]
    response_token: Optional[str]
    run_count: int
    metadata: Optional[Dict] = None

    def to_dict(self) -> Dict:
        return {
            "stamp_id": self.stamp_id,
            "root_hash": self.root_hash,
            "timestamp": self.timestamp,
            "backend": self.backend,
            "service_url": self.service_url,
            "response_token": self.response_token,
            "run_count": self.run_count,
            "metadata": self.metadata,
        }


def migrate_add_stamps_table(db_path: Path) -> None:
    """Create stamps table if not present. Safe to call multiple times."""
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS stamps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stamp_id TEXT UNIQUE NOT NULL,
                root_hash TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                backend TEXT NOT NULL,
                service_url TEXT,
                response_token TEXT,
                run_count INTEGER,
                metadata TEXT
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_stamps_hash ON stamps(root_hash)")
        conn.commit()
    finally:
        conn.close()


def compute_root_hash(session_ids: Optional[List[str]] = None) -> Dict:
    """Compute a Merkle-like root hash over all (or selected) runs.

    The root hash combines all run combined_hashes in deterministic order,
    providing a single fingerprint for the entire verification state.

    Parameters
    ----------
    session_ids : list of str, optional
        Specific sessions to include. If None, includes all successful runs.

    Returns
    -------
    dict
        {root_hash, run_count, session_ids}
    """
    db = get_db()
    conn = sqlite3.connect(str(db.db_path))
    conn.row_factory = sqlite3.Row
    try:
        if session_ids:
            placeholders = ",".join("?" * len(session_ids))
            rows = conn.execute(
                f"SELECT session_id, combined_hash FROM runs "
                f"WHERE session_id IN ({placeholders}) "
                f"ORDER BY session_id",
                session_ids,
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT session_id, combined_hash FROM runs "
                "WHERE status = 'success' AND combined_hash IS NOT NULL "
                "ORDER BY session_id"
            ).fetchall()

        if not rows:
            return {"root_hash": None, "run_count": 0, "session_ids": []}

        hasher = hashlib.sha256()
        ids = []
        for row in rows:
            hasher.update(row["session_id"].encode())
            hasher.update((row["combined_hash"] or "").encode())
            ids.append(row["session_id"])

        return {
            "root_hash": hasher.hexdigest(),
            "run_count": len(ids),
            "session_ids": ids,
        }
    finally:
        conn.close()


def stamp(
    backend: str = "file",
    service_url: Optional[str] = None,
    session_ids: Optional[List[str]] = None,
    output_dir: Optional[str] = None,
) -> Stamp:
    """Record root hash with external timestamp.

    Parameters
    ----------
    backend : str
        One of: file, rfc3161, zenodo.
    service_url : str, optional
        URL for RFC 3161 TSA or Zenodo API.
    session_ids : list of str, optional
        Specific sessions to stamp. If None, stamps all successful runs.
    output_dir : str, optional
        Directory for file-based stamps (default: .scitex/stamps/).

    Returns
    -------
    Stamp
        The timestamp proof record.
    """
    if backend not in STAMP_BACKENDS:
        raise ValueError(
            f"Invalid backend '{backend}'. Must be one of: {STAMP_BACKENDS}"
        )

    root = compute_root_hash(session_ids)
    if not root["root_hash"]:
        raise ValueError("No runs to stamp (no successful runs with combined hashes)")

    now = datetime.now(timezone.utc).isoformat()
    root_hash = root["root_hash"]
    raw = f"{root_hash}:{now}"
    stamp_id = f"stamp_{hashlib.sha256(raw.encode()).hexdigest()[:12]}"

    if backend == "file":
        result = _stamp_file(stamp_id, root, now, output_dir)
    elif backend == "rfc3161":
        result = _stamp_rfc3161(stamp_id, root, now, service_url)
    elif backend == "zenodo":
        result = _stamp_zenodo(stamp_id, root, now, service_url)
    elif backend == "scitex_cloud":
        result = _stamp_scitex_cloud(stamp_id, root, now, service_url)
    else:
        raise ValueError(f"Unsupported backend: {backend}")

    stamp_obj = Stamp(
        stamp_id=stamp_id,
        root_hash=root["root_hash"],
        timestamp=now,
        backend=backend,
        service_url=result.get("service_url"),
        response_token=result.get("response_token"),
        run_count=root["run_count"],
        metadata={"session_ids": root["session_ids"]},
    )

    # Store in database
    db = get_db()
    _ensure_stamps_table(db)
    conn = sqlite3.connect(str(db.db_path))
    try:
        conn.execute(
            """
            INSERT INTO stamps
                (stamp_id, root_hash, timestamp, backend, service_url,
                 response_token, run_count, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                stamp_obj.stamp_id,
                stamp_obj.root_hash,
                stamp_obj.timestamp,
                stamp_obj.backend,
                stamp_obj.service_url,
                stamp_obj.response_token,
                stamp_obj.run_count,
                json.dumps(stamp_obj.metadata),
            ),
        )
        conn.commit()
    finally:
        conn.close()

    return stamp_obj


def check_stamp(stamp_id: Optional[str] = None) -> Dict:
    """Verify a stamp against current verification state.

    Parameters
    ----------
    stamp_id : str, optional
        Specific stamp to check. If None, checks the latest stamp.

    Returns
    -------
    dict
        {stamp, current_root_hash, matches, details}
    """
    db = get_db()
    _ensure_stamps_table(db)

    conn = sqlite3.connect(str(db.db_path))
    conn.row_factory = sqlite3.Row
    try:
        if stamp_id:
            row = conn.execute(
                "SELECT * FROM stamps WHERE stamp_id = ?", (stamp_id,)
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT * FROM stamps ORDER BY id DESC LIMIT 1"
            ).fetchone()

        if not row:
            return {"status": "not_found", "message": "No stamps found"}

        stored_stamp = Stamp(
            stamp_id=row["stamp_id"],
            root_hash=row["root_hash"],
            timestamp=row["timestamp"],
            backend=row["backend"],
            service_url=row["service_url"],
            response_token=row["response_token"],
            run_count=row["run_count"],
            metadata=json.loads(row["metadata"]) if row["metadata"] else None,
        )

        # Recompute root hash from the same sessions
        session_ids = (
            stored_stamp.metadata.get("session_ids") if stored_stamp.metadata else None
        )
        current = compute_root_hash(session_ids)

        matches = current["root_hash"] == stored_stamp.root_hash
        details = []

        if matches:
            details.append(f"Root hash matches stamp from {stored_stamp.timestamp}")
        else:
            details.append(f"Root hash CHANGED since stamp at {stored_stamp.timestamp}")
            details.append(f"  Stamped:  {stored_stamp.root_hash[:32]}...")
            details.append(f"  Current:  {current['root_hash'][:32]}...")

        if current["run_count"] != stored_stamp.run_count:
            details.append(
                f"  Run count changed: {stored_stamp.run_count} → {current['run_count']}"
            )

        return {
            "stamp": stored_stamp.to_dict(),
            "current_root_hash": current["root_hash"],
            "matches": matches,
            "details": details,
        }
    finally:
        conn.close()


def list_stamps(limit: int = 20) -> List[Stamp]:
    """List all stamps."""
    db = get_db()
    _ensure_stamps_table(db)

    conn = sqlite3.connect(str(db.db_path))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT * FROM stamps ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [
            Stamp(
                stamp_id=r["stamp_id"],
                root_hash=r["root_hash"],
                timestamp=r["timestamp"],
                backend=r["backend"],
                service_url=r["service_url"],
                response_token=r["response_token"],
                run_count=r["run_count"],
                metadata=json.loads(r["metadata"]) if r["metadata"] else None,
            )
            for r in rows
        ]
    finally:
        conn.close()


# ── Backend implementations ──


def _stamp_file(stamp_id, root, timestamp, output_dir=None):
    """File-based stamping: write JSON proof to local directory."""
    if output_dir:
        stamp_dir = Path(output_dir)
    else:
        db = get_db()
        stamp_dir = db.db_path.parent / "stamps"

    stamp_dir.mkdir(parents=True, exist_ok=True)
    stamp_path = stamp_dir / f"{stamp_id}.json"

    proof = {
        "stamp_id": stamp_id,
        "root_hash": root["root_hash"],
        "timestamp": timestamp,
        "run_count": root["run_count"],
        "backend": "file",
    }

    stamp_path.write_text(json.dumps(proof, indent=2))
    return {"service_url": str(stamp_path), "response_token": None}


def _stamp_rfc3161(stamp_id, root, timestamp, service_url=None):
    """RFC 3161 Timestamping Authority."""
    try:
        import rfc3161ng
    except ImportError:
        raise ImportError(
            "RFC 3161 stamping requires 'rfc3161ng' package. "
            "Install with: pip install rfc3161ng"
        )

    url = service_url or "http://zeitstempel.dfn.de"
    certificate = rfc3161ng.RemoteTimestamper(url)

    hash_bytes = bytes.fromhex(root["root_hash"])
    tst = certificate.timestamp(data=hash_bytes)

    token_hex = tst.hex() if isinstance(tst, bytes) else str(tst)
    return {"service_url": url, "response_token": token_hex[:256]}


def _stamp_zenodo(stamp_id, root, timestamp, service_url=None):
    """Zenodo deposit: create a record with the root hash."""
    raise NotImplementedError(
        "Zenodo stamping is planned for a future release. "
        "Use 'file' or 'rfc3161' backend instead."
    )


def _stamp_scitex_cloud(stamp_id, root, timestamp, service_url=None):
    """SciTeX Cloud registry: register root hash with server-side timestamp."""
    from ._registry import get_registry

    registry = get_registry(base_url=service_url)
    result = registry.register(
        root["root_hash"],
        source_type="stamp",
        metadata={
            "stamp_id": stamp_id,
            "run_count": root["run_count"],
            "timestamp": timestamp,
        },
    )

    url = service_url or registry.base_url
    token = (
        result.get("data", {}).get("registered_at") if result.get("success") else None
    )
    return {"service_url": url, "response_token": token}


def _ensure_stamps_table(db) -> None:
    """Ensure the stamps table exists."""
    migrate_add_stamps_table(db.db_path)


__all__ = [
    "STAMP_BACKENDS",
    "Stamp",
    "check_stamp",
    "compute_root_hash",
    "list_stamps",
    "migrate_add_stamps_table",
    "stamp",
]
