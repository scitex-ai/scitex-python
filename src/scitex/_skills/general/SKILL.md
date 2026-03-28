---
name: scitex-general
description: SciTeX ecosystem general standards — branding, package architecture, four interfaces, version management, and repository quality. Use when creating, auditing, or maintaining any SciTeX package.
user-invocable: false
---

# SciTeX General Standards

## Installation

```bash
pip install scitex
# Development:
pip install -e /home/ywatanabe/proj/scitex-code
```

Core standards that apply to ALL SciTeX ecosystem packages.

## Sub-skills

### Four Interfaces
- [four-interfaces.md](four-interfaces.md) — Overview and delegation chain
- [interface-python-api.md](interface-python-api.md) — Minimal API, `__all__`, hide internals, PyPI first publish
- [interface-cli.md](interface-cli.md) — Required sub-commands, flags, AI-friendly rules, Click patterns
- [interface-mcp.md](interface-mcp.md) — fastmcp, tool naming, reproducibility, standard commands
- [interface-skills.md](interface-skills.md) — `_skills/` layout, no-monolith, registration, export
- [interface-http-api.md](interface-http-api.md) — Optional FastAPI delegation

### Guides
- [skills.md](skills.md) — Practical guide for writing skills: lessons learned, workflow, quality checklist
- [how-to-update-skills.md](how-to-update-skills.md) — Source-of-truth locations, editable vs non-editable paths, export workflow

### Repository Standards
- [readme-organization.md](readme-organization.md) — Standard README template, sections, badges, footer
- [sphinx-organization.md](sphinx-organization.md) — Sphinx docs, conf.py, RTD config, troubleshooting
- [github-actions.md](github-actions.md) — CI, PyPI publish, CLA, reusable workflow patterns
- [repository-quality.md](repository-quality.md) — Quality checklist, documentation accuracy, GitHub setup

### Architecture
- [upstream-and-downstream-packages.md](upstream-and-downstream-packages.md) — 3-layer cascade architecture
- [version-management.md](version-management.md) — Version sync across ecosystem
- [blanding.md](blanding.md) — Brand logo and CSS rules
- [environment-variables.md](environment-variables.md) — `SCITEX_<MODULE_NAME>_*` prefix rule for env vars
