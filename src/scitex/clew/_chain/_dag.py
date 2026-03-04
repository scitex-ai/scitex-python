#!/usr/bin/env python3
# Timestamp: "2026-02-01 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/clew/_chain/_dag.py
"""DAG topological sort and multi-target DAG verification."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Union

from .._db import get_db
from ._types import DAGVerification, RunVerification, VerificationStatus
from ._verify_ops import verify_run


def _topological_sort(adjacency: Dict[str, List[str]]) -> List[str]:
    """Topological sort of DAG using Kahn's algorithm.

    Parameters
    ----------
    adjacency : dict
        {child_session: [parent_sessions, ...]}

    Returns
    -------
    list of str
        Session IDs in topological order (roots first)

    Raises
    ------
    ValueError
        If a cycle is detected in the DAG
    """
    from collections import defaultdict, deque

    # Build in-degree and forward adjacency (parent -> children)
    all_nodes = set()
    forward: Dict[str, List[str]] = defaultdict(list)
    in_degree: Dict[str, int] = {}

    for child, parents in adjacency.items():
        all_nodes.add(child)
        for p in parents:
            all_nodes.add(p)
            forward[p].append(child)

    for node in all_nodes:
        in_degree[node] = len(adjacency.get(node, []))

    queue = deque(n for n in all_nodes if in_degree[n] == 0)
    result = []

    while queue:
        node = queue.popleft()
        result.append(node)
        for child in forward[node]:
            in_degree[child] -= 1
            if in_degree[child] == 0:
                queue.append(child)

    if len(result) != len(all_nodes):
        raise ValueError("Cycle detected in DAG")

    return result


def verify_dag(
    targets: List[Union[str, Path]],
) -> DAGVerification:
    """Verify the full DAG for one or more target files.

    Traces back through all sessions that produced the target files,
    collecting the full multi-parent DAG and verifying each session.

    Parameters
    ----------
    targets : list of str or Path
        Target files to trace back to sources

    Returns
    -------
    DAGVerification
        Unified verification result for the entire DAG
    """
    db = get_db()

    # Resolve targets to leaf session IDs
    leaf_sessions = []
    resolved_targets = []
    for target in targets:
        target_str = str(Path(target).resolve())
        resolved_targets.append(target_str)
        sessions = db.find_session_by_file(target_str, role="output")
        if sessions:
            leaf_sessions.append(sessions[0])

    if not leaf_sessions:
        return DAGVerification(
            target_files=resolved_targets,
            runs=[],
            edges=[],
            status=VerificationStatus.UNKNOWN,
            topological_order=[],
        )

    # BFS backward to collect full DAG
    adjacency, all_ids = db.get_dag(leaf_sessions)

    # Topological sort (roots first)
    topo_order = _topological_sort(adjacency)

    # Verify each session exactly once
    verifications: Dict[str, RunVerification] = {}
    for sid in topo_order:
        verifications[sid] = verify_run(sid, propagate=False)

    # Propagate failures forward through the DAG
    failed_sessions: set = set()
    for sid in topo_order:
        parents = adjacency.get(sid, [])
        has_failed_parent = any(p in failed_sessions for p in parents)
        if has_failed_parent or not verifications[sid].is_verified:
            failed_sessions.add(sid)

    # Build edges list
    edges = []
    for child, parents in adjacency.items():
        for p in parents:
            edges.append((p, child))

    # Determine overall status
    run_list = [verifications[sid] for sid in topo_order]
    if all(sid not in failed_sessions for sid in topo_order):
        status = VerificationStatus.VERIFIED
    elif any(
        verifications[sid].status == VerificationStatus.MISMATCH for sid in topo_order
    ):
        status = VerificationStatus.MISMATCH
    elif any(
        verifications[sid].status == VerificationStatus.MISSING for sid in topo_order
    ):
        status = VerificationStatus.MISSING
    else:
        status = VerificationStatus.UNKNOWN

    return DAGVerification(
        target_files=resolved_targets,
        runs=run_list,
        edges=edges,
        status=status,
        topological_order=topo_order,
    )


# EOF
