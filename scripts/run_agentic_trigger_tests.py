#!/usr/bin/env python3.11
"""Run agentic skill-trigger tests locally and write a Markdown report.

Uses scitex_dev._agentic_testing to shell out to `claude -p` (Claude Code
non-interactive mode), parse the JSON transcript, and check whether the
expected SKILL.md was auto-loaded by the agent for each realistic query.

Usage:
    python3.11 scripts/run_agentic_trigger_tests.py \\
        --eval tests/agentic/pilot.json \\
        --runs 1 \\
        --model claude-haiku-4-5 \\
        --report GITIGNORED/reports/agentic_trigger_$(date +%Y%m%d_%H%M).md
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
import time
from pathlib import Path

from scitex_dev._agentic_testing import (
    DEFAULT_MODEL,
    get_runner,
    load_eval_set,
    run_trigger_case,
)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--eval", type=Path, required=True)
    p.add_argument("--runs", type=int, default=1)
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--backend", default="host", choices=["host", "docker"])
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--limit", type=int, default=0, help="Only run first N cases")
    args = p.parse_args()

    cases = load_eval_set(args.eval)
    if args.limit:
        cases = cases[: args.limit]

    runner = get_runner(args.backend)

    started = dt.datetime.now().isoformat(timespec="seconds")
    lines: list[str] = []
    lines.append("# Agentic Skill-Trigger Report")
    lines.append("")
    lines.append(f"- Started: {started}")
    lines.append(f"- Eval set: `{args.eval}`")
    lines.append(f"- Model: `{args.model}`")
    lines.append(f"- Backend: `{args.backend}`")
    lines.append(f"- Runs per case: {args.runs}")
    lines.append(f"- Cases: {len(cases)}")
    lines.append("")
    lines.append("| # | Case | Expected | Hard? | Soft? | Pass | Viewed (top 3) |")
    lines.append("|---|------|----------|-------|-------|------|----------------|")

    pass_count = 0
    per_case = []
    for i, case in enumerate(cases, 1):
        t0 = time.time()
        print(f"[{i}/{len(cases)}] {case.id} — {case.query[:70]}...", flush=True)
        try:
            r = run_trigger_case(runner, case, model=args.model, runs=args.runs)
            hard = "✔" if any(r.hard_trigger_per_run) else "✘"
            soft = "✔" if any(r.soft_trigger_per_run) else "✘"
            passed_bool = sum(r.runs) / len(r.runs) >= 0.5
            passed = "✔" if passed_bool else "✘"
            viewed = sorted({v for run in r.viewed_paths_per_run for v in run})
            viewed_str = ", ".join(f"`{v}`" for v in viewed[:3]) or "-"
            if passed_bool:
                pass_count += 1
            per_case.append(
                dict(
                    id=case.id,
                    expected=case.expected_skill,
                    hard=hard,
                    soft=soft,
                    pass_rate=r.pass_rate,
                    viewed=viewed,
                    elapsed=time.time() - t0,
                )
            )
            lines.append(
                f"| {i} | `{case.id}` | `{case.expected_skill or '(none)'}` "
                f"| {hard} | {soft} | {passed} | {viewed_str} |"
            )
            print(
                f"   → hard={hard} soft={soft} pass={passed} "
                f"({time.time() - t0:.1f}s, {len(viewed)} views)",
                flush=True,
            )
        except Exception as e:
            lines.append(
                f"| {i} | `{case.id}` | `{case.expected_skill or '(none)'}` "
                f"| ERR | ERR | ✘ | {e!s:.80} |"
            )
            print(f"   → ERROR: {e}", flush=True)

    lines.append("")
    lines.append(
        f"**Overall pass rate: {pass_count}/{len(cases)} = "
        f"{100 * pass_count / max(len(cases), 1):.0f}%**"
    )
    lines.append("")
    lines.append(f"- Finished: {dt.datetime.now().isoformat(timespec='seconds')}")

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(lines) + "\n")
    print(f"\nReport written: {args.report}", flush=True)

    runner.close()
    return 0 if pass_count == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main())
