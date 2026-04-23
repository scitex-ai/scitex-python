---
name: arch-dependency-and-version-pinning
description: Dependency hygiene and version-pinning rules across the SciTeX 3-layer cascade — optional extras, minima, coordinated release waves.
---

# Dependency Hygiene & Version Pinning

Companion to [07_arch-upstream-and-downstream.md](07_arch-upstream-and-downstream.md). The 3-layer cascade imposes strict rules on what each layer may depend on and how versions are pinned.

## Dependency Hygiene

Downstream is **standalone**, not **zero-dep**. Third-party runtime deps (numpy, matplotlib, click, …) are allowed; sibling/middle/upstream SciTeX packages are not, except via optional extras.

| Dep kind | Downstream | Middle | Upstream |
|----------|------------|--------|----------|
| Third-party (numpy, matplotlib, click, …) | ✅ Allowed, **keep minimal** | ✅ Allowed | ✅ Allowed |
| `scitex-dev` (shared infra) | ✅ Allowed (dev tooling / entry points) | ✅ Allowed | ✅ Allowed |
| Sibling downstream (e.g. figrecipe → scitex-writer) | ❌ Not at runtime — only via optional extras | ⚠️ Via plugin registry only | ✅ Allowed |
| Middle (`scitex-io`, `scitex-stats`, …) | ❌ Not at runtime — optional extras only | ✅ Allowed between middle pkgs | ✅ Allowed |
| Upstream (`scitex`, `scitex-cloud`) | ❌ **Never** | ❌ **Never** | ✅ Self |

### Minimality checklist (downstream)

- [ ] Every runtime dep is actually imported in `src/`.
- [ ] No convenience deps that belong in `[dev]` or `[docs]`.
- [ ] Heavy or rarely-used deps moved to **named extras** (`[imaging]`, `[scientific]`, `[mcp]`, …).
- [ ] Any SciTeX-ecosystem dep is either `scitex-dev` (infra) or listed under an **optional** extra.
- [ ] `pip install <pkg>` in a clean venv produces a working package with no other `scitex-*` installed.

Good example (`figrecipe`): `matplotlib`, `numpy`, `ruamel.yaml`, `scipy`, `click`, `rich` — six tight runtime deps, everything else (Pillow, seaborn, scitex integration) behind extras.

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

## Version Pinning Rules

**Principle**: pin the **minimum** version that contains features you rely on. Do **not** pin upper bounds unless a known incompatibility exists. This keeps the ecosystem composable and avoids lockstep upgrades.

### Lower bound: always set it
```toml
# Good
dependencies = [
    "numpy>=1.21.0",         # we use numpy.typing, first in 1.21
    "scitex-io>=0.3.0",      # we call scitex-io.save with new dry_run= kwarg
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
   - Bump its `scitex-io` lower bound to the new minimum that contains the feature.
   - Add a note in the consumer's CHANGELOG linking the feature used.
   - Bump the consumer's own **patch** version (feature now requires newer dep).
3. **Do not** bump minima speculatively — only when you actually use a new API.
4. **Breaking changes** (rename, signature change, removal):
   - Major-bump the producing package.
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

## Quick Checklist (dependencies & versions)

- [ ] **Downstream**: third-party runtime deps are minimal, justified, and actually imported.
- [ ] **Downstream**: `pip install <pkg>` in a clean venv yields a working package with no other `scitex-*` installed.
- [ ] **Downstream**: tests pass with only `[dev]` extras installed.
- [ ] **All layers**: every dep has a lower bound (`>=X.Y`); no speculative upper bounds.
- [ ] **Producers**: when releasing a feature consumers need, bump their minimum **only** in consumers that actually use it.
