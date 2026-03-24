---
name: stx.cli
description: Command-line interface for SciTeX platform operations (cloud, scholar, writer, project).
---

# stx.cli

The `stx.cli` module provides the unified `scitex` command-line interface for interacting with SciTeX platform services including cloud operations, scholar literature management, writer manuscript tools, and project workflows.

## Python API

```python
import scitex as stx

# Access the Click CLI group programmatically
cli = stx.cli.cli
```

## CLI Usage

```bash
# Main entry point
scitex --help

# Cloud operations (wraps Gitea)
scitex cloud status
scitex cloud push

# Scholar operations
scitex scholar search "deep learning EEG"
scitex scholar enrich papers.bib

# Writer operations
scitex writer compile manuscript/
scitex writer figures list

# Project operations
scitex project init my_experiment
```

## Key Features

- Unified `scitex` CLI built with Click
- Cloud operations: project management, file sync, Git integration
- Scholar operations: paper search, BibTeX enrichment, PDF download
- Writer operations: LaTeX compilation, figure/table management
- Project operations: integrated research workflow automation
- `print_help_recursive` utility for displaying all subcommand help
