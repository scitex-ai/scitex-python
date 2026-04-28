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

### Why setuptools needs the explicit `package-data` entry

`[tool.setuptools.packages.find] where = ["src"]` only picks up **Python packages** (directories containing `__init__.py`). Markdown files in subdirectories like `_skills/<pkg>/SKILL.md` are NOT auto-included. The result is a silent failure mode:

- `git ls-files` shows `SKILL.md` is tracked ✅
- The source tree under `src/<pkg>/_skills/` is intact ✅
- `python -m build --wheel` builds successfully ✅
- But the resulting wheel does NOT contain the file ❌

PyPI users who `pip install <pkg>` see no skill page, and skill-discovery agents iterate over an empty `<pkg>._skills` namespace. The CI workflow won't catch this because nothing imports the markdown file.

### Pre-publish verification (5-second check that catches the silent failure)

After every `python -m build`, **before tagging the release**, verify the wheel actually contains the data files you expect:

```bash
unzip -l dist/<pkg>-<version>-py3-none-any.whl | grep -E '_skills|SKILL\.md'
```

Expected output (one line per shipped skill leaf):
```
6716  2026-04-28 01:58   <pkg>/_skills/<pip-name>/SKILL.md
```

No matching lines = the wheel is missing skills. Re-check `pyproject.toml`'s `[tool.setuptools.package-data]` (or the hatch `force-include` block), rebuild, re-verify. **Don't tag until this passes.**

A real instance of this trap, scitex-hpc 0.6.1 (2026-04-28): the SKILL.md was added to git but the package-data entry was missing. The wheel built without errors, the version bumped fine, CI was green. Caught at the unzip-l step before the tag was pushed; shipped 0.6.2 with the fix on the same day. Without the unzip check, 0.6.1 would have been an "everything looks done" release that failed silently for every PyPI user.

### Post-install verification (after the wheel is live)

For belt-and-suspenders, confirm a fresh `pip install scitex-<pkg>` into a clean venv resolves the skill:

```bash
python -c "from importlib.resources import files; print(list(files('<pkg_name>._skills').iterdir()))"
```

## Why this matters

Without this split, ordinary PyPI users see no skills (because nothing on their disk points at a repo clone), while developers get confused when edits don't appear (because the loader is reading the wheel copy, not the source). Making install mode the source-resolution axis removes both failure modes.

## Cross-references

- [06_skills_02_how-to-update.md](06_skills_02_how-to-update.md) — source-of-truth locations, export command
- [06_skills_03_public-vs-private.md](06_skills_03_public-vs-private.md) — where a skill belongs
- [01_arch_06_local-state-directories.md](01_arch_06_local-state-directories.md) — canonical filesystem layout
