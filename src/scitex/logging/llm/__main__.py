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

    args = parser.parse_args()

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
