# Thin `scitex` core with entry-point module registration

Status: **DRAFT, needs a decision**. Nothing in this note has been released.
Date: 2026-11-19. Prototype: `packages/scitex-thin-core/` (this PR) plus the
`proto/scitex-modules-entry-point-20261119` branches of scitex-io and scitex-str.

## 1. Goal (user decision 2026-11-19)

- User code writes `import scitex as stx` and calls `stx.io.save(...)`,
  `stx.stats...`, `@stx.session`, and so on.
- Installing any **single** leaf (`pip install scitex-io`) makes both
  `import scitex_io` and `import scitex as stx; stx.io` work.
- Code inside SciTeX packages keeps importing leaves directly
  (`import scitex_io`). Packages never import `scitex`, which keeps the
  dependency graph acyclic and the coupling loose.

## 2. Current state (verified 2026-11-19)

| Item | Finding |
|---|---|
| Who provides the `scitex` import package | The PyPI distribution **`scitex`**, built from this repo (`scitex-ai/scitex-python`). PyPI has no `scitex-python` distribution (the JSON API returns 404). `packages/scitex-python-redirect/` exists but has never been published. |
| PyPI latest | `scitex` **2.30.8** (uploaded 2026-07-07). 86 releases. Its metadata still points at `github.com/ywatanabe1989/scitex-python`. |
| main vs develop | Both `pyproject.toml` files say **2.30.9**, which is unreleased (no `v2.30.9` tag). `origin/main...origin/develop` is **6 / 34**: main has 6 commits that are not on develop, and develop has 34 that are not on main. |
| What `scitex/__init__.py` does today | It is already almost a pure re-export layer. It holds about 60 hard-coded `_LazyModule("io", external="scitex_io")` proxies, two `_CallableModuleWrapper`s (`session`, `module`, `usage`), deprecated aliases through PEP 562 `__getattr__`, and an eager `PATHS = scitex_config.ScitexPaths()`. `scitex.re_export` pre-registers the peers in `sys.modules` with `LazyLoader` and installs a `MetaPathFinder` so that `import scitex.<x>` resolves to the peer. The finder's alias map comes from `scitex_dev._ecosystem` plus a branded map (`plt -> figrecipe.pyplot`, `cloud -> scitex_hub`, ...). |
| Where the knowledge lives | In the **umbrella**. The map from short name to peer is curated in `re_export.EXTERNAL_REEXPORTS` and `_DEFAULT_BRANDED`, so adding a leaf means editing the umbrella. |
| Hard dependencies | The umbrella hard-depends on about 35 leaves (`scitex-io`, `-stats`, `-scholar`, `-ui`, ...). `pip install scitex` is therefore heavy (PyPI `requires_dist` has 630 entries counting extras). |
| Proxy identity | `stx.io` is a `_LazyModule` proxy, so `stx.io is scitex_io` is False. |
| Latent bug | `_ScitexAliasLoader.create_module` returns the peer module, and CPython then overwrites the peer's `__spec__`. After `import scitex.io`, `scitex_io.__spec__.name == "scitex.io"`. The prototype restores the original spec in `exec_module`. |
| Does any leaf ship a `scitex/` directory? | **No.** The only local `src/scitex/` is this repo's. |
| Leaf code importing the umbrella (against the rule in §1) | `scitex-io` develop, all lazy imports inside functions: `_cache.py:102 import scitex`, `bundle/kinds/_plot/_backend/_export.py:53,99` and `_render.py:35 import scitex as stx`, `bundle/kinds/_table/_latex/__init__.py:10` and `_plot/_utils/_plot_layout.py:15 from scitex.io.bundle...`. Under a thin core these break unless the umbrella is installed, so they must be rewritten to direct leaf imports. |
| Dependents of the `scitex` dist | `scitex-hub` declares `scitex>=2.29.3` in two places (runtime and dev), using `@stx.session` and `@stx.module`. `packages/scitex-python-redirect` declares `scitex>=2.5.0`. There are also external user projects (`neurovista`, ...). |
| Weight of "one leaf" | In a clean venv, `pip install scitex-io` (develop, 0.6.2) also installs **13 other scitex-\* distributions**: browser, config, context, dev, dict, logging, plt, repro, scholar, sdk, session, ssh, and str. `uv pip tree` shows the chain: scitex-io → `scitex-dev>=0.63.0` (needed for the linter plugin) → `scitex-scholar`. scitex-scholar brings scitex-session, scitex-browser, playwright, mcp, pymupdf and onnxruntime. There is also a cycle: scitex-scholar → scitex-dev → scitex-scholar. The thin core does not change any of this, so "one leaf" is not light today. Moving `scitex-dev` to an extra of scitex-io (and of every leaf) is a separate, recommended follow-up. |
| `scitex-core` | The PyPI dist **exists**: 0.2.0–0.2.8, last upload 2026-05-01. Its import package is `scitex_core`, not `scitex`. It depends on the `scitex` dist. The repo `ywatanabe1989/scitex-core` is **archived**. **0.2.8 ships a SyntaxError**: compiling the wheel fails in `scitex_core/dt/_normalize_timestamp.py`, line 47. The wheel also ships stray test output (`sh/test_sh_out/RUNNING/...`). It should be yanked whichever option below is chosen (yanking is irreversible-ish, so it needs approval). |

