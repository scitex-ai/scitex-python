#!/usr/bin/env python3
# Timestamp: 2026-03-19
# File: /home/ywatanabe/proj/scitex-python/src/scitex/logging/llm/_renderer.py

"""Render Claude Code session as self-contained HTML."""

from __future__ import annotations

import html
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ._parser import ClaudeCodeSession

_CSS = """\
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
       background: #0d1117; color: #c9d1d9; padding: 24px; max-width: 960px; margin: 0 auto; }
h1 { color: #58a6ff; margin-bottom: 8px; font-size: 1.4em; }
.meta { color: #8b949e; font-size: 0.85em; margin-bottom: 24px; }
.meta span { margin-right: 16px; }
.entry { margin-bottom: 16px; border-radius: 8px; padding: 12px 16px; }
.entry-user { background: #0d2847; border-left: 3px solid #58a6ff; }
.entry-assistant { background: #161b22; border-left: 3px solid #8b949e; }
.entry-system { background: #1a1206; border-left: 3px solid #d29922; font-size: 0.85em; }
.role { font-weight: 600; font-size: 0.8em; text-transform: uppercase; margin-bottom: 6px; }
.role-user { color: #58a6ff; }
.role-assistant { color: #8b949e; }
.role-system { color: #d29922; }
.text { white-space: pre-wrap; word-wrap: break-word; line-height: 1.5; }
.tool-call { background: #1c2128; border: 1px solid #30363d; border-radius: 6px;
             margin: 8px 0; overflow: hidden; }
.tool-header { padding: 8px 12px; background: #21262d; cursor: pointer; font-size: 0.85em;
               display: flex; justify-content: space-between; align-items: center; }
.tool-header:hover { background: #282e36; }
.tool-name { color: #f0883e; font-weight: 600; }
.tool-body { padding: 12px; display: none; font-size: 0.8em; }
.tool-body.open { display: block; }
.tool-body pre { background: #0d1117; padding: 8px; border-radius: 4px;
                 overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; }
.tool-result { background: #0d2818; border: 1px solid #238636; border-radius: 6px;
               margin: 8px 0; padding: 8px 12px; font-size: 0.8em; }
.tool-result pre { white-space: pre-wrap; word-wrap: break-word; }
.tool-result-label { color: #3fb950; font-weight: 600; font-size: 0.8em; margin-bottom: 4px; }
.summary { background: #161b22; border: 1px solid #30363d; border-radius: 8px;
           padding: 16px; margin-top: 32px; }
.summary h2 { color: #58a6ff; font-size: 1.1em; margin-bottom: 12px; }
.summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                gap: 8px; }
.summary-item { padding: 8px; background: #0d1117; border-radius: 4px; }
.summary-label { color: #8b949e; font-size: 0.75em; }
.summary-value { color: #c9d1d9; font-size: 1.1em; font-weight: 600; }
.toggle-arrow { transition: transform 0.2s; display: inline-block; }
.toggle-arrow.open { transform: rotate(90deg); }
"""

_JS = """\
document.querySelectorAll('.tool-header').forEach(h => {
  h.addEventListener('click', () => {
    const body = h.nextElementSibling;
    const arrow = h.querySelector('.toggle-arrow');
    body.classList.toggle('open');
    arrow.classList.toggle('open');
  });
});
"""


def _esc(text: str) -> str:
    return html.escape(text, quote=True)


def _render_tool_input(inp: dict[str, Any]) -> str:
    parts = []
    for k, v in inp.items():
        val = str(v)
        if len(val) > 2000:
            val = val[:2000] + "\n... (truncated)"
        parts.append(f"{_esc(k)}: {_esc(val)}")
    return "\n".join(parts)


