# Security Scanning with stx.audit

The `audit()` function orchestrates four security checkers in a single call. It discovers which tools are installed on the system and skips unavailable ones gracefully rather than failing.

## Checker Categories

| Check key | Tool required | What it scans |
|-----------|--------------|---------------|
| `"python"` | `bandit` | Python static analysis for security issues |
| `"shell"` | `shellcheck` | Shell script linting |
| `"deps"` | `pip-audit` | Dependency vulnerabilities (CVE lookup) |
| `"github"` | `gh` CLI + auth | GitHub security alerts for the current repo |

## Basic Usage

```python
from scitex.audit import audit

# Scan everything under current directory with all available checkers
results = audit(".")

# Only run Python and dependency checks
results = audit("./src", checks=["python", "deps"])

# Write a JSON report to disk
results = audit(".", output_file="security_report.json")
```

## Return Value Structure

Each key in the returned dict maps to `{status, findings, summary}`:

```python
results = audit(".")

# Status is one of: "ok", "findings", "skipped", "error"
print(results["python"]["status"])     # "findings"
print(results["python"]["summary"])    # "3 issues (0 high, 2 medium, 1 low)"

for f in results["python"]["findings"]:
    print(f["severity"], f["file"], f["line"], f["message"])

# Dependency vulnerabilities
for f in results["deps"]["findings"]:
    print(f["package"], f["version"], f["vuln_id"], f["fix_versions"])

# Shell check findings
for f in results["shell"]["findings"]:
    print(f["level"], f["file"], f["line"], f["message"])
```

## Individual Checker Details

### bandit (Python static analysis)
- Runs `bandit -r <path> -f json --exclude .venv,node_modules,__pycache__,.git`
- Finding fields: `severity` (HIGH/MEDIUM/LOW), `confidence`, `file`, `line`, `test_id`, `message`
- Exit code 1 from bandit means findings exist (not an error)

### shellcheck (Shell script analysis)
- Finds all `*.sh` files recursively, skipping `.venv`, `node_modules`, `.git`
- Finding fields: `level`, `file`, `line`, `code`, `message`

### pip-audit (Dependency vulnerabilities)
- Uses `requirements.txt` from the scanned directory if present; otherwise scans the current environment
- Finding fields: `package`, `version`, `vuln_id`, `description`, `fix_versions`

### GitHub security alerts
- Requires `gh` CLI installed and authenticated
- Delegates to `scitex.security.check_github_alerts(repo)`
- Finding fields: `category`, plus alert-specific fields

## Checking Tool Availability

```python
import shutil

# Check which tools are available before running
for tool in ["bandit", "shellcheck", "pip-audit", "gh"]:
    available = shutil.which(tool) is not None
    print(f"{tool}: {'available' if available else 'not installed'}")
```

## CLI Equivalent

```bash
scitex audit run .
scitex audit run ./src --checks python deps
```