## 3. Design

### 3.1 Entry-point contract (`scitex.modules`)

Each leaf adds a few lines to its own `pyproject.toml`:

```toml
[project]
dependencies = [ ..., "scitex>=3,<4" ]   # the thin core (stdlib only)

[project.entry-points."scitex.modules"]
io = "scitex_io"                          # module form
```

- **name**: the attribute exposed as `stx.<name>`. It must be a valid
  identifier, must not start with `_`, and must not be a reserved core name
  (`list_modules`, `ENTRY_POINT_GROUP`, `ScitexModuleNotInstalled`,
  `__version__`). A leaf may register several names: `scitex-logging` gives
  `logging` and `errors`, and `scitex-datetime` gives `datetime` and `dt`.
- **value**: either a module path (`scitex_io`, `figrecipe.pyplot`) or an
  object path (`scitex_session:session`).
  - **Module form** gives `stx.io`, `import scitex.io`,
    `from scitex.io import load`, and `import scitex.io.bundle`, all of which
    resolve to the real module object (identity, no proxy).
  - **Object form** gives `stx.<name>` only. Use it for non-module attributes
    such as `PATHS = "scitex_config:PATHS"`.
- **Branded peers register themselves**: figrecipe registers
  `plt = "figrecipe.pyplot"` and `diagram = "figrecipe.diagram"`, and socialia
  registers `social`. After that the core holds no peer list.
- **Callable modules** (`@stx.session`, `@stx.module`): the leaf owns this.
  It makes its module object callable (a `ModuleType` subclass assigned to
  `sys.modules[__name__].__class__`, with `__call__ = session`) and registers
  the module form. This keeps `@stx.session`, `stx.session.INJECTED`, and
  `from scitex.session import INJECTED` all working, and the core needs no
  special case.
- **Collision**: two distributions registering the same name with
  *different* values is a hard error on access, and the error names both
  distributions. The core never picks one silently.

### 3.2 Core behaviour (prototype: `packages/scitex-thin-core/src/scitex/__init__.py`, about 230 lines, stdlib only)

- `import scitex` does no entry-point scan, imports no leaf, and does not
  import `importlib.metadata` (that import alone costs about 35 ms cold).
  The prototype measured 2–4 ms (see §6).
- PEP 562 `__getattr__(name)` runs these steps:
  1. Map deprecated aliases (`ai`, `reproduce`, `rng`, `verify`, `notify`) to
     their new names with a `DeprecationWarning`.
  2. Scan the `scitex.modules` group once and cache the result.
  3. Load the module or object.
  4. Store it in `globals()`, so later accesses are plain attribute hits.
- **Missing module**: the core raises `ScitexModuleNotInstalled`, a subclass
  of `AttributeError`, so `hasattr(stx, "io")` is False. The message names
  the distribution to install: by convention `scitex-<name>`, with a small
  override table (`plt` and `diagram` -> `figrecipe`, `cloud`, `module` and
  `project` -> `scitex-hub`, `torch` -> `scitex-linalg`, ...).
  `import scitex.io` and `from scitex import io` raise ImportError with the
  same hint. The override table only words error messages and has no effect
  on resolution.
- A `MetaPathFinder` is appended after the default finders, so
  `import scitex.<name>[.sub]` maps onto the registered module.
- `stx.list_modules()` returns `{name: {value, dist, version}}` for
  discoverability and for `scitex-dev` audits.
- `__dir__` adds every registered name for tab completion.

### 3.3 Version-skew policy

- The core's **contract** is the group name, the value grammar, and the
  resolution semantics. A breaking change to the contract requires a core
  major bump. Leaves pin `scitex>=3,<4`.
- The core never pins leaves (only extras name them), so leaves release
  independently. A leaf's `scitex.modules` value is part of that leaf's
  public API: renaming it is a breaking change of the leaf.
- `scitex-dev` gets an audit for this: every ecosystem leaf declares exactly
  its expected names, no collisions across the registry, and a `scitex>=3,<4`
  dependency. This fits the rule-id renumbering in step 4.

### 3.4 Backwards compatibility of today's `stx.<attr>` surface

