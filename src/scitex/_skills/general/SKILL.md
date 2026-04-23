---
name: general
description: SciTeX ecosystem general standards — branding, package architecture, five interfaces, version management, and repository quality. Use when creating, auditing, or maintaining any SciTeX package.
user-invocable: false
primary_interface: mixed
interfaces:
  python: 3
  cli: 2
  mcp: 2
  skills: 3
  hook: 0
  http: 0
---

# SciTeX General Standards

> **Interfaces:** Python ⭐⭐⭐ · CLI ⭐⭐ · MCP ⭐⭐ · Skills ⭐⭐⭐ · Hook — · HTTP —

## Installation

```bash
pip install scitex
# Development:
pip install -e /home/ywatanabe/proj/scitex-python
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
- [07_arch-upstream-and-downstream.md](07_arch-upstream-and-downstream.md) — 3-layer cascade, test scope, cascade pattern
- [08_arch-dependency-and-version-pinning.md](08_arch-dependency-and-version-pinning.md) — Dependency hygiene, optional extras, version-pinning rules
- [09_arch-modules-and-standalone-packages.md](09_arch-modules-and-standalone-packages.md) — Module vs standalone package boundaries
- [10_arch-environment-variables.md](10_arch-environment-variables.md) — `SCITEX_<MODULE_NAME>_*` prefix rule

### Version Control
- [11_version-control-management.md](11_version-control-management.md) — Branches, tags, release waves, release gates (core workflow)
- [12_version-control-release-automation.md](12_version-control-release-automation.md) — Automation commands, ecosystem sync CLI, MCP tools, Python API

### Repository
- [13_repo-layout-src-tests-scripts-examples.md](13_repo-layout-src-tests-scripts-examples.md) — Layout boundaries between `src/`, `tests/`, `scripts/`, `examples/`, `references/`
- [14_repo-github-actions.md](14_repo-github-actions.md) — CI, PyPI publish, CLA, reusable workflow patterns
- [15_repo-quality.md](15_repo-quality.md) — Repository-level quality (AGPL, Four Freedoms, README rules, GitHub setup)
- [16_repo-brand-logo-and-css.md](16_repo-brand-logo-and-css.md) — Brand logo and CSS rules

### Documentation
- [17_docs-readme.md](17_docs-readme.md) — Standard README template, sections, badges, footer
- [18_docs-sphinx.md](18_docs-sphinx.md) — Sphinx docs, conf.py, RTD config, troubleshooting

### Skill Authoring
- [19_skills-overview.md](19_skills-overview.md) — Practical guide for writing skills: lessons learned, workflow
- [20_skills-how-to-update.md](20_skills-how-to-update.md) — Source-of-truth locations, editable vs non-editable paths, export workflow
- [21_skills-public-vs-private.md](21_skills-public-vs-private.md) — Where a skill belongs: shipped with the package vs `~/.scitex/<pkg>/`
- [22_skills-quality-checklist.md](22_skills-quality-checklist.md) — Release-gate checklist for `_skills/` directories (naming, indexing, no-monolith, no-duplication, cache hygiene)

### Logs
- [23_remediation-log.md](23_remediation-log.md) — Dated remediation log for audit findings
- [24_package-gaps-2026-04-23.md](24_package-gaps-2026-04-23.md) — Package-gap audit snapshot

### Session
- [25_session-config.md](25_session-config.md) — `@stx.session` and the `CONFIG` object (SDIR_OUT, SDIR_RUN, YAML merging)

### Scratch
- [40_playground.md](40_playground.md) — Scratch notes
