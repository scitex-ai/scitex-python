<!-- ---
!-- Timestamp: 2026-04-24 10:30:00
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-python/src/scitex/_skills/general/99_scitex-quality-checklist.md
!-- --- -->

# SciTeX Ecosystem — Periodic Quality Checklist

Run this during `/speak-and-call` autonomous passes or manually. Each
section lists what to verify, how to verify, and the canonical fix. Keep
the check cheap — delegate the big ones to subagents.

**Section groups:**

- **§0** Prerequisites & scope gate
- **§1–§3 — Repository-level audits** (branch, push, CI)
- **§4–§7 — Content-level audits** (test scope, SKILL.md, README callout, doc chains)
- **§8–§10 — Automation audits** (nightly schedule, deps, reporting)
- **Response protocol + do-not-touch list** — agent behavior rules
- **§16–§17 — Planned** (dynamic audits, dashboard export)

Failure-mode cookbook lives in a sibling file:
[98_scitex-quality-failure-playbook.md](98_scitex-quality-failure-playbook.md)
(PyPI traps, wheel drift, numpy 2 / pandas / optional-dep guards,
extras-completeness, Doc-Drift CI install source).

## 0. Prerequisites

- `gh auth status` succeeds
- `$HOME/proj/scitex-*` repos are present
- `gh`, `git -C`, and `pip` are on PATH

Never touch user's uncommitted edits — run `git -C <path> status --short`
and only stage files YOU modified. Use `-c core.hooksPath=/dev/null` on
pushes to bypass the X11-dependent pre-push hook.

**Scope this sweep to the library ecosystem only.** Some `scitex-*`
directories are peripheral and will throw false positives if included:

- Paper/manuscript drafts: `scitex-paper-*`, papers — no Python package
- Agentic / TS exploration repos: `scitex-agentic-test`, any bun-only
  repo — no `pyproject.toml`

Gate every probe on two conditions, not just `pyproject.toml`:

1. `test -f "$p/pyproject.toml"` — has a Python package config
2. directory name matches the pyproject `name` field — filters out
   project instances built from a template (e.g. `scitex-paper-1st/`
   uses `name = "scitex-writer"` because it's a manuscript repo
   scaffolded from the writer template).

One-liner gate:

```bash
name=$(grep -oP '^name\s*=\s*"\K[^"]+' "$p/pyproject.toml" | head -1)
[ "$name" = "$(basename $p)" ] || continue
```

Packages in scope = pass both conditions above, or are on an explicit
ecosystem allowlist.

## 1. Branch hygiene (every repo on `develop`)

**Check:** for each `scitex-*` repo, confirm current branch is `develop`
and it is equal-to or ahead-of `main`.

```
for p in $HOME/proj/scitex-*; do
  br=$(git -C "$p" rev-parse --abbrev-ref HEAD 2>/dev/null) || continue
  [ "$br" != "develop" ] && echo "ANOMALY: $(basename $p) on $br"
done
```

