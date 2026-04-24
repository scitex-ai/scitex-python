<!-- ---
!-- Timestamp: 2026-04-23 09:00:00
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-python/src/scitex/_skills/general/06_skills_04_quality-checklist.md
!-- --- -->

---
name: skills-quality-checklist
description: Release-gate checklist for _skills/ directories — naming, indexing, no-monolith, no-duplication, cache hygiene.
---

# SciTeX Package Skills — Quality Checklist

Canonical reference: this directory (`src/scitex/_skills/general/`). Every
SciTeX ecosystem package **MUST** pass this checklist before release; audit
findings from 2026-04-23 drove the concrete rules below.

## 0. Scope

Applies to every `src/<pkg>/_skills/<skill>/` directory in every package in
the ecosystem. Does **not** apply to private skills under
`~/.scitex/<pkg>/shared/skills/` (those follow the private-skill schema in
`06_skills_03_public-vs-private.md`).

## 1. Directory structure

- [ ] One `_skills/` directory per package at `src/<pkg>/_skills/`.
- [ ] Each sub-skill lives in its own subdirectory: `_skills/<skill-name>/`.
- [ ] **Exactly one** `SKILL.md` per sub-skill directory. **NEVER** ship a
      parallel `SKILL_INDEX.md`, nested `_skills/<pkg>/SKILL.md`, or any
      other alias index — one sub-skill → one index.
- [ ] **NEVER** ship `legacy/` or `.old/` subdirectories inside `_skills/`.
      Delete before release; if retention is required, move outside
      `_skills/`.

## 2. File naming & ordering

- [ ] Every leaf `.md` carries a **2-digit zero-padded numeric prefix**:
      `01_`, `02_`, …, `99_`. No gaps within a group.
- [ ] Prefixes express **logical order**, not alphabetical. Recommended
      grouping (mirrors `general/`):
      - `01–09` core concepts / interfaces
      - `10–19` workflows / guides
      - `20–29` standards / conventions
      - `30–39` architecture / internals
      - `40–49` lessons, scratch, playground
- [ ] `SKILL.md` itself has **no** numeric prefix.
- [ ] Filenames are **kebab-case** after the prefix:
      `01_arch_01_upstream-and-downstream.md`.
- [ ] **NEVER** rename a prefixed file by hand; use `git mv` so history is
      preserved.

## 3. SKILL.md as index only

- [ ] `SKILL.md` contains frontmatter (`name`, `description`,
      `user-invocable`) plus a short intro plus **grouped links** to every
      sibling `.md`. **MUST NOT** contain substantive content beyond the
      intro.
- [ ] Every sibling `.md` leaf is listed exactly once in `SKILL.md`. No
      missing entries, no dead links.
- [ ] Links use the **new prefixed filenames**; no stale references to
      un-prefixed legacy names.
- [ ] `SKILL.md` itself stays under **~4 KB / ~80 lines**. If growing
      beyond, split the content into a new leaf — do not let the index
      itself become a monolith.

## 4. Leaf file size — no-monolith rule

- [ ] No leaf `.md` exceeds **~10 KB** (~200 lines). Split if larger.
- [ ] No leaf is a near-empty stub (<300 B) unless it is an explicit
      placeholder with a `TODO` marker.
- [ ] Each leaf covers **one focused topic**. The filename describes the
      topic precisely in 2–5 words.

## 5. No duplication / no parallel content

- [ ] **NEVER** maintain two versions of the same topic in one package
      (e.g. top-level `app-lifecycle.md` AND `references/app-lifecycle.md`).
      Pick one canonical location.
- [ ] A `references/` subdirectory is allowed **only** when every file
      inside is a pure technical reference that differs in kind (not in
      depth) from top-level guides, and every file is indexed from
      `SKILL.md`.
- [ ] **NEVER** restate general-ecosystem rules (four interfaces, env-var
      prefix, branding, version management) inside a package skill. Link
      to `general/` instead:
      `See [../general/01_arch_04_environment-variables.md] for the canonical rule.`

## 6. No contradictions with `general/`

- [ ] Package must not redefine or contradict any rule documented in
      `src/scitex/_skills/general/`. Specifically:
  - [ ] Env-var prefix is `SCITEX_<MODULE>_*` (never bare `SCITEX_*`).
  - [ ] Four-interface delegation chain is Python API → CLI → MCP → Skills
        (optional HTTP). No custom interface layering.
  - [ ] `import scitex` in docs/READMEs (never `import scitex as stx`).
  - [ ] No `ywatanabe@scitex.ai` signature in package-shipped docs.
  - [ ] Skill source of truth is `src/<pkg>/_skills/…` — **NEVER** edit
        the exported copies under `~/.claude/skills/scitex/` directly.

## 7. Cache-friendliness (context-cost hygiene)

- [ ] Leaf ordering in `SKILL.md` is **stable** across releases —
      re-ordering busts prompt cache for every downstream consumer.
- [ ] Edits that only add content append near the end of a leaf where
      possible; refactors that split a file are acceptable cache
      invalidation but should not happen more than once per release cycle.
- [ ] SKILL.md index is **markdown-linked** (`[text](file.md)`) by default,
      not `@`-included, so agents can lazy-load leaves. Promote a leaf to
      `@`-include only when it is genuinely always-needed for the skill.

## 8. Release gate

Before bumping the package version:

- [ ] `find src/<pkg>/_skills -name '*.md' | sort` matches the links in
      every `SKILL.md` (no dead links, no orphans).
- [ ] No file in `_skills/` exceeds 10 KB.
- [ ] No `_skills/legacy/` or `_skills/.old/` present.
- [ ] Exported skills refreshed via `scitex-dev skills export` so
      `~/.claude/skills/scitex/<pkg>/` mirrors source.

## 9. Automation

Future work: add a `scitex-linter` plugin that checks §1–§8
programmatically and runs as part of the release gate. Tracking: see
`02_repo_03_quality.md` (sibling) for the broader release checklist.

<!-- EOF -->
