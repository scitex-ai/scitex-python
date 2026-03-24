---
name: stx.dev
description: Development, debugging, and ecosystem management utilities for SciTeX package developers.
---

# stx.dev

The `stx.dev` module provides development and ecosystem management utilities for SciTeX package developers. It covers version checking, documentation, bulk renaming, HPC testing, SSH host management, and GitHub operations.

## Python API

```python
import scitex as stx

# Ecosystem overview
packages = stx.dev.get_all_packages()
stx.dev.check_versions()
stx.dev.fix_mismatches()

# Documentation
docs = stx.dev.get_docs("scitex.stats")
stx.dev.build_docs()

# Bulk rename across files
result = stx.dev.bulk_rename(
    pattern="old_name", replacement="new_name",
    paths=["./src"]
)

# HPC testing
job_id = stx.dev.submit_hpc_test("test_dsp.py")
result = stx.dev.fetch_hpc_result(job_id)

# SSH host management
stx.dev.check_all_hosts()

# GitHub remote management
stx.dev.check_all_remotes()
```

## Key Features

- `ECOSYSTEM` — registry of all SciTeX packages and their configurations
- `get_all_packages` / `check_versions` / `fix_mismatches` — ecosystem version management
- `bulk_rename` / `execute_rename` — safe file content renaming with dry-run support
- `build_docs` / `get_docs` — documentation building and retrieval
- `check_all_hosts` — verify SSH connectivity to all configured hosts
- `check_all_remotes` / `check_rtd_status` — GitHub and Read-the-Docs status
- Delegates to `scitex-dev` package