**Fix:**
- If on a feature branch that fast-forwards develop: advance develop
  via `git update-ref` (avoids checkout touching user's dirty tree),
  push, delete local feature branch with `-d`.
- If `develop` doesn't exist yet: `git checkout -b develop main`, push
  with `-u origin develop`, keep `main` intact.

## 2. Push state (no silent unpushed work)

**Check:** no repo has committed-but-unpushed changes.

```
git -C "$p" log "origin/$br..$br" --oneline
```

If ahead: push (`-c core.hooksPath=/dev/null push origin develop`).
Never force-push to shared branches.

## 3. CI green (per repo, latest run on develop)

**Check:** `gh run list --repo ywatanabe1989/<pkg> --branch develop --limit 1`.

Flag: `failure`, `cancelled`, `in_progress > 1h`.

**Typical failure modes & canonical fixes:**

Severity guide — **CRITICAL**: blocks downstream consumers or PyPI
release. **HIGH**: one package red but independent. **MEDIUM**: tests
flaky or a single test bug. **LOW**: cosmetic / threshold / lint.
Triage CRITICAL first.

Top-severity rows only (full cookbook in
[98_scitex-quality-failure-playbook.md](98_scitex-quality-failure-playbook.md)):

| Symptom | Severity | Fix |
|---|---|---|
| `ModuleNotFoundError: scitex_dev._skills_quality_pytest` | CRITICAL | bump+release scitex-dev so the wheel contains the module (see §98) |
| Publish-to-PyPI `invalid-publisher` | CRITICAL | configure trusted publisher; verify "Manage current publishers" *actually* saved (see §98) |
| Downstream ModuleNotFoundError for something that IS in git | CRITICAL | PyPI wheel stale — bump version + re-release |
| `Unnamed: *` columns appear in DataFrame | HIGH | pandas dtype guard too narrow — use try/except (§98 §5c) |
| `isinstance(obj, plotly.graph_objs.Figure)` → NoneType crash | HIGH | optional-dep guard missing (§98 §5a) |
| `assert func() is True` fails on numpy 2 | MEDIUM | coerce `bool(np.any(...))` at return (§98 §5b) |
| `coverage < fail_under` even though tests pass | LOW | lower `fail_under` to realistic floor |
| SKILL.md / leaf over size cap | LOW | trim description or split topically |

Full table with all ~18 observed patterns is in the playbook.

## 4. Test scope purity

Leaf packages (scitex-io, scitex-stats, etc.) MUST NOT import the
`scitex` umbrella in their own tests — only in `scripts/` or
`examples/`. Cross-package imports should be `pytest.importorskip`-gated.

**Check:** run `scripts/audit_test_scope.py --projects-root $HOME/proj`
in scitex-python. Reports every test-level `import scitex` or bare
sibling import.

## 5. SKILL.md frontmatter completeness

Every `scitex-*/src/scitex_*/_skills/<pkg>/SKILL.md` must carry:

```yaml
name: <pkg>
description: <single-sentence trigger phrase with drop-in replacement>
primary_interface: python | cli | mcp | hook | mixed
interfaces:
  python: 0..3
  cli: 0..3
  mcp: 0..3
  skills: 0..3
  hook: 0..3
  http: 0..3
```

Body must start with the callout:

```
> **Interfaces:** Python ⭐⭐⭐ (primary) · CLI — · MCP — · Skills ⭐⭐ · Hook — · HTTP —
```

**Check:** glob all SKILL.md, parse frontmatter, report missing fields.

## 6. README callout mirror

Every `scitex-*/README.md` should have the same `> **Interfaces:** ...`
callout line just above its `## Problem and Solution` table. Mirror the
body callout in SKILL.md.

## 7. Doc-example chains resolve

Every `stx.X.Y.Z` chain in every README / docs/*.md must resolve against
the installed scitex API. Run:

```
python3.11 scripts/audit_doc_examples.py --projects-root $HOME/proj
```

If a chain fails: (a) install the missing downstream in the workflow,
or (b) fix the docstring chain.

## 8. Nightly workflows are scheduled

Every package test workflow should run daily (07:00 UTC) and support
`workflow_dispatch`:

```yaml
on:
  push: {branches: [develop, main]}
  schedule:
    - cron: "0 7 * * *"
  workflow_dispatch:
```

## 9. Optional-deps hygiene

- Leaf packages keep a minimal default install — heavy deps in
  `[project.optional-dependencies]`.
- Every package defines an `[all]` extra (may be empty for utilities).
- When a scitex package is consumed at import-time, pin its minimum
  version in the consumer's `pyproject.toml` (see
  `08_arch-dependency-and-version-pinning.md`).

## 10. Reporting back

Two outputs per pass.

### 10a. Current-state table (for the human)

| package | branch | push | CI | notes |

Only call out anomalies. No false positives — verify each finding
before reporting. If a failure is a pre-existing test-debt item (not a
regression from this pass), say so explicitly.

### 10b. Append-only audit log (for regression tracking)

Append one entry per pass to `scitex-dev/quality-audits/YYYY-MM-DD.md`
(top-level, not under `logs/` which is gitignored):

```markdown
## YYYY-MM-DD HH:MM UTC — /speak-and-call pass

- Fixes applied:
  - <pkg>: <one-line fix> (<commit-sha>)
- Outstanding (flagged for user):
  - <pkg>: <one-line blocker>
- Next scheduled check: <ScheduleWakeup delay / cron>
```

This makes multi-week trends legible — e.g. "scitex-audio fails the
same way on 3/7 runs" → systemic, worth investing in.

## 11. Response protocol for a /speak-and-call quality run

1. Branch + push audit (§1, §2) — report anomalies only.
2. CI audit (§3) — table of failing runs + canonical fix per symptom.
3. Apply canonical fixes to the non-dirty repos; skip user's dirty
   trees and report them separately.
4. Wait for CI to rerun (use `ScheduleWakeup` 270–900 s depending on
   workflow length). Do not poll in tight loops.
5. Final summary: X/N green, Y requires user attention, Z in progress.
6. Append one entry to `scitex-dev/quality-audits/YYYY-MM-DD.md` (§10b).

## 12. Do-not-touch list (refresh every run)

Never modify files in a repo that has uncommitted user work. Determine
via `git -C <path> status --short` per repo *at the start of every pass*
— do not rely on a hardcoded list; dirty trees shift over time.

If a probe in §§1–10 flags an issue inside a dirty tree, use
non-invasive paths:

- GitHub-API merge (`gh api --method PUT repos/.../pulls/<n>/update-branch`)
- `git worktree add` to a scratch dir
- Report to user with exact commands, don't execute

Touching a dirty tree risks clobbering the user's in-progress edits —
always safer to report than to stash/pop under automation.

## 16. Dynamic audit via agent task execution (planned)

Static checks above verify the **"looks right"** dimension. Dynamic
checks will verify **"works right"** under realistic workloads — agents
executing end-to-end research tasks (paper drafts, data pipelines) and
logging tool-use distributions, error recovery, and output quality.

- **Static pass gates commit.** Static audits in §§1–15 + the playbook
  (§98) must be green before merging to develop.
- **Dynamic pass gates release.** A PyPI release wave additionally
  requires a passing dynamic-audit run covering the ecosystem's primary
  research workflows.

See the forthcoming
[scitex-dev/_skills/scitex-dev/20_dynamic-audit.md](../../scitex-dev/_skills/scitex-dev/20_dynamic-audit.md)
(not yet in tree) for task dataset, execution infrastructure, and
metric-collection design.

## 17. Dashboard export (planned)

Pipeline: each /speak-and-call pass → append to §10b log → a weekly
aggregator generates `scitex-dev/dashboards/quality.md` with:

| package | CI | skills | API docs | last audit |

Render at README top for external visibility (grant reviewers,
contributors). Implementation detail TBD.

<!-- EOF -->
