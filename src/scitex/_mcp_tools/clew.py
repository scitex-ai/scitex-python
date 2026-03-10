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
        from scitex.clew import list_runs as do_list_runs
        from scitex.clew import run as do_run

        runs = do_list_runs(status=status_filter, limit=limit)

        results = []
        for run in runs:
            verification = do_run(run["session_id"])
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

        from scitex.clew import run as do_run

        # run() accepts session_id; for file paths, resolve to session first
        path = Path(session_or_path)
        if path.exists():
            from scitex.clew import get_db

            db = get_db()
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

        verification = do_run(session_id)

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

        path = Path(target_file)
        if not path.exists():
            return _json(
                {
                    "error": f"File not found: {target_file}",
                    "target_file": target_file,
                }
            )

        chain = do_chain(str(path.resolve()))

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
        from scitex.clew import status as do_status

        return _json(do_status())

    @mcp.tool()
    async def clew_stats() -> str:
        """Show verification database statistics.

        Returns
        -------
        str
            JSON with database statistics
        """
        from scitex.clew import stats as do_stats

        return _json(do_stats())

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

        from scitex.clew import mermaid as do_mermaid

        if target_file:
            target_file = str(Path(target_file).resolve())

        multi_files = None
        if target_files:
            multi_files = [
                str(Path(f.strip()).resolve()) for f in target_files.split(",")
            ]

        mermaid_code = do_mermaid(
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

        from scitex.clew import dag as do_dag

        if claims:
            dag_result = do_dag(claims=True)
        elif target_files:
            targets = [str(Path(f.strip()).resolve()) for f in target_files.split(",")]
            dag_result = do_dag(targets)
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

    def _format_dag_result(dag_result) -> str:
        """Format DAGVerification to JSON string."""
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

    @mcp.tool()
    async def clew_rerun_dag(
        target_files: Optional[str] = None,
        timeout: int = 300,
    ) -> str:
        """Re-execute entire DAG in topological order and compare outputs.

        Each session is re-executed in a sandbox — original outputs are
        never overwritten. This is the most thorough verification mode.

        Parameters
        ----------
        target_files : str, optional
            Comma-separated list of target file paths.
            If omitted, reruns the entire project DAG.
        timeout : int, optional
            Maximum execution time per session in seconds (default: 300).

        Returns
        -------
        str
            JSON with DAG rerun verification results.
        """
        from pathlib import Path

        from scitex.clew import rerun_dag as do_rerun_dag

        targets = None
        if target_files:
            targets = [str(Path(f.strip()).resolve()) for f in target_files.split(",")]

        dag_result = do_rerun_dag(targets, timeout=timeout)
        return _format_dag_result(dag_result)

    @mcp.tool()
    async def clew_rerun_claims(
        file_path: Optional[str] = None,
        claim_type: Optional[str] = None,
        timeout: int = 300,
    ) -> str:
        """Re-execute all sessions backing manuscript claims.

        Traces each claim to its source session, builds the upstream DAG,
        and reruns every session in a sandbox.

        Parameters
        ----------
        file_path : str, optional
            Filter claims by manuscript file path.
        claim_type : str, optional
            Filter by claim type: statistic, figure, table, text, value.
        timeout : int, optional
            Maximum execution time per session in seconds (default: 300).

        Returns
        -------
        str
            JSON with DAG rerun verification results.
        """
        from scitex.clew import rerun_claims as do_rerun_claims

        dag_result = do_rerun_claims(
            file_path=file_path, claim_type=claim_type, timeout=timeout
        )
        return _format_dag_result(dag_result)


# EOF
