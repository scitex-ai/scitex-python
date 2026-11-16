---
name: stx.cli
description: SciTeX umbrella CLI discovery, canonical product and developer namespaces, and programmatic Click access. Available commands depend on installed, eligible providers.
---

# stx.cli

The `scitex` command dispatches to installed owner-qualified providers and
explicit umbrella workflows. Python availability alone does not imply a CLI.
Shared CLI conventions belong to scitex-dev. The source-backed umbrella guide
is [CLI reference](../../_skills/scitex/04_cli-reference.md).

## Sub-skills

- [cli-commands.md](cli-commands.md) — canonical public paths and migration
- [core-commands.md](core-commands.md) — entry point and metadata discovery
- [module-clis.md](module-clis.md) — selected provider workflows
- [programmatic-use.md](programmatic-use.md) — Click and JSON helpers

## Quick reference

```bash
scitex --help
scitex --json
scitex sdk --help
scitex cards --help
scitex clew --help
scitex ssh tunnel --help
scitex dev --help
scitex dev cli list --json
scitex dev completion install --dry-run
scitex dev skills --help
```

Normal help, JSON and completion omit hidden aliases. Recursive help can
resolve provider parsers; use a selected group's help when that is sufficient.
CLI discovery does not enable MCP tools, hosted routes or agent skill loading.
