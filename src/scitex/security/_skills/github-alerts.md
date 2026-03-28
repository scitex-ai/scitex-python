---
description: Fetch, format, and save GitHub secret scanning, Dependabot, and code scanning alerts using the gh CLI.
---

# stx.security — GitHub Security Alerts

`stx.security` uses the GitHub CLI (`gh`) to aggregate three alert types for a repository.

## check_github_alerts

Fetch all open security alerts (secret scanning + Dependabot + code scanning) for a repo.

```python
from scitex.security import check_github_alerts, GitHubSecurityError

try:
    alerts = check_github_alerts()        # uses current repo
    alerts = check_github_alerts(repo="owner/repo")  # explicit repo
except GitHubSecurityError as e:
    print(f"Could not fetch: {e}")        # gh not installed or not authenticated

if alerts:
    print(f"Found {len(alerts)} security alerts")
else:
    print("No open alerts")
```

Returns a list of dicts. Each alert has at minimum:
- `state` — alert state (e.g., `"open"`)
- `url` — link to the alert on GitHub
- `created_at` — ISO timestamp

Additional fields vary by alert type:
- Secret scanning: `secretType`, `path`, `line`
- Dependabot: `severity`, `summary`, `package`, `cve`
- Code scanning: `severity`, `description`, `location`, `line`

`GitHubSecurityError` is raised when `gh` is not installed or not authenticated.

## format_alerts_report

Format a list of alerts into a human-readable text report.

```python
from scitex.security import check_github_alerts, format_alerts_report

alerts = check_github_alerts()
report = format_alerts_report(alerts)
print(report)
```

## save_alerts_to_file / get_latest_alerts_file

Persist alerts to a JSON file and retrieve the most recent saved file.

```python
from scitex.security import (
    check_github_alerts, save_alerts_to_file, get_latest_alerts_file
)

alerts = check_github_alerts()
save_alerts_to_file(alerts, "security_report.json")

latest = get_latest_alerts_file()
print(latest)   # Path to most recent saved alerts file
```

## CLI

```bash
# Requires gh CLI authenticated (gh auth login)
python -m scitex.security check
python -m scitex.security check --repo owner/repo
```

Internally calls `check_github_alerts()` and prints a formatted report.
