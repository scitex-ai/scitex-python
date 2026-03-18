#!/usr/bin/env python3
# Timestamp: 2026-03-19
# File: /home/ywatanabe/proj/scitex-python/src/scitex/logging/llm/_dag.py

"""Build DAG from Claude Code session tool calls."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ._parser import ClaudeCodeSession


def build_dag(session: ClaudeCodeSession) -> dict[str, Any]:
    """Build a directed acyclic graph of tool call dependencies.

    Each tool call becomes a node. Sequential tool calls within an assistant
    turn are connected by edges. Cross-turn edges connect the last tool call
    of one turn to the first of the next.

    Parameters
    ----------
    session : ClaudeCodeSession
        Parsed session data.

    Returns
    -------
    dict
        DAG with "nodes" and "edges" lists.
        Each node: {"id": str, "name": str, "timestamp": str}
        Each edge: {"from": str, "to": str}
    """
    nodes = []
    edges = []
    prev_id = None

    for entry in session.entries:
        for tc in entry.tool_calls:
            node = {
                "id": tc.id,
                "name": tc.name,
                "timestamp": tc.timestamp or entry.timestamp,
            }
            nodes.append(node)

            if prev_id is not None:
                edges.append({"from": prev_id, "to": tc.id})
            prev_id = tc.id

    return {"nodes": nodes, "edges": edges}


def to_mermaid(session: ClaudeCodeSession) -> str:
    """Generate a Mermaid flowchart from session tool calls.

    Returns
    -------
    str
        Mermaid diagram source.
    """
    dag = build_dag(session)
    lines = ["graph TD"]

    for node in dag["nodes"]:
        safe_id = node["id"].replace("-", "_")
        lines.append(f'    {safe_id}["{node["name"]}"]')

    for edge in dag["edges"]:
        from_id = edge["from"].replace("-", "_")
        to_id = edge["to"].replace("-", "_")
        lines.append(f"    {from_id} --> {to_id}")

    return "\n".join(lines)


# EOF
