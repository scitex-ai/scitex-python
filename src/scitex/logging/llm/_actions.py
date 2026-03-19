#!/usr/bin/env python3
# Timestamp: 2026-03-19
# File: /home/ywatanabe/proj/scitex-python/src/scitex/logging/llm/_actions.py

"""Extract agent actions (tool calls + results) from Claude Code sessions.

Pairs each tool_use with its tool_result for reproducibility tracking.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass
class Action:
    """A single agent action: tool call paired with its result."""

    tool_name: str
    tool_input: dict[str, Any]
    tool_use_id: str
    timestamp: str = ""
    result_content: str = ""
    stdout: str = ""
    stderr: str = ""
    exit_code: Optional[int] = None
    interrupted: bool = False
    is_image: bool = False

    @property
    def command(self) -> str:
        """For Bash tools, return the command string."""
        return self.tool_input.get("command", "")

    @property
    def file_path(self) -> str:
        """For file tools (Read/Write/Edit), return the path."""
        return self.tool_input.get("file_path", "")

    @property
    def description(self) -> str:
        """Short description of the action."""
        return self.tool_input.get("description", "")

    def to_dict(self) -> dict[str, Any]:
        d = {
            "tool_name": self.tool_name,
            "timestamp": self.timestamp,
            "tool_use_id": self.tool_use_id,
        }
        if self.command:
            d["command"] = self.command
        if self.file_path:
            d["file_path"] = self.file_path
        if self.description:
            d["description"] = self.description
        if self.tool_input:
            d["tool_input"] = self.tool_input
        if self.stdout:
            d["stdout"] = self.stdout
        if self.stderr:
            d["stderr"] = self.stderr
        if self.exit_code is not None:
            d["exit_code"] = self.exit_code
        if self.result_content:
            d["result_content"] = self.result_content
        return d


def extract_actions(path: str | Path) -> list[Action]:
    """Extract all tool actions with paired results from a JSONL session.

    Reads the raw JSONL (not via parser) to capture tool_result pairing
    at the content-block level using tool_use_id matching.

    Parameters
    ----------
    path : str or Path
        Path to session .jsonl file.

    Returns
    -------
    list[Action]
        Ordered list of tool actions with inputs and outputs.
    """
    path = Path(path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"Session log not found: {path}")

    # First pass: collect all tool_use blocks
    pending: dict[str, Action] = {}  # tool_use_id -> Action
    actions: list[Action] = []
    order: list[str] = []  # preserve ordering

    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError:
                continue

            entry_type = raw.get("type", "")
            timestamp = raw.get("timestamp", "")
            msg = raw.get("message", {})
            if not isinstance(msg, dict):
                continue

            content = msg.get("content", "")
            if not isinstance(content, list):
                continue

            for block in content:
                if not isinstance(block, dict):
                    continue

                if block.get("type") == "tool_use":
                    tool_id = block.get("id", "")
                    action = Action(
                        tool_name=block.get("name", ""),
                        tool_input=block.get("input", {}),
                        tool_use_id=tool_id,
                        timestamp=timestamp,
                    )
                    pending[tool_id] = action
                    order.append(tool_id)

                elif block.get("type") == "tool_result":
                    tool_id = block.get("tool_use_id", "")
                    if tool_id in pending:
                        action = pending[tool_id]
                        # Extract result content
                        bc = block.get("content", "")
                        if isinstance(bc, str):
                            action.result_content = bc
                        elif isinstance(bc, list):
                            parts = []
                            for sub in bc:
                                if isinstance(sub, dict) and sub.get("type") == "text":
                                    parts.append(sub.get("text", ""))
                            action.result_content = "\n".join(parts)
                        else:
                            action.result_content = str(bc)

            # Also check toolUseResult (structured stdout/stderr)
            tr = raw.get("toolUseResult")
            if tr and isinstance(tr, dict):
                # Find which tool this result belongs to
                prompt_id = raw.get("promptId", "")
                # Match by looking at content for tool_result blocks
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_result":
                        tid = block.get("tool_use_id", "")
                        if tid in pending:
                            pending[tid].stdout = tr.get("stdout", "") or ""
                            pending[tid].stderr = tr.get("stderr", "") or ""
                            pending[tid].exit_code = tr.get(
                                "exit_code", tr.get("exitCode")
                            )
                            pending[tid].interrupted = tr.get("interrupted", False)
                            pending[tid].is_image = tr.get("isImage", False)

    # Build ordered list
    for tid in order:
        if tid in pending:
            actions.append(pending[tid])

    return actions


def actions_to_log(actions: list[Action], max_output: int = 3000) -> str:
    """Format actions as a human-readable log (similar to hook output).

    Parameters
    ----------
    actions : list[Action]
        Actions to format.
    max_output : int
        Max chars for stdout/stderr.

    Returns
    -------
    str
        Formatted log text.
    """
    lines = []
    for a in actions:
        lines.append("=" * 72)
        lines.append(f"Time: {a.timestamp}")
        lines.append(f"Tool: {a.tool_name}")

        if a.tool_name == "Bash" and a.command:
            cmd = a.command.replace("\n", "\\n")[:200]
            lines.append(f"Cmd:  {cmd}")
            if a.description:
                lines.append(f"Desc: {a.description[:100]}")
        elif a.tool_name in ("Write", "Edit", "Read") and a.file_path:
            lines.append(f"File: {a.file_path}")
            if a.tool_name == "Edit":
                old = (a.tool_input.get("old_string", "") or "")[:80].replace(
                    "\n", "\\n"
                )
                new = (a.tool_input.get("new_string", "") or "")[:80].replace(
                    "\n", "\\n"
                )
                if old:
                    lines.append(f"Old:  {old}")
                if new:
                    lines.append(f"New:  {new}")
        elif a.tool_name in ("Glob", "Grep"):
            pat = a.tool_input.get("pattern", "")
            p = a.tool_input.get("path", "")
            if pat:
                lines.append(f"Pattern: {pat}")
            if p:
                lines.append(f"Path: {p}")
        elif a.tool_name == "Agent":
            desc = a.tool_input.get("description", "")
            agent = a.tool_input.get("subagent_type", "")
            if desc:
                lines.append(f"Desc: {desc}")
            if agent:
                lines.append(f"Agent: {agent}")
        else:
            for k, v in list(a.tool_input.items())[:3]:
                if v and isinstance(v, str):
                    val = str(v)[:100].replace("\n", "\\n")
                    lines.append(f"{k}: {val}")

        if a.exit_code is not None:
            lines.append(f"Exit: {a.exit_code}")

        output = a.stdout or a.result_content
        if output and output not in ("None", "", "null"):
            lines.append("--- stdout ---")
            if len(output) > max_output:
                lines.append(output[:max_output])
                lines.append(f"... [truncated, {len(output)} total chars]")
            else:
                lines.append(output)

        if a.stderr:
            lines.append("--- stderr ---")
            if len(a.stderr) > max_output:
                lines.append(a.stderr[:max_output])
                lines.append(f"... [truncated, {len(a.stderr)} total chars]")
            else:
                lines.append(a.stderr)

        lines.append("")

    return "\n".join(lines)


def actions_to_jsonl(actions: list[Action]) -> str:
    """Export actions as JSONL for reproducibility.

    Parameters
    ----------
    actions : list[Action]
        Actions to export.

    Returns
    -------
    str
        One JSON object per line.
    """
    return "\n".join(json.dumps(a.to_dict()) for a in actions)


# EOF
