---
name: arch-re-export
description: Re-export convention that lets `scitex.<name>.X` and `scitex_<name>.X` always resolve to the same object — the `scitex.<name>` umbrella subpackage thin-re-exports the standalone `scitex_<name>` public API, with a lazy-import guard so unused optional deps never trigger import errors, a stable `__all__` contract, and no original logic in the bridge. Prevents the common bug where agents read one form in docs and the other in examples, getting different runtime behaviour. Use when setting up a new scitex-* standalone + its bridge, adding a new public symbol, or debugging why `scitex.X.Y` differs from `scitex_X.Y`.
canonical-location: scitex-python/src/scitex/_skills/general/01_arch_05_re-export.md
tags: [scitex-python, scitex-general, scitex-package, meta]
---

# Umbrella Re-Export Convention

## Why re-export

Agents and humans discover features through **both** namespaces:

- `scitex.path.find_git_root` — the ecosystem-wide umbrella.
- `scitex_path.find_git_root` — the standalone leaf package.

These MUST resolve to the **same** object. If they drift, searchability, docs,
and example chains break silently (`stx.path.find_git_root()` falls back to a
shim while the real implementation only exists in the standalone).

## Where to re-export

Each umbrella bridge module lives at `src/scitex/<name>/__init__.py` inside the
`scitex-python` umbrella. The bridge is **thin**: it re-exports from the
standalone and adds only a lazy-import guard that raises a clear
`ImportError` when the optional extra isn't installed.

Prefer explicit re-exports (named imports + `__all__`) over `from X import *`
so the public surface is grep-able.

## Separation of concerns

| Layer | Owns | Must NOT |
|---|---|---|
| Standalone `scitex_<name>` | Implementation, tests, version, API stability | Depend on the umbrella |
| Umbrella `scitex.<name>` bridge | Thin re-export + `ImportError` guard | Ship implementation; override behaviour |

The umbrella NEVER implements logic. If the extra isn't installed, the bridge
raises `ImportError` with a pointer to `pip install scitex[<name>]`. This is
the hard rule; see `01_arch_03_modules-and-standalone-packages.md` §12.

## When NOT to re-export

- Underscore-prefixed helpers (`_internal_foo`) — private to the standalone.
- Test utilities under `scitex_<pkg>.testing._*` — not public API.
- APIs that intentionally don't exist in the umbrella namespace (experimental,
  deprecated, or standalone-only CLI plumbing).
- Symbols that may not exist in the pinned PyPI release — guard with
  `try/except ImportError` and provide a minimal shim (see scholar pattern
  below).

## Concrete pattern — `scitex.scholar`

Working shim after the 2026-04-24 `clean_abstract` guard fix:

```python
# src/scitex/scholar/__init__.py
"""SciTeX Scholar — delegates to scitex-scholar."""

from scitex_scholar import (
    SCHOLAR_AVAILABLE,
    CitationGraphBuilder,
    Paper,
    Papers,
    Scholar,
    ScholarConfig,
    apply_filters,
    from_connected_papers,
    generate_cite_key,
    make_citation_key,
    papers_to_format,
    plot_citation_graph,
    to_bibtex,
    to_connected_papers,
    to_endnote,
    to_ris,
    to_text_citation,
)

try:
    from scitex_scholar import clean_abstract
except ImportError:
    # clean_abstract lands in scitex-scholar >= 1.3; fall back to no-op
    # so this umbrella shim imports cleanly against 1.2.x on PyPI.
    def clean_abstract(text):
        return text


__all__ = [
    "Scholar", "Paper", "Papers", "ScholarConfig", "CitationGraphBuilder",
    "plot_citation_graph", "to_bibtex", "to_ris", "to_endnote",
    "to_text_citation", "papers_to_format", "generate_cite_key",
    "make_citation_key", "from_connected_papers", "to_connected_papers",
    "apply_filters", "clean_abstract", "SCHOLAR_AVAILABLE",
]
```

Key points:

1. Explicit named re-exports (not `from scitex_scholar import *`) — the public
   surface is grep-able and stable.
2. `__all__` matches the re-export list exactly.
3. New-in-next-release symbols are guarded with `try/except ImportError` and a
   minimal no-op shim. This keeps the umbrella import-clean against older
   standalone releases on PyPI.
4. No logic lives in the bridge. All real work is in `scitex_scholar`.

## Release-gate check

At release time:

```bash
python -c "import scitex_<pkg> as a, scitex.<pkg> as b; \
  print(sorted(set(a.__all__) - set(b.__all__)) or 'OK')"
```

Any symbol missing from the umbrella that the standalone exports is a bug —
either add the re-export or explicitly document why it's standalone-only.

## Alternative bridge — `sys.modules` aliasing (use sparingly)

The explicit-named-re-export pattern above does not preserve **deep
submodule paths**. After:

```python
# scitex/foo/__init__.py
from scitex_foo import bar, baz
```

`from scitex.foo import bar` works, but `from scitex.foo._private.helpers import X` does NOT — that import resolves through `scitex/foo/__path__`, which only contains the bridge `__init__.py`, no `_private/` subdir.

When the package has callers that reach into private submodules (legacy code, tests, deeply-coupled MCP handlers) the alternative is **module-level `sys.modules` aliasing**:

```python
# scitex/template/__init__.py — the entire shim
"""SciTeX template — thin compatibility shim for scitex-template."""

import sys as _sys

try:
    import scitex_template as _real
except ImportError as _e:
    raise ImportError(
        "scitex.template requires the 'scitex-template' package. "
        "Install with: pip install scitex[template]"
    ) from _e

_sys.modules[__name__] = _real
```

Effect: `scitex.template` becomes literally the same module object as `scitex_template`. Every submodule path — `scitex.template._mcp.handlers`, `scitex.template._project.clone_research`, `scitex.template.<anything>` — resolves through `scitex_template`'s `__path__`. Subpackage attribute access works identically.

**Tradeoffs:**

| | Explicit named re-export (scholar pattern) | sys.modules aliasing (template pattern) |
|---|---|---|
| Public API discoverable in the bridge file | ✓ grep-able | ✗ docstring-only |
| Deep submodule paths preserved | ✗ | ✓ |
| Static analysers (Pyright) trace the API | ✓ | ⚠️ each tool varies |
| Survives a `__all__` drift between bridge and standalone | ✗ release-gate catches it | ✓ no drift possible |
| Implementation size | ~30 lines, one rule per symbol | ~5 lines, one trick |

**When to choose which:**

- Default to **explicit named re-exports** (scholar pattern). Most packages are fine — public surface stays grep-able and the release-gate check has teeth.
- Reach for **sys.modules aliasing** only when external callers reach into private submodules and you cannot rewrite them all in one PR (transition shim during extraction). Plan to delete the shim once consumers are migrated to direct `scitex_<name>` imports.

**Rule for tests inside the standalone repo** — never use the umbrella shim path in `tests/`. Always import via `from scitex_<name>.…`. The umbrella may not even be installed in CI; the shim path collapses (`ModuleNotFoundError`) and every test fails at collection time. See general/02_repo_03_github-actions.md §"Test imports".
