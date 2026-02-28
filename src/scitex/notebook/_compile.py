#!/usr/bin/env python3
"""Compile notebook execution history into a DAG from clew DB timestamps."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Union

logger = logging.getLogger(__name__)

from ._verify import _get_runs_for_notebook


@dataclass
class CompiledNotebook:
    """Result of compiling a notebook's execution history.

    Attributes
    ----------
    notebook_path : str
        Path to the source notebook.
    execution_order : list of str
        Session IDs in actual execution order (by timestamp).
    dag : dict
        Adjacency list: {session_id: [dependent_session_ids]}.
    runs : list of dict
        Run records sorted by execution time.
    """

    notebook_path: str
    execution_order: List[str] = field(default_factory=list)
    dag: Dict[str, List[str]] = field(default_factory=dict)
    runs: List[Dict] = field(default_factory=list)

    def to_script(self) -> str:
        """Generate a .py script with sessions in DAG order."""
        topo_order = _topological_sort(self.dag, self.execution_order)
        lines = [
            "#!/usr/bin/env python3",
            '"""Auto-compiled from notebook execution history."""',
            "",
            "import scitex as stx",
            "",
        ]

        for idx, sid in enumerate(topo_order):
            run = _find_run(self.runs, sid)
            script_path = run.get("script_path", "") if run else ""
            func_name = f"step_{idx:02d}_{_safe_name(sid)}"

            lines.append("")
            lines.append("@stx.session")
            lines.append(f"def {func_name}():")
            lines.append(f'    """Session: {sid}"""')
            lines.append(f"    # Original script: {script_path}")
            lines.append("    pass")
            lines.append("")
            lines.append(f"{func_name}()")
            lines.append("")

        return "\n".join(lines)

    def to_mermaid(self) -> str:
        """Generate a Mermaid DAG diagram of execution flow."""
        lines = ["graph TD"]
        for sid in self.execution_order:
            run = _find_run(self.runs, sid)
            label = _short_id(sid)
            if run:
                started = run.get("started_at", "")[:19]
                label = f"{_short_id(sid)}<br/>{started}"
            lines.append(f'    {_mermaid_id(sid)}["{label}"]')

        for parent, children in self.dag.items():
            for child in children:
                lines.append(f"    {_mermaid_id(parent)} --> {_mermaid_id(child)}")

        return "\n".join(lines)


def compile_notebook(path: Union[str, Path]) -> CompiledNotebook:
    """Compile a notebook's execution history into a DAG.

    Queries the clew DB for all sessions associated with this notebook,
    sorts by timestamp, and builds a dependency DAG based on shared
    input/output files.

    Parameters
    ----------
    path : str or Path
        Path to the .ipynb file.

    Returns
    -------
    CompiledNotebook
        Compiled execution history with DAG and execution order.
    """
    from scitex.clew import get_db

    path = Path(path).resolve()
    db = get_db()
    runs = _get_runs_for_notebook(db, str(path))

    if not runs:
        return CompiledNotebook(notebook_path=str(path))

    execution_order = [r["session_id"] for r in runs]
    dag = _build_dag(runs, db)

    return CompiledNotebook(
        notebook_path=str(path),
        execution_order=execution_order,
        dag=dag,
        runs=runs,
    )


def _build_dag(runs: List[Dict], db) -> Dict[str, List[str]]:
    """Build DAG from IO dependencies between sessions.

    Session A -> Session B if A produced a file that B consumed.
    """
    dag: Dict[str, List[str]] = {r["session_id"]: [] for r in runs}
    session_ids = {r["session_id"] for r in runs}

    # Map: output file -> producing session
    output_producers: Dict[str, str] = {}
    for run in runs:
        outputs = db.get_file_hashes(run["session_id"], role="output")
        for file_path in outputs:
            output_producers[file_path] = run["session_id"]

    # For each session's inputs, find the producer
    for run in runs:
        inputs = db.get_file_hashes(run["session_id"], role="input")
        for file_path in inputs:
            producer = output_producers.get(file_path)
            if producer and producer != run["session_id"]:
                if producer in session_ids:
                    if run["session_id"] not in dag[producer]:
                        dag[producer].append(run["session_id"])

    return dag


def _topological_sort(
    dag: Dict[str, List[str]], fallback_order: List[str]
) -> List[str]:
    """Topological sort of DAG, falling back to timestamp order.

    Detects cycles and warns if nodes are unreachable due to cycles.
    """
    from collections import deque as _deque  # noqa: STX-I007
    from warnings import warn as _warn  # noqa: STX-I007

    if not dag:
        return fallback_order

    in_degree: Dict[str, int] = dict.fromkeys(dag, 0)
    for children in dag.values():
        for child in children:
            in_degree.setdefault(child, 0)
            in_degree[child] += 1

    # Kahn's algorithm with fallback_order as tiebreaker
    order_map = {sid: i for i, sid in enumerate(fallback_order)}
    queue = _deque(
        sorted(
            [n for n, d in in_degree.items() if d == 0],
            key=lambda n: order_map.get(n, 999),
        )
    )
    result = []

    while queue:
        node = queue.popleft()
        result.append(node)
        for child in dag.get(node, []):
            in_degree[child] -= 1
            if in_degree[child] == 0:
                queue.append(child)
        # Re-sort for stable tiebreaking
        tmp = sorted(queue, key=lambda n: order_map.get(n, 999))
        queue.clear()
        queue.extend(tmp)

    # Detect cycle: nodes in DAG but not in result
    all_nodes = set(in_degree.keys())
    sorted_nodes = set(result)
    cyclic_nodes = all_nodes - sorted_nodes
    if cyclic_nodes:
        _warn(
            f"Cyclic dependencies detected among sessions: "
            f"{sorted(cyclic_nodes)}. These sessions will be appended "
            f"in timestamp order.",
            stacklevel=2,
        )

    # Add remaining nodes (cyclic or not in DAG) in fallback order
    remaining = [sid for sid in fallback_order if sid not in sorted_nodes]
    result.extend(remaining)

    return result


def _find_run(runs: List[Dict], session_id: str) -> Optional[Dict]:
    """Find a run by session ID."""
    for r in runs:
        if r["session_id"] == session_id:
            return r
    return None


def _safe_name(session_id: str) -> str:
    """Convert session ID to a valid Python identifier fragment."""
    return session_id.replace("-", "_").replace(".", "_")[:20]


def _short_id(session_id: str) -> str:
    """Shorten session ID for display."""
    return session_id[:20] if len(session_id) > 20 else session_id


def _mermaid_id(session_id: str) -> str:
    """Convert session ID to valid Mermaid node ID."""
    return session_id.replace("-", "_").replace(".", "_")


# EOF
