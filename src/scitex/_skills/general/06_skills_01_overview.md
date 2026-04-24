---
name: skills
description: Practical author's guide for writing and maintaining `_skills/` content in every SciTeX package — what a "skill" is in the Claude Code sense (an agent-loadable rule file, not a dev doc), the SKILL.md-as-index pattern, leaf-file scope (one topic per `.md`), prose over checkboxes, the two-level `NN_<category>_NN_<topic>.md` numbering rule, lessons from past audits (audit-driven remediation), and the authoring workflow from idea → draft → export → commit. Use when writing any new skill or overhauling an existing one.
---

> Structure rules: see [03_interface_04_skills.md](03_interface_04_skills.md)

# Writing Skills for SciTeX Packages

Practical lessons from building skills for scitex-io and scitex general.

## Workflow

Source of truth lives in the package source. Dotfiles / `~/.claude/skills/scitex/` copies are **auto-generated exports** — never edit them directly (a pre-tool-use hook blocks such edits).

```bash
# 1. Investigate the codebase first
#    Read _builtin_handlers.py, __init__.py, _save.py — not just README
#    Claims in docs must match actual registered handlers

# 2. Edit in the package source (single source of truth)
vi ~/proj/<repo>/src/<pkg>/_skills/<pip-name>/<file>.md

# 3. Export to ~/.claude/skills/scitex/<pip-name>/
scitex-dev skills export --package <pip-name>
```

Do NOT add `[tool.hatch.build.targets.wheel.force-include]` for `_skills/` — hatch already includes files under `src/<pkg>/` in the wheel. See [03_interface_04_skills.md](03_interface_04_skills.md).

## Lessons Learned

### 1. No monolith SKILL.md

SKILL.md is an **index only** — links to sub-skills, MCP tools table, CLI summary. All content in separate focused files.

Bad:
```
_skills/scitex-io/
  SKILL.md          # 120 lines of everything
```

Good:
```
_skills/scitex-io/
  SKILL.md              # 40 lines: index + links
  save-and-load.md      # Focused: signatures, path routing, symlinks
  centralized-config.md # Focused: load_configs, DotDict, DEBUG_
  supported-formats.md  # Reference table from _builtin_handlers.py
  cache.md              # Focused: caching, reload, flush
  glob.md               # Focused: natural sort, parse_glob
  ...
```

### 2. Investigate before documenting

The old `formats.md` listed `.parquet` and `.feather` as supported — but they were **not registered** in `_builtin_handlers.py`. A `_load_parquet` function existed but was never added to `_LOADER_MAP`.

**Always verify against actual source code:**
- Check `_builtin_handlers.py` for registered formats
- Check `__init__.py` for exported functions
- Check `_save.py` / `_load.py` for actual signatures and behavior
- Run small experiments if uncertain

### 3. Cover main features with actual examples

Each sub-skill file must show:
- **Actual function signatures** (from source, not memory)
- **Real code examples** that would run
- **Edge cases** (e.g., `use_caller_path` — when wrappers break path routing)
- **Tables** for structured data (path routing contexts, format support)

Example — `save-and-load.md` covers:
```
save() signature with all 9 parameters
Auto path routing table (Script/Jupyter/Interactive/Absolute)
use_caller_path — why wrappers need it, with before/after
symlink_from_cwd — creates symlink from cwd to saved file
symlink_to — creates symlink at explicit path
no_csv — skip auto CSV export for images
dry_run — preview resolved path
f-string paths — evaluated with caller's variables
load() signature, glob support, caching
Two-tier registry — decorator and direct form
```

### 4. Keep consistent across README, Sphinx, and skills

When you find a discrepancy (e.g., README says "Four Interfaces" but skills say five), fix all three:
- `README.md`
- `docs/sphinx/*.rst`
- `_skills/<pip-name>/*.md`

### 5. Real files in packages, not symlinks

Symlinks break in Python wheels. The package directory `src/<pkg>/_skills/<pip-name>/` must contain real files so they bundle into the wheel. Export copies (`~/.claude/skills/scitex/<pip-name>/`) are refreshed via `scitex-dev skills export`.

## Reference Implementation

**scitex-io** (`~/proj/scitex-io/src/scitex_io/_skills/scitex-io/`) is the reference:
- 9 focused sub-skill files, no monolith
- SKILL.md is index-only with MCP tools table and CLI summary
- Each sub-skill verified against `_builtin_handlers.py` and `_save.py`
- Consistent with README.md and `docs/sphinx/` (Five Interfaces with HTTP optional, format tables)
- Real files (not symlinks) bundled by hatch under `src/<pkg>/_skills/`

## Quality Checklist

- [ ] SKILL.md is index-only (no content blocks)
- [ ] Each sub-skill has frontmatter (name, description)
- [ ] All format/feature claims verified against `_builtin_handlers.py` or source
- [ ] Actual code examples (not pseudo-code)
- [ ] Function signatures match current source
- [ ] MCP tools table in SKILL.md
- [ ] CLI summary in SKILL.md
- [ ] Consistent with README and Sphinx docs
- [ ] No cross-ecosystem generic rules restated inside a package skill (link to `general/` instead)
- [ ] Real files in `_skills/`, not symlinks
