# SciTeX Package Architecture (3-Layer Cascade)

```
Downstream (apps — standalone, own IO):
  figrecipe, scitex-writer, scitex-clew, ...
      ^ wraps/cascades via plugin registry

Middle (shared infrastructure):
  scitex-io, scitex-app, scitex-ui, scitex-stats, scitex-audio, scitex-dev
      ^ integrates/re-exposes (SOC — integration tests ONLY)

Upstream (orchestration):
  scitex (scitex-python), scitex-cloud
```

Full rules: `~/proj/scitex-dev/docs/MASTER/00_SCITEX_UPSTREAM_AND_DOWNSTREAM_RULES.md`

## Key Rules

- **Apps work standalone** — no scitex dependency for core functionality
- **scitex-io wraps, not replaces** — cascades through plugin registry
- **scitex re-exposes only** — no logic, just re-export from middle layer
- **Upstream has ONLY integration tests** — unit tests belong downstream
- **All 3 interfaces cascade** — Python API, CLI, MCP same direction
- **`_AVAILABLE` flags** — detect optional deps, provide install instructions
- **Extras in pyproject.toml** — `pip install figrecipe[scitex]`
- **Never reverse imports** — upstream never imports downstream directly
- **Single source of truth** (DRY) + separation of concerns
