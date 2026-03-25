---
name: stx.dev
description: Development utilities — module reloading, code flow analysis, pyproject management, and demo plotters.
---

# stx.dev

The `stx.dev` module provides development and ecosystem management utilities for SciTeX package developers.

## Sub-skills

- [development-tools.md](development-tools.md) — `reload`, `reload_auto`, `CodeFlowAnalyzer`, `pyproject` management, demo plotters, CV utilities

## Quick Reference

```python
# Module hot-reload during development
from scitex.dev._reload import reload, reload_auto, reload_stop
reload()             # reload all scitex submodules once
reload_auto(10)      # background auto-reload every 10s
reload_stop()

# pyproject.toml management
from scitex.dev import _pyproject as pyproject
pp = pyproject.load()
pyproject.print_report()
pyproject.find_duplicates()

# Ecosystem management (via scitex-dev package)
packages = stx.dev.get_all_packages()
stx.dev.check_versions()
stx.dev.fix_mismatches()
stx.dev.bulk_rename(pattern="old_name", replacement="new_name", paths=["./src"])
```

## Key Subpackages

| Subpackage | Purpose |
|-----------|---------|
| `stx.dev.plt` | Demo plotters for all supported plot types |
| `stx.dev.cv` | Computer vision utilities (compose, title_card) |
| `stx.dev._reload` | Hot-reload utilities |
| `stx.dev._analyze_code_flow` | AST-based code flow analysis |
| `stx.dev._pyproject` | pyproject.toml dependency management |
