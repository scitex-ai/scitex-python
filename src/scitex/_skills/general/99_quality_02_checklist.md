<!-- ---
!-- Timestamp: 2026-04-24 11:30:59
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-python/src/scitex/_skills/general/99_quality_02_checklist.md
!-- --- -->

---
name: ecosystem-quality-checklist
description: Periodic ecosystem-wide quality checklist — run during `/speak-and-call` passes or manually between release waves. Each section lists what to verify, how to run the check, and the canonical fix — covering README consistency, Sphinx build health, CI status across all repos, PyPI ↔ git-tag ↔ pyproject version alignment, skills-tree quality (via `06_skills_05_quality-checklist.md`), CLI noun-verb conformance (via `scitex-dev quality audit-cli`), frontmatter health (via `scitex-dev quality audit-frontmatter`), docs drift, and test-coverage regressions. Use as the strategic runbook when the ecosystem feels off, after a release wave, or on a fixed cadence. Append-only findings log at the end of the file; each pass timestamps new entries.
canonical-location: scitex-python/src/scitex/_skills/general/99_quality_02_checklist.md
---

# SciTeX Ecosystem — Periodic Quality Checklist

Run during `/speak-and-call` passes or manually. Each section lists
what to verify, how, and the canonical fix. Keep the check cheap —
delegate big ones to subagents.

**Section groups:**

- **§0** Prerequisites & scope gate
- **§1–§3 — Repository-level audits** (branch, push, CI)
- **§4–§7 — Content-level audits** (test scope, SKILL.md, README callout, doc chains)
- **§8–§10 — Automation audits** (nightly schedule, deps, reporting)
- **§14 — Extras-completeness** (every canonical pkg reachable)
- **Response protocol + do-not-touch list** — agent behavior rules
- **§16–§17 — Planned** (dynamic audits, dashboard export)

Failure-mode cookbook: sibling
[98_quality_01_failure-playbook.md](98_quality_01_failure-playbook.md)
(PyPI traps, wheel drift, numpy2/pandas/optional-dep guards,
extras-completeness, Doc-Drift CI install source).

## 0. Prerequisites

- `gh auth status` succeeds; `$HOME/proj/scitex-*` present;
  `gh`/`git -C`/`pip` on PATH.
- Never touch user uncommitted edits (`git -C <path> status --short`);
  only stage files YOU modified. Bypass X11 pre-push hook with
  `-c core.hooksPath=/dev/null`.

**Scope** = has `pyproject.toml` AND directory name == pyproject `name`
(filters paper/template repos like `scitex-paper-1st/` that vendor
`name = "scitex-writer"`):

```bash
name=$(grep -oP '^name\s*=\s*"\K[^"]+' "$p/pyproject.toml" | head -1)
[ "$name" = "$(basename $p)" ] || continue
```

Or use an explicit allowlist — see `audit_english_only.py`.

## 1. Branch hygiene (every repo on `develop`)

Every in-scope repo on `develop`, ahead-of-or-equal `main`:

```bash
for p in $HOME/proj/scitex-*; do
  br=$(git -C "$p" rev-parse --abbrev-ref HEAD 2>/dev/null) || continue
  [ "$br" != "develop" ] && echo "ANOMALY: $(basename $p) on $br"
done
```

Fix: fast-forward develop via `git update-ref` (avoids checkout on
dirty tree), push, delete feature branch. If no `develop`:
`git checkout -b develop main; git push -u origin develop`.

## 2. Push state

No unpushed commits: `git -C "$p" log "origin/$br..$br" --oneline` →
empty. If ahead, push (`-c core.hooksPath=/dev/null` bypasses X11 hook).
Never force-push shared branches.

## 3. CI green (per repo, latest run on develop)

**Check:** `gh run list --repo ywatanabe1989/<pkg> --branch develop --limit 1`.
Flag `failure`, `cancelled`, `in_progress > 1h`.

Severity: **CRITICAL** blocks release; **HIGH** one pkg; **MEDIUM**
test bug; **LOW** cosmetic. Full cookbook (~18 patterns):
[98_quality_01_failure-playbook.md](98_quality_01_failure-playbook.md).

## 4. Test scope purity

Leaf packages (scitex-io, scitex-stats, etc.) MUST NOT import the
`scitex` umbrella in their tests — only in `scripts/` or `examples/`.
Cross-package imports use `pytest.importorskip`.

**Check:** `scripts/audit_test_scope.py --projects-root $HOME/proj` in
scitex-python. Reports every test-level `import scitex` / bare sibling.

