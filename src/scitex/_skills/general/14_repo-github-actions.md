---
name: github-actions
description: Standard GitHub Actions workflows for SciTeX packages — CI, PyPI publish, CLA, and advanced patterns.
---

# GitHub Actions (SciTeX)

## SciTeX-Specific CLA Allowlist

```yaml
# cla.yml — ywatanabe1989 is always in the allowlist for SciTeX packages
allowlist: bot*,ywatanabe1989
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
