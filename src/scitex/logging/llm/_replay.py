#!/usr/bin/env python3
# Timestamp: 2026-03-19
# File: /home/ywatanabe/proj/scitex-python/src/scitex/logging/llm/_replay.py

"""Export agent actions as runnable shell scripts for reproducibility."""

from __future__ import annotations

import html
import stat
from pathlib import Path
from typing import Any

from ._actions import Action, extract_actions


def export_scripts(
    session_path: str | Path,
    output_dir: str | Path,
    tools: tuple[str, ...] = ("Bash",),
) -> Path:
    """Export session actions as numbered shell scripts.

    Parameters
    ----------
    session_path : str or Path
        Path to JSONL session file.
    output_dir : str or Path
        Directory to write scripts into.
    tools : tuple of str
        Tool names to export (default: Bash only).

    Returns
    -------
    Path
        Path to output directory.
    """
    output_dir = Path(output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    actions = extract_actions(session_path)
    filtered = [a for a in actions if a.tool_name in tools]

    scripts = []
    for i, action in enumerate(filtered, 1):
        filename = f"{i:04d}_{_safe_name(action)}.sh"
        script_path = output_dir / filename
        script_content = _action_to_script(action, i)
        script_path.write_text(script_content, encoding="utf-8")
        # Make executable
        script_path.chmod(script_path.stat().st_mode | stat.S_IEXEC)
        scripts.append({"index": i, "filename": filename, "action": action})

    # Write index
    _write_index(output_dir, scripts)
    # Write run-all script
    _write_run_all(output_dir, scripts)
    # Write browseable HTML
    _write_html_index(output_dir, scripts)

    return output_dir


def _safe_name(action: Action) -> str:
    """Generate a safe filename fragment from an action."""
    if action.tool_name == "Bash":
        cmd = action.command.split()[0] if action.command else "cmd"
        cmd = cmd.split("/")[-1]  # basename
        return cmd[:30].replace("/", "_").replace(" ", "_")
    if action.file_path:
        return Path(action.file_path).stem[:30]
    desc = action.description or action.tool_name
    return desc[:30].replace("/", "_").replace(" ", "_")


def _action_to_script(action: Action, index: int) -> str:
    """Convert a single action to a shell script."""
    lines = [
        "#!/bin/bash",
        f"# Action {index}: {action.tool_name}",
        f"# Timestamp: {action.timestamp}",
        f"# Tool ID: {action.tool_use_id}",
    ]

    if action.description:
        lines.append(f"# Description: {action.description}")

    lines.append("")

    if action.tool_name == "Bash":
        cmd = action.command
        if not cmd:
            lines.append("# (empty command)")
        else:
            lines.append("set -euo pipefail")
            lines.append("")
            # Add the command
            lines.append(cmd)
    elif action.tool_name == "Write":
        fp = action.file_path
        content = action.tool_input.get("content", "")
        lines.append(f"# Write file: {fp}")
        lines.append(f"cat > '{fp}' << 'SCITEX_EOF'")
        lines.append(content)
        lines.append("SCITEX_EOF")
    elif action.tool_name == "Edit":
        fp = action.file_path
        old = action.tool_input.get("old_string", "")
        new = action.tool_input.get("new_string", "")
        lines.append(f"# Edit file: {fp}")
        lines.append("# Replace old_string with new_string")
        lines.append('python3 -c "')
        lines.append("import pathlib")
        lines.append(f"p = pathlib.Path('{fp}')")
        lines.append("t = p.read_text()")
        old_escaped = old.replace("'", "\\'").replace('"', '\\"')
        new_escaped = new.replace("'", "\\'").replace('"', '\\"')
        lines.append(f"t = t.replace('''{old_escaped}''', '''{new_escaped}''', 1)")
        lines.append("p.write_text(t)")
        lines.append('"')
    elif action.tool_name in ("Read", "Glob", "Grep"):
        lines.append(f"# {action.tool_name} (read-only, no script needed)")
        for k, v in action.tool_input.items():
            lines.append(f"# {k}: {str(v)[:200]}")
    else:
        lines.append(f"# Tool: {action.tool_name}")
        for k, v in action.tool_input.items():
            val = str(v)[:500]
            lines.append(f"# {k}: {val}")

    lines.append("")
    return "\n".join(lines)


def _write_index(output_dir: Path, scripts: list[dict[str, Any]]) -> None:
    """Write a text index of all scripts."""
    lines = [
        "# Session Action Scripts",
        "# Run individual scripts or use run_all.sh",
        "",
    ]
    for s in scripts:
        a = s["action"]
        desc = a.description or a.command[:60] if a.command else a.tool_name
        lines.append(f"{s['filename']:40s}  # {desc}")
    (output_dir / "INDEX.txt").write_text("\n".join(lines), encoding="utf-8")


def _write_run_all(output_dir: Path, scripts: list[dict[str, Any]]) -> None:
    """Write a run-all script that executes scripts in order."""
    lines = [
        "#!/bin/bash",
        "# Run all action scripts in order",
        "set -euo pipefail",
        "",
        'DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"',
        "",
    ]
    for s in scripts:
        a = s["action"]
        if a.tool_name not in ("Bash", "Write", "Edit"):
            continue
        lines.append(f'echo "=== [{s["index"]}] {a.tool_name}: {_safe_name(a)} ==="')
        lines.append(f'"$DIR/{s["filename"]}"')
        lines.append("")

    path = output_dir / "run_all.sh"
    path.write_text("\n".join(lines), encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC)


def _esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def _write_html_index(output_dir: Path, scripts: list[dict[str, Any]]) -> None:
    """Write a browseable HTML index of all scripts."""
    css = """\
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: monospace; background: #0d1117; color: #c9d1d9; padding: 24px;
       max-width: 1000px; margin: 0 auto; }
h1 { color: #58a6ff; margin-bottom: 16px; }
.action { background: #161b22; border: 1px solid #30363d; border-radius: 8px;
          margin-bottom: 12px; overflow: hidden; }
.action-header { padding: 10px 16px; display: flex; justify-content: space-between;
                 align-items: center; cursor: pointer; }
.action-header:hover { background: #1c2128; }
.action-index { color: #8b949e; font-size: 0.8em; min-width: 40px; }
.action-tool { color: #f0883e; font-weight: 600; min-width: 80px; }
.action-desc { color: #c9d1d9; flex: 1; margin: 0 12px; font-size: 0.85em;
               overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.action-time { color: #8b949e; font-size: 0.75em; }
.action-body { display: none; border-top: 1px solid #30363d; }
.action-body.open { display: block; }
.code-block { background: #0d1117; padding: 12px; margin: 8px; border-radius: 4px;
              overflow-x: auto; white-space: pre-wrap; font-size: 0.8em; }
.code-label { color: #8b949e; font-size: 0.7em; padding: 8px 12px 0; }
.output { background: #0d2818; border-left: 3px solid #238636; }
.error { background: #2d1117; border-left: 3px solid #da3633; }
.toggle { transition: transform 0.2s; display: inline-block; }
.toggle.open { transform: rotate(90deg); }
.stats { color: #8b949e; font-size: 0.85em; margin-bottom: 16px; }
"""

    js = """\
document.querySelectorAll('.action-header').forEach(h => {
  h.addEventListener('click', () => {
    const body = h.nextElementSibling;
    const arrow = h.querySelector('.toggle');
    body.classList.toggle('open');
    arrow.classList.toggle('open');
  });
});
"""

    bash_count = sum(1 for s in scripts if s["action"].tool_name == "Bash")
    parts = [
        "<!DOCTYPE html>",
        '<html lang="en"><head><meta charset="utf-8">',
        "<title>Session Actions</title>",
        f"<style>{css}</style>",
        "</head><body>",
        "<h1>Session Actions</h1>",
        f'<div class="stats">{len(scripts)} actions, {bash_count} Bash commands</div>',
    ]

    for s in scripts:
        a = s["action"]
        desc = a.description or (a.command[:80] if a.command else a.tool_name)
        ts = a.timestamp[:19] if a.timestamp else ""

        parts.append('<div class="action">')
        parts.append(
            f'<div class="action-header">'
            f'<span class="action-index"><span class="toggle">&#9654;</span> {s["index"]}</span>'
            f'<span class="action-tool">{_esc(a.tool_name)}</span>'
            f'<span class="action-desc">{_esc(desc)}</span>'
            f'<span class="action-time">{_esc(ts)}</span>'
            f"</div>"
        )
        parts.append('<div class="action-body">')

        # Command / input
        if a.tool_name == "Bash" and a.command:
            parts.append('<div class="code-label">Command</div>')
            parts.append(f'<div class="code-block">{_esc(a.command)}</div>')
        elif a.file_path:
            parts.append(f'<div class="code-label">File: {_esc(a.file_path)}</div>')
            if a.tool_name == "Edit":
                old = a.tool_input.get("old_string", "")[:500]
                new = a.tool_input.get("new_string", "")[:500]
                if old:
                    parts.append(f'<div class="code-block error">- {_esc(old)}</div>')
                if new:
                    parts.append(f'<div class="code-block output">+ {_esc(new)}</div>')
        else:
            inp = "\n".join(f"{k}: {str(v)[:200]}" for k, v in a.tool_input.items())
            parts.append(f'<div class="code-block">{_esc(inp)}</div>')

        # Output
        output_text = a.stdout or a.result_content
        if output_text:
            truncated = output_text[:3000]
            if len(output_text) > 3000:
                truncated += f"\n... [{len(output_text)} total chars]"
            parts.append('<div class="code-label">Output</div>')
            parts.append(f'<div class="code-block output">{_esc(truncated)}</div>')

        if a.stderr:
            parts.append('<div class="code-label">Stderr</div>')
            parts.append(f'<div class="code-block error">{_esc(a.stderr[:1000])}</div>')

        # Script file link
        parts.append(f'<div class="code-label">Script: {_esc(s["filename"])}</div>')

        parts.append("</div></div>")

    parts.append(f"<script>{js}</script>")
    parts.append("</body></html>")

    (output_dir / "index.html").write_text("\n".join(parts), encoding="utf-8")


# EOF
