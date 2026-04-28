---
name: scitex-ecosystem-quality-failure-playbook
description: Per-symptom cookbook for the failure modes encountered across the SciTeX ecosystem. Paired with 99_quality_02_checklist.md — §99 is the strategic runbook, §98 is the cookbook. Each symptom carries a severity (CRITICAL / HIGH / MEDIUM / LOW) so an autonomous agent triages top-down.
canonical-location: scitex-python/src/scitex/_skills/general/98_quality_01_failure-playbook.md
tags: [scitex-python, scitex-general, scitex-package, meta]
---

# SciTeX Quality Failure Playbook

Cookbook of the specific symptoms observed during ecosystem-wide remediation passes, with severity ratings and canonical fixes. Use from §99 of the checklist when a probe flags one of these patterns.

**Severity:**
- **CRITICAL** — blocks multiple downstream repos or the whole release wave
- **HIGH** — blocks a single repo's CI or release
- **MEDIUM** — test-level assertion / config threshold
- **LOW** — cosmetic / content drift

## 1. CI failure-mode table (from §3 of checklist)

| Severity | Symptom | Root cause | Fix |
|---|---|---|---|
| **CRITICAL** | `ModuleNotFoundError: scitex_dev._skills_quality_pytest` across many repos | `scitex-dev` on PyPI lacks the module even though it exists on develop | Bump scitex-dev version, release → downstream picks it up (§4 below) |
| **CRITICAL** | Publish-to-PyPI `invalid-publisher: no corresponding publisher` | trusted publishing not configured on PyPI (or form silently discarded the save) | See §3 — verify "Manage current publishers" lists the entry after submit |
| **HIGH** | Downstream `ModuleNotFoundError` for something that IS in git | new submodule added after last tag; PyPI wheel is stale | See §4 — bump version + re-release |
| **HIGH** | `pytest: command not found` | `pip install -e .[dev]` but no `[dev]` extra defined | add explicit `pip install pytest pytest-cov` to workflow |
| **HIGH** | `isinstance(obj, plotly.graph_objs.Figure)` → `NoneType has no attribute 'graph_objs'` | optional plotly fell back to `None`, check was unconditional | helper that short-circuits when dep is `None` — see §5 |
| **HIGH** | `Doc-Drift Nightly` fails with `cannot import scitex_<x>` | downstream pkg not pulled by `.[all]` | add explicit `pip install scitex-<x>` after the `.[all]` line, or fix `[x]` extra |
| **MEDIUM** | `assert func() is True` fails on numpy 2 runners | `np.any()`/`np.all()` return `np.True_`; `np.True_ is not True` | coerce at return: `return bool(np.any(...))` — see §5 |
| **MEDIUM** | `Unnamed: *` columns in pandas DataFrame | loader's dtype guard matches `"object"` only; pandas ≥ 2.2 uses `str` dtype | try/except over string-match — see §5 |
| **MEDIUM** | Test uses `patch("pkg._torch")` and fails | `_torch` sentinel isn't a module-level attr | add `try: import torch as _torch / except: _torch = None` at module top, or `pytest.importorskip("torch")` |
| **MEDIUM** | `patch("git.Repo")` fails with `No module named 'git'` | gitpython not a test dep | `pytest.importorskip("git")` at top of test class |
| **MEDIUM** | `patch("pkg._get_x.split") AttributeError` | module was simplified to a one-line alias; mock target no longer exists | replace stale mock-based tests with a minimal alias check (`assert get_x is new_x`) |
| **MEDIUM** | Test references fake package e.g. `'mypackage'` | test never had a fixture | `tmp_path` + `sys.path.insert` + real package creation, or skip |
| **LOW** | `Doc-Drift Nightly` cancelled | 10-minute `timeout-minutes` hit by pip resolver backtracking | bump to 25 min, or constrain sphinx version to avoid backtracking |
| **LOW** | `coverage < fail_under` even though tests all pass | aspirational threshold; real coverage is lower | lower `fail_under` to current floor; raise again when new tests land |
| **LOW** | Skill quality `§2.prefix: MANIFEST.md filename must match NN_kebab-name.md` | MANIFEST.md is a system file, not a leaf | upgrade scitex-dev to a version where the checker exempts `SYSTEM_FILES = {"MANIFEST.md"}` |
| **LOW** | Skill quality `§3.index-monolith: SKILL.md > 4096B` | bloated frontmatter description | trim `description:` — it gets copied into skill-matching prompts; verbose prose costs tokens without helping trigger rates |
| **LOW** | Skill quality `§4.monolith: NN_foo.md > 10240B` | leaf grew unmanageably | split into two leaves with new prefixes, link both from `SKILL.md`, prefer topical split over length-based |

