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
| **HIGH** | "I added the change and the deploy log shows it landed" — yet the user-visible behavior is unchanged | **Confused "I made the change" with "the change took effect."** Between input and output sit silent defeats: CDN/browser cache, wrong build artifact, wrong code path / wrong host, identity mismatch (same name in two places), unmet preconditions — none throw errors | Verify the EFFECT, not the change. Read the live response / measurement on the deployed system, not the source diff. Quote numbers in the report. (Cross-cuts every package; CSS-specific instances live in package-private skills.) |

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

## 8. a2a-sdk + protobuf 6.x — `FieldDescriptor.label` AttributeError

**Symptom (CI):** test runs against `a2a-sdk[http-server]>=1.0.2` fail with::

    AttributeError: 'google._upb._message.FieldDescriptor' object has no attribute 'label'

**Root cause.** protobuf **6.x** removed `FieldDescriptor.label` from the
upb backend. a2a-sdk 1.0.x's `validate_proto_required_fields` still
references it (see `a2a/utils/proto_utils.py`). protobuf 7.x continues
to lack the attribute.

**Fix.** In `pyproject.toml`::

    "protobuf<6",   # not <7 — the bug is in 6.x already

Don't write `protobuf<7`: that allows 6.x which has the bug.

**Discovered.** scitex-agent-container 2026-04-27 (CI red on every
develop push since the a2a SDK 1.0 PR). Fixed in v0.5.1 of scitex-hpc
and v0.9.1 of sac. scitex-orochi shipped the same fix on 2026-04-28.

## 9. SLURM cgroup kills tmux spawned by `srun --overlap`

**Symptom.** `tmux new-session -d` returns rc=0 inside an `srun --jobid
--overlap` invocation, but `tmux ls` 2 seconds later shows no sessions.
The daemon you just started is gone.

**Root cause.** SLURM kills *all processes in a step's cgroup* when the
step ends. A tmux daemon spawned by `srun --jobid --overlap …` runs in
that step's transient cgroup, not the job's cgroup. When the wrapping
bash process exits, SIGKILL takes the daemon with it.

**Fix.** Run tmux as **PID 1 of the sbatch script**, before the hold
body. The daemon then lives in the job's main cgroup and survives
across `srun --overlap` invocations. Tenants connect via the same
named socket::

    # In the sbatch script body (e.g. from Reservation.book(tmux_server="sac"))
    tmux -L sac new-session -d -s _root 'sleep infinity'
    tail -f /dev/null   # holds the allocation

    # Tenants (run via srun --overlap) attach to the same server
    tmux -L sac new-session -d -s tenant-a 'claude --flags ...'

**Discovered.** scitex-agent-container 2026-04-28, Phase 4 multi-tenant
runtime (verified live on spartan-bm005). The `tmux_server` parameter
on `scitex_hpc.Reservation.book()` exists for exactly this reason.

## 10. Chatty login-shell banners break SLURM-output parsing

**Symptom.** ``squeue`` / ``scancel`` / ``scontrol`` calls run via
``ssh <host> 'bash -lc "squeue ..."'`` return data that *contains* the
expected output, but parsers fail because the data is preceded by 5-10
banner lines like::

    XAUTHORITY:
    DISPLAY: 1.2.3.4:0
    DISPLAY_GPU: :42
    RUNNING node-x

Naive parsing (``stdout.strip().split()[0]``) returns ``"XAUTHORITY:"``
as the SLURM state, never matches ``"RUNNING"``, and the polling loop
runs to timeout.

**Fix.** Parse line-by-line and filter against a known vocabulary
(SLURM states, jobid integers, etc.) — don't trust the first whitespace
token. ``scitex_hpc._reservation._parse_squeue_state_node`` is the
reference implementation.

**Discovered.** scitex-agent-container 2026-04-28 — first call to
``Reservation.book()`` on Spartan polled forever because Spartan's
``.bashrc`` emits 7 banner lines before any command output. Fixed in
scitex-hpc 0.5.1.

<!-- EOF -->