def _fmt_tokens(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def render_html(session: ClaudeCodeSession, output: str | Path) -> Path:
    """Render a ClaudeCodeSession to a self-contained HTML file.

    Parameters
    ----------
    session : ClaudeCodeSession
        Parsed session data.
    output : str or Path
        Output HTML file path.

    Returns
    -------
    Path
        Path to the written HTML file.
    """
    output = Path(output).expanduser().resolve()
    stats = session.summary()

    parts = [
        "<!DOCTYPE html>",
        '<html lang="en"><head><meta charset="utf-8">',
        f"<title>Claude Code Session: {_esc(session.slug or session.session_id[:12])}</title>",
        f"<style>{_CSS}</style>",
        "</head><body>",
        f"<h1>Claude Code Session: {_esc(session.slug or session.session_id[:12])}</h1>",
        '<div class="meta">',
        f"<span>Branch: {_esc(session.git_branch)}</span>",
        f"<span>Version: {_esc(session.version)}</span>",
        f"<span>Entries: {stats['total_entries']}</span>",
        f"<span>Tokens: {_fmt_tokens(stats['total_tokens'])}</span>",
        "</div>",
    ]

    for entry in session.entries:
        css_class = f"entry entry-{entry.type}"
        role_class = f"role role-{entry.type}"
        label = entry.type.upper()
        if entry.model:
            label += f" ({_esc(entry.model)})"

        parts.append(f'<div class="{css_class}">')
        parts.append(f'<div class="{role_class}">{label}</div>')

        if entry.text:
            parts.append(f'<div class="text">{_esc(entry.text)}</div>')

        for tc in entry.tool_calls:
            inp_text = _render_tool_input(tc.input)
            parts.append('<div class="tool-call">')
            parts.append(
                f'<div class="tool-header">'
                f'<span class="tool-name">{_esc(tc.name)}</span>'
                f'<span class="toggle-arrow">&#9654;</span>'
                f"</div>"
            )
            parts.append(f'<div class="tool-body"><pre>{inp_text}</pre></div>')
            parts.append("</div>")

        if entry.tool_result and (entry.tool_result.stdout or entry.tool_result.stderr):
            result_text = entry.tool_result.stdout
            if entry.tool_result.stderr:
                result_text += f"\n[stderr] {entry.tool_result.stderr}"
            if len(result_text) > 5000:
                result_text = result_text[:5000] + "\n... (truncated)"
            parts.append('<div class="tool-result">')
            parts.append('<div class="tool-result-label">Tool Result</div>')
            parts.append(f"<pre>{_esc(result_text)}</pre>")
            parts.append("</div>")

        parts.append("</div>")

    # Summary section
    parts.append('<div class="summary">')
    parts.append("<h2>Session Summary</h2>")
    parts.append('<div class="summary-grid">')
    for label, value in [
        ("User Turns", stats["user_turns"]),
        ("Assistant Turns", stats["assistant_turns"]),
        ("Tool Calls", stats["total_tool_calls"]),
        ("Input Tokens", _fmt_tokens(stats["total_input_tokens"])),
        ("Output Tokens", _fmt_tokens(stats["total_output_tokens"])),
        ("Total Tokens", _fmt_tokens(stats["total_tokens"])),
    ]:
        parts.append(
            f'<div class="summary-item">'
            f'<div class="summary-label">{label}</div>'
            f'<div class="summary-value">{value}</div>'
            f"</div>"
        )
    parts.append("</div>")

    # Tool usage breakdown
    if stats["tool_usage"]:
        parts.append(
            "<h3 style='color:#8b949e;margin-top:12px;font-size:0.9em;'>Tool Usage</h3>"
        )
        parts.append('<div class="summary-grid">')
        for name, count in list(stats["tool_usage"].items())[:15]:
            parts.append(
                f'<div class="summary-item">'
                f'<div class="summary-label">{_esc(name)}</div>'
                f'<div class="summary-value">{count}</div>'
                f"</div>"
            )
        parts.append("</div>")

    parts.append("</div>")
    parts.append(f"<script>{_JS}</script>")
    parts.append("</body></html>")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(parts), encoding="utf-8")
    return output


# EOF
