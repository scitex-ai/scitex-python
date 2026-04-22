---
name: interface-skills
description: Skills system — _skills/ directory layout, SKILL.md format, no-monolith rule, registration, export.
---

# Skills System

Skills provide structured documentation for AI agents to discover package capabilities.

## Directory Layout

### Package-level (standalone pip packages)

```
src/<pkg>/_skills/<pip-name>/
  SKILL.md                # Required index (links only, no content)
  save-and-load.md        # Focused topic with actual examples
  centralized-config.md   # Focused topic with actual examples
  supported-formats.md    # Reference table
  ...
```

Legacy `src/<pkg>/skills/SKILL.md` still supported but `_skills/` preferred.

### Module-level (submodules within scitex-python)

Each public module under `src/scitex/<module>/` MUST have its own `_skills/` directory:

```
src/scitex/<module>/_skills/
  SKILL.md                # Required index — same format as package-level
  feature-topic.md        # Focused sub-skill (optional, add as needed)
  ...
```

**Rules for module-level skills:**
1. Every public module gets a `_skills/SKILL.md` — no exceptions
2. Real files only — **no symlinks** (files are bundled in wheels)
3. SKILL.md follows the same frontmatter format as package skills
4. `name` field uses `stx.<module>` format (e.g., `stx.ai`, `stx.stats`)
5. `description` is a one-line summary for AI agent discovery
6. List Python API, relevant MCP tools, and CLI commands if any
7. Sub-skill files are optional — add them when a module has complex features
8. Skip internal/private directories (`_dev`, `_mcp_tools`, `_mcp_resources`, `_sphinx_html`, `__pycache__`)

## No Monolith SKILL.md

SKILL.md is an **index file only**. Content goes in focused sub-skill files.

```markdown
---
name: scitex-io
description: Universal file I/O supporting 30+ formats. Use when loading or saving data.
allowed-tools: mcp__scitex__io_*
---

# scitex-io

Universal scientific data I/O with plugin registry.

## Sub-skills

* [save-and-load](save-and-load.md) — Core save/load API, registry
* [centralized-config](centralized-config.md) — load_configs() and DotDict
* [supported-formats](supported-formats.md) — All 30+ format tables

## MCP Tools

| Tool | Purpose |
|------|---------|
| `io_save` | Save data to file |
| `io_load` | Load data from file |

## CLI

scitex-io info data.csv
scitex-io skills list
```

## Sub-skill File Format

Each sub-skill covers one feature with actual code examples:

```markdown
---
name: save-and-load
description: Core save/load API with two-tier format registry.
---

# Save and Load

## save()

def save(obj, path, makedirs=True, ...):

[Actual function signature, parameters, behavior]

### Auto path routing

[Table showing context → output directory]

### use_caller_path

[When and why to use it, with before/after examples]

## load()

[Same pattern — signature, examples, edge cases]
```

**Rules for sub-skill files:**
1. Cover main features of that topic
2. Include actual code examples (not just descriptions)
3. Verify all claims against source code
4. Be consistent with README and Read the Docs

## Registration

```toml
# pyproject.toml
[project.entry-points."scitex_dev.skills"]
my-package = "my_package"
```

Do NOT add `[tool.hatch.build.targets.wheel.force-include]` for `_skills/` — hatch already includes files under `src/<pkg>/`.

## Export Commands

```bash
scitex-dev skills export    # Copy to .claude/skills/scitex/
scitex-dev skills update    # Rsync-like, preserves local changes
scitex-dev skills upgrade   # Clean replacement
```

`SCITEX_DEV_SKILLS_DEFAULT_EXPORT_DIR` env var overrides default export destination.

## Symlink vs Copy Convention

- **Packages bundled for PyPI**: use real copies in `_skills/` (symlinks break in wheels)
- **Development convenience**: symlink `_skills/<pip-name>/` → dotfiles for editing
- **Single source of truth**: `~/.dotfiles/src/.claude/to_claude/skills/scitex/<pip-name>/`
- **Sync direction**: edit in dotfiles → copy to repo before release

## Discovery Resolution (scitex-dev)

Three-tier fallback:
1. `src/<pkg>/_skills/<pip-name>/SKILL.md` (preferred)
2. `src/<pkg>/skills/SKILL.md` (legacy, deprecated)
3. `src/<pkg>/docs/MASTER/skills/` (oldest, deprecated)
