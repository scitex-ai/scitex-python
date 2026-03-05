#!/usr/bin/env python3
# Timestamp: "2026-02-01 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/_mcp_tools/clew.py
"""Clew module tools for FastMCP unified server."""

import json
from typing import Optional


def _json(data: dict) -> str:
    return json.dumps(data, indent=2, default=str)


def register_clew_tools(mcp) -> None:
    """Register clew tools with FastMCP server."""

    @mcp.tool()
    async def clew_list(
        limit: int = 50,
        status_filter: Optional[str] = None,
    ) -> str:
        """List all tracked runs with verification status.

        Parameters
        ----------
        limit : int, optional
            Maximum number of runs to return (default: 50)
        status_filter : str, optional
            Filter by status: 'success', 'failed', 'running', or None for all

        Returns
        -------
        str
            JSON with list of runs and their verification status
        """
        from scitex.clew import get_db, verify_run

        db = get_db()
        runs = db.list_runs(status=status_filter, limit=limit)

        results = []
        for run in runs:
            verification = verify_run(run["session_id"])
            results.append(
                {
                    "session_id": run["session_id"],
                    "script_path": run.get("script_path"),
                    "db_status": run.get("status"),
                    "verification_status": verification.status.value,
                    "is_verified": verification.is_verified,
                    "started_at": run.get("started_at"),
                    "finished_at": run.get("finished_at"),
                }
            )

        return _json(
            {
                "count": len(results),
                "runs": results,
            }
        )

    @mcp.tool()
    async def clew_run(
        session_or_path: str,
    ) -> str:
        """Verify a specific session run by checking all file hashes.

        Parameters
        ----------
        session_or_path : str
            Session ID (e.g., '2025Y-11M-18D-09h12m03s_HmH5') or
            path to a file to find its associated session

        Returns
        -------
        str
            JSON with verification results including file-level details
        """
        from pathlib import Path

        from scitex.clew import get_db
        from scitex.clew import verify_run as do_verify_run

        db = get_db()

        # Check if it's a file path
        path = Path(session_or_path)
        if path.exists():
            sessions = db.find_session_by_file(str(path.resolve()), role="output")
            if not sessions:
                sessions = db.find_session_by_file(str(path.resolve()), role="input")

            if not sessions:
                return _json(
                    {
                        "error": f"No session found for file: {session_or_path}",
                        "session_id": None,
                    }
                )
            session_id = sessions[0]
        else:
            session_id = session_or_path

        verification = do_verify_run(session_id)

        return _json(
            {
                "session_id": verification.session_id,
                "script_path": verification.script_path,
                "status": verification.status.value,
                "is_verified": verification.is_verified,
                "combined_hash_expected": verification.combined_hash_expected,
                "files": [
                    {
                        "path": f.path,
                        "role": f.role,
                        "status": f.status.value,
                        "expected_hash": f.expected_hash,
                        "current_hash": f.current_hash,
                        "is_verified": f.is_verified,
                    }
                    for f in verification.files
                ],
                "mismatched_count": len(verification.mismatched_files),
                "missing_count": len(verification.missing_files),
            }
        )

    @mcp.tool()
    async def clew_chain(
        target_file: str,
    ) -> str:
        """Verify the dependency chain for a target file.

        Traces back through all sessions that contributed to producing
        the target file and verifies each one.

        Parameters
        ----------
        target_file : str
            Path to the target file to trace

        Returns
        -------
        str
            JSON with chain verification results
        """
        from pathlib import Path

        from scitex.clew import verify_chain as do_verify_chain

        path = Path(target_file)
        if not path.exists():
            return _json(
                {
                    "error": f"File not found: {target_file}",
                    "target_file": target_file,
                }
            )

        chain = do_verify_chain(str(path.resolve()))

        return _json(
            {
                "target_file": chain.target_file,
                "status": chain.status.value,
                "is_verified": chain.is_verified,
                "chain_length": len(chain.runs),
                "failed_runs_count": len(chain.failed_runs),
                "runs": [
                    {
                        "session_id": r.session_id,
                        "script_path": r.script_path,
                        "status": r.status.value,
                        "is_verified": r.is_verified,
                        "mismatched_files": [f.path for f in r.mismatched_files],
                        "missing_files": [f.path for f in r.missing_files],
                    }
                    for r in chain.runs
                ],
            }
        )

    @mcp.tool()
    async def clew_status() -> str:
        """Show verification status summary (like git status).

        Returns
        -------
        str
            JSON with counts of verified, mismatched, and missing runs
        """
        from scitex.clew import get_status

        status = get_status()
        return _json(status)

    @mcp.tool()
    async def clew_stats() -> str:
        """Show verification database statistics.

        Returns
        -------
        str
            JSON with database statistics
        """
        from scitex.clew import get_db

        db = get_db()
        stats = db.stats()
        return _json(stats)

    @mcp.tool()
    async def clew_mermaid(
        session_id: Optional[str] = None,
        target_file: Optional[str] = None,
        target_files: Optional[str] = None,
        claims: bool = False,
    ) -> str:
        """Generate Mermaid diagram for verification DAG.

        Parameters
        ----------
        session_id : str, optional
            Start from this session
        target_file : str, optional
            Start from session that produced this file
        target_files : str, optional
            Comma-separated list of target files (multi-target DAG)
        claims : bool, optional
            If True, build DAG from all registered claims

        Returns
        -------
        str
            Mermaid diagram code
        """
        from pathlib import Path

        from scitex.clew import generate_mermaid_dag

        if target_file:
            target_file = str(Path(target_file).resolve())

        multi_files = None
        if target_files:
            multi_files = [
                str(Path(f.strip()).resolve()) for f in target_files.split(",")
            ]

        mermaid_code = generate_mermaid_dag(
            session_id=session_id,
            target_file=target_file,
            target_files=multi_files,
            claims=claims,
        )

        return _json(
            {
                "mermaid": mermaid_code,
                "session_id": session_id,
                "target_file": target_file,
                "target_files": multi_files,
                "claims": claims,
            }
        )

    @mcp.tool()
    async def clew_dag(
        target_files: Optional[str] = None,
        claims: bool = False,
    ) -> str:
        """Verify full DAG for multiple targets or claims.

        Parameters
        ----------
        target_files : str, optional
            Comma-separated list of target file paths
        claims : bool, optional
            If True, build DAG from all registered claims

        Returns
        -------
        str
            JSON with DAG verification results
        """
        from pathlib import Path

        if claims:
            from scitex.clew import verify_claims_dag

            dag_result = verify_claims_dag()
        elif target_files:
            from scitex.clew import verify_dag

            targets = [str(Path(f.strip()).resolve()) for f in target_files.split(",")]
            dag_result = verify_dag(targets)
        else:
            return _json({"error": "Specify target_files or claims=True"})

        return _json(
            {
                "target_files": dag_result.target_files,
                "status": dag_result.status.value,
                "is_verified": dag_result.is_verified,
                "num_runs": len(dag_result.runs),
                "num_edges": len(dag_result.edges),
                "topological_order": dag_result.topological_order,
                "runs": [
                    {
                        "session_id": r.session_id,
                        "script_path": r.script_path,
                        "status": r.status.value,
                        "is_verified": r.is_verified,
                    }
                    for r in dag_result.runs
                ],
                "edges": [{"parent": p, "child": c} for p, c in dag_result.edges],
            }
        )


# EOF
