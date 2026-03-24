---
name: sphinx-organization
description: Standard Sphinx documentation structure, conf.py patterns, and Read the Docs configuration for SciTeX packages.
---

> General patterns: see [programming-common/sphinx-organization.md](../../commands/.claude/skills/programming-common/sphinx-organization.md)

# Sphinx & Read the Docs Organization (SciTeX)

## SciTeX-Specific conf.py Settings

```python
# Version auto-detection — use the package name
try:
    from importlib.metadata import version as _get_version
    release = _get_version("scitex-io")   # replace with actual package name
except Exception:
    release = "0.1.0"

# GitHub "Edit on GitHub" link — always ywatanabe1989
html_context = {
    "display_github": True,
    "github_user": "ywatanabe1989",
    "github_repo": "scitex-io",           # replace with actual repo name
    "github_version": "develop",
    "conf_py_path": "/docs/sphinx/",
}
```

## Four Interfaces Table (index.rst Rule)

SciTeX packages must include a four-interfaces table in `index.rst`:

| Interface | Description |
|-----------|-------------|
| Python API | `import scitex_io` |
| CLI | `scitex-io <command>` |
| MCP | AI agent tools via fastmcp |
| Skills | AI agent knowledge pages |

## RTD Reference Implementations

- `~/proj/figrecipe` — working RTD setup
- `~/proj/scitex-writer` — working RTD setup

## SciTeX-Specific Rules

- **Four interfaces table** in index.rst: Python API, CLI, MCP, Skills
- **Use `develop` branch** as github_version for "Edit on GitHub" links
- **Exclude `to_claude/`** from Sphinx builds
- `api/scitex_io.rst` — follow scitex-io naming pattern for API doc files
