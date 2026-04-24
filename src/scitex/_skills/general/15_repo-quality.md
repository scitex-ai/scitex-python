---
name: repository-quality
description: Repository quality checklist for SciTeX packages — AGPL, Four Freedoms, _builtin_handlers.py verification, skills authoritative.
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
