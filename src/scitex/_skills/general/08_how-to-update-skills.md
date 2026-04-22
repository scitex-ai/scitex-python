---
description: How to update SciTeX skills — source-of-truth locations, editable vs non-editable install paths, and the export workflow.
---

# How to Update SciTeX Skills

## Source of Truth

SciTeX skills live in package source code, NOT in `~/.dotfiles/.../skills/scitex/` or `~/.claude/skills/scitex/`. Those are auto-generated export copies. A pre-tool-use hook blocks direct edits to the export copies.

## Editable Install (pip install -e)

If the package is installed in editable mode, edit the source directly:

| Package type | Source location |
|---|---|
| Modules (within scitex-python) | `~/proj/scitex-python/src/scitex/<module>/_skills/` |
| Standalone packages | `~/proj/<pkg>/src/<pkg_name>/_skills/<pip-name>/` |

After editing, export to dotfiles:

```bash
scitex-dev skills export --package <pkg>
```

Verify:

```bash
scitex-dev skills list --package <pkg>
scitex-dev skills export --package <pkg> --dry-run
python -m pytest tests/test_skills.py -v
```

### Examples

```bash
# scitex-notification (standalone)
vi ~/proj/scitex-notification/src/scitex_notification/_skills/scitex-notification/configuration.md
scitex-dev skills export --package scitex-notification

# notification module (within scitex-python)
vi ~/proj/scitex-python/src/scitex/notification/_skills/voice-sms.md
scitex-dev skills export --package scitex

# general standards (within scitex-python)
vi ~/proj/scitex-python/src/scitex/_skills/general/environment-variables.md
scitex-dev skills export --package scitex
```

## Non-Editable Install

If the package is NOT installed in editable mode (e.g., installed from PyPI), you cannot edit the source directly. Instead, create an issue:

```bash
gh issue create --repo ywatanabe1989/<package-name> --title "Skills update: <description>"
```

## Skill-Writing Rules

- SKILL.md is an index only — content goes in focused sub-skill files
- No checkboxes (`- [ ]`) — use prose, code blocks, tables
- No "Confirmation" / "Understanding Check" sections
- Show `$ENV_VAR_NAME` in CLI help defaults, not resolved values
- Consolidate thin sub-files (< 20 lines each) into SKILL.md
- Include MANIFEST.md with version (auto-stamped from pyproject.toml on export)