> Canonical: `scitex-dev/scripts/quality/audit_test_scope.py` (mirrored
> to `scitex-python/scripts/`). Prefer
> `python -m scitex_dev._cli_quality audit_scope --projects-root $HOME/proj`.

## 5. SKILL.md frontmatter completeness

Every `scitex-*/src/scitex_*/_skills/<pkg>/SKILL.md` must carry:

```yaml
name: <pkg>
description: <one-sentence trigger with drop-in replacement>
primary_interface: python | cli | mcp | hook | mixed
interfaces: {python: 0..3, cli: 0..3, mcp: 0..3, skills: 0..3, hook: 0..3, http: 0..3}
```

Body starts with the callout:
`> **Interfaces:** Python ⭐⭐⭐ (primary) · CLI — · MCP — · Skills ⭐⭐ · Hook — · HTTP —`

**Check:** glob all SKILL.md, parse frontmatter, report missing fields.

## 6. README callout mirror

Every `scitex-*/README.md` has the same `> **Interfaces:** ...` callout
just above its `## Problem and Solution` table (mirrors SKILL.md body).

## 7. Doc-example chains resolve

Every `stx.X.Y.Z` chain in READMEs / docs/*.md must resolve against the
installed scitex API:

```
python3.11 scripts/audit_doc_examples.py --projects-root $HOME/proj
```

On failure: (a) install the missing downstream in the workflow, or (b)
fix the docstring chain.

> Canonical: `scitex-dev/scripts/quality/audit_doc_examples.py` (mirrored
> to `scitex-python/scripts/`). Prefer
> `python -m scitex_dev._cli_quality audit_docs --projects-root $HOME/proj`.

Line-limit auditor: `scitex-dev/scripts/quality/audit_line_limits.py`
(mirrored), allowlist `line_limits_allowlist.txt` alongside.

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

- Leaf pkgs keep a minimal default install; heavy deps go in
  `[project.optional-dependencies]`.
- Every package defines an `[all]` extra (may be empty for utilities).
- Consumers of scitex pkgs pin min version in their pyproject (see
  `01_arch_02_dependency-and-version-pinning.md`).

## 10. Reporting back

Two outputs per pass.

### 10a. Current-state table (for the human)

`| package | branch | push | CI | notes |` — anomalies only. Verify
each finding (no false positives). Mark pre-existing test-debt as such.

### 10b. Append-only audit log (for regression tracking)

Append one entry per pass to `scitex-dev/quality-audits/YYYY-MM-DD.md`
(top-level, not `logs/` which is gitignored):

```markdown
## YYYY-MM-DD HH:MM UTC — /speak-and-call pass

- Fixes applied:
  - <pkg>: <one-line fix> (<commit-sha>)
- Outstanding (flagged for user):
  - <pkg>: <one-line blocker>
- Next scheduled check: <ScheduleWakeup delay / cron>
```

Makes multi-week trends legible ("audio fails same way 3/7" → systemic).

## 11. Response protocol for a /speak-and-call quality run

1. Branch + push audit (§1, §2) — anomalies only.
2. CI audit (§3) — table of failing runs + canonical fix.
3. Apply fixes to non-dirty repos; report dirty ones separately.
4. `ScheduleWakeup` 270–900 s for CI to rerun; no tight polling.
5. Summary: X/N green, Y needs user, Z in progress.
6. Append entry to `scitex-dev/quality-audits/YYYY-MM-DD.md` (§10b).

## 12. Do-not-touch list (refresh every run)

Never modify a repo with uncommitted user work. Run
`git -C <path> status --short` each pass. For issues in dirty trees:
prefer GH-API merge, `git worktree add`, or report commands. Never
stash/pop.

Commit-in-dirty-tree guard (mandatory):

```bash
~/.claude/to_claude/bin/git_guard_commit.sh --repo <abs-path> \
    <file1> [...] -- -m "msg"
```

Aborts if index has extras. Prevents the 2026-04-24 accident (commit
swept 40 pre-staged user files). Home: `~/.claude/to_claude/bin/`.

## 14. Extras-completeness (every canonical package reachable)

Stricter than playbook §6 (which only catches `foo = []` when
`src/scitex/foo/` exists). Every canonical ecosystem package MUST appear
in at least one named extra AND in `[all]`, so
`pip install scitex[<name>]` actually pulls `scitex-<name>`.

**Failure (2026-04-24).** `clew = []`, `path = ["GitPython","matplotlib"]`
(no `scitex-path`), `ui = []`, `linter`/`core`/`scholar` absent.
`pip install scitex[path]` installs GitPython but NOT `scitex-path`, so
`stx.path.find_git_root()` silently falls back to the umbrella shim
instead of the standalone's full implementation. Rule:
`01_arch_03_modules-and-standalone-packages.md` §12.

**Probe (uses canonical registry):**

```bash
python3.11 - <<'EOF'
import subprocess, json, tomllib
reg = json.loads(subprocess.check_output(
  ["scitex","dev","ecosystem","list","--json"]))["packages"]
non_lib = {"pip-project-template","singularity-template",
  "automated-research-demo","scitex-research-template","scitex"}
libs = sorted(p for p in reg if p not in non_lib)
ex = tomllib.loads(open("pyproject.toml","rb").read()
  )["project"]["optional-dependencies"]
m_any = [p for p in libs if not any(p in ex.get(e,[]) for e in ex)]
m_all = [p for p in libs if p not in ex.get("all", [])]
if m_any: print("MISSING any extra:", m_any); raise SystemExit(1)
if m_all: print("MISSING [all]:", m_all); raise SystemExit(1)
print("OK:", len(libs), "ecosystem pkgs reachable")
EOF
```

**Fix.** Add missing entries. TS-only modules (`ui`) either declare the
pypi package OR raise an explicit ImportError from the shim (see `09`
§12). Never merge pyproject changes that leave a canonical pkg
unreachable.

## 15. Env-var documentation completeness

Every package that reads one or more `SCITEX_*` env vars MUST carry an
`NN_env-vars.md` leaf under `src/<pkg_snake>/_skills/<pkg>/` that documents
each variable (purpose, default, type, opt-in vs opt-out). Rule defined in
`01_arch_04_environment-variables.md`.

**Probe** (diff source vs docs across the ecosystem):

```bash
for p in $(scitex dev ecosystem list --json | python3 -c "import sys,json; d=json.load(sys.stdin); print(' '.join(x for x in d['packages'] if not x.endswith('template') and x!='scitex' and x!='automated-research-demo'))"); do
  src_envs=$(grep -rhoE 'SCITEX_[A-Z0-9_]+' $HOME/proj/$p/src/ 2>/dev/null | sort -u | wc -l)
  docs_envs=$(grep -rhoE 'SCITEX_[A-Z0-9_]+' $HOME/proj/$p/src/*/_skills/$p/*.md 2>/dev/null | sort -u | wc -l)
  [ "$src_envs" -gt 0 ] && [ "$docs_envs" -lt "$src_envs" ] && echo "$p: $docs_envs/$src_envs documented"
done
```

Any non-empty line is a release blocker — create/augment the leaf, link it
from `SKILL.md`, commit as `docs(env-vars): document SCITEX_* variables
actually read by <pkg>`.

## 16. Dynamic audit via agent task execution (planned)

Static = "looks right"; dynamic = "works right" under realistic
workloads (agents on end-to-end tasks, logging tool-use + output
quality). Static pass (§§1–15 + playbook §98) gates commit; dynamic
additionally gates PyPI release.

Design: `scitex-dev/src/scitex_dev/_skills/scitex-dev/20_dynamic-audit.md`
(tasks T01–T10; 3-task first pass). Host: `scitex-dev` owns
`scripts/quality/` + `logs/quality-audits/`; `scitex-python/scripts/`
is a mirror.

## 17. Dashboard export

`python3.11 ~/proj/scitex-python/scripts/audit_quality_dashboard.py` →
`scitex-dev/dashboards/quality.md`. Scope = §0 ∩ (`scitex*` or
allowlist: figrecipe, socialia, openalex-local, crossref-local).

## 18. English-only enforcement

Exempt with `# i18n-ok` / `<!-- i18n-ok -->` (±2-line marker).
`python3.11 ~/proj/scitex-python/scripts/audit_english_only.py`.

## 19. License enforcement (AGPL-3.0-only)

SPDX `license = "AGPL-3.0-only"` + AGPL classifier + LICENSE at root.
`scitex-dev/scripts/quality/audit_license.py` (+ `fix_license.py
--apply --commit`; skips dirty trees).

## Release-gate questions

1. Useful for Ph.D. students/researchers?
2. Meaningful tests, all green?
3. Easy to understand for humans and AI?
4. Easy to use for humans and AI?
5. Easy to maintain?
6. Docs / Read the Docs / examples in sync with code?
7. Periodic quality check actually running?
8. SciTeX conventions followed throughout?
9. All packages standardized and consistent?
10. English-only in comments and docs?

<!-- EOF -->