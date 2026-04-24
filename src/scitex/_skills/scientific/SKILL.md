---
name: scientific
description: Scientific-methodology skills for the SciTeX ecosystem — publication-quality figures, statistics, experiment reproducibility. Distinct from `general/` (which covers package engineering) and per-package skills (which cover package-specific APIs). Load when authoring analysis scripts, preparing figures for manuscripts, or checking scientific rigour of ecosystem output.
user-invocable: false
primary_interface: mixed
group: [scitex-python, scitex-scientific, scitex-package, research, paper]
invocation:
  - "how should my figure look for a paper"
  - "comparison plot rules"
  - "multi-panel layout standards"
  - "PDF report layout"
  - "which stats test should I use"
context_tokens_total: 1200
canonical-location: scitex-python/src/scitex/_skills/scientific/SKILL.md
---

# SciTeX Scientific Standards

`pip install scitex` — scientific-methodology conventions shared across every ecosystem package that produces research artefacts.

These complement (never duplicate) the engineering rules in [../general/SKILL.md](../general/SKILL.md). General covers *how a package is built*; scientific covers *how the research outputs should look*.

## Sub-skills

### 1. Figures
- [01_figures_01_standards.md](01_figures_01_standards.md) — Universal scientific-figure standards: comparison rules (shared color scale, aligned axes), multi-panel layout, color maps, PDF report layout. Pairs with `figrecipe/21_scientific-figure-patterns.md` for matplotlib code.
