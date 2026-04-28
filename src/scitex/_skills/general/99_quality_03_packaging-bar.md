---
name: packaging-quality-bar
description: Ecosystem-wide packaging quality bar for SciTeX packages — declared deps, peer-pin minimums, extras (always all/dev/docs), install-test CI, audit tooling in scitex-dev, twine-first publishing, no bot signatures in commits. Captures the directives that emerged during the 2026-04 standalonization wave.
canonical-location: scitex-python/src/scitex/_skills/general/99_quality_03_packaging-bar.md
tags: [scitex-python, scitex-general, scitex-package, packaging, quality, ci, pypi]
---

# SciTeX packaging quality bar

What every package in the ecosystem must satisfy. Distilled from the
2026-04 standalonization wave (24 new packages + 32 pre-existing audited).
**Every rule below is enforceable via `scitex_dev` and CI** — don't
audit by hand.

## 1. Don't reinvent the wheel

Before writing utility code, check PyPI for an existing well-maintained
package. Examples from this ecosystem:

| Need | Use |
|---|---|
| Title-case strings | `titlecase` (Stuart Colville's NYT-style) |
| TOML parsing | stdlib `tomllib` (3.11+) / `tomli` (3.10) |
| Trove classifier validation | `trove-classifiers` |

Wrap the dep in a thin domain-specific layer (e.g. SciTeX acronym
callback for `titlecase`). The wrapper goes in our package; the
canonical algorithm stays in the upstream package.

## 2. Declared dependencies must cover module-level imports

A package can build, upload, and pass its own tests with the wrong
`pyproject.toml` — the bug only shows up when a fresh user runs
`pip install <pkg>` in a clean venv.

Tools:

```python
from scitex_dev import audit_dependencies
print(audit_dependencies("/path/to/scitex-foo"))
# → flags missing externals, missing peers, peers without min-version pins
```

Rules:

- Every **module-level non-try-wrapped** external import must be in
  `[project.dependencies]` or in an `[project.optional-dependencies]`
  extra **and** lazy-imported (try/except in `__init__.py`).
- Heavy deps (`torch`, `tensorflow`, `cv2`) that are only used by a small
  fraction of the API go in an extra (`[torch]`, `[cv]`, etc.) and the
  imports they trigger are wrapped in `try/except ImportError`.
- Map import → dist names correctly: `cv2` → `opencv-python`,
  `bs4` → `beautifulsoup4`, `yaml` → `PyYAML`, `git` → `GitPython`,
  `docx` → `python-docx`, `ruamel` → `ruamel.yaml`,
  `psycopg2` → `psycopg2-binary`, `umap` → `umap-learn`.

## 3. SciTeX peer packages must have minimum-version pins

Always `scitex-X>=Y.Z.W`, never bare `scitex-X`. A bare spec lets the
resolver pick a stale release that lacks a needed feature, breaking
downstream installs silently.

The audit flags this as `scitex_peers_without_min_version`.

## 4. `[project.optional-dependencies]` must include `all`, `dev`, `docs`

```python
from scitex_dev import audit_extras, write_extras_to_pyproject
print(audit_extras("/path/to/scitex-foo"))
# → flags missing all/dev/docs + missing all-refs
write_extras_to_pyproject("/path/to/scitex-foo")  # idempotent canonical rewrite
```

Conventions:

- `all` references **every feature extra** (e.g. `pkg[torch]`, `pkg[mcp]`)
  so a single `pip install pkg[all]` gets every feature.
- `dev` is `pytest + pytest-cov + ruff` minimum; packages may add custom
  dev tools.
- `docs` is `sphinx + sphinx-rtd-theme + myst-parser + sphinx-copybutton +
  sphinx-autodoc-typehints` minimum.
- `dev` and `docs` are **intentionally NOT in `all`** (separate concerns:
  development setup vs. user feature install).

## 5. `install-test.yml` CI on every repo

Every SciTeX repo has `.github/workflows/install-test.yml` that:

- Builds the wheel
- `pip install dist/*.whl` in a fresh venv on Python 3.10/3.11/3.12
- Imports the package by detecting the import name from `src/`
- Optionally runs `scitex_dev.audit_dependencies` as a secondary check

This catches undeclared deps **before publish**, not after a user files
a bug. Template is in `scitex-template/.github/workflows/install-test.yml`.

## 5a. Wheel-vs-source data-file audit

Non-Python data files (`SKILL.md`, `*.yaml`, `*.json`, `*.png`, ...) sitting
in `src/<pkg>/` on disk can be silently dropped from the wheel:
`setuptools.packages.find` and hatchling's defaults pick up Python files
plus dirs with `__init__.py` — arbitrary data files are **not shipped**
unless explicitly declared via `[tool.setuptools.package-data]` or
hatchling's `force-include`.

Failure mode: `pip install scitex-X` works, but `<pkg>/_skills/SKILL.md`
(or any data leaf) is missing. The package can't load its skill, the
helper can't find its template, etc.

```python
from scitex_dev import audit_package_data
r = audit_package_data("/path/to/scitex-foo")
print(r.summary())              # one-line pass/fail
if not r.is_clean:
    print(r.fix_suggestion)     # ready-to-paste pyproject snippet
```

Run pre-publish per package; the report includes the exact
pyproject.toml snippet (setuptools or hatchling form, matched to the
package's build-backend) needed to ship the missing files.

## 6. Twine-first for new ecosystem batches

PyPI's pending-publisher form is gated to **3 pending entries per
account** and rate-limits the upload endpoint at the **hour scale** for
new project creation. For ecosystems > 3 packages, do this:

1. `twine upload` once per package (creates the project on PyPI).
2. Attach a trusted publisher from each project's manage page (no
   3-publisher limit there because publishers attach to existing
   projects).
3. Future releases use OIDC via `publish-pypi.yml` workflow on `v*`
   tag push.

Reusable helper:

```python
from scitex_dev import publish, publish_all
publish_all([f"~/proj/{p}" for p in PACKAGES],
            method="auto",      # 'auto' = OIDC if workflow file exists
            dry_run=False,
            skip_if_published=True)  # idempotent for partial-batch retries
```

## 7. Validate trove classifiers locally before build

PyPI rejects with **400 Bad Request** on upload if any classifier is
unknown. Plausible-looking strings like
`Topic :: Software Development :: Testing :: Benchmark` are *not* in the
trove list.

```python
from scitex_dev.pypi import validate_classifiers
bad = validate_classifiers("/path/to/scitex-foo")
if bad:
    raise ValueError(f"invalid trove classifiers: {bad}")
```

`publish_via_twine()` runs this automatically with
`validate_classifiers_first=True`.

## 8. CLA gates do NOT accept bot-signature commits

Trailers like `Co-Authored-By: <bot> <noreply@…>` from automated tooling
(Claude / Copilot / etc.) cause CLA-assistant to block PR merge with
"unsigned contributor". Drop those trailers — attribution metadata
belongs in PR descriptions, not commit messages.

The CLA gate matches the **GitHub identity that authored the commit**,
not co-author trailers.

## 9. Git workflow conventions

- **Never push directly to `main`.** Use `develop` or feature branches.
  The pre-push hook blocks `main` pushes.
- **Always use `git -C /full/path`** in scripts so the CWD doesn't matter.
- **Always use `cp -f`** in scripts to avoid interactive prompts that
  hang automation.
- **Always use full paths to `pytest`** in scripts (`pytest --rootdir=/full/path tests/`).

## 10. Working examples + tests for examples

Every package should ship:

- `examples/` directory with a small set of runnable scripts
  demonstrating real usage (not docstrings — actual `.py` files).
- `tests/test_examples.py` (or similar) that imports each example or
  runs a smoke version of it.

This catches "the README example actually crashes" bugs at PR time.
**Wave-extracted packages currently lack this** — open follow-up.

## 11. README + RTD + skills must be uniform-quality

Each package's README has:

- 1-line description matching `pyproject.toml` `[project].description`
- Install instructions (`pip install scitex-X`)
- Minimal usage example (real code, copy-paste runnable)
- Status block (alpha/beta/stable + tested-on)
- Badges (PyPI version, Python versions, CI test, Codecov, RTD, License)
- "Part of SciTeX" + Four Freedoms section
- License footer (no `ywatanabe@scitex.ai` per
  `02_repo_04_quality.md` — community project)

RTD must be live for every package (`scitex_dev.check_all_rtd()` audits
this). `_skills/` directory present for any package that exposes
domain-specific patterns to AI agents.

## 12. Coverage + Codecov badges are part of CI

Every package's `test.yml` runs `pytest --cov=src/<pkg> --cov-report=xml`
+ uploads to Codecov. The README has the resulting badge. **Open
follow-up — currently only ~5/56 packages have this.**

## 13. Verify before declaring; no false-positive reports

Always test the actual end-to-end path (e.g. fresh-venv `pip install`)
before saying "fixed." Don't claim work is done based on `python -m
build` succeeding — the real test is `pip install <wheel> && python -c
"import <pkg>"` in a clean environment.

## 14. Skip difficult parts and continue autonomously

When a particular fix would take too long or requires deep domain
knowledge (e.g. test-quality audits for upstream pre-existing tests),
document it in TODO and move to the next item rather than blocking on
it. The user explicitly prefers progress on multiple fronts over deep
focus on one stuck issue.

## 15. Ecosystem-wide management lives in `scitex-dev`

All cross-cutting tooling (audits, publishing, ecosystem registry,
RTD checks, host sync) lives in `scitex_dev`. Don't write one-off
scripts; extend the package. Current modules:

| Module | Purpose |
|---|---|
| `scitex_dev.ecosystem` | `ECOSYSTEM` dict — single source of truth for package names, paths, repos |
| `scitex_dev.pypi` | `publish` / `publish_all` / `publish_via_tag` / `publish_via_twine` / `trusted_publisher_form` / `validate_classifiers` / `is_published` |
| `scitex_dev._pypi_deps` | `audit_dependencies` / `audit_all` / `DepAuditReport` |
| `scitex_dev._pypi_extras` | `audit_extras` / `write_extras_to_pyproject` |
| `scitex_dev.rtd` | `check_all_rtd` / `check_rtd_status` |
| `scitex_dev.sync` | local ↔ remote host sync |
| `scitex_dev.versions` | version consistency checks |

When you find a recurring problem, add it as a new audit / fix function
here so the next person doesn't re-discover it.

## Companion skills

- `04_development-workflow/12_pypi.md` (global) — full PyPI playbook.
- `04_development-workflow/11_readthedocs.md` (global) — RTD onboarding.
- `04_development-workflow/07_git-versioning.md` (global) — version-bump checklist.
- `02_repo_04_quality.md` — README rules (Four Freedoms, no `as stx`, etc.).
- `01_arch_02_dependency-and-version-pinning.md` — when consumers' minimum versions need bumping.

<!-- EOF -->
