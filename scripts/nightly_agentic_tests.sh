#!/usr/bin/env bash
# Run the SciTeX agentic skill-trigger pilot and archive the report.
#
# Designed for a nightly systemd-timer / cron slot. Uses the host-side
# `claude` CLI (Claude Code Max subscription) — NOT the Anthropic API —
# so it respects the user's plan quota.
#
# Example systemd-timer install (user-scope):
#   # ~/.config/systemd/user/scitex-agentic-tests.service
#   [Unit]
#   Description=SciTeX nightly agentic skill-trigger tests
#   [Service]
#   Type=oneshot
#   ExecStart=%h/proj/scitex-python/scripts/nightly_agentic_tests.sh
#
#   # ~/.config/systemd/user/scitex-agentic-tests.timer
#   [Unit]
#   Description=SciTeX nightly agentic tests — daily 07:15
#   [Timer]
#   OnCalendar=*-*-* 07:15:00
#   Persistent=true
#   [Install]
#   WantedBy=timers.target
#
#   systemctl --user enable --now scitex-agentic-tests.timer

set -euo pipefail

REPO_ROOT="${SCITEX_REPO_ROOT:-$HOME/proj/scitex-python}"
PYTHON="${SCITEX_PYTHON:-python3.11}"
EVAL_PATH="${SCITEX_EVAL_PATH:-$REPO_ROOT/tests/skill_evals/pilot.json}"
REPORT_DIR="${SCITEX_REPORT_DIR:-$REPO_ROOT/GITIGNORED/reports}"
MODEL="${SCITEX_MODEL:-claude-haiku-4-5}"
BACKEND="${SCITEX_BACKEND:-host}"
RUNS="${SCITEX_RUNS:-1}"

mkdir -p "$REPORT_DIR"
stamp="$(date -u +%Y%m%d_%H%MZ)"
report="$REPORT_DIR/agentic_pilot_${stamp}.md"

cd "$REPO_ROOT"
"$PYTHON" scripts/run_agentic_trigger_tests.py \
    --eval "$EVAL_PATH" \
    --runs "$RUNS" \
    --model "$MODEL" \
    --backend "$BACKEND" \
    --report "$report"

echo "Report: $report"

# Prune old reports (keep last 30)
find "$REPORT_DIR" -maxdepth 1 -name 'agentic_pilot_*.md' -printf '%T@ %p\n' 2>/dev/null |
    sort -rn | tail -n +31 | cut -d' ' -f2- | xargs -r rm -f