## 2. Triage order

Agent-mode: address CRITICAL before anything else — one CRITICAL can mask dozens of downstream failures. Then HIGH. Batch MEDIUM (they usually share a root cause). LOW is opportunistic.

## 3. PyPI trusted-publisher setup (silent-save gotcha)

The **first** release of any new PyPI project must be `twine upload` from a local build — trusted publishing cannot create a new project. Afterwards, configure the trusted publisher at:

```
https://pypi.org/manage/project/<pkg>/settings/publishing/
```

Fields: owner `ywatanabe1989`, repo `<pkg>`, workflow `publish-pypi.yml`, environment `pypi`.

**Silent-save gotcha** — after submit, the "Manage current publishers" list must actually show the new entry. If it still says *"No publishers are currently configured"*, the form didn't persist. Re-enter it. This is the single most common cause of `invalid-publisher` errors on a tag-triggered publish when the package already exists on PyPI. Once configured, `gh run rerun <id>` — no retag needed.

**Probe** (tag ↔ PyPI alignment):

```bash
for r in ~/proj/scitex-*; do
  [ -f "$r/pyproject.toml" ] || continue
  pkg=$(basename $r)
  tag=$(git -C $r tag --sort=-v:refname | head -1)
  pypi=$(curl -s https://pypi.org/pypi/$pkg/json \
         | python3 -c "import sys,json;d=json.load(sys.stdin);print('v'+d['info']['version'])" 2>/dev/null)
  [ -n "$tag" ] && [ -n "$pypi" ] && [ "$tag" != "$pypi" ] && echo "$pkg: tag=$tag pypi=$pypi"
done
```

## 4. Wheel-content drift (git has it, PyPI doesn't)

When downstream tests `ModuleNotFoundError` a submodule that clearly exists in `src/` on develop, the PyPI wheel was cut before that module landed. Verify:

```bash
pip download <pkg>==<pypi-version> --no-deps -d /tmp/check
python3 -c "import zipfile,os;p='/tmp/check';w=[f for f in os.listdir(p) if f.endswith('.whl')][0];z=zipfile.ZipFile(os.path.join(p,w));print([n for n in z.namelist() if 'submodule_name' in n])"
```

**Fix:** bump the package version, tag, push — publishes the current state. Never "fix" downstream by pinning to an older version; fix the upstream release.

Session hit: `scitex-dev 0.6.1` on PyPI lacked `_skills_quality_pytest.py`; released 0.7.0 to unblock 10 downstream CIs.

## 5. Optional-dep guards + numpy 2 + pandas compat

### 5a. Optional imports

```python
try:
    import plotly
except ImportError:
    plotly = None

def _is_plotly_figure(obj) -> bool:
    if plotly is None:
        return False
    return isinstance(obj, plotly.graph_objs.Figure)
```

Same for `pandas`, `xarray`, `PIL.Image`, `torch`, `seaborn`. Bare `isinstance(obj, plotly.graph_objs.Figure)` crashes with `'NoneType' has no attribute 'graph_objs'` when the dep isn't installed.

### 5b. numpy 2 bool identity

`np.any()`, `np.all()`, and similar reductions return `np.True_` / `np.False_` on numpy 2+. `np.True_ is not True`. Coerce at return:

```python
def is_listed_X(obj, types) -> bool:
    ...
    return bool(np.any(conditions))
```

