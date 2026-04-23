---
name: upstream-and-downstream-packages
description: SciTeX ecosystem architecture — the 3-layer library cascade (upstream / middle / downstream) plus orthogonal ecosystem/platform packages (scitex-dev, scitex-orochi, scitex-agent-container, scitex-container, scitex-cloud). Covers dependency direction, import rules, test scope per layer, and the cascade pattern across Python API / CLI / MCP.
---

# SciTeX Package Architecture

The ecosystem has **two orthogonal axes**:

- **Axis 1 — Library cascade** (this skill's primary subject): a strict 3-layer dependency cascade for library code shipped as `scitex`, `scitex-io`, `figrecipe`, etc.
- **Axis 2 — Ecosystem & platform packages**: orthogonal packages that *manage*, *orchestrate*, or *host* the cascade rather than participating in it. These do not fit the cascade rules and must be reasoned about separately.

## Axis 1 — Library Cascade (3-Layer)

Dependencies flow in one direction only: upstream may import middle and downstream; middle may import downstream; downstream never imports upward.

```
Upstream (orchestration — SOC, integration tests only)
    scitex (scitex-python)
        │ imports / re-exposes
        ▼
Middle (shared infrastructure — integration tests of cascade)
    scitex-io, scitex-app, scitex-ui, scitex-stats, scitex-audio
        │ integrates / wraps via plugin registry
        ▼
Downstream (apps — standalone, own IO/GUI, unit tests)
    figrecipe, scitex-writer, scitex-scholar, scitex-clew, scitex-notebook, ...
```

**One-line contract**: Downstream does not know upstream exists. Upstream does not duplicate downstream logic.

## Axis 2 — Ecosystem & Platform Packages (Orthogonal)

These packages belong to the SciTeX ecosystem but sit **outside** the library cascade. They are not "downstream of scitex" and not "upstream of figrecipe" — they serve a different concern entirely. Treat them as peers of the cascade, not members of it.

| Package | Role | Relation to cascade |
|---|---|---|
| **scitex-dev** | Ecosystem-wide developer tooling, cross-repo management, skills quality harness, release automation | *Manages* the cascade (CI, tests, packaging) — not a library tier |
| **scitex-orochi** | Multi-agent orchestration (head / master / telegrammer roles) | Runs alongside the cascade; drives development workflows |
| **scitex-agent-container** | Container images & configuration for SciTeX agents | Infrastructure for scitex-orochi |
| **scitex-container** | General container layer for SciTeX services | Infrastructure host |
| **scitex-cloud** | Research hub, app-centric platform for creating and sharing custom lab apps | Different direction — user-facing platform, not a library layer |

**Why this matters**: applying cascade rules (e.g. "downstream must not import upstream", "upstream has no logic") to these packages is a category error. They have their own internal architectures.

> For dependency hygiene and version-pinning rules (optional extras, `>=X` minima, coordinated waves), see the sibling skill [08_arch-dependency-and-version-pinning.md](08_arch-dependency-and-version-pinning.md).

---

## Layer Responsibilities

| Layer | Role | Knows About | Tested With |
|-------|------|-------------|-------------|
| **Downstream** | Standalone apps with their own IO/GUI | Only itself and std-lib/third-party | **Unit tests** — covers its own logic fully |
| **Middle** | Shared infrastructure (wraps, doesn't replace) | Downstream (as optional plugins) | **Integration tests** — does the cascade work? Plus unit tests for its own unique code |
| **Upstream** | Orchestration, re-exposure, session framework | Middle + downstream | **Integration tests ONLY** — does the full pipeline flow? No unit tests for delegated logic |

---

## Upstream vs Downstream — The Difference

| Dimension | Downstream (e.g. figrecipe) | Upstream (e.g. scitex) |
|-----------|-----------------------------|------------------------|
| **Dependency direction** | Imports nothing scitex-specific | Imports / re-exposes middle + downstream |
| **Standalone** | MUST work without scitex installed | Requires full ecosystem |
| **Owns logic?** | Yes — all app-specific logic lives here | **No** — pure re-export + orchestration (`@stx.session`) |
| **Test scope** | **Unit tests** — covers all its own behaviour | **Integration only** — verifies the pipeline flows |
| **May duplicate logic?** | N/A (it is the source of truth) | **Never** — re-expose only |
| **CI install** | `pip install -e ".[dev]"` — no scitex | Full ecosystem installed |
| **Breaking change risk** | Isolated — only its users affected | Cascades across all packages |
| **Example feature** | `fr.save(fig, "plot.png")` — does the save | `stx.io.save(fig, ...)` — re-exports `fr.save` via plugin registry |

### Testing the difference concretely

```
Layer        Test scope                              Example test
-----------  --------------------------------------  ----------------------------------
figrecipe    Unit: fr.save() produces YAML + PNG?    test_save_produces_yaml_png
(down)       Unit: fr.reproduce() matches hashes?    test_reproduce_matches

scitex-io    Integration: cascade reaches fr.save?   test_stx_io_save_calls_fr_save
(middle)     Integration: plugin discovered?         test_figrecipe_plugin_found
             Unit: type-check rejects bad input?     test_invalid_type_raises

scitex       Integration: session → io → figrecipe?  test_session_saves_via_io
(up)         Integration: all subpkgs importable?    test_import_all_subpackages
             NO unit tests for downstream logic      (do not re-test fr.save here)
```

**Rule of thumb**: if a test would still make sense after deleting the upstream package, it belongs downstream. If a test only makes sense because multiple packages exist, it is an integration test and belongs at the layer that composes them.

---

## Core Principles

### 1. Downstream apps must work standalone
- `figrecipe` must function without `scitex` installed.
- `fr.save()`, `fr.load()`, `fr.reproduce()` work independently.
- GUI (`figrecipe gui`) works without scitex.

### 2. Middle layer wraps, doesn't replace
- `scitex-io` provides universal `stx.io.save()` / `stx.io.load()`.
- It **wraps** downstream IO via a plugin registry (cascades to the right handler).
- Downstream apps register their formats via entry points.
- `scitex-ui` provides shared React components, not app-specific logic.
- `scitex-app` provides shared Python backends (FilesBackend, ChatBackend, ...).

### 3. Upstream orchestrates only (SOC)
- `scitex` is an orchestration package — Separation of Concerns.
- `@stx.session` provides reproducible experiment tracking.
- Session composes figrecipe output with scitex-io file operations.
- Session is **optional** — downstream apps work fine without it.
- **scitex has NO logic of its own** — it only re-exposes and integrates.

### 4. Test scope follows the layer
- **Downstream** → unit tests of own logic.
- **Middle** → integration tests of the cascade + unit tests of its own unique code.
- **Upstream** → integration tests of the full pipeline. No duplicate unit coverage of delegated logic.

### 5. Examples are the exception
- Examples may use `@stx.session` for organized output.
- Gallery CI installs scitex for examples but must handle failure gracefully.

---

## Cascade Pattern — IO as the Canonical Example

### (1) Downstream defines its own IO
```python
# figrecipe defines its own save/load for .yaml + .png
def save(fig, path, **kwargs):
    ...  # figrecipe-specific logic

# Register with scitex-io plugin registry (only if scitex-io is present)
FIGRECIPE_IO_SPEC = {
    "extensions": [".yaml", ".yml"],
    "save": save,
    "load": load,
    "description": "FigRecipe YAML recipe format",
}
```

### (2) Middle detects and delegates
```python
# scitex-io auto-discovers downstream plugins via entry points
def save(obj, path, **kwargs):
    ext = Path(path).suffix
    plugin = _registry.get(ext)
    if plugin:
        return plugin.save(obj, path, **kwargs)  # cascade to downstream
    ...
```

### (3) Upstream re-exposes with no modification
```python
# scitex just re-exports — NO additional logic
from scitex_io import save, load  # stx.io.save == scitex_io.save
```

### Cascade flows through all three interfaces

```
                    Python API          CLI                   MCP
                    ----------          -----------           ----------
scitex              stx.io.save()       scitex io save        io_save
(upstream)          (re-exposed)        (re-exposed)          (re-exposed)
                         │                   │                    │
                         ▼                   ▼                    ▼
scitex-io           stx.io.save()       scitex io save        io_save
(middle)                 │                   │                    │
                         ▼                   ▼                    ▼
figrecipe           fr.save()           figrecipe save        plt_plot
(downstream)
```

### Cascade rules
1. **Downstream defines** — each app implements save/load for its formats.
2. **Middle detects** — discovers downstream plugins via entry points / registry.
3. **Upstream re-exposes** — no additional wrapping.
4. **Type checking** — middle validates input/output during cascade.
5. **All three interfaces cascade the same direction** — Python API, CLI, MCP.
6. **Never reverse** — upstream never imports from downstream directly; downstream never imports upstream.

---

## CI Rules per Layer

### Downstream CI
- Install: `pip install -e ".[dev]"` — standalone only.
- Must NOT require scitex.
- Tests downstream logic only (unit tests).

### Middle CI
- Install: `pip install -e ".[dev]"` + relevant downstream packages.
- Integration tests: does the cascade work through the plugin registry?
- Plus unit tests for its own unique code (type checking, registry, adapters).

### Upstream CI
- Full ecosystem installed.
- Integration tests ONLY — does the full pipeline flow?
- NO unit tests re-testing downstream functionality.

---

## Quick Checklist (architecture)

- [ ] **Downstream**: package imports no upstream/middle/sibling-downstream packages at runtime (only as optional extras).
- [ ] **Middle**: own unique code (type checking, registry) is covered by unit tests.
- [ ] **Middle**: cascade to at least one downstream plugin is covered by an integration test.
- [ ] **Upstream**: no logic beyond re-export and orchestration.
- [ ] **Upstream**: tests are integration tests only; no duplicate unit coverage of downstream behaviour.
- [ ] All three interfaces (Python API, CLI, MCP) cascade in the same direction.
- [ ] No reverse imports (check with grep / linter).

For dependency hygiene and version-pinning checks, see [08_arch-dependency-and-version-pinning.md](08_arch-dependency-and-version-pinning.md).
