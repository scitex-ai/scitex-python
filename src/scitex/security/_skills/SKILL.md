---
name: stx.security
description: GitHub security alert aggregation — fetch secret scanning, Dependabot, and code scanning alerts via the gh CLI.
---

# stx.security — Skills Index

Aggregate and report GitHub security alerts (secret scanning, Dependabot, code scanning) for any repository.

## Sub-skills

| File | Description |
|------|-------------|
| [github-alerts.md](github-alerts.md) | check_github_alerts, format_alerts_report, save_alerts_to_file, get_latest_alerts_file, GitHubSecurityError, CLI |

## Quick Reference

```python
from scitex.security import check_github_alerts, format_alerts_report, GitHubSecurityError

try:
    alerts = check_github_alerts()
    print(format_alerts_report(alerts))
except GitHubSecurityError as e:
    print(e)
```

```bash
python -m scitex.security check
```
