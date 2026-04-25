---
name: github-actions
description: Canonical GitHub Actions workflows that every SciTeX repo ships — test matrix across supported Python versions, PyPI publish via trusted-publisher OIDC (no API tokens), CLA-bot, reusable workflow patterns, artefact caching, the `pip install -e ".[dev]"` rule, dep-hygiene gotchas (test imports must use the standalone module name not the umbrella shim), and release-gate checks that guard the main branch. Use when creating a new scitex-* repo, auditing CI drift across the ecosystem, or debugging a red workflow.
canonical-location: scitex-python/src/scitex/_skills/general/02_repo_03_github-actions.md
tags: [scitex-python, scitex-general, scitex-package, meta]
---

# GitHub Actions (SciTeX)

## Test job — install with the `[dev]` extra

CI runners start clean: no `pytest`, no `pytest-cov`, no `pytest-asyncio`, no project deps. The single canonical install line in every test workflow is:

```yaml
- name: Install
  run: pip install -e ".[dev]"
```

The `[dev]` extra in `pyproject.toml` MUST cover everything the test suite imports:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov",
    "pytest-asyncio>=0.21",   # only if any test uses @pytest.mark.asyncio
    # … any other dev-time-only dep (mypy, ruff for the CI lint job, etc.)
]
```

Common breakage modes:

| Symptom in CI logs | Root cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'pytest'` | bare `pip install -e .` | switch to `pip install -e ".[dev]"` |
| `PytestUnknownMarkWarning: Unknown pytest.mark.asyncio` then test counted as fail | `pytest-asyncio` missing from `[dev]` | add it |
| `ModuleNotFoundError: No module named 'click'` while running CLI | runtime dep declared only under `[dev]` | move to `dependencies = [...]` |

## Test imports — use the standalone module name, not the umbrella shim

**Rule.** Inside a standalone `scitex-X` package's `tests/`, always import via `scitex_X` directly:

```python
# YES — works in any environment that has scitex-X installed
from scitex_template import clone_template_from_cache
from scitex_template._mcp.handlers import list_templates_handler

# NO — only works when the scitex umbrella + its sys.modules alias shim
# are both installed. Fresh CI venv installs scitex-X alone, so this raises
# ModuleNotFoundError at collection time:
from scitex.template import clone_template_from_cache
from scitex.template._mcp.handlers import list_templates_handler
```

The same rule applies to internal imports inside `src/scitex_X/`. The umbrella shim path is only for users discovering the API via `scitex.X.…`; it is never a runtime path the package itself should rely on.

**Quick sed to fix a broken test suite after extraction:**

```bash
grep -rl "from scitex\.<name>\." tests/ \
  | xargs sed -i 's/from scitex\.<name>\b/from scitex_<name>/g'
```

## Downstream-dep hygiene in CI

A standalone `scitex-X` package SHOULD install cleanly without the `scitex` umbrella present (general/01_arch_02 §"Dependency Hygiene"). This is enforced in CI by running the test job in a fresh venv that installs ONLY `pip install -e ".[dev]"` — no `scitex`. If any test imports `scitex.…` (the umbrella) it will fail; that's the intended signal.

When a few legacy code paths still need umbrella access (e.g. the cloner's remote-clone fallback that uses `scitex.git`), declare a separate optional extra:

```toml
[project.optional-dependencies]
legacy = ["scitex"]
```

…and gate the imports with `try/except ImportError`. The default `[dev]` install must NOT pull `[legacy]`; otherwise the dep-hygiene check is meaningless.

## SciTeX-Specific CLA Allowlist

```yaml
# cla.yml — <username> (committer) is always in the allowlist for SciTeX packages
allowlist: bot*,<username>
```

## scitex-python Transitional Pattern

scitex-python is transitioning from monorepo to standalone packages; use path-filtered reusable workflows where modules remain in-tree.

```yaml
# test-stats.yml (module-specific caller)
on:
  push:
    paths: [src/scitex/stats/**, tests/scitex/stats/**]
jobs:
  test:
    uses: ./.github/workflows/_test-module.yml
    with:
      module: stats
```

The reusable `_test-module.yml` calls `./scripts/test-module.sh ${{ inputs.module }}`.

## Module-Specific Workflows Table

| Workflow file | Module | Path filter |
|---------------|--------|-------------|
| `test-io.yml` | io | `src/scitex/io/**` |
| `test-plt.yml` | plt | `src/scitex/plt/**` |
| `test-stats.yml` | stats | `src/scitex/stats/**` |
| ... | ... | ... |

## PyPI publish — OIDC trusted publisher only

```yaml
# publish-pypi.yml
on:
  push:
    tags: ['v*']
jobs:
  publish:
    runs-on: ubuntu-latest
    environment:
      name: pypi
      url: https://pypi.org/p/<pkg-name>     # MUST match exact PyPI project name
    permissions:
      id-token: write                        # required for OIDC
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install build
      - run: python -m build
      - uses: pypa/gh-action-pypi-publish@release/v1
```

Trigger: push a `v0.1.0`-style tag. The first publish requires a one-time browser configuration at https://pypi.org/manage/account/publishing/ — bind the GitHub repo + workflow name + environment name. After that, every tag triggers an automatic release. **Never** store `PYPI_API_TOKEN` in repo secrets.

Naming patterns:
- Tag-based publish: used by most scitex-* packages (push `v*` tag).
- Release-based publish: used by scitex-python (GitHub Release published).

## Weekly quality audit

Every package inheriting from `scitex-minimal-template` carries `.github/workflows/scitex-quality.yml`. Runs `scitex-dev quality {audit-cli, audit-frontmatter, audit-docs, audit-lines, audit-scope}` on a Monday cron + on push/PR. Warn-only (`continue-on-error: true`) until the package is clean; flip individual steps to fail-the-build once green.

## Release-gate checklist

Before tagging `v*`:

1. CI green on `main` (the test workflow + scitex-quality both passing).
2. `CHANGELOG.md` updated with the new version section.
3. Version bumped in `pyproject.toml` AND any `__version__.py`.
4. Local fresh-venv probe: `pip install -e ".[dev]"` then `pytest` — must mirror what CI sees.
5. `pip install` from a sibling dir without scitex installed (dep-hygiene self-check).
6. Tag pushed (`git push origin v0.1.0`) — triggers `publish-pypi.yml`.
