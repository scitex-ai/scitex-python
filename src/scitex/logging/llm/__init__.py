#!/usr/bin/env python3
# Timestamp: 2026-03-19
# File: /home/ywatanabe/proj/scitex-python/src/scitex/logging/llm/__init__.py

"""LLM session log utilities.

Parse, render, and analyze Claude Code JSONL session logs.

Usage
-----
>>> import scitex
>>> log = scitex.logging.llm.load("~/.claude/projects/xxx/session.jsonl")
>>> log.summary()          # Token counts, duration, tool stats
>>> log.render("out.html") # Rich self-contained HTML
>>> log.to_dag()           # DAG of tool call dependencies
"""

from __future__ import annotations

from ._actions import Action, actions_to_jsonl, actions_to_log, extract_actions
from ._dag import build_dag, to_mermaid
from ._dashboard import discover_sessions, render_dashboard
from ._parser import ClaudeCodeSession, Entry, ToolCall, ToolResult, load
from ._replay import export_scripts
from ._spa import render_spa

__all__ = [
    "load",
    "ClaudeCodeSession",
    "Entry",
    "ToolCall",
    "ToolResult",
    "Action",
    "extract_actions",
    "actions_to_log",
    "actions_to_jsonl",
    "build_dag",
    "to_mermaid",
    "discover_sessions",
    "render_dashboard",
    "export_scripts",
    "render_spa",
]

# EOF
