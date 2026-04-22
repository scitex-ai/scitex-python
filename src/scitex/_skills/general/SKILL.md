---
name: scitex-general
description: SciTeX ecosystem general standards — branding, package architecture, five interfaces, version management, and repository quality. Use when creating, auditing, or maintaining any SciTeX package.
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

### Interfaces
- [01_interfaces-overview.md](01_interfaces-overview.md) — Five interfaces: overview and delegation chain
- [02_interface-python-api.md](02_interface-python-api.md) — Minimal API, `__all__`, hide internals, PyPI first publish
- [03_interface-cli.md](03_interface-cli.md) — Required sub-commands, flags, AI-friendly rules, Click patterns
- [04_interface-mcp.md](04_interface-mcp.md) — fastmcp, tool naming, reproducibility, standard commands
- [05_interface-skills.md](05_interface-skills.md) — `_skills/` layout, no-monolith, registration, export
- [06_interface-http-api.md](06_interface-http-api.md) — Optional FastAPI delegation

### Architecture
- [07_arch-upstream-and-downstream.md](07_arch-upstream-and-downstream.md) — 3-layer cascade, test scope, dependency hygiene, version pinning
- [08_arch-modules-and-standalone-packages.md](08_arch-modules-and-standalone-packages.md) — Module vs standalone package boundaries
- [09_arch-environment-variables.md](09_arch-environment-variables.md) — `SCITEX_<MODULE_NAME>_*` prefix rule

### Version Control
- [10_version-control-management.md](10_version-control-management.md) — Version sync across ecosystem, tagging, release waves

### Repository
- [11_repo-layout-src-tests-scripts-examples.md](11_repo-layout-src-tests-scripts-examples.md) — Layout boundaries between `src/`, `tests/`, `scripts/`, `examples/`, `references/`
- [12_repo-github-actions.md](12_repo-github-actions.md) — CI, PyPI publish, CLA, reusable workflow patterns
- [13_repo-quality.md](13_repo-quality.md) — Repository-level quality (AGPL, Four Freedoms, README rules, GitHub setup)
- [14_repo-brand-logo-and-css.md](14_repo-brand-logo-and-css.md) — Brand logo and CSS rules

### Documentation
- [15_docs-readme.md](15_docs-readme.md) — Standard README template, sections, badges, footer
- [16_docs-sphinx.md](16_docs-sphinx.md) — Sphinx docs, conf.py, RTD config, troubleshooting

### Skill Authoring
- [17_skills-overview.md](17_skills-overview.md) — Practical guide for writing skills: lessons learned, workflow
- [18_skills-how-to-update.md](18_skills-how-to-update.md) — Source-of-truth locations, editable vs non-editable paths, export workflow
- [19_skills-public-vs-private.md](19_skills-public-vs-private.md) — Where a skill belongs: shipped with the package vs `~/.scitex/<pkg>/`
- [20_skills-quality-checklist.md](20_skills-quality-checklist.md) — Release-gate checklist for `_skills/` directories (naming, indexing, no-monolith, no-duplication, cache hygiene)

### Scratch
- [21_playground.md](21_playground.md) — Scratch notes
