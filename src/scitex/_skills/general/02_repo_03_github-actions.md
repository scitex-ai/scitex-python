---
name: github-actions
description: Canonical GitHub Actions workflows that every SciTeX repo ships — test matrix across supported Python versions, PyPI publish via trusted-publisher OIDC (no API tokens), CLA-bot, reusable workflow patterns, artefact caching, and release-gate checks that guard the main branch. Use when creating a new scitex-* repo, auditing CI drift across the ecosystem, or wiring a new release-on-tag action.
canonical-location: scitex-python/src/scitex/_skills/general/02_repo_03_github-actions.md
---

# GitHub Actions (SciTeX)

## SciTeX-Specific CLA Allowlist

```yaml
# cla.yml — <username> (commiter) is always in the allowlist for SciTeX packages
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

## Naming Patterns

- Tag-based publish: used by scitex-io (push `v*` tag)
- Release-based publish: used by scitex-python (GitHub release published)

Both use OIDC trusted publishers — never store PyPI tokens in secrets.
