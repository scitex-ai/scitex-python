---
description: |
  [TOPIC] CLI reference — scitex umbrella
  [DETAILS] `scitex` console entry dispatches to per-package CLIs (`scitex io ...`, `scitex plt ...`, `scitex scholar ...`); the umbrella itself adds version + MCP server entry points.
tags: [scitex-cli-reference]
---

# CLI reference — scitex

The `scitex` console script is a thin dispatcher. For per-package
sub-commands, refer to the sister-package skill (e.g. `scitex-scholar`
documents `scitex scholar bibtex ...`).

## Top-level commands

```bash
scitex --version            # umbrella version
scitex --help               # list available sub-commands
scitex mcp                  # umbrella MCP server entry
```

## Sub-command dispatch

Each installed sister package contributes its own sub-command tree. The
exact subset depends on what you have installed:

```bash
scitex scholar ...          # literature management
scitex writer  ...          # manuscript compilation
scitex cloud   ...          # SciTeX Cloud
scitex notebook ...         # notebook reproducibility
scitex container ...        # container management
scitex io ...               # I/O helpers
# ...
```

Each top-level group accepts `--help`:

```bash
scitex scholar --help
scitex writer compile --help
```

## Standalone aliases

Sister packages also ship their own console scripts (e.g.
`crossref-local`, `openalex-local`, `scitex-notebook`). The umbrella
`scitex <sub>` form and the standalone scripts share implementations.

## MCP server

```bash
scitex mcp                  # serve the umbrella's mounted MCP namespaces
```

This boots the FastMCP server defined in `scitex.mcp_server`, which
mounts every sister-package MCP server under its namespaced prefix
(`io_*`, `plt_*`, `stats_*`, `scholar_*`, ...).
