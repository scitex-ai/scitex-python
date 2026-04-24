---
name: stx.cli
description: Command-line interface for SciTeX platform operations — 30+ subcommands with lazy loading. Specialization of scitex-cli-convention.
---

# stx.cli

> **This skill is a specialization of the canonical SciTeX CLI convention.**
> See: `src/scitex/_skills/general/03_interface_02_cli.md` (same repo)
> for the canonical rules. This file only covers `scitex` (scitex-python)
> specific nouns, the 30+ module-CLI layout, and Click lazy-loading.

The `stx.cli` module provides the unified `scitex` command-line interface for interacting with SciTeX platform services. It uses lazy loading so startup is instant regardless of how many subcommands exist.

## Sub-skills

- [cli-commands.md](cli-commands.md) — Full command reference table, common usage patterns, key examples
- [programmatic-use.md](programmatic-use.md) — Accessing the Click group, `print_help_recursive`, `group_to_json`, `format_python_signature`

## Quick Reference

```bash
# Entry point
scitex --help
scitex --help-recursive        # all subcommands
scitex --json                  # structured JSON output

# Core workflows
scitex config list
scitex cloud clone user/project
scitex scholar bibtex papers.bib
scitex mcp start
scitex audit run ./src
scitex completion install      # tab-completion setup
```

```python
# Programmatic access
from scitex.cli import cli, print_help_recursive, group_to_json
import click

ctx = click.Context(cli)
group_to_json(ctx, cli)   # JSON summary of all subcommands
```
