---
name: sphinx-organization
description: Canonical Sphinx documentation layout for every SciTeX package — `docs/source/` tree, required `conf.py` patterns (theme = sphinx_rtd_theme, autodoc, myst-parser, autodoc-typehints, copybutton), `.readthedocs.yaml` for RTD builds, version-switcher, RTD build-status checks, and common troubleshooting (empty autodoc, broken myst include, RTD failing on `import scitex`). Use when setting up RTD for a new package or fixing a failing Read the Docs build.
canonical-location: scitex-python/src/scitex/_skills/general/04_docs_02_sphinx.md
---

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

## Five Interfaces Table (index.rst Rule)

SciTeX packages must include a five-interfaces table in `index.rst` (HTTP API is optional and included only when the package exposes web endpoints):

| Interface | Description |
|-----------|-------------|
| Python API | `import scitex_io` |
| CLI | `scitex-io <command>` |
| MCP | AI agent tools via fastmcp |
| Skills | AI agent knowledge pages |
| HTTP API (optional) | FastAPI endpoints for web clients |

## RTD Reference Implementations

- `~/proj/figrecipe` — working RTD setup
- `~/proj/scitex-writer` — working RTD setup

## SciTeX-Specific Rules

- **Five interfaces table** in index.rst: Python API, CLI, MCP, Skills, plus HTTP API when applicable
- **Use `develop` branch** as github_version for "Edit on GitHub" links
- **Exclude `to_claude/`** from Sphinx builds
- `api/scitex_io.rst` — follow scitex-io naming pattern for API doc files