| Today | Thin core |
|---|---|
| `stx.<leaf>` (about 55 names in `EXTERNAL_REEXPORTS` and `_DEFAULT_BRANDED`) | Each leaf registers the same name. This is the roll-out table for step 2. |
| `stx.ai`, `reproduce`, `rng`, `verify`, `notify` | Core alias table with a `DeprecationWarning` (prototype implements this). |
| `stx.dt` | `scitex-datetime` registers both `datetime` and `dt`. |
| `@stx.session`, `@stx.module`, `stx.usage()` | Callable-module form, owned by the leaf (scitex-session, scitex-hub, and the new home of `usage`). |
| `stx.PATHS` | `scitex-config` registers `PATHS = "scitex_config:PATHS"` (object form). It is no longer created eagerly at `import scitex`. |
| `stx.INJECTED`, `stx.Diagram`, `stx.show_install_guide` (deprecated) | Dropped in 3.0, or kept in the core alias table as attribute redirects (`INJECTED -> session.INJECTED`). **Decision D4.** |
| `stx.gen` (fail-loud shim), `stx.cli`, `fts`, `schema`, `canvas`, `fig`, `dev` (in-tree) | `gen` stays as a core shim or moves. `cli`, `_mcp`, `_skills`, `usage` and the console scripts `scitex`, `scitex-pkg` and `scitex-mcp-server` move to a new leaf, **`scitex-cli`** (import `scitex_cli`), which registers `cli` and `usage`. `fts`, `schema`, `canvas` and `fig` already have no in-tree code; they are dropped or registered by their owners. |

## 4. Decision D1: who owns the `scitex` distribution name

### Option A (recommended): the thin core *is* `scitex` 3.0.0, and the old umbrella becomes `scitex[all]`

- `pip install scitex` installs the thin core only, and `stx.io` raises
  "pip install scitex-io".
- `pip install 'scitex[all]'` gives today's full set. The per-module extras
  that exist today keep their spelling (`scitex[io]`, `scitex[stats]`, ...),
  because the extra just names the leaf. A self-referencing
  `all = ["scitex[io,stats,...]"]` is allowed by pip and uv.
- Leaves depend on `scitex>=3,<4`. The umbrella's extras depend on the
  leaves. There is no install-time cycle, because the core has no hard
  dependencies.
- **Pros**:
  - One distribution owns the `scitex/` directory, so upgrades are atomic and
    no files are clobbered.
  - The RTD project, PyPI name and repo stay where they are.
  - Matches the user's "scitex[all]" wording.
- **Cons, which make this a breaking release (3.0)**:
  - A fresh `pip install scitex` no longer pulls the leaves.
  - Every open-ended dependent (`scitex-hub: scitex>=2.29.3`, external
    projects) silently receives the thin core on its next resolve. Those
    dependents must move to `scitex[all]>=3`, or to the leaves they actually
    use, **before** 3.0 is published.
  - Users with existing environments are unaffected until they upgrade.
    After upgrading, already-installed 2.x-era leaves lack the entry point
    until those leaves are also upgraded. Mitigation: the "not installed"
    message also says "or upgrade it". As a further option, the core can
    fall back to `importlib.util.find_spec("scitex_<name>")` for one minor
    series, with a DeprecationWarning. **Decision D3.**

### Option B: a new thin distribution (for example `scitex-base`) ships `scitex/__init__.py`, and `scitex` stays the full umbrella that depends on it

- **Pro**: `pip install scitex` keeps installing everything.
- **Fatal con**: during the transition, two distributions write
  `site-packages/scitex/__init__.py`. Installing a new leaf into an
  environment that still has `scitex==2.30.x` (which ships its own
  `scitex/__init__.py`) overwrites the umbrella's file. Python packaging has
  no "conflicts" metadata to prevent this, so environments break silently.
  To avoid it, the umbrella would have to ship no files under `scitex/` from
  the same day, which is the same breaking change as A, just under a
  confusing name split.
- Reusing the name `scitex-core` for this is worse still: that name already
  means the `scitex_core` import package, depends on `scitex`, and has a
  broken latest release.

### Option C: A, but the thin `scitex` also hard-depends on a "starter set" of leaves (io, session, stats, plt, clew)

- `pip install scitex` stays useful.
- This creates a real dependency cycle (`scitex` -> `scitex-io` -> `scitex`).
  pip and uv tolerate the cycle, but it brings back weight and coupling and
  defeats "thin". Not recommended.
- PEP 771 (default extras) would be the clean form of this, but it is not
  usable yet.

**Recommendation: A**, released as `scitex` **3.0.0**. Before that release:

1. Every first-party dependent switches to `scitex[all]>=3` or to direct
   leaves.
2. The last 2.x release (2.31) emits a `FutureWarning` on `import scitex` that
   announces the change and the `scitex[all]` spelling.
3. 2.31 also starts reading `scitex.modules` entry points in addition to its
   hard-coded map, so leaves can register before the cutover.

## 5. Test matrix

