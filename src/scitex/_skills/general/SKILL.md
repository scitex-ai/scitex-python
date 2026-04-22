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
- [01_four-interfaces.md](01_four-interfaces.md) — Overview and delegation chain
- [02_interface-python-api.md](02_interface-python-api.md) — Minimal API, `__all__`, hide internals, PyPI first publish
- [03_interface-cli.md](03_interface-cli.md) — Required sub-commands, flags, AI-friendly rules, Click patterns
- [04_interface-mcp.md](04_interface-mcp.md) — fastmcp, tool naming, reproducibility, standard commands
- [05_interface-skills.md](05_interface-skills.md) — `_skills/` layout, no-monolith, registration, export
- [06_interface-http-api.md](06_interface-http-api.md) — Optional FastAPI delegation

### Skill Authoring Guides
- [07_skills.md](07_skills.md) — Practical guide for writing skills: lessons learned, workflow, quality checklist
- [08_how-to-update-skills.md](08_how-to-update-skills.md) — Source-of-truth locations, editable vs non-editable paths, export workflow
- [09_skills-public-vs-private.md](09_skills-public-vs-private.md) — Where a skill belongs: shipped with the package vs `~/.scitex/<pkg>/`

### Repository Standards
- [10_readme-organization.md](10_readme-organization.md) — Standard README template, sections, badges, footer
- [11_sphinx-organization.md](11_sphinx-organization.md) — Sphinx docs, conf.py, RTD config, troubleshooting
- [12_github-actions.md](12_github-actions.md) — CI, PyPI publish, CLA, reusable workflow patterns
- [13_repository-quality.md](13_repository-quality.md) — Quality checklist, documentation accuracy, GitHub setup

### Architecture
- [14_upstream-and-downstream-packages.md](14_upstream-and-downstream-packages.md) — 3-layer cascade architecture
- [15_version-management.md](15_version-management.md) — Version sync across ecosystem
- [16_environment-variables.md](16_environment-variables.md) — `SCITEX_<MODULE_NAME>_*` prefix rule for env vars
- [17_blanding.md](17_blanding.md) — Brand logo and CSS rules

### Lessons & Scratch
- [18_standalonization.md](18_standalonization.md) — Lessons from splitting packages into standalones
- [19_src-vs-tests-vs-scripts.md](19_src-vs-tests-vs-scripts.md) — Layout boundaries between `src/`, `tests/`, `scripts/`
- [20_playground.md](20_playground.md) — Scratch notes

### Quality Gates
- [21_scitex-package-quality-checklist.md](21_scitex-package-quality-checklist.md) — Release-gate checklist for `_skills/` directories (naming, indexing, no-monolith, no-duplication, cache hygiene) + 2026-04-23 remediation snapshot
