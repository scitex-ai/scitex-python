---
name: repository-quality
description: Release-gate repository quality checklist for every SciTeX package — AGPL-3.0-or-later licence + the Four Freedoms, README rules (no `import scitex as stx`, no trailing ywatanabe@ signature), `_builtin_handlers.py`/fallback-verification hygiene, skills-authoritative rule (no out-of-band docs in `docs/` duplicating `_skills/`), GitHub repo config (topics, default branch, branch protection), and allowlist checks before `git push` / PyPI release. Use as the final sign-off before any `vb release`.
canonical-location: scitex-python/src/scitex/_skills/general/02_repo_04_quality.md
tags: [scitex-python, scitex-general, scitex-package, meta]
---

# Repository Quality (SciTeX)

## SciTeX-Specific README Rules

- **"Part of SciTeX" section** with Four Freedoms blockquote
- **Use `import scitex`** (not `import scitex as stx`) in all examples
- **Footer**: SciTeX icon only — do NOT include `ywatanabe@scitex.ai` (community project)

## Licensing

- AGPL v3.0 (required for SciTeX ecosystem packages)
- CLA.md + CONTRIBUTING.md

## Documentation Accuracy (SciTeX-Specific)

- **Verify documentation claims against the source of truth in the package, not just the README.** For each claim (supported formats, available flags, registered tools), open the actual registration/dispatch code in `src/` and confirm the claim matches.
- **Skills are authoritative for AI agents** — keep `src/<pkg>/_skills/` as the single source of truth; exported copies under `~/.claude/skills/scitex/<pkg>/` are refreshed via `scitex-dev skills export`.

## GitHub Setup (SciTeX Packages)

- Add `scitex` keyword as a topic for ecosystem discoverability
- CLA workflow with `allowlist: bot*,ywatanabe1989`
