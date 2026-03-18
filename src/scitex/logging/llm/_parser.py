#!/usr/bin/env python3
# Timestamp: 2026-03-19
# File: /home/ywatanabe/proj/scitex-python/src/scitex/logging/llm/_parser.py

"""Parse Claude Code JSONL session logs into structured data."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass
class ToolCall:
    """A tool invocation by the assistant."""

    id: str
    name: str
    input: dict[str, Any]
    timestamp: Optional[str] = None


@dataclass
class ToolResult:
    """Result returned for a tool call."""

    tool_use_id: str
    stdout: str = ""
    stderr: str = ""
    interrupted: bool = False
    is_image: bool = False


@dataclass
class Entry:
    """A single conversation entry (user or assistant turn)."""

    type: str  # "user", "assistant", "system"
    uuid: str = ""
    parent_uuid: str = ""
    timestamp: str = ""
    role: str = ""  # "user" or "assistant"
    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_result: Optional[ToolResult] = None
    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_tokens: int = 0
    cache_read_tokens: int = 0
    duration_ms: int = 0
    raw: dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass
class ClaudeCodeSession:
    """A parsed Claude Code session."""

    path: Path
    session_id: str = ""
    slug: str = ""
    entries: list[Entry] = field(default_factory=list)
    version: str = ""
    git_branch: str = ""

    @property
    def user_entries(self) -> list[Entry]:
        return [e for e in self.entries if e.type == "user"]

    @property
    def assistant_entries(self) -> list[Entry]:
        return [e for e in self.entries if e.type == "assistant"]

    @property
    def tool_calls(self) -> list[ToolCall]:
        calls = []
        for e in self.entries:
            calls.extend(e.tool_calls)
        return calls

    @property
    def total_input_tokens(self) -> int:
        return sum(e.input_tokens for e in self.entries)

    @property
    def total_output_tokens(self) -> int:
        return sum(e.output_tokens for e in self.entries)

    @property
    def total_tokens(self) -> int:
        return self.total_input_tokens + self.total_output_tokens

    def summary(self) -> dict[str, Any]:
        """Return session statistics."""
        tool_names = {}
        for tc in self.tool_calls:
            tool_names[tc.name] = tool_names.get(tc.name, 0) + 1

        durations = [e.duration_ms for e in self.entries if e.duration_ms > 0]
        return {
            "session_id": self.session_id,
            "slug": self.slug,
            "version": self.version,
            "git_branch": self.git_branch,
            "total_entries": len(self.entries),
            "user_turns": len(self.user_entries),
            "assistant_turns": len(self.assistant_entries),
            "total_tool_calls": len(self.tool_calls),
            "tool_usage": dict(sorted(tool_names.items(), key=lambda x: -x[1])),
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_tokens,
            "total_duration_ms": sum(durations),
        }

    def render(self, output: str | Path) -> Path:
        """Render session as rich HTML."""
        from ._renderer import render_html

        return render_html(self, output)

    def to_dag(self) -> dict[str, Any]:
        """Extract DAG of tool call dependencies."""
        from ._dag import build_dag

        return build_dag(self)


def _parse_entry(raw: dict[str, Any]) -> Optional[Entry]:
    """Parse a single JSONL line into an Entry."""
    entry_type = raw.get("type", "")

    if entry_type not in ("user", "assistant", "system"):
        return None

    entry = Entry(type=entry_type, raw=raw)
    entry.uuid = raw.get("uuid", "")
    entry.parent_uuid = raw.get("parentUuid", "")
    entry.timestamp = raw.get("timestamp", "")

    msg = raw.get("message", {})
    if isinstance(msg, dict):
        entry.role = msg.get("role", "")
        content = msg.get("content", "")

        if isinstance(content, str):
            entry.text = content
        elif isinstance(content, list):
            text_parts = []
            for block in content:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
                elif block.get("type") == "tool_use":
                    entry.tool_calls.append(
                        ToolCall(
                            id=block.get("id", ""),
                            name=block.get("name", ""),
                            input=block.get("input", {}),
                            timestamp=entry.timestamp,
                        )
                    )
                elif block.get("type") == "tool_result":
                    for sub in block.get("content", []):
                        if isinstance(sub, dict) and sub.get("type") == "text":
                            text_parts.append(sub.get("text", ""))
            entry.text = "\n".join(text_parts)

        usage = msg.get("usage", {})
        if usage:
            entry.input_tokens = usage.get("input_tokens", 0)
            entry.output_tokens = usage.get("output_tokens", 0)
            entry.cache_creation_tokens = usage.get("cache_creation_input_tokens", 0)
            entry.cache_read_tokens = usage.get("cache_read_input_tokens", 0)
        entry.model = msg.get("model", "")

    # Tool result from user entry
    tr = raw.get("toolUseResult")
    if tr and isinstance(tr, dict):
        entry.tool_result = ToolResult(
            tool_use_id=raw.get("promptId", ""),
            stdout=tr.get("stdout", ""),
            stderr=tr.get("stderr", ""),
            interrupted=tr.get("interrupted", False),
            is_image=tr.get("isImage", False),
        )

    # System turn duration
    if entry_type == "system" and raw.get("subtype") == "turn_duration":
        entry.duration_ms = raw.get("durationMs", 0)

    return entry


def load(path: str | Path) -> ClaudeCodeSession:
    """Load a Claude Code JSONL session log.

    Parameters
    ----------
    path : str or Path
        Path to a .jsonl session file.

    Returns
    -------
    ClaudeCodeSession
        Parsed session with entries, tool calls, and metadata.

    Examples
    --------
    >>> import scitex
    >>> log = scitex.logging.llm.load("~/.claude/projects/xxx/session.jsonl")
    >>> log.summary()
    >>> log.render("output.html")
    """
    path = Path(path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"Session log not found: {path}")

    session = ClaudeCodeSession(path=path)
    entries = []

    with open(path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError:
                continue

            # Extract session metadata from first entry
            if not session.session_id:
                session.session_id = raw.get("sessionId", "")
                session.slug = raw.get("slug", "")
                session.version = raw.get("version", "")
                session.git_branch = raw.get("gitBranch", "")

            entry = _parse_entry(raw)
            if entry is not None:
                entries.append(entry)

    session.entries = entries
    return session


# EOF
