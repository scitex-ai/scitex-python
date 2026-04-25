---
name: skills-editable-installation
description: How skill sources resolve under editable (`pip install -e`) vs wheel (PyPI) installs. Editable installs symlink to the source tree so edits are live; wheel installs use the bundled copy inside the wheel.
user-invocable: false
canonical-location: scitex-python/src/scitex/_skills/general/06_skills_04_editable-installation.md
tags: [scitex-python, scitex-general, scitex-package, meta]
---

# Editable vs PyPI Install — Skill Source Resolution

Every `scitex-*` package ships `_skills/` as package data in the wheel. At runtime, the skill loader must use **one of two paths** depending on how the package was installed:

| Install mode | Skill source | Edits are live? |
|---|---|---|
| Editable (`pip install -e .` or `uv pip install -e .`) | **Symlink** to `src/<pkg>/_skills/` in the cloned repo | Yes — edit the source, reload |
| Wheel / PyPI (`pip install scitex-<pkg>`) | **Bundled copy** inside the installed wheel under `site-packages/<pkg>/_skills/` | No — read-only, rebuild wheel to change |

Rule: **a pre-tool-use hook blocks edits inside `~/.dotfiles/.../skills/scitex/` and `~/.claude/skills/scitex/`** regardless of install mode — those are always exported copies. Edits always go to the source of truth.

## Detection

A package is editable-installed when its `*.dist-info` contains a `direct_url.json` with `"editable": true`, or when the installed path is a symlink (typical with `uv`/`flit`). The skill exporter reads this:

```python
import importlib.metadata as im
dist = im.distribution("scitex-<pkg>")
direct_url = dist.read_text("direct_url.json")
is_editable = direct_url and '"editable": true' in direct_url
```

## Export workflow

`scitex-dev skills export` resolves sources as follows:

1. **Editable install** → export creates a **symlink** from `~/.claude/skills/scitex/<pip-name>/` to the repo's `src/<pkg>/_skills/<pip-name>/`. Edits in the repo appear instantly in Claude Code.
2. **Wheel install** → export copies the bundled files from `site-packages/<pkg>/_skills/<pip-name>/` to `~/.claude/skills/scitex/<pip-name>/`. Edits require re-installing the package.
3. **Both installed** → editable wins.

## Authoring implications

- Write skill content in `src/<pkg>/_skills/<pip-name>/` always. Never in `site-packages/…`, never in `~/.claude/…`, never in dotfiles skill export paths.
- When you change a skill during development, you do **not** need to re-run `scitex-dev skills export` if you're on an editable install — the symlink keeps `~/.claude/skills/scitex/…` pointing at your edits in real time.
- When you publish a new wheel, **include `_skills/` as package data** in `pyproject.toml`. Otherwise PyPI consumers get no skills:

```toml
[tool.setuptools.package-data]
<pkg_name> = ["_skills/**/*"]

[tool.hatch.build.targets.wheel.force-include]
"src/<pkg_name>/_skills" = "<pkg_name>/_skills"
```

- After every wheel-publish, verify a fresh `pip install scitex-<pkg>` into a clean venv still sees the skills:

```bash
python -c "from importlib.resources import files; print(list(files('<pkg_name>._skills').iterdir()))"
```

## Why this matters

Without this split, ordinary PyPI users see no skills (because nothing on their disk points at a repo clone), while developers get confused when edits don't appear (because the loader is reading the wheel copy, not the source). Making install mode the source-resolution axis removes both failure modes.

## Cross-references

- [06_skills_02_how-to-update.md](06_skills_02_how-to-update.md) — source-of-truth locations, export command
- [06_skills_03_public-vs-private.md](06_skills_03_public-vs-private.md) — where a skill belongs
- [01_arch_06_local-state-directories.md](01_arch_06_local-state-directories.md) — canonical filesystem layout
