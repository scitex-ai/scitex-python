#!/usr/bin/env python3
# Timestamp: "2026-03-04 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/clew/_db_chain.py
"""Chain and DAG relationship operations for VerificationDB."""

from __future__ import annotations

from typing import Dict, List


class ChainMixin:
    """Mixin providing chain and multi-parent DAG operations.

    Requires _connect() context manager from VerificationDB.
    """

    # -------------------------------------------------------------------------
    # Migration
    # -------------------------------------------------------------------------

    def _migrate_session_parents(self) -> None:
        """Populate session_parents from existing runs.parent_session (idempotent)."""
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO session_parents (session_id, parent_session)
                SELECT session_id, parent_session FROM runs
                WHERE parent_session IS NOT NULL
                """
            )

    # -------------------------------------------------------------------------
    # Chain operations
    # -------------------------------------------------------------------------

    def get_chain(self, session_id: str) -> List[str]:
        """Get the chain of parent sessions for a given session.

        Parameters
        ----------
        session_id : str
            Session identifier

        Returns
        -------
        list of str
            List of session IDs from current to root
        """
        chain = [session_id]
        current = session_id

        with self._connect() as conn:
            while True:
                row = conn.execute(
                    "SELECT parent_session FROM runs WHERE session_id = ?",
                    (current,),
                ).fetchone()
                if not row or not row["parent_session"]:
                    break
                current = row["parent_session"]
                chain.append(current)

        return chain

    def get_children(self, session_id: str) -> List[str]:
        """Get child sessions that depend on this session."""
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT session_id FROM runs
                WHERE parent_session = ?
                ORDER BY started_at
                """,
                (session_id,),
            ).fetchall()
            return [row["session_id"] for row in rows]

    def set_parent(self, session_id: str, parent_session: str) -> None:
        """Set the parent session for a run.

        Parameters
        ----------
        session_id : str
            Session identifier
        parent_session : str
            Parent session identifier
        """
        with self._connect() as conn:
            conn.execute(
                "UPDATE runs SET parent_session = ? WHERE session_id = ?",
                (parent_session, session_id),
            )
            conn.execute(
                """
                INSERT OR IGNORE INTO session_parents
                (session_id, parent_session)
                VALUES (?, ?)
                """,
                (session_id, parent_session),
            )

    def add_parent(self, session_id: str, parent_session: str) -> None:
        """Add a parent relationship for a session.

        Stores in the junction table for multi-parent DAG support.
        Also sets runs.parent_session if currently NULL (backward compat).

        Parameters
        ----------
        session_id : str
            Child session identifier
        parent_session : str
            Parent session identifier
        """
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO session_parents
                (session_id, parent_session)
                VALUES (?, ?)
                """,
                (session_id, parent_session),
            )
            # Set primary parent if not yet set (backward compat)
            conn.execute(
                """
                UPDATE runs SET parent_session = ?
                WHERE session_id = ? AND parent_session IS NULL
                """,
                (parent_session, session_id),
            )

    def get_parents(self, session_id: str) -> List[str]:
        """Get all parent sessions for a given session.

        Parameters
        ----------
        session_id : str
            Session identifier

        Returns
        -------
        list of str
            List of parent session IDs
        """
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT parent_session FROM session_parents
                WHERE session_id = ?
                ORDER BY recorded_at
                """,
                (session_id,),
            ).fetchall()
            return [row["parent_session"] for row in rows]

    def get_dag(self, session_ids: List[str]) -> tuple:
        """BFS backward from leaf sessions to collect the full DAG.

        Parameters
        ----------
        session_ids : list of str
            Leaf session IDs to start from

        Returns
        -------
        tuple of (dict, set)
            - adjacency: {child_session: [parent_sessions, ...]}
            - all_ids: set of all session IDs in the DAG
        """
        from collections import deque

        adjacency: Dict[str, List[str]] = {}
        all_ids: set = set()
        queue = deque(session_ids)
        visited: set = set()

        with self._connect() as conn:
            while queue:
                sid = queue.popleft()
                if sid in visited:
                    continue
                visited.add(sid)
                all_ids.add(sid)

                rows = conn.execute(
                    """
                    SELECT parent_session FROM session_parents
                    WHERE session_id = ?
                    ORDER BY recorded_at
                    """,
                    (sid,),
                ).fetchall()

                parents = [row["parent_session"] for row in rows]

                # Fallback: if no junction table entries, check runs.parent_session
                if not parents:
                    row = conn.execute(
                        "SELECT parent_session FROM runs WHERE session_id = ?",
                        (sid,),
                    ).fetchone()
                    if row and row["parent_session"]:
                        parents = [row["parent_session"]]

                adjacency[sid] = parents
                for p in parents:
                    all_ids.add(p)
                    if p not in visited:
                        queue.append(p)

        # Ensure root nodes have empty parent lists
        for sid in all_ids:
            if sid not in adjacency:
                adjacency[sid] = []

        return adjacency, all_ids


# EOF