Probe: `grep -rn 'return np\.\(any\|all\|bool_\)' <repo>/src/`.

### 5c. pandas dtype breadth

Don't hardcode `"object"` when checking column dtypes. pandas ≥ 2.2 uses `str`, `string`, `string[python]`. Prefer try/except:

```python
try:
    unnamed = obj.columns.str.contains("^Unnamed")
except (AttributeError, TypeError):
    unnamed = None
if unnamed is not None and unnamed.any():
    obj = obj.loc[:, ~unnamed]
```

## 6. Extras-completeness (empty `[foo]` breaks umbrella bridges)

Every bridge directory under `src/scitex/<name>/` that re-exports a standalone package must have its extra populated. Empty `[container] = []` leaves `stx.container.apptainer` unreachable from `pip install scitex[all]`; Doc-Drift flags every chain.

**Probe (inside scitex-python):**

```bash
python3 -c "
import tomllib, pathlib
d = tomllib.loads(open('pyproject.toml','rb').read())
extras = d['project']['optional-dependencies']
bridges = [p.name for p in pathlib.Path('src/scitex').iterdir()
           if p.is_dir() and not p.name.startswith('_')]
for b in bridges:
    if b in extras and extras[b] == []:
        print(f'EMPTY: scitex[{b}] but src/scitex/{b}/ exists')
"
```

**Fix:** `container = ["scitex-container"]`, `dataset = ["scitex-dataset"]`, etc.

## 7. Doc-Drift CI install source

`doc-drift-nightly.yml` must install scitex from **the current checkout** (`pip install ".[all]"`) rather than from PyPI (`pip install "scitex[all]"`). Otherwise a pyproject.toml fix in the same push won't take effect until a PyPI release catches up.

The workflow's `on: push: paths:` filter also excludes `pyproject.toml` — force a run with `gh workflow run "Doc-Drift Nightly" --ref develop` after the push.

## 8. Implicit transitive dep after a refactor (the 2026-04-28 class-action)

**Symptom.** `pip install <pkg>==<latest>` in a fresh venv fails with
`ModuleNotFoundError: No module named 'scitex_config'` (or any other
ecosystem package). CI's *Test* job is green because the dev environment
has the dep installed editable; only the *Install Test (fresh venv)* job
catches it.

**Root cause.** A migration sweep edits `src/<pkg>/...` to `from
scitex_config._ecosystem import local_state` but doesn't audit
`pyproject.toml` for the new transitive dep. The package now imports
something it doesn't declare, so PyPI consumers hit ModuleNotFoundError.

**Detection** is automated in
`scitex-dev/scripts/quality/audit_ecosystem.py` (`§C5 src imports
scitex_config but pyproject does not declare scitex-config`). The
nightly `quality-audit.yml` workflow opens a tracking GitHub issue
tagged `quality-audit` if any CRITICAL findings appear.

**Fix recipe.**

1. Add the dep to `dependencies = [...]` (NOT `optional-dependencies`).
2. Bump the patch version (`0.1.9 → 0.1.10`).
3. `git tag v<new>` and push tags. If the publish workflow uses
   `event: release` instead of `push: tags: ['v*']`, also create a
   `gh release create v<new>` so PyPI publish actually fires.
4. Verify on PyPI with `pip index versions <pkg>` — a pushed tag without
   a corresponding release is invisible to consumers.

**Affected on 2026-04-28 (all fixed + republished):** scitex-core 0.2.5,
scitex-container 0.1.10, scitex-browser 0.1.11, scitex-dataset 0.3.5,
scitex-decorators 0.1.4, scitex-template 0.6.1.

## 9. Local-state path migration breaks tests (silent twin of §8)

**Symptom.** Local pytest passes; CI Test fails with assertions like
`assert "scitex-dataset" in str(path)` because the resolved path is now
`<scitex_dir>/dataset/runtime/datasets.db` — no `scitex-` prefix anywhere.

