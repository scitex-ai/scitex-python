#!/usr/bin/env python3
# Timestamp: 2026-03-19
# File: /home/ywatanabe/proj/scitex-python/src/scitex/logging/llm/_spa.py

"""Generate a single-page app for browsing Claude Code session logs."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from ._actions import extract_actions
from ._dashboard import discover_sessions
from ._parser import load
from ._replay import _action_to_script
from ._spa_css import CSS
from ._spa_js import JS


def _truncate_input(inp: dict[str, Any], max_len: int) -> dict[str, Any]:
    result = {}
    for k, v in inp.items():
        if isinstance(v, str) and len(v) > max_len:
            result[k] = v[:max_len] + "..."
        else:
            result[k] = v
    return result


def _serialize_session(
    session_info: dict[str, Any], max_output: int = 5000
) -> dict[str, Any] | None:
    """Load and serialize a full session for embedding."""
    path = session_info["path"]
    try:
        session = load(path)
        actions = extract_actions(path)
    except Exception:
        return None

    entries = []
    for e in session.entries:
        entry: dict[str, Any] = {
            "type": e.type,
            "ts": e.timestamp,
            "text": e.text[:max_output] if e.text else "",
            "model": e.model,
        }
        if e.tool_calls:
            entry["tool_calls"] = [
                {
                    "id": tc.id,
                    "name": tc.name,
                    "input": _truncate_input(tc.input, 2000),
                }
                for tc in e.tool_calls
            ]
        if e.tool_result:
            tr = e.tool_result
            entry["tool_result"] = {
                "tool_use_id": tr.tool_use_id,
                "stdout": (tr.stdout or "")[:max_output],
                "stderr": (tr.stderr or "")[:1000],
            }
        entries.append(entry)

    action_list = []
    for i, a in enumerate(actions, 1):
        ad: dict[str, Any] = {
            "index": i,
            "tool_name": a.tool_name,
            "tool_use_id": a.tool_use_id,
            "ts": a.timestamp,
            "description": a.description,
            "command": a.command[:200] if a.command else "",
            "file_path": a.file_path,
            "stdout": (a.stdout or a.result_content or "")[:max_output],
            "stderr": (a.stderr or "")[:1000],
            "exit_code": a.exit_code,
        }
        try:
            ad["script"] = _action_to_script(a, i)
        except Exception:
            ad["script"] = f"# {a.tool_name} (script generation failed)"
        action_list.append(ad)

    stats = session.summary()
    return {
        "id": session.session_id,
        "slug": session.slug or session.session_id[:12],
        "git_branch": session.git_branch,
        "version": session.version,
        "first_ts": session_info.get("first_timestamp", ""),
        "last_ts": session_info.get("last_timestamp", ""),
        "stats": {
            "entries": stats["total_entries"],
            "user_turns": stats["user_turns"],
            "assistant_turns": stats["assistant_turns"],
            "tool_calls": stats["total_tool_calls"],
            "input_tokens": stats["total_input_tokens"],
            "output_tokens": stats["total_output_tokens"],
            "tokens": stats["total_tokens"],
            "tool_usage": stats["tool_usage"],
        },
        "entries": entries,
        "actions": action_list,
    }


def render_spa(
    output: str | Path,
    claude_dir: str | Path = "~/.claude",
    max_output_chars: int = 3000,
    max_sessions_per_project: int = 3,
    max_entries_per_session: int = 200,
) -> Path:
    """Generate a single-page HTML app for browsing all Claude Code sessions.

    Parameters
    ----------
    output : str or Path
        Output HTML file path.
    claude_dir : str or Path
        Claude config directory.
    max_output_chars : int
        Max chars per tool output.
    max_sessions_per_project : int
        Max sessions to fully load per project (most recent).
    max_entries_per_session : int
        Max entries per session to include.

    Returns
    -------
    Path
        Path to written HTML file.
    """
    output = Path(output).expanduser().resolve()
    projects_raw = discover_sessions(claude_dir)

    data: dict[str, Any] = {
        "generated_at": datetime.now().isoformat(),
        "projects": {},
    }

    for proj_path, sessions_info in projects_raw.items():
        serialized = []
        # Only fully load the N most recent sessions
        for si in sessions_info[:max_sessions_per_project]:
            s = _serialize_session(si, max_output_chars)
            if s:
                # Limit entries
                if len(s["entries"]) > max_entries_per_session:
                    s["entries"] = s["entries"][:max_entries_per_session]
                    s["truncated"] = True
                serialized.append(s)
        if serialized:
            data["projects"][proj_path] = {"sessions": serialized}

    data_json = json.dumps(data, ensure_ascii=False, default=str)
    # Escape </script> to prevent breaking out of the script tag
    # Use unicode escape which is valid JSON
    data_json = data_json.replace("</", "<\\u002f")

    html_content = _build_html(data_json)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html_content, encoding="utf-8")
    return output


def _build_html(data_json: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Claude Code Sessions</title>
<style>{CSS}</style>
</head>
<body>
<div id="chrome">
  <div id="topbar">
    <a href="#projects" class="logo">Claude Code Sessions</a>
    <div id="topbar-right">
      <input type="text" id="search" placeholder="Search..." oninput="filterCurrent()">
      <button onclick="exportHTML()" class="btn">Export HTML</button>
    </div>
  </div>
  <div id="breadcrumb"></div>
</div>
<div id="app"></div>
<div id="toast" class="toast"></div>
<script id="app-data" type="application/json">{data_json}</script>
<script>{JS}</script>
</body>
</html>"""


# EOF
