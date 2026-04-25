---
name: general
description: Canonical engineering standards every `scitex-*` package and research project must follow — 3-layer architecture cascade, dependency/version pinning, local-state directory layout (`~/.scitex/<pkg-short>/` and `<project>/.scitex/<pkg-short>/`), repo layout (src/tests/scripts/examples), the five interfaces (Python API → CLI → MCP → Skills → optional HTTP) with their delegation rules and the noun-verb CLI convention, README/Sphinx docs, version-control workflow plus `scitex-dev ecosystem …` release automation, skill-authoring rules (layout, editable-vs-wheel install, public-vs-private), and the periodic quality checklist. Use as the single entry point for creating, auditing, reviewing, or releasing any SciTeX package.
user-invocable: false
primary_interface: mixed
interfaces:
  python: 3
  cli: 2
  mcp: 2
  skills: 3
  hook: 0
  http: 0
tags: [scitex-python, scitex-general, scitex-package]
invocation:
  - "how do I structure a scitex package"
  - "noun-verb CLI convention"
  - "what's the release workflow"
  - "where does config live"
  - "skills directory layout"
  - "AGPL license rules"
  - "PathManager SCITEX_DIR"
context_tokens_total: 41400
canonical-location: scitex-python/src/scitex/_skills/general/SKILL.md
---

# SciTeX General Standards

> **Interfaces:** Python ⭐⭐⭐ · CLI ⭐⭐ · MCP ⭐⭐ · Skills ⭐⭐⭐ · Hook — · HTTP —

`pip install scitex` — standards for all ecosystem packages.

## Sub-skills

Read in this order when building or auditing a package. Each section presupposes the ones above it.

### 1. Architecture — what does this package *exist as*?
- [01_arch_01_upstream-and-downstream.md](01_arch_01_upstream-and-downstream.md) — 3-layer cascade, test scope, cascade pattern
- [01_arch_02_dependency-and-version-pinning.md](01_arch_02_dependency-and-version-pinning.md) — Dependency hygiene, optional extras, version-pinning rules
- [01_arch_03_modules-and-standalone-packages.md](01_arch_03_modules-and-standalone-packages.md) — Module vs standalone package boundaries
- [01_arch_04_environment-variables.md](01_arch_04_environment-variables.md) — `SCITEX_<MODULE_NAME>_*` prefix rule; mandates per-package `NN_env-vars.md` leaf
- [01_arch_05_re-export.md](01_arch_05_re-export.md) — Umbrella `scitex.<name>` thin-re-export pattern + lazy-import guard
- [01_arch_06_local-state-directories.md](01_arch_06_local-state-directories.md) — `<project>/.scitex/<pkg-short>/` + `~/.scitex/<pkg-short>/` layout, precedence, `SCITEX_DIR`, `PathManager`

### 2. Repository — how does the code live on disk?
- [02_repo_01_layout-src-tests-scripts-examples.md](02_repo_01_layout-src-tests-scripts-examples.md) — Layout boundaries between `src/`, `tests/`, `scripts/`, `examples/`, `references/`
- [02_repo_02_config-and-parameters.md](02_repo_02_config-and-parameters.md) — `@stx.session` and the `CONFIG` object (SDIR_OUT, SDIR_RUN, YAML merging)
- [02_repo_03_github-actions.md](02_repo_03_github-actions.md) — CI, PyPI publish, CLA, reusable workflow patterns
- [02_repo_04_quality.md](02_repo_04_quality.md) — Repository-level quality (AGPL, Four Freedoms, README rules, GitHub setup)

### 3. Interfaces — how do users and agents touch the package?
- [03_interface_00_overview.md](03_interface_00_overview.md) — Five interfaces: overview and delegation chain
- [03_interface_01_python-api.md](03_interface_01_python-api.md) — Minimal API, `__all__`, hide internals, PyPI first publish
- [03_interface_02_cli.md](03_interface_02_cli.md) — Required sub-commands, flags, noun-verb convention, AI-friendly rules
- [03_interface_03_mcp.md](03_interface_03_mcp.md) — fastmcp, tool naming, reproducibility, standard commands
- [03_interface_04_skills.md](03_interface_04_skills.md) — `_skills/` layout, no-monolith, registration, export
- [03_interface_05_http-api.md](03_interface_05_http-api.md) — Optional FastAPI delegation

### 4. Documentation — how does the package become understandable?
- [04_docs_01_readme.md](04_docs_01_readme.md) — Standard README template, sections, badges, footer
- [04_docs_02_sphinx.md](04_docs_02_sphinx.md) — Sphinx docs, conf.py, RTD config, troubleshooting

### 5. Version Control — how does it ship?
- [05_version-control_01_management.md](05_version-control_01_management.md) — Branches, tags, release waves, release gates (core workflow)
- [05_version-control_02_release-automation.md](05_version-control_02_release-automation.md) — Automation commands, ecosystem sync CLI, MCP tools, Python API

### 6. Skill Authoring — meta: how do we write these rules themselves?
- [06_skills_01_overview.md](06_skills_01_overview.md) — Practical guide for writing skills: lessons learned, workflow
- [06_skills_02_how-to-update.md](06_skills_02_how-to-update.md) — Source-of-truth locations, editable vs non-editable paths, export workflow
- [06_skills_03_public-vs-private.md](06_skills_03_public-vs-private.md) — Where a skill belongs: shipped with the package vs `~/.scitex/<pkg>/`
- [06_skills_04_editable-installation.md](06_skills_04_editable-installation.md) — Skill source resolution: editable install symlinks to `src/`, wheel install reads bundled copy
- [06_skills_05_quality-checklist.md](06_skills_05_quality-checklist.md) — Release-gate checklist for `_skills/` directories
- [06_skills_06_frontmatter-metadata.md](06_skills_06_frontmatter-metadata.md) — Optional YAML fields: `group`, `invocation`, `context_tokens`, `canonical-location`, `see-also`

### 7. Periodic ecosystem quality — run when something feels off
- [98_quality_01_failure-playbook.md](98_quality_01_failure-playbook.md) — Severity-tagged cookbook of ecosystem failure modes
- [99_quality_02_checklist.md](99_quality_02_checklist.md) — Strategic /speak-and-call runbook with append-only log

### Scratch
- [40_playground.md](40_playground.md) — Scratch notes
