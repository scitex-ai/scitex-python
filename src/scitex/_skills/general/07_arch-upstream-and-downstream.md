---
name: upstream-and-downstream-packages
description: Three-layer cascade architecture of the SciTeX ecosystem. Covers dependency direction, import rules, test scope per layer, and the cascade pattern across Python API / CLI / MCP.
---

# SciTeX Package Architecture (3-Layer Cascade)

The SciTeX ecosystem is organized as a **strict 3-layer cascade**. Dependencies flow in one direction only: upstream may import middle and downstream; middle may import downstream; downstream never imports upward.

```
Upstream (orchestration — SOC, integration tests only)
    scitex (scitex-python), scitex-cloud
        │ imports / re-exposes
        ▼
Middle (shared infrastructure — integration tests of cascade)
    scitex-io, scitex-app, scitex-ui, scitex-stats, scitex-audio, scitex-dev
        │ integrates / wraps via plugin registry
        ▼
Downstream (apps — standalone, own IO/GUI, unit tests)
    figrecipe, scitex-writer, scitex-scholar, scitex-clew, scitex-notebook, ...
```

**One-line contract**: Downstream does not know upstream exists. Upstream does not duplicate downstream logic.

> Downstream packages **may** have third-party dependencies (numpy, matplotlib, click, …) — keep them **minimal** and **well-justified**. What a downstream package must NOT depend on at runtime is any *upstream* or *sibling* SciTeX package. See [Dependency Hygiene](#dependency-hygiene) below.

---

## Layer Responsibilities

| Layer | Role | Knows About | Tested With |
|-------|------|-------------|-------------|
| **Downstream** | Standalone apps with their own IO/GUI | Only itself and std-lib/third-party | **Unit tests** — covers its own logic fully |
| **Middle** | Shared infrastructure (wraps, doesn't replace) | Downstream (as optional plugins) | **Integration tests** — does the cascade work? Plus unit tests for its own unique code (type checking, plugin discovery, adapters) |
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
             Unit: GUI editor renders?               test_editor_elements

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
- Same applies to Writer, Scholar, Clew, Notebook, etc.

### 2. Middle layer wraps, doesn't replace
- `scitex-io` provides universal `stx.io.save()` / `stx.io.load()`.
- It **wraps** downstream IO via a plugin registry (cascades to the right handler).
- It adds type checking, format detection, standardization.
- Downstream apps register their formats via entry points.
- `scitex-ui` provides shared React components, not app-specific logic.
- `scitex-app` provides shared Python backends (FilesBackend, ChatBackend, ...).

### 3. Upstream orchestrates only (SOC)
- `scitex` is an orchestration package — Separation of Concerns.
- `@stx.session` provides reproducible experiment tracking (organized output dirs, CONFIG/logger injection).
- Session composes figrecipe output with scitex-io file operations.
- Session is **optional** — downstream apps work fine without it.
- **scitex has NO logic of its own** — it only re-exposes and integrates.

### 4. Test scope follows the layer
- **Downstream** → unit tests of own logic.
- **Middle** → integration tests of the cascade + unit tests of its own unique code.
- **Upstream** → integration tests of the full pipeline. No duplicate unit tests for delegated logic.

### 5. Examples are the exception
- Examples may use `@stx.session` for organized output.
- Gallery CI installs scitex for examples but must handle failure gracefully.
- If scitex install fails, examples should fall back to plain usage or skip.

---

## Cascade Pattern — IO as the Canonical Example

### (1) Downstream defines its own IO
```python
# figrecipe defines its own save/load for .yaml + .png
def save(fig, path, **kwargs):
    """Save figure as recipe YAML + PNG."""
    ...  # figrecipe-specific logic

def load(path):
    """Load recipe from YAML."""
    ...

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
    """Universal save — detects format, delegates to downstream plugin."""
    ext = Path(path).suffix
    plugin = _registry.get(ext)
    if plugin:
        return plugin.save(obj, path, **kwargs)  # cascade to downstream
    # Fallback: standard formats (CSV, NPY, PKL, ...)
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

## Optional Dependency Pattern

Downstream packages declare upstream features as **optional extras** so they remain standalone.

### `pyproject.toml`
```toml
[project.optional-dependencies]
scitex = ["scitex[io,session]>=2.24.0"]
all = ["figrecipe[scitex]", "figrecipe[dev]"]
```

### `_AVAILABLE` flags in code
```python
try:
    import scitex as stx
    _SCITEX_AVAILABLE = True
except ImportError:
    _SCITEX_AVAILABLE = False
```

### Clear instructions when deps are missing
```python
def some_feature_requiring_scitex():
    if not _SCITEX_AVAILABLE:
        raise ImportError(
            "This feature requires scitex. "
            "Install it with: pip install figrecipe[scitex]"
        )
```

### Examples — graceful fallback
```python
try:
    import scitex as stx

    @stx.session
    def main(CONFIG=stx.INJECTED, plt=stx.INJECTED, ...):
        ...
except ImportError:
    def main():
        import figrecipe as fr
        fig, ax = fr.subplots()
        ...
```

---

## Shared Infrastructure (Middle Layer Details)

### `scitex-ui` — frontend infrastructure
- Reusable React components (Workspace, Viewer, DataTable, ...).
- Ported from scitex-cloud (the reference implementation).
- All apps consume `scitex-ui`; apps only provide app-specific content.
- Port from scitex-cloud; never create new parallel implementations.

### `scitex-app` — backend infrastructure
- Shared Python backends (FilesBackend, ChatBackend, ...).
- Apps consume `scitex-app` for file operations, chat, etc.
- Zero runtime dependencies — pure Python SDK.

### Apps contain app-specific code only
- figrecipe: Canvas, PlotTypeNav, Properties, Gallery.
- Writer: Editor, Bibliography, Claims.
- Scholar: Search, Library, Citations.

---

## CI Rules per Layer

### Downstream CI (e.g. figrecipe tests)
- Install: `pip install -e ".[dev]"` — standalone only.
- Must NOT require scitex.
- Tests downstream logic only (unit tests).

### Downstream CI — gallery / examples
- Install: `pip install -e ".[all]"` + optional `pip install scitex`.
- If scitex install fails: warn, skip session examples, run plain ones.

### Middle CI (e.g. scitex-io)
- Install: `pip install -e ".[dev]"` + relevant downstream packages.
- Integration tests: does the cascade work through the plugin registry?
- Plus unit tests for its own unique code (type checking, registry, adapters).

### Upstream CI (e.g. scitex)
- Full ecosystem installed.
- Integration tests ONLY — does the full pipeline flow?
- NO unit tests re-testing downstream functionality.

---

## Dependency Hygiene

Downstream is **standalone**, not **zero-dep**. The rules:

| Dep kind | Downstream | Middle | Upstream |
|----------|------------|--------|----------|
| Third-party (numpy, matplotlib, click, ...) | ✅ Allowed, **keep minimal** | ✅ Allowed | ✅ Allowed |
| `scitex-dev` (shared infra) | ✅ Allowed (dev tooling / entry points) | ✅ Allowed | ✅ Allowed |
| Sibling downstream (e.g. figrecipe → scitex-writer) | ❌ Not at runtime — only via optional extras | ⚠️ Via plugin registry only | ✅ Allowed |
| Middle (`scitex-io`, `scitex-stats`, ...) | ❌ Not at runtime — optional extras only | ✅ Allowed between middle pkgs | ✅ Allowed |
| Upstream (`scitex`, `scitex-cloud`) | ❌ **Never** | ❌ **Never** | ✅ Self |

### Minimality checklist (downstream)
- [ ] Every runtime dep is actually imported in `src/`.
- [ ] No convenience deps that belong in `[dev]` or `[docs]`.
- [ ] Heavy or rarely-used deps moved to **named extras** (`[imaging]`, `[scientific]`, `[mcp]`, ...).
- [ ] Any SciTeX-ecosystem dep is either `scitex-dev` (infra) or listed under an **optional** extra.
- [ ] `pip install <pkg>` in a clean venv produces a working package with no other `scitex-*` installed.

Good example (`figrecipe`): `matplotlib`, `numpy`, `ruamel.yaml`, `scipy`, `click`, `rich` — six tight runtime deps, everything else (Pillow, seaborn, scitex integration) behind extras.

---

## Version Pinning Rules

**Principle**: pin the **minimum** version that contains features you rely on. Do **not** pin upper bounds unless a known incompatibility exists. This keeps the ecosystem composable and avoids lockstep upgrades.

### Lower bound: always set it
```toml
# Good
dependencies = [
    "numpy>=1.21.0",         # we use `numpy.typing`, first in 1.21
    "scitex-io>=0.3.0",      # we call scitex-io.save with new `dry_run=` kwarg
]

# Bad
dependencies = [
    "numpy",                 # ambiguous — breaks reproducibility of CI
    "scitex-io==0.3.4",      # too tight — blocks consumers
]
```

### Upper bound: only when proven broken
- Add `,<X` **only** when a specific release is known to break, and open an issue to track.
- Prefer fixing forward (new release with `>=Y.Z`) over capping upstream.
- Never cap by default — capping a major version (`<2`) traps consumers.

### When YOU update a package, bump minima in consumers
When you cut `scitex-io 0.4.0` containing a new feature used by `scitex`:

1. In `scitex-io`: bump its own version → `0.4.0`, publish, tag.
2. In every consumer (middle + upstream + downstream that uses it via `[scitex]` extra):
   - Bump its `scitex-io` lower bound to the new minimum that contains the feature:
     ```toml
     dependencies = [
         "scitex-io>=0.4.0",  # was >=0.3.0; needs dry_run= kwarg
     ]
     ```
   - Add a note in the consumer's CHANGELOG linking the feature used.
   - Bump the consumer's own **patch** version (feature now requires newer dep).
3. **Do not** bump minima speculatively — only when you actually use a new API.
4. **Breaking changes** (rename, signature change, removal):
   - Major-bump the producing package (`0.4.0 → 1.0.0` or `0.4.x → 0.5.0` pre-1.0).
   - Update every consumer's lower bound **and** code in the same coordinated release wave.
   - Consumers should fail fast on the old minimum rather than silently accept it.

### SciTeX-ecosystem-specific rules
- **Downstream → middle/upstream**: runtime minima live only inside **optional extras** (`[scitex]`). The bare install stays ecosystem-free.
  ```toml
  [project.optional-dependencies]
  scitex = ["scitex-io>=0.4.0", "scitex[session]>=2.24.0"]
  ```
- **Middle → downstream**: minima go under **test** extras (plugin targets for integration tests), not runtime.
  ```toml
  [project.optional-dependencies]
  dev = ["scitex-dev", "pytest>=7.0", "figrecipe>=0.13.0"]  # for cascade tests
  ```
- **Upstream → everything**: minima go under **runtime** deps with matched version ranges.
  ```toml
  dependencies = [
      "scitex-io>=0.4.0",
      "scitex-stats>=0.5.0",
      "figrecipe>=0.13.0",
  ]
  ```
- **Coordinated waves**: when multiple ecosystem packages change together, bump them in one wave with matched minima so a fresh `pip install scitex` resolves cleanly.
- **`scitex-dev ecosystem sync`** (or equivalent) is the canonical tool for fanning minima updates across the ecosystem. Prefer it over hand-editing.

### Quick rule of thumb
> Raise a lower bound **only** when you rely on something that version introduced. Lower it **never**. Cap an upper bound **only** when a release is proven broken.

---

## Quick Checklist

Before publishing any SciTeX-ecosystem package, verify:

- [ ] **Downstream**: package imports no upstream/middle/sibling-downstream packages at runtime (only as optional extras).
- [ ] **Downstream**: third-party runtime deps are minimal, justified, and actually imported.
- [ ] **Downstream**: `pip install <pkg>` in a clean venv yields a working package with no other `scitex-*` installed.
- [ ] **Downstream**: tests pass with only `[dev]` extras installed.
- [ ] **All layers**: every dep has a lower bound (`>=X.Y`); no speculative upper bounds.
- [ ] **Producers**: when releasing a feature consumers need, bump their minimum **only** in consumers that actually use it.
- [ ] **Middle**: own unique code (type checking, registry) is covered by unit tests.
- [ ] **Middle**: cascade to at least one downstream plugin is covered by an integration test.
- [ ] **Upstream**: no logic beyond re-export and orchestration.
- [ ] **Upstream**: tests are integration tests only; no duplicate unit coverage of downstream behaviour.
- [ ] All three interfaces (Python API, CLI, MCP) cascade in the same direction.
- [ ] No reverse imports (check with grep / linter).