| Leg | Install | Must hold |
|---|---|---|
| core-only | `scitex` (3.x) | `import scitex` loads no leaf. `stx.io` raises AttributeError naming `scitex-io`. `hasattr` is False. `from scitex import io` raises ImportError with the hint. `list_modules() == {}`. |
| one leaf | `scitex-io` only | The core is pulled transitively. `stx.io is scitex_io`. save/load round-trips. `from scitex.io import load` works. `import scitex.io as sio` works. `scitex_io.__spec__` is intact. `stx.str` gives the "install scitex-str" hint. |
| two leaves | `scitex-io scitex-str` | Both resolve. `list_modules()` lists exactly `io` and `str`. |
| all | `scitex[all]` | Every name in the roll-out table resolves (`scitex-dev` audit). No collisions. Import time of `scitex` is unchanged. |
| skew | new core plus an old leaf without the entry point | The hint says to install or upgrade (and the D3 fallback, if chosen). |
| collision | two dists register the same name | ImportError names both distributions. |
| no-umbrella leaf code | each leaf's own test suite in a venv **without** `scitex[all]` | Proves the leaf never imports the umbrella (catches the scitex-io sites listed in §2). |

The first three legs are automated in
`packages/scitex-thin-core/tests/run_proof.sh` (clean `uv venv` per leg,
local wheels only, nothing uploaded).

## 6. Prototype proof

Command (local wheels only; nothing uploaded):

```bash
packages/scitex-thin-core/tests/run_proof.sh /scratch/$USER/thin-core/proof-run \
    <scitex-io checkout @ proto/scitex-modules-entry-point-20261119> \
    <scitex-str checkout @ proto/scitex-modules-entry-point-20261119>
```

Result on 2026-11-19 (uv 0.11.24, CPython 3.12.3): **ALL LEGS PASS**.

| Leg | Installed | Checks |
|---|---|---|
| core-only | `scitex 3.0.0.dev0` | 10/10 PASS. `stx.io` raises "Install it with: pip install scitex-io". `from scitex import io` raises the same hint. `stx.plt` names `figrecipe`. `import scitex` takes 2.6 ms. |
| io-only | `scitex_io-0.6.2` wheel only. The core came in transitively; 13 other scitex-\* came from PyPI. | 13/13 PASS. `stx.io is scitex_io`. JSON and npy save/load round-trip. `from scitex.io import load` and `import scitex.io as sio` work. `scitex_io.__spec__` is intact. `stx.str` (scitex-str 0.1.14 from PyPI, which has **no** entry point, i.e. the version-skew case) gives the hint. |
| io-and-str | both leaf wheels | 14/14 PASS. `list_modules()` shows exactly `io` and `str`. `stx.str.squeeze_spaces` works. |

## 7. Migration steps

1. **(this PR)** Design note and prototype. No release.
2. **Leaf roll-out.** For each leaf, add the `scitex.modules` entry and the
   `scitex>=3.0.0.dev0,<4` dependency on develop. Leaf releases wait until
   the core 3.0 exists on PyPI. Fix leaf→umbrella imports (scitex-io first).
   figrecipe and socialia register their branded names.
3. **2.31 bridge release of the umbrella.** It reads entry points first,
   falls back to the hard-coded map, and emits the FutureWarning. Dependents
   migrate to `scitex[all]>=3` or to direct leaves.
4. **3.0.0.** `src/scitex/` becomes the thin core. `cli`, `_mcp`, `_skills`
   and `usage` move to `scitex-cli`. `[all]` and the per-module extras list
   the leaves. Run the full test matrix in CI per leg.
5. **Lint rules (scitex-dev, folded into the rule-id renumbering).**
   - In user code (`research` projects), importing a SciTeX leaf directly is
     a warning: use `stx.<name>`.
   - In package code (`src/` of a SciTeX package), `import scitex` is an
     error: import the leaf directly.
6. Yank `scitex-core` 0.2.8 (SyntaxError) after approval, and point its
   README at the new design.

## 8. Decisions needed

- **D1**: dist naming. Recommendation: Option A, the thin core is `scitex`
  3.0.0 and the umbrella becomes `scitex[all]`.
- **D2**: home of the umbrella-only code (`cli`, `_mcp`, `_skills`, `usage`,
  console scripts). Recommendation: a new `scitex-cli` leaf.
- **D3**: for one minor series, should the core fall back to
  `find_spec("scitex_<name>")` for leaves that are installed but predate the
  entry point (with a DeprecationWarning)? Recommendation: yes, for 3.0.x
  only.
- **D4**: what happens to the deprecated attribute redirects (`INJECTED`,
  `Diagram`, `show_install_guide`) in 3.0. Recommendation: drop them in 3.0,
  since they are already deprecated.
- **D5**: whether to yank `scitex-core` 0.2.8.
