---
name: skills-public-vs-private
description: Decision rule for every skill — does it belong in the public package (`src/<pkg>/_skills/<pip-name>/`, shipped to PyPI and GitHub) or in the private fleet store (`~/.scitex/<pkg-short>/shared/skills/<pip-name>-private/`, symlinked into `~/.claude/skills/`)? A skill is private if it names any specific hostname, container, credential, zone ID, fleet role, or incident detail; otherwise it is public. Includes the decision flow, split-pattern (public = pattern / private = operational recipe), and the grep-based safety check to run before `git push`. Use when starting any new skill or auditing an existing one for leaked fleet-internal details.
---

# Public vs Private Skills

A skill is either **public** (shipped with the package on PyPI/GitHub) or
**private** (fleet-internal, lives under `~/.scitex/<pkg>/`). Before
writing a skill, decide which side it belongs on. Leaking fleet-internal
specifics into a public skill is the most common mistake — once it
ships, you cannot easily unship.

## The two locations

| Kind | Source of truth | Exported to |
|---|---|---|
| **Public** | `src/<pkg>/_skills/<pip-name>/` (in the package repo) | `~/.claude/skills/scitex/<pip-name>/` via `scitex-dev skills export` |
| **Private** | `~/.scitex/<pkg-short>/shared/skills/<pip-name>-private/` (in dotfiles) | `~/.claude/skills/scitex/<pip-name>-private/` via symlink |

Public SKILL.md has no `user-invocable` frontmatter (defaults to true).
Private SKILL.md sets `user-invocable: false`.

## Decision rule

A skill is **private** if it names any of:

- Specific hostnames (`mba`, `spartan`, `ywata-note-win`)
- Specific container names (`orochi-server-stable`)
- Specific credentials, API keys, zone IDs, tunnel IDs, tokens
- Specific deploy paths (`/Users/...`, `~/proj/scitex-orochi/...`)
- Specific agents or fleet roster
- Incident post-mortems or fleet history

Otherwise it is **public**. The public form describes a *pattern*
(e.g., "pipe a file through `docker exec -i` to bypass the host disk"),
the private form fills in the concrete nouns
(e.g., "on mba, pipe into `orochi-server-stable`, then purge Cloudflare
zone `2eda29d6…`").

## Decision flow

```
Does the skill mention any specific host, container, credential,
zone ID, or fleet role?
  YES → private (~/.scitex/<pkg>/shared/skills/<pkg>-private/)
  NO  → public (src/<pkg>/_skills/<pip-name>/)
```

When in doubt, write the public version generically first; if you
can't explain the idea without a specific hostname, it is private.

## Split pattern (when both are useful)

Sometimes the *pattern* is worth documenting publicly while the
*operational recipe* belongs privately. Put the pattern in the
package, then cross-reference the private instance:

- Public: `src/<pkg>/_skills/<pip-name>/hotpatch-pattern.md` —
  describes the general technique, no hostnames.
- Private: `~/.scitex/<pkg>/shared/skills/<pip-name>-private/infra-hotpatch-<host>.md` —
  exact commands for the real host, credentials, zone ID.

## Concrete example — scitex-orochi docker deploy

Originally written as a public skill `hub-docker-deploy.md` in
`scitex-orochi/_skills/scitex-orochi/`. Audit found it named `mba`,
`orochi-server-stable`, Cloudflare zone `2eda29d6…`, and
`~/.colima/...` — all fleet-internal. Moved to
`~/.scitex/orochi/shared/skills/scitex-orochi-private/infra-hub-docker-disk-full.md`,
dropped from the public index.

## Safety check before `git push`

Grep the public skills directory for fleet-internal nouns before
publishing a release:

```bash
cd ~/proj/<pkg>
grep -rEn 'mba|spartan|orochi-server-stable|cloudflare.*key|zones/[a-f0-9]{32}' \
  src/<pkg>/_skills/
# Expected: no matches. Any hit is either (a) a public pattern that
# can be rewritten generically, or (b) content that should move to
# the private skills directory.
```

## Cross-references

- [03_interface_04_skills.md](03_interface_04_skills.md) — `_skills/` layout and registration
- [06_skills_02_how-to-update.md](06_skills_02_how-to-update.md) — edit sources, export workflow
