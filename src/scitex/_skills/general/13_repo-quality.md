---
name: repository-quality
description: Repository quality checklist for SciTeX packages — AGPL, Four Freedoms, _builtin_handlers.py verification, skills authoritative.
---

> General patterns: see [programming-common/repository-quality.md](../../commands/.claude/skills/programming-common/repository-quality.md)

# Repository Quality (SciTeX)

## SciTeX-Specific README Rules

- **"Part of SciTeX" section** with Four Freedoms blockquote
- **Use `import scitex`** (not `import scitex as stx`) in all examples
- **Footer**: SciTeX icon only — do NOT include `ywatanabe@scitex.ai` (community project)

## Licensing

- AGPL v3.0 (required for SciTeX ecosystem packages)
- CLA.md + CONTRIBUTING.md

## Documentation Accuracy (SciTeX-Specific)

- **Verify format claims against `_builtin_handlers.py`** — if a format is listed as supported, its handler must be registered. Unregistered loaders (e.g., `_load_parquet` defined but not in `_LOADER_MAP`) are NOT supported
- **Skills are authoritative for AI agents** — keep `_skills/` as single source of truth via dotfiles symlinks

## GitHub Setup (SciTeX Packages)

- Add `scitex` keyword as a topic for ecosystem discoverability
- CLA workflow with `allowlist: bot*,ywatanabe1989`
