<!-- ---
!-- Timestamp: 2026-04-24 11:30:59
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

**Scope** = has `pyproject.toml` AND directory name equals pyproject
`name`. The second condition filters paper/template repos like
`scitex-paper-1st/` that vendor `name = "scitex-writer"`. One-liner:

```bash
name=$(grep -oP '^name\s*=\s*"\K[^"]+' "$p/pyproject.toml" | head -1)
[ "$name" = "$(basename $p)" ] || continue
```

(Or use an explicit ecosystem allowlist — see `audit_english_only.py`.)

## 1. Branch hygiene (every repo on `develop`)

Every in-scope repo on `develop`, ahead-of-or-equal `main`:

```bash
for p in $HOME/proj/scitex-*; do
  br=$(git -C "$p" rev-parse --abbrev-ref HEAD 2>/dev/null) || continue
  [ "$br" != "develop" ] && echo "ANOMALY: $(basename $p) on $br"
done
```

Fix: fast-forward develop via `git update-ref` (avoids checkout touching
dirty tree), push, delete feature branch. If `develop` doesn't exist,
`git checkout -b develop main; git push -u origin develop`.

## 2. Push state

No committed-but-unpushed changes:
`git -C "$p" log "origin/$br..$br" --oneline` → empty.
If ahead, push (use `-c core.hooksPath=/dev/null` to bypass X11 hook).
Never force-push shared branches.

## 3. CI green (per repo, latest run on develop)

**Check:** `gh run list --repo ywatanabe1989/<pkg> --branch develop --limit 1`.

Flag: `failure`, `cancelled`, `in_progress > 1h`.

**Typical failure modes & canonical fixes:**

Severity: **CRITICAL** blocks downstream/release; **HIGH** one package;
**MEDIUM** test bug; **LOW** cosmetic. Triage top-down. Full cookbook:
[98_scitex-quality-failure-playbook.md](98_scitex-quality-failure-playbook.md).

| Symptom | Severity | Fix |
|---|---|---|
| `ModuleNotFoundError: scitex_dev._skills_quality_pytest` | CRITICAL | bump+release scitex-dev (§98) |
| Publish-to-PyPI `invalid-publisher` | CRITICAL | config trusted publisher; verify it *saved* (§98) |
| Downstream import missing for a module that IS in git | CRITICAL | stale PyPI wheel — bump+release |
| `Unnamed: *` column leaks past DataFrame loader | HIGH | narrow dtype guard (§98 §5c) |
| `isinstance(plotly.graph_objs.Figure)` → NoneType crash | HIGH | optional-dep guard missing (§98 §5a) |
| `assert func() is True` fails on numpy 2 | MEDIUM | `return bool(np.any(...))` (§98 §5b) |
| `coverage < fail_under` despite tests green | LOW | lower `fail_under` to real floor |
| SKILL.md/leaf over size cap | LOW | trim description or topical split |

Full table (~18 patterns) in the playbook.

## 4. Test scope purity

Leaf packages (scitex-io, scitex-stats, etc.) MUST NOT import the
`scitex` umbrella in their own tests — only in `scripts/` or
`examples/`. Cross-package imports should be `pytest.importorskip`-gated.

**Check:** run `scripts/audit_test_scope.py --projects-root $HOME/proj`
in scitex-python. Reports every test-level `import scitex` or bare
sibling import.

> Canonical location: `scitex-dev/scripts/quality/audit_test_scope.py`,
> mirrored for convenience in `scitex-python/scripts/`. Prefer
> `python -m scitex_dev._cli_quality audit_scope --projects-root $HOME/proj`
> once `scitex-dev` is installed.

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

> Canonical location: `scitex-dev/scripts/quality/audit_doc_examples.py`,
> mirrored for convenience in `scitex-python/scripts/`. Prefer
> `python -m scitex_dev._cli_quality audit_docs --projects-root $HOME/proj`
> once `scitex-dev` is installed.

Line-limit auditor (§cap enforcement) lives alongside these:
`scitex-dev/scripts/quality/audit_line_limits.py` (mirrored to
`scitex-python/scripts/audit_line_limits.py`), allowlist at
`scitex-dev/scripts/quality/line_limits_allowlist.txt`.

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

Design skeleton:
`scitex-dev/src/scitex_dev/_skills/scitex-dev/20_dynamic-audit.md` —
task dataset T01–T10, execution infra, metrics. Not yet implemented;
minimal first pass (3 tasks) specified there.

Host: `scitex-dev` owns the canonical quality-audit scripts under
`scitex-dev/scripts/quality/` and the audit logs under
`scitex-dev/logs/quality-audits/`. The `scitex-python/scripts/` copies
are a convenience mirror for in-repo workflows.

## 17. Dashboard export

Run after a pass (or as a weekly cron):

```bash
python3.11 ~/proj/scitex-python/scripts/audit_quality_dashboard.py
```

→ `scitex-dev/dashboards/quality.md`: per-package CI/tag/PyPI/aligned.
Scope = §0 ∩ (`scitex*` or allowlist: figrecipe, socialia,
openalex-local, crossref-local).

## 18. English-only enforcement

English-only. Exempt a line with `# i18n-ok` / `<!-- i18n-ok -->`
(marker in ±2 lines covers docstring/class pairs and formatter splits).

```bash
python3.11 ~/proj/scitex-python/scripts/audit_english_only.py
```

Excludes caches, node_modules, vendored `.claude/` mirrors.

## Last Questions
01. Is SciTeX ecosystem useful for Ph.D. students and researchers?
02. Meaningful tests implemented? All green?
03. Is it easy to understand SciTeX packages for both human and AI researchers?
04. Is it easy to use SciTeX packages for both human and AI researchers?
05. Is it easy to maintain SciTeX packages for both human and AI researchers?
06. Are documents, Read the Docs, and examples up-to-date for actual codebase?
07. Is periodical quality check implemented and actually running regularly?
08. Are SciTeX conventions followed throughout the packages?
09. Are all packages standardized and consistent as ecosystem?
10. Is the ecosystem only written in English, including comments and documents?

<!-- EOF -->