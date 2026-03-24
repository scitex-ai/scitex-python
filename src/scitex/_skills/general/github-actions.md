---
name: github-actions
description: Standard GitHub Actions workflows for SciTeX packages — CI, PyPI publish, CLA, and advanced patterns.
---

> General patterns: see [programming-common/github-actions.md](../../commands/.claude/skills/programming-common/github-actions.md)

# GitHub Actions (SciTeX)

## SciTeX-Specific CLA Allowlist

```yaml
# cla.yml — ywatanabe1989 is always in the allowlist for SciTeX packages
allowlist: bot*,ywatanabe1989
```

## scitex-python Monorepo Pattern

For the scitex-python monorepo with 50+ modules, use path-filtered reusable workflows:

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
