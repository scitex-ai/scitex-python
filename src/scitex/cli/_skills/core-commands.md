---
name: cli-core-commands
description: The 'scitex' root CLI command — entry point, available subcommand groups, and how to get help for any command.
---

# Core CLI Commands

## Entry point

The `scitex` CLI is installed as a console script pointing to `scitex.cli.main:cli`.

```bash
scitex --help
scitex <subcommand> --help
```

## Available subcommand groups

```bash
scitex audio        # TTS / speech synthesis
scitex audit        # Security scanning
scitex cloud        # Cloud sync and project management
scitex container    # Container management
scitex dataset      # Dataset fetching and search
scitex dev          # Development utilities
scitex docs         # Documentation building and serving
scitex introspect   # Python API introspection
scitex linter       # SciTeX linter
scitex mcp          # MCP server management
scitex notebook     # Jupyter notebook utilities
scitex notification # Send notifications
scitex plt          # Plotting utilities
scitex repro        # Reproducibility tools
scitex scholar      # Literature management
scitex security     # GitHub security alerts
scitex social       # Social media posting
scitex stats        # Statistical analysis
scitex template     # Code templates
scitex tunnel       # SSH tunnel management
scitex web          # Web scraping
scitex writer       # LaTeX manuscript tools
```

## Getting help

```bash
# Root help
scitex --help

# Subcommand help
scitex audio --help
scitex scholar --help
scitex scholar fetch --help
```
