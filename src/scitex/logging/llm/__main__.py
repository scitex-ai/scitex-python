#!/usr/bin/env python3
# Timestamp: 2026-03-19
# File: /home/ywatanabe/proj/scitex-python/src/scitex/logging/llm/__main__.py

"""CLI for Claude Code session log viewer.

Usage:
    python -m scitex.logging.llm render SESSION.jsonl [-o output.html]
    python -m scitex.logging.llm summary SESSION.jsonl
    python -m scitex.logging.llm dag SESSION.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="python -m scitex.logging.llm",
        description="Claude Code session log viewer",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # render
    p_render = sub.add_parser("render", help="Render session as HTML")
    p_render.add_argument("session", help="Path to .jsonl session file")
    p_render.add_argument("-o", "--output", default=None, help="Output HTML path")
    p_render.add_argument(
        "--open", action="store_true", help="Open in browser after rendering"
    )

    # summary
    p_summary = sub.add_parser("summary", help="Print session summary")
    p_summary.add_argument("session", help="Path to .jsonl session file")

    # dag
    p_dag = sub.add_parser("dag", help="Print tool call DAG as mermaid")
    p_dag.add_argument("session", help="Path to .jsonl session file")

    # actions
    p_actions = sub.add_parser(
        "actions", help="Extract agent actions (tool calls + results)"
    )
    p_actions.add_argument("session", help="Path to .jsonl session file")
    p_actions.add_argument(
        "-f",
        "--format",
        choices=["log", "jsonl", "json"],
        default="log",
        help="Output format (default: log)",
    )
    p_actions.add_argument(
        "-o", "--output", default=None, help="Output file (default: stdout)"
    )

    # dashboard
    p_dash = sub.add_parser("dashboard", help="Render multi-session dashboard")
    p_dash.add_argument(
        "-o", "--output", default="/tmp/claude_dashboard.html", help="Output HTML"
    )
    p_dash.add_argument("--claude-dir", default="~/.claude", help="Claude config dir")
    p_dash.add_argument("--open", action="store_true", help="Open in browser")

    # scripts
    p_scripts = sub.add_parser(
        "scripts", help="Export actions as runnable shell scripts"
    )
    p_scripts.add_argument("session", help="Path to .jsonl session file")
    p_scripts.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output directory (default: <session>_scripts/)",
    )
    p_scripts.add_argument(
        "--tools",
        default="Bash,Write,Edit",
        help="Tool names to export (comma-separated, default: Bash,Write,Edit)",
    )
    p_scripts.add_argument(
        "--open", action="store_true", help="Open HTML index in browser"
    )

    # spa
    p_spa = sub.add_parser("spa", help="Generate browseable SPA dashboard")
    p_spa.add_argument(
        "-o", "--output", default="/tmp/claude_spa.html", help="Output HTML"
    )
    p_spa.add_argument("--claude-dir", default="~/.claude", help="Claude config dir")
    p_spa.add_argument("--open", action="store_true", help="Open in browser")

    args = parser.parse_args()

    if args.command == "spa":
        from ._spa import render_spa

        path = render_spa(args.output, args.claude_dir)
        print(f"SPA: {path}")
        if args.open:
            import subprocess

            subprocess.Popen(["xdg-open", str(path)])
        return 0

    if args.command == "scripts":
        from ._replay import export_scripts

        output = args.output
        if output is None:
            output = str(Path(args.session).with_suffix("")) + "_scripts"
        tools = tuple(t.strip() for t in args.tools.split(","))
        path = export_scripts(args.session, output, tools=tools)
        print(f"Scripts: {path}")
        if args.open:
            import subprocess

            subprocess.Popen(["xdg-open", str(path / "index.html")])
        return 0

    if args.command == "dashboard":
        from ._dashboard import render_dashboard

        path = render_dashboard(args.output, args.claude_dir)
        print(f"Dashboard: {path}")
        if args.open:
            import subprocess

            subprocess.Popen(["xdg-open", str(path)])
        return 0

    if args.command == "actions":
        from ._actions import actions_to_jsonl, actions_to_log, extract_actions

        actions = extract_actions(args.session)
        if args.format == "log":
            text = actions_to_log(actions)
        elif args.format == "jsonl":
            text = actions_to_jsonl(actions)
        else:
            text = json.dumps([a.to_dict() for a in actions], indent=2)

        if args.output:
            from pathlib import Path

            Path(args.output).write_text(text, encoding="utf-8")
            print(f"Written: {args.output} ({len(actions)} actions)")
        else:
            print(text)
        return 0

    from . import load, to_mermaid

    session = load(args.session)

    if args.command == "render":
        output = args.output
        if output is None:
            output = str(session.path.with_suffix(".html"))
        path = session.render(output)
        print(f"Rendered: {path}")
        if args.open:
            import subprocess

            subprocess.Popen(["xdg-open", str(path)])

    elif args.command == "summary":
        print(json.dumps(session.summary(), indent=2))

    elif args.command == "dag":
        print(to_mermaid(session))

    return 0


if __name__ == "__main__":
    sys.exit(main())

# EOF
