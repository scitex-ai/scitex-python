#!/usr/bin/env python3
# Timestamp: "2026-02-01 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/clew/_viz/_mermaid_dag.py
"""DAG-building helpers for Mermaid diagram generation."""

from __future__ import annotations

from typing import List, Literal, Optional

from .._chain import VerificationLevel, verify_run
from .._db import get_db
from ._json import format_path
from ._mermaid_nodes import (
    add_file_nodes,
    add_script_node,
    append_class_definitions,
)

PathMode = Literal["name", "relative", "absolute"]


def collect_runs_data(chain_ids: list, db) -> list:
    """Collect run data for all sessions in chain."""
    runs_data = []
    for sid in chain_ids:
        run = db.get_run(sid)
        verification = verify_run(sid)

        latest_verification = db.get_latest_verification(sid)
        if (
            latest_verification
            and latest_verification.get("level") == "rerun"
            and latest_verification.get("status") == "verified"
        ):
            verification.level = VerificationLevel.RERUN

        inputs = db.get_file_hashes(sid, role="input")
        outputs = db.get_file_hashes(sid, role="output")
        runs_data.append(
            {
                "session_id": sid,
                "run": run,
                "verification": verification,
                "inputs": inputs,
                "outputs": outputs,
            }
        )
    return runs_data


def generate_simple_dag(
    lines: list,
    runs_data: list,
    chain_ids: list,
    path_mode: PathMode = "name",
) -> None:
    """Generate simple script-only DAG."""
    for data in runs_data:
        sid = data["session_id"]
        run = data["run"]
        verification = data["verification"]
        node_id = sid.replace("-", "_").replace(".", "_")
        status_class = "verified" if verification.is_verified else "failed"
        script_name = format_path(
            run.get("script_path", "unknown") if run else "unknown", path_mode
        )
        lines.append(f'    {node_id}["{script_name}"]:::{status_class}')

    for i in range(len(chain_ids) - 1):
        curr = chain_ids[i].replace("-", "_").replace(".", "_")
        parent = chain_ids[i + 1].replace("-", "_").replace(".", "_")
        lines.append(f"    {parent} --> {curr}")


def generate_detailed_dag(
    lines: list,
    runs_data: list,
    show_hashes: bool = False,
    path_mode: PathMode = "name",
) -> None:
    """Generate detailed DAG with input/output files and verification status."""
    from ._json import verify_file_hash

    file_nodes = {}
    failed_files = set()
    runs_data = list(reversed(runs_data))

    for data in runs_data:
        inputs = data["inputs"]
        outputs = data["outputs"]
        for fpath, stored_hash in {**inputs, **outputs}.items():
            if not verify_file_hash(fpath, stored_hash):
                failed_files.add(fpath)

    for data in runs_data:
        inputs = data["inputs"]
        outputs = data["outputs"]
        has_failed_input = any(fpath in failed_files for fpath in inputs.keys())
        if has_failed_input:
            for fpath in outputs.keys():
                failed_files.add(fpath)

    for i, data in enumerate(runs_data):
        sid = data["session_id"]
        run = data["run"]
        verification = data["verification"]
        inputs = data["inputs"]
        outputs = data["outputs"]

        has_failed_input = any(fpath in failed_files for fpath in inputs.keys())

        add_script_node(
            lines, i, sid, run, verification, path_mode, show_hashes, has_failed_input
        )
        is_rerun = verification.is_verified_from_scratch
        add_file_nodes(
            lines,
            f"script_{i}",
            inputs,
            file_nodes,
            show_hashes,
            path_mode,
            "input",
            False,
            failed_files,
        )
        add_file_nodes(
            lines,
            f"script_{i}",
            outputs,
            file_nodes,
            show_hashes,
            path_mode,
            "output",
            is_rerun,
            failed_files,
        )


def generate_multi_target_dag(
    target_files: Optional[List[str]] = None,
    claims: bool = False,
    show_files: bool = True,
    show_hashes: bool = False,
    path_mode: PathMode = "name",
) -> str:
    """Generate Mermaid diagram for a multi-target DAG."""
    lines = ["graph TD"]

    if claims:
        from .._claim import verify_claims_dag

        dag = verify_claims_dag()
    elif target_files:
        from .._dag import verify_dag

        dag = verify_dag(target_files)
    else:
        lines.append('    empty["No targets specified"]')
        return "\n".join(lines)

    if not dag.runs:
        lines.append('    empty["No runs found"]')
        return "\n".join(lines)

    db = get_db()
    verifications = {r.session_id: r for r in dag.runs}

    runs_data = []
    for sid in dag.topological_order:
        run = db.get_run(sid)
        verification = verifications.get(sid)
        if not verification:
            continue
        inputs = db.get_file_hashes(sid, role="input")
        outputs = db.get_file_hashes(sid, role="output")
        runs_data.append(
            {
                "session_id": sid,
                "run": run,
                "verification": verification,
                "inputs": inputs,
                "outputs": outputs,
            }
        )

    if show_files:
        generate_detailed_dag(lines, runs_data, show_hashes, path_mode)
    else:
        generate_simple_dag(
            lines,
            runs_data,
            [d["session_id"] for d in runs_data],
            path_mode,
        )

    append_class_definitions(lines)
    return "\n".join(lines)


# EOF
