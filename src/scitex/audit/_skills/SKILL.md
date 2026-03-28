---
name: stx.audit
description: Unified security scanning orchestrating bandit, shellcheck, pip-audit, and GitHub alerts.
---

# stx.audit

The `stx.audit` module provides a unified security scanning interface that orchestrates multiple security tools: bandit (Python static analysis), shellcheck (shell script linting), pip-audit (dependency vulnerabilities), and GitHub security alerts.

## Sub-skills

- [security-scanning.md](security-scanning.md) — Running security scans, checker categories, return value structure, and individual checker details

## Quick Reference

```python
from scitex.audit import audit

# Audit entire project with all available checkers
results = audit(".")

# Audit with specific checks only
results = audit(".", checks=["python", "shell"])

# Write JSON report to disk
results = audit(".", output_file="security_report.json")

# Check results
print(results["python"]["status"])   # "ok", "findings", "skipped", or "error"
print(results["python"]["summary"])  # human-readable summary
```

## Supported Check Keys

- `"python"` — bandit static analysis
- `"shell"` — shellcheck for `.sh` files
- `"deps"` — pip-audit for CVE vulnerabilities
- `"github"` — GitHub security alerts (requires `gh` CLI)
