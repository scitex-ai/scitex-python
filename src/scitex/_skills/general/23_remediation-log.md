---
name: remediation-log
description: Dated remediation log for package-skills audit findings. Historical record only — rule-shaped checklist lives in 22_skills-quality-checklist.md.
---

# Skills Remediation Log

Historical record of audit findings against `22_skills-quality-checklist.md`. Rule-shaped content stays in the checklist; concrete findings and their status live here.

## 2026-04-23 — Audit snapshot (status verified 2026-04-23)

Findings from the 2026-04-23 ecosystem audit and their current resolution status:

| # | Package | Original finding | Status (2026-04-23) |
|---|---------|------------------|---------------------|
| 1 | scitex-orochi | 13 unlisted leaves, 12 files >15 KB, dual `SKILL_INDEX.md` + `SKILL.md`, `legacy/` + `.old/` in-tree | RESOLVED 2026-04-23 |
| 2 | scitex-app | `backend-sdk.md` and entire `references/` unlisted; duplicate `app-lifecycle` and `app-registration` top-level vs references | RESOLVED 2026-04-23 |
| 3 | crossref-local | Dual `_skills/SKILL.md` and `_skills/crossref-local/SKILL.md` with disjoint content; partial prefixes | RESOLVED 2026-04-23 |
| 4 | scitex-writer | `manuscript-workflow.md` unlisted; 4 leaves >10 KB | RESOLVED 2026-04-23 (4 monoliths flagged TODO) |
| 5 | scitex-scholar | `SKILL.md` itself 168 lines (becoming monolith) | RESOLVED 2026-04-23 |
| 6 | scitex-cloud | `scitex-versions.md` 10.8 KB; 118 B / 181 B legacy stubs | RESOLVED 2026-04-23 (1 monolith flagged TODO) |
| 7 | scitex-dev | `full-update.md` 13.6 KB monolith | RESOLVED 2026-04-23 (1 monolith flagged TODO) |
| 8 | scitex-ui | 2 leaves >10 KB | RESOLVED 2026-04-23 (1 monolith flagged TODO) |
| 9 | All remaining packages | Adopt `01_–NN_` prefixes to match `general/` | RESOLVED 2026-04-23 |

Open monolith TODOs (flagged 2026-04-23):
- scitex-writer: 4 leaves still >10 KB — split before next release.
- scitex-cloud: 1 leaf still >10 KB.
- scitex-dev: 1 leaf still >10 KB.
- scitex-ui: 1 leaf still >10 KB.

## How to use this log

- When a new audit uncovers findings, append a new dated section with a table.
- Status values: `IN PROGRESS`, `RESOLVED YYYY-MM-DD`, `DEFERRED`, `WONTFIX`.
- Do not delete historical entries — they are the receipts for the checklist.

---

## Package-level gaps (2026-04-23)

Moved to sibling file to keep this log under the 10 KB cap:
See `24_package-gaps-2026-04-23.md` for the full per-package sweep and aggregate summary.
