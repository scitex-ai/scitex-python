#!/usr/bin/env python3
# Timestamp: 2026-03-19
# File: /home/ywatanabe/proj/scitex-python/src/scitex/logging/llm/_dashboard.py

"""Multi-session dashboard with project grouping and session switching."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


def _decode_project_path(encoded: str) -> str:
    """Decode Claude Code's encoded project directory name back to a path.

    Claude Code encodes paths by replacing '/' with '-'.
    e.g. '-home-ywatanabe-proj-scitex-python' -> '/home/ywatanabe/proj/scitex-python'

    We greedily resolve from left to right, preferring existing directories.
    """
    if not encoded.startswith("-"):
        return encoded

    # Split on '-', first element is empty (leading '-')
    parts = encoded.split("-")
    parts = parts[1:]  # remove leading empty string

    # Greedy left-to-right: try to find longest existing directory segments
    result = ""
    i = 0
    while i < len(parts):
        # Try joining remaining parts with '-' and check if adding to path works
        best_len = 1
        for j in range(len(parts), i, -1):
            candidate_segment = "-".join(parts[i:j])
            candidate_path = result + "/" + candidate_segment
            if Path(candidate_path).exists():
                best_len = j - i
                break
        result += "/" + "-".join(parts[i : i + best_len])
        i += best_len

    return result


def discover_sessions(
    claude_dir: str | Path = "~/.claude",
) -> dict[str, list[dict[str, Any]]]:
    """Discover all Claude Code sessions grouped by project.

    Parameters
    ----------
    claude_dir : str or Path
        Claude config directory (default: ~/.claude).

    Returns
    -------
    dict[str, list[dict]]
        Project path -> list of session info dicts.
        Each dict: {"path": Path, "session_id": str, "slug": str, ...}
    """
    claude_dir = Path(claude_dir).expanduser().resolve()
    projects_dir = claude_dir / "projects"
    if not projects_dir.exists():
        return {}

    projects: dict[str, list[dict[str, Any]]] = {}

    for project_dir in sorted(projects_dir.iterdir()):
        if not project_dir.is_dir():
            continue

        # Decode project path from directory name
        project_name = _decode_project_path(project_dir.name)
        sessions = []

        for jsonl_file in sorted(project_dir.glob("*.jsonl")):
            info = _peek_session(jsonl_file)
            if info:
                sessions.append(info)

        if sessions:
            # Sort by most recent first
            sessions.sort(key=lambda s: s.get("first_timestamp", ""), reverse=True)
            projects[project_name] = sessions

    return projects


def _peek_session(path: Path) -> dict[str, Any] | None:
    """Read first few lines to get session metadata without full parse."""
    info: dict[str, Any] = {"path": path, "session_id": "", "slug": ""}
    entry_count = 0
    user_count = 0
    assistant_count = 0

    try:
        with open(path, encoding="utf-8") as f:
            for i, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                try:
                    raw = json.loads(line)
                except json.JSONDecodeError:
                    continue

                entry_type = raw.get("type", "")

                if not info["session_id"]:
                    info["session_id"] = raw.get("sessionId", "")
                    info["slug"] = raw.get("slug", "")
                    info["version"] = raw.get("version", "")
                    info["git_branch"] = raw.get("gitBranch", "")
                    info["first_timestamp"] = raw.get("timestamp", "")

                if entry_type == "user":
                    user_count += 1
                elif entry_type == "assistant":
                    assistant_count += 1

                entry_count += 1
                # Read last timestamp from every entry
                ts = raw.get("timestamp", "")
                if ts:
                    info["last_timestamp"] = ts

        info["entry_count"] = entry_count
        info["user_count"] = user_count
        info["assistant_count"] = assistant_count
        info["file_size_kb"] = path.stat().st_size // 1024

    except Exception:
        return None

    if entry_count == 0:
        return None

    return info


def _esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def render_dashboard(
    output: str | Path,
    claude_dir: str | Path = "~/.claude",
) -> Path:
    """Render a multi-session dashboard as self-contained HTML.

    Parameters
    ----------
    output : str or Path
        Output HTML file path.
    claude_dir : str or Path
        Claude config directory.

    Returns
    -------
    Path
        Path to written HTML file.
    """
    output = Path(output).expanduser().resolve()
    projects = discover_sessions(claude_dir)

    total_sessions = sum(len(s) for s in projects.values())

    css = """\
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
       background: #0d1117; color: #c9d1d9; padding: 24px; }