**Root cause.** Migrating to
`scitex_config._ecosystem.local_state.{path,runtime_path,user_path}`
changes the layout from `~/.cache/scitex-<pkg>/...` or
`~/.scitex/<full-pkg-name>/...` to the canonical
`<scitex_dir>/<pkg-short>/runtime/...` (where `pkg-short` strips the
`scitex-` prefix). Tests that asserted the old substrings now fail.

**Fix recipe.**

- Replace `assert "scitex-<pkg>" in str(path)` with semantic checks
  against the new layout: `assert "<pkg-short>" in s and "runtime" in s`,
  or construct the expected path via
  `local_state.runtime_path("<pkg-short>", "...")` rather than asserting
  string substrings.
- Canonical fixups: scitex-dataset `2190783`, scitex-container `8724740`.

## 10. PostToolUse CI watcher closes the loop end-to-end

`~/.claude/hooks/post-tool-use/check_ci_status.sh` emits
`WARN  CI FAILURE  ...` to stderr + `exit 2` so Claude Code forwards the
message to the assistant on every tool call inside a git repo. Pair it
with the `speak-and-call` directive ("don't continue past a WARN").
Without the watcher, the bugs from §8 and §9 stay silent until a human
notices PyPI is broken.

The companion `audit_ecosystem.py` script runs nightly, opens a
GitHub issue tagged `quality-audit` on CRITICAL/HIGH, and uploads the
full JSON as an artifact.

## 11. Orphan License classifier blocks setuptools 80+ build (the 2026-04-28b class-action)

**Symptom.** ``pip install -e .`` fails with
``setuptools.errors.InvalidConfigError: License classifiers have been
superseded by license expressions``. CI's *Test* / *Tests* job aborts
before any test runs.

**Root cause.** PEP 639 deprecated the legacy
``"License :: OSI Approved :: ..."`` classifier in favour of the
``license = "AGPL-3.0-only"`` SPDX expression. setuptools 80+ refuses
the build when *both* are present. After our 2026-04-28a normalization
to SPDX (E5C11), 41 ecosystem packages still carried the legacy
classifier alongside the new SPDX form.

**Detection** is automated in
`scitex_dev._pyproject_lint.check_orphan_license_classifier`
(rule ``E5C13_orphan_license_classifier``, severity HIGH).

**Fix.** Remove the classifier line; SPDX is authoritative now:

```toml
[project]
license = "AGPL-3.0-only"
classifiers = [
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    # "License :: OSI Approved :: GNU Affero General Public License v3",  ← drop
]
```

**Affected on 2026-04-28 (all 31 fixed + republished):** crossref-local,
figrecipe, openalex-local, scitex-agent-container, scitex-audio,
scitex-audit, scitex-browser, scitex-clew, scitex-compat, scitex-core,
scitex-dataset, scitex-db, scitex-dict, scitex-etc, scitex-gists,
scitex-io, scitex-logging, scitex-notification, scitex-orochi,
scitex-parallel, scitex-path, scitex-plt, scitex-repro, scitex-scholar,
scitex-stats, scitex-str, scitex-template, scitex-types, scitex-writer,
socialia, scitex-python.

## 12. Click subcommand rename desyncs tests

**Symptom.** Click CLI tests exit with code 2 ("usage error") because
``runner.invoke(cli, ["send", ...])`` references the old command name
after a refactor renamed it to ``send-notification``.

**Root cause.** A package introduces a deprecated-redirect for old
command names:

```python
cli.add_command(_deprecated_redirect("send", "send-notification"))
```

The redirect prints a usage error and exits 2 (correctly — operators
shouldn't keep using the old name). But test code that still invokes
``["send", ...]`` hits this exit-2 path and asserts ``exit_code == 0``.

**Fix.** Update the test invocations to the new names. Caught for
scitex-notification on 2026-04-28: send→send-notification,
sms→send-sms, config→show-config, backends→list-backends.

**Followup rule** (not yet codified): every Click command rename
should sweep `tests/` for the old literal at the same time. Could
codify as `E5G2_test_uses_renamed_cli` if this pattern recurs.

<!-- EOF -->
