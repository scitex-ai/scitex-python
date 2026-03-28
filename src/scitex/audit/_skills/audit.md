---
description: Run security scans across Python code (bandit), shell scripts (shellcheck), dependencies (pip-audit), and GitHub alerts in a single call with audit().
---

# Audit Pipeline

## audit

Run security checks against a target directory or path.

```python
audit(
    path: str = ".",
    checks: list[str] | None = None,  # default: all
) -> dict
```

Available check names: `"python"` (bandit), `"shell"` (shellcheck), `"deps"` (pip-audit), `"github"` (GitHub alerts).

Returns a dict with one key per check type, each containing a list of finding dicts.

```python
from scitex.audit import audit

# Run all checks
results = audit(".")
print(results.keys())
# dict_keys(['python', 'shell', 'deps', 'github'])

# Run subset
results = audit(".", checks=["python", "deps"])

# Check for critical issues
for check, findings in results.items():
    if findings:
        print(f"{check}: {len(findings)} finding(s)")
        for f in findings:
            print(" ", f["severity"], f["summary"])
```

## CLI usage

```bash
# Via scitex CLI
scitex audit .
scitex audit . --checks python shell
```

## Individual runners (internal API)

The following are used internally by `audit()`:

| Function | Tool | Purpose |
|----------|------|---------|
| `_bandit.run_bandit(path)` | bandit | Python static analysis |
| `_shellcheck.run_shellcheck(path)` | shellcheck | Shell script analysis |
| `_pip_audit.run_pip_audit()` | pip-audit | Dependency vulnerability scan |
| `_github.run_github_audit()` | gh CLI | GitHub security alerts |