h1 { color: #58a6ff; margin-bottom: 4px; font-size: 1.5em; }
.subtitle { color: #8b949e; margin-bottom: 24px; font-size: 0.85em; }
.project { margin-bottom: 24px; }
.project-header { background: #161b22; padding: 12px 16px; border-radius: 8px 8px 0 0;
                   border: 1px solid #30363d; border-bottom: none; cursor: pointer;
                   display: flex; justify-content: space-between; align-items: center; }
.project-header:hover { background: #1c2128; }
.project-name { color: #58a6ff; font-weight: 600; font-size: 0.95em; }
.project-count { color: #8b949e; font-size: 0.8em; }
.project-body { border: 1px solid #30363d; border-top: none; border-radius: 0 0 8px 8px;
                display: none; }
.project-body.open { display: block; }
.session { padding: 10px 16px; border-bottom: 1px solid #21262d; display: flex;
           justify-content: space-between; align-items: center; cursor: pointer; }
.session:last-child { border-bottom: none; }
.session:hover { background: #161b22; }
.session-left { display: flex; flex-direction: column; gap: 2px; }
.session-slug { color: #c9d1d9; font-weight: 500; font-size: 0.9em; }
.session-id { color: #8b949e; font-size: 0.75em; font-family: monospace; }
.session-meta { color: #8b949e; font-size: 0.75em; }
.session-right { display: flex; gap: 12px; align-items: center; }
.badge { padding: 2px 8px; border-radius: 10px; font-size: 0.7em; font-weight: 600; }
.badge-entries { background: #1f3a5f; color: #58a6ff; }
.badge-size { background: #2a1f0b; color: #d29922; }
.session-actions { display: flex; gap: 6px; }
.btn { padding: 4px 10px; border-radius: 4px; border: 1px solid #30363d; background: #21262d;
       color: #c9d1d9; font-size: 0.75em; cursor: pointer; text-decoration: none; }
.btn:hover { background: #30363d; }
.btn-primary { border-color: #58a6ff; color: #58a6ff; }
.btn-primary:hover { background: #0d2847; }
.toggle-arrow { transition: transform 0.2s; display: inline-block; margin-right: 8px; }
.toggle-arrow.open { transform: rotate(90deg); }
.stats { display: flex; gap: 24px; margin-bottom: 24px; }
.stat { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 12px 16px;
        min-width: 120px; }
.stat-label { color: #8b949e; font-size: 0.75em; }
.stat-value { color: #c9d1d9; font-size: 1.3em; font-weight: 700; }
"""

    js = """\
document.querySelectorAll('.project-header').forEach(h => {
  h.addEventListener('click', () => {
    const body = h.nextElementSibling;
    const arrow = h.querySelector('.toggle-arrow');
    body.classList.toggle('open');
    arrow.classList.toggle('open');
  });
});
"""

    parts = [
        "<!DOCTYPE html>",
        '<html lang="en"><head><meta charset="utf-8">',
        "<title>Claude Code Dashboard</title>",
        f"<style>{css}</style>",
        "</head><body>",
        "<h1>Claude Code Dashboard</h1>",
        f'<div class="subtitle">{len(projects)} projects, {total_sessions} sessions</div>',
        '<div class="stats">',
        f'<div class="stat"><div class="stat-label">Projects</div><div class="stat-value">{len(projects)}</div></div>',
        f'<div class="stat"><div class="stat-label">Sessions</div><div class="stat-value">{total_sessions}</div></div>',
        "</div>",
    ]

    for project_name, sessions in sorted(projects.items()):
        parts.append('<div class="project">')
        parts.append(
            f'<div class="project-header">'
            f'<span><span class="toggle-arrow">&#9654;</span>'
            f'<span class="project-name">{_esc(project_name)}</span></span>'
            f'<span class="project-count">{len(sessions)} sessions</span>'
            f"</div>"
        )
        parts.append('<div class="project-body">')

        for s in sessions:
            slug = s.get("slug", "") or s["session_id"][:12]
            sid = s["session_id"][:12]
            branch = s.get("git_branch", "")
            entries = s.get("entry_count", 0)
            size_kb = s.get("file_size_kb", 0)
            ts = s.get("first_timestamp", "")[:19]
            jsonl_path = str(s["path"])

            parts.append(f'<div class="session" data-path="{_esc(jsonl_path)}">')
            parts.append('<div class="session-left">')
            parts.append(f'<div class="session-slug">{_esc(slug)}</div>')
            parts.append(
                f'<div class="session-id">{_esc(sid)} &middot; {_esc(branch)} &middot; {_esc(ts)}</div>'
            )
            parts.append("</div>")
            parts.append('<div class="session-right">')
            parts.append(f'<span class="badge badge-entries">{entries} entries</span>')
            parts.append(f'<span class="badge badge-size">{size_kb} KB</span>')
            parts.append("</div>")
            parts.append("</div>")

        parts.append("</div></div>")

    parts.append(f"<script>{js}</script>")
    parts.append("</body></html>")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(parts), encoding="utf-8")
    return output


# EOF
