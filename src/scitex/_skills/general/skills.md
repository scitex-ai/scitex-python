---
name: skills
description: Practical guide for writing and maintaining skills for SciTeX packages — lessons learned, workflow, and quality checklist.
---

> Structure rules: see [interface-skills.md](interface-skills.md)

# Writing Skills for SciTeX Packages

Practical lessons from building skills for scitex-io and scitex general.

## Workflow

```bash
# 1. Investigate the codebase first
#    Read _builtin_handlers.py, __init__.py, _save.py — not just README
#    Claims in docs must match actual registered handlers

# 2. Write to dotfiles (single source of truth)
~/.dotfiles/src/.claude/to_claude/skills/scitex/<pip-name>/

# 3. Copy to repo _skills/ (real files, no symlinks — wheels can't follow symlinks)
cp -rf ~/.dotfiles/.../scitex/<pip-name>/* ~/proj/<repo>/src/<pkg>/_skills/<pip-name>/

# 4. Update pyproject.toml if first time
[tool.hatch.build.targets.wheel.force-include]
"src/<pkg>/_skills" = "<pkg>/_skills"
```

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

When you find a discrepancy (e.g., README says "Three Interfaces" but skills say four), fix all three:
- `README.md`
- `docs/sphinx/*.rst`
- `_skills/<pip-name>/*.md`

### 5. Separate general from SciTeX-specific

Skills that apply to any Python package go in `programming-common/`:
- readme-organization, sphinx-organization, github-actions
- interface-python-api, interface-cli, interface-mcp
- repository-quality, no-fallbacks, no-false-positives

SciTeX-specific files cross-reference the general ones:
```markdown
> General patterns: see [programming-common/interface-cli.md](...)

# CLI Commands (SciTeX)
[Only SciTeX-specific content: scitex-io examples, scitex-dev helpers]
```

### 6. Real files for packages, not symlinks

Symlinks break in Python wheels. Always use real file copies in `_skills/`:
```bash
# WRONG (breaks in pip install)
ln -s ~/.dotfiles/.../scitex-io _skills/scitex-io

# RIGHT (works in pip install)
cp -rf ~/.dotfiles/.../scitex-io/* _skills/scitex-io/
```

## Reference Implementation

**scitex-io** (`~/proj/scitex-io/src/scitex_io/_skills/scitex-io/`) is the reference:
- 9 focused sub-skill files, no monolith
- SKILL.md is index-only with MCP tools table and CLI summary
- Each sub-skill verified against `_builtin_handlers.py` and `_save.py`
- Consistent with README.md and `docs/sphinx/` (Four Interfaces, format tables)
- Real files (not symlinks), bundled via `pyproject.toml` force-include

## Quality Checklist

- [ ] SKILL.md is index-only (no content blocks)
- [ ] Each sub-skill has frontmatter (name, description)
- [ ] All format/feature claims verified against `_builtin_handlers.py` or source
- [ ] Actual code examples (not pseudo-code)
- [ ] Function signatures match current source
- [ ] MCP tools table in SKILL.md
- [ ] CLI summary in SKILL.md
- [ ] Consistent with README and Sphinx docs
- [ ] No SciTeX-specific content in programming-common files
- [ ] Real files in `_skills/`, not symlinks
