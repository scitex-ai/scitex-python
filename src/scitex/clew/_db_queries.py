#!/usr/bin/env python3
# Timestamp: "2026-03-04 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/clew/_db_queries.py
"""Verification recording, history, and statistics queries for VerificationDB."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class VerificationQueryMixin:
    """Mixin providing verification recording and statistics methods.

    Requires _connect() context manager from VerificationDB.
    """

    def record_verification(
        self,
        session_id: str,
        level: str,
        status: str,
    ) -> None:
        """Record a verification result.

        Parameters
        ----------
        session_id : str
            Session identifier
        level : str
            Verification level (cache, from_scratch)
        status : str
            Verification status (verified, mismatch, missing, unknown)
        """
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO verification_results
                (session_id, level, status)
                VALUES (?, ?, ?)
                """,
                (session_id, level, status),
            )

    def get_latest_verification(
        self,
        session_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get the most recent verification result for a session.

        Parameters
        ----------
        session_id : str
            Session identifier

        Returns
        -------
        dict or None
            Latest verification result with level, status, and timestamp
        """
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT level, status, verified_at
                FROM verification_results
                WHERE session_id = ?
                ORDER BY verified_at DESC
                LIMIT 1
                """,
                (session_id,),
            ).fetchone()
            return dict(row) if row else None

    def get_verification_history(
        self,
        session_id: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get verification history for a session.

        Parameters
        ----------
        session_id : str
            Session identifier
        limit : int, optional
            Maximum number of results

        Returns
        -------
        list of dict
            Verification results ordered by timestamp (newest first)
        """
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT level, status, verified_at
                FROM verification_results
                WHERE session_id = ?
                ORDER BY verified_at DESC
                LIMIT ?
                """,
                (session_id, limit),
            ).fetchall()
            return [dict(row) for row in rows]

    def stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with self._connect() as conn:
            total_runs = conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
            success_runs = conn.execute(
                "SELECT COUNT(*) FROM runs WHERE status = 'success'"
            ).fetchone()[0]
            failed_runs = conn.execute(
                "SELECT COUNT(*) FROM runs WHERE status = 'failed'"
            ).fetchone()[0]
            total_files = conn.execute("SELECT COUNT(*) FROM file_hashes").fetchone()[0]
            unique_files = conn.execute(
                "SELECT COUNT(DISTINCT file_path) FROM file_hashes"
            ).fetchone()[0]

            return {
                "total_runs": total_runs,
                "success_runs": success_runs,
                "failed_runs": failed_runs,
                "total_file_records": total_files,
                "unique_files": unique_files,
                "db_path": str(self.db_path),
            }


# EOF
