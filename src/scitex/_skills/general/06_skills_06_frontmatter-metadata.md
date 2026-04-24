---
name: skills-frontmatter-metadata
description: Additional YAML frontmatter fields every SciTeX skill (SKILL.md and every leaf) may declare to improve agent discoverability and cost accounting — `group` (must-read categorisation), `invocation` (trigger words beyond the description), `context_tokens` (loading-cost estimate), and `canonical-location`. Use when authoring new skills, auditing discoverability, or computing context budgets before loading a skill bundle.
user-invocable: false
canonical-location: scitex-python/src/scitex/_skills/general/06_skills_06_frontmatter-metadata.md
---

# Skill Frontmatter Metadata

Every SciTeX skill file (the per-skill `SKILL.md` and every leaf `.md` under it) carries YAML frontmatter. The required fields are `name` and `description` (see `06_skills_01_overview.md`). This document defines the **optional metadata fields** that a well-authored skill SHOULD also declare.

## Required (already documented elsewhere)

| Field | Type | Notes |
|---|---|---|
| `name` | string | kebab-case id, typically matches filename minus `NN_` prefix |
| `description` | string (≥ 200 chars) | Written to help the model decide *when to load this skill*. See `06_skills_01_overview.md` |
| `user-invocable` | bool | `true` for user-facing /slash commands; `false` for background rule sets |

## Optional (defined here)

### `group` — must-read categorisation

```yaml
group: [scitex-package, research]
```

Array of tags. Agents scanning skills for a project may auto-load every skill whose `group` matches the project's declared context. Canonical tag values (extend per-team as needed):

| Tag | Meaning |
|---|---|
| `scitex-package` | Rules for every `scitex-*` repo — package architecture, CLI, MCP, skills, release |
| `research` | Rules for a research project *using* SciTeX — reproducibility, config, session decorator |
| `paper` | Rules for manuscript preparation — figures, LaTeX, citation hygiene |
| `infra` | Cross-cutting infrastructure — SSH, containers, cloud, tunnels |
| `meta` | Rules about writing rules — skill authoring, quality checklists, release gates |
| `scientific` | Scientific methodology — figures, statistics, experiment design |

Rule: if you add a new tag, document it here first. An unknown tag is treated as a free-form label but will not trigger any must-read behaviour.

### `invocation` — discoverability hints

```yaml
invocation:
  - "how should I structure a scitex package"
  - "noun-verb CLI convention"
  - "audit-cli violations"
```

Free-text strings (≤ 80 chars each) the user might say. Complements `description` — the description reads as a factual topic statement; `invocation` reads as things the user literally asks. An agent can keyword-match against these when the user's wording doesn't align with `description`.

Rule of thumb: 3–7 invocations per skill. Too few misses real queries; too many pollutes the index.

### `context_tokens` — loading-cost estimate

```yaml
context_tokens: 2400
```

Rough estimate of how many tokens loading this file will cost. Agents with a context budget can use this to pick which skills to load first.

Estimation convention: **`context_tokens ≈ file_size_bytes / 4`** rounded to the nearest 100. This matches the rough ratio of ~4 bytes per token for English prose in modern BPE tokenizers. For files under 400 bytes, set `context_tokens: 100`.

For a multi-file skill bundle, the top-level `SKILL.md` may declare `context_tokens_total` covering the whole bundle (index + all leaves). Leaves declare their own per-file `context_tokens`.

Automate with:

```bash
wc -c <file> | awk '{printf "%d\n", int(($1/4)/100+0.5)*100}'
```

Future work: `scitex-dev skills audit-frontmatter` will warn when declared `context_tokens` drifts by more than 20 % from the auto-estimate.

### `canonical-location` — source-of-truth path

```yaml
canonical-location: scitex-python/src/scitex/_skills/general/06_skills_06_frontmatter-metadata.md
```

Relative to `~/proj/`. Pins the file's home so drift is easy to detect. Required for every file in the canonical `general/`, `scientific/` trees; optional elsewhere. When a file is renamed or moved, update this field in the same commit.

### `see-also` — cross-references (optional)

```yaml
see-also:
  - 03_interface_02_cli.md
  - 06_skills_01_overview.md
```

Sibling skill files whose content is related but distinct. Rendered as a footer section when generating skill docs.

## Example

```yaml
---
name: interface-cli
description: Canonical CLI design convention for every SciTeX package — subcommand structure (noun-verb), universal flags, exit codes, help format, deprecation redirect, env var namespace, config precedence, MCP parity, stdout/stderr discipline.
user-invocable: false
group: [scitex-package, meta]
invocation:
  - "how do I structure CLI subcommands"
  - "noun-verb rule"
  - "mcp install-tab-completion naming"
  - "bare transitive verb at top level"
  - "scitex-dev quality audit-cli"
context_tokens: 5400
canonical-location: scitex-python/src/scitex/_skills/general/03_interface_02_cli.md
see-also:
  - 03_interface_03_mcp.md
  - 06_skills_05_quality-checklist.md
---
```

## Audit

Before a release, verify:

1. Every file in `general/` and `scientific/` has a `canonical-location` field and it points at the right path.
2. Every file's `context_tokens` is within 20 % of `wc -c / 4 / 100` rounded.
3. Every file declares at least one `group` tag.
4. Every SKILL.md (index) declares `invocation` (3–7 strings).

Automated via `scitex-dev quality audit-frontmatter` (future) and `06_skills_05_quality-checklist.md` §10 (to be added).
