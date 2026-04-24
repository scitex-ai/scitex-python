---
name: skills-frontmatter-metadata
description: "Additional YAML frontmatter fields every SciTeX skill (SKILL.md and every leaf) declares to improve agent discoverability and cost accounting — `tags` (stacked three-level categorisation — package / category / ecosystem scope), `invocation` (trigger words beyond the description), `context_tokens` / `context_tokens_total` (loading-cost estimate), `canonical-location` (source-of-truth path), and `see-also` (cross-references). Also documents the Claude Code standard fields (`disable-model-invocation`, `allowed-tools`, `context` fork, etc.) for completeness. Use when authoring new skills, auditing discoverability, or computing context budgets before loading a bundle."
user-invocable: false
canonical-location: scitex-python/src/scitex/_skills/general/06_skills_06_frontmatter-metadata.md
tags: [scitex-python, scitex-general, scitex-package, meta]
---

# Skill Frontmatter Metadata

Every SciTeX skill file (the per-skill `SKILL.md` and every leaf `.md` under it) carries YAML frontmatter. Two sources of truth stack:

1. **Claude Code standard fields** — defined by the [Agent Skills](https://agentskills.io) open standard and documented at [Extend Claude with skills](https://code.claude.com/docs/en/claude-code/skills). These control how Claude Code loads, invokes, and scopes the skill.
2. **SciTeX ecosystem extensions** — additional fields this project introduces for discoverability, context-cost accounting, and multi-repo hygiene. Claude Code ignores unknown fields, so extending the standard is safe.

## 1. Claude Code standard fields (authoritative)

From the official docs — only `description` is strictly recommended; the rest are optional.

| Field | Required | Purpose |
|---|---|---|
| `name` | No | Display name / slash-command id. Defaults to the directory name. Lowercase + hyphens only, ≤ 64 chars. |
| `description` | **Recommended** | What the skill does and when to apply it. Claude uses this to decide whether to auto-load. If omitted, the first paragraph of the body is used. |
| `argument-hint` | No | Autocomplete hint, e.g. `[issue-number]`. |
| `disable-model-invocation` | No | `true` = only the user can invoke via `/name`; Claude cannot auto-load. Default `false`. |
| `user-invocable` | No | `false` = hide from the `/` menu. Default `true`. |
| `allowed-tools` | No | Tools the skill may use without per-use approval. |
| `model` | No | Model override while the skill is active. |
| `effort` | No | `low` / `medium` / `high` / `max` — overrides session effort. |
| `context` | No | Set `fork` to run the skill body in an isolated subagent. |
| `agent` | No | Subagent type when `context: fork` (e.g. `Explore`, `Plan`, `general-purpose`). |
| `hooks` | No | Skill-scoped lifecycle hooks. |

SciTeX authors usually only set the first three (`name`, `description`, `user-invocable`). The others are for interactive workflow commands — not for the rule-file skills that dominate this repo.

## 2. SciTeX ecosystem extensions (defined here)

### `tags` — must-read categorisation

```yaml
tags: [scitex-package, research]
```

Array of string tags (YAML frontmatter convention, same field name as Hugo / Jekyll / Gatsby / most SSGs). Agents scanning skills for a project may auto-load every skill whose `tags:` array contains a matching entry. Canonical tag values:

| Tag | Meaning |
|---|---|
| `scitex-package` | Rules that apply to every `scitex-*` repo (package architecture, CLI, MCP, skills, release gates) |
| `scitex-general` | The ecosystem-wide `general/` skill category in scitex-python |
| `scitex-python` | Specific to the scitex-python umbrella package itself |
| `scitex-scientific` | The `scientific/` skill category (publication figures, stats, reproducibility) |
| `research` | Rules for a research project *using* SciTeX — reproducibility, config, session decorator |
| `paper` | Rules for manuscript preparation — figures, LaTeX, citation hygiene |
| `infra` | Cross-cutting infrastructure — SSH, containers, cloud, tunnels |
| `meta` | Rules about writing rules — skill authoring, quality checklists, release gates |
| `scientific` | Scientific methodology topics (alias of `scitex-scientific` when used outside scitex-python) |
| `claude-code` | Claude Code runtime reference material (hooks, MCP, skills, CLI, etc.) |

### How to stack tags (package / category / ecosystem levels)

A single skill usually belongs to **three nested levels** — apply all three tags:

```yaml
tags: [scitex-python, scitex-general, scitex-package]
#        ^-- package      ^-- category     ^-- ecosystem-wide
```

Reading the tags:

| Position | Role | Example values |
|---|---|---|
| Package | The concrete pip-name that owns the file | `scitex-python`, `scitex-io`, `figrecipe`, `scitex-cloud` |
| Category | The `_skills/<category>/` subdirectory | `scitex-general`, `scitex-scientific`, `scitex-io` (for per-package skills) |
| Ecosystem scope | What the skill applies to globally | `scitex-package` (every scitex-* repo), `research`, `paper`, `infra`, `meta` |

Why all three? A **CLAUDE.md** at any level (ecosystem / package / project) can pick which tag layer to match and pull in exactly the skills relevant to that layer:

- `<research-project>/CLAUDE.md` auto-loads everything tagged `research` or `scitex-package` (the rules authors must follow) but **not** `scitex-python` (which is about building that upstream package, not using it).
- `~/proj/scitex-io/CLAUDE.md` auto-loads everything tagged `scitex-package` (ecosystem rules) and `scitex-io` (its own skills), skipping unrelated `scitex-cloud` tags.
- `~/.claude/CLAUDE.md` (fleet-wide) can pull every `scitex-general` skill as must-read for any session.

Rule: **every skill leaf declares all three levels** whenever they apply — never rely on inheritance from SKILL.md. Claude Code currently picks each file's frontmatter independently.

### CLAUDE.md tag shortcuts

Once every skill carries proper `tags:`, a **research project's `CLAUDE.md` can reference a tag instead of hand-listing files**:

```markdown
<!-- research-project/CLAUDE.md -->
# Project context

@scitex                         # expands to every skill tagged `scitex-package`
@scitex-scientific              # expands to every skill tagged `scitex-scientific`
@research                       # expands to every skill tagged `research`
```

A resolver (future `scitex-dev skills tags-expand <tag>`) walks every installed package's `_skills/` tree, grepping for files whose `tags:` frontmatter contains the requested tag, and emits the absolute paths. The project's CLAUDE.md keeps a single `@scitex` line; the resolver fans it out.

Benefits:

- New/removed skills appear automatically — no hand-editing every project CLAUDE.md when the ecosystem changes.
- Projects opt into exactly the layers they need (`research` but not `paper`, say).
- Package authors own the `tags:` field in their own tree; downstream consumers only touch tags, not file paths.

Convention for the shorthand:

| CLAUDE.md reference | Resolves to files whose `tags:` includes |
|---|---|
| `@scitex` | `scitex-package` (must-know for every scitex-using project) |
| `@scitex-general` | `scitex-general` |
| `@scitex-scientific` | `scitex-scientific` |
| `@research` | `research` |
| `@paper` | `paper` |
| `@infra` | `infra` |

Until the resolver lands, projects can hand-list files — but tag them consistently now so the eventual resolver picks them up automatically.

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
tags: [scitex-python, scitex-general, scitex-package, meta]
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
3. Every file declares at least one `tags:` entry.
4. Every SKILL.md (index) declares `invocation` (3–7 strings).

Automated via `scitex-dev quality audit-frontmatter <dir>` — shipped as of scitex-dev v0.4+. Rules FM-0 through FM-6 cover all checks above, including legacy `group:` → `tags:` migration (FM-6).
