# 0001 — Relocate `scitex.media` out of the umbrella (future work)

## Status

**Superseded by operator decision (2026-06-07)** — Phase B of the
scitex-gen full retirement wave. Operator characterized `scitex-etc` as the
catch-all bin and routed `media` to **figrecipe** instead (`scitex.media`
→ `figrecipe.media`, shipped in figrecipe 0.29.0). `scitex-etc` retains
only `count_grids` / `yield_grids` / `search`.

Original status: Proposed (deferred) — 2026-05-30.

## Context

As part of the umbrella separation-of-concerns cleanup (the broader effort
that turned `scitex.{io,rng,verify,tunnel,clew,stats,…}` into thin aliases of
standalone packages), every in-tree `src/scitex/<x>/` directory is being
audited: it should either be a thin alias to the owning standalone package or
hold genuinely umbrella-specific assembly code (`__init__`, `re_export`,
`__main__`, `usage`, `cli`, `_mcp/` bootstrap).

`src/scitex/media/` is an exception: it contains real, self-contained logic
(`render/` — detect/classify/format media references for chat-pane, terminal
overlay, and markdown-embed targets; `media.detect()`, `media.show()`), it is
**not** a re-export of any existing standalone, and it is **not** imported by
any peer package. It therefore violates "the umbrella hosts no logic" (R5), but
there is no ready home for it today.

## Decision

Keep `scitex.media` in the umbrella **for now**. Do not extract it in the
current cleanup pass. When the next ecosystem-grooming pass happens, relocate
its implementation into a standalone package — most likely **`scitex-etc`**
(the catch-all for small cross-cutting utilities) — and reduce `scitex.media`
to a thin alias, consistent with the other modules.

A dedicated `scitex-media` package was considered and rejected for now: the
surface is small (one `render` submodule) and does not justify a standalone
repo + release cadence. `scitex-etc` is the lighter-weight home.

## Consequences

- The umbrella temporarily retains one logic-bearing module (`media/`),
  knowingly and with this record, rather than silently.
- No API change for users: `scitex.media.render` / `stx.media.show(...)`
  continue to work unchanged through the relocation (the alias preserves the
  public path).
- Follow-up work item: move `scitex/media/render/` → `scitex_etc.media`
  (optional figrecipe/PIL deps), add the `scitex-etc` test coverage, release
  `scitex-etc`, then replace `src/scitex/media/` with an alias in
  `re_export.py`'s `_DEFAULT_BRANDED` (`"media": "scitex_etc.media"` or
  similar) and delete the in-tree dir.

## Notes

- Related cleanup: see the umbrella-decomposition map (rng/verify/tunnel
  already aliased; clew/stats glue moved to their standalones; diagram →
  figrecipe; torch → scitex-linalg; `_env_loader` → scitex-config; project's
  MCP file-op handlers → scitex-app).
- This ADR is the "add adr as future work" item requested for `media` on
  2026-05-30.
