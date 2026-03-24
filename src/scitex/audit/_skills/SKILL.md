---
name: stx.audit
description: Unified security scanning orchestrating bandit, shellcheck, pip-audit, and GitHub alerts.
---

# stx.audit

The `stx.audit` module provides a unified security scanning interface that orchestrates multiple security tools: bandit (Python static analysis), shellcheck (shell script linting), pip-audit (dependency vulnerabilities), and GitHub security alerts.

## Python API

```python
import scitex as stx

# Audit entire project
results = stx.audit.audit(".")

# Audit with specific checks only
results = stx.audit.audit(".", checks=["python", "shell"])

# Audit a specific subdirectory
results = stx.audit.audit("./src", checks=["python", "deps"])
```

## Key Features

- `audit(path, checks=None)` — run all or selected security checks on a path
- Supports check categories: `"python"` (bandit), `"shell"` (shellcheck), `"deps"` (pip-audit), `"github"` (GitHub alerts)
- Returns structured results with findings per checker
- Single entry point for project-wide security scanning
