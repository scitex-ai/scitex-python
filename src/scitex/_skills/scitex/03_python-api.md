---
description: |
  [TOPIC] Python API — scitex umbrella surface
  [DETAILS] Top-level `scitex.*` exposes lazy sub-modules (io, plt, stats, ...) plus the `@scitex.session` decorator and `scitex.INJECTED` sentinel. Full per-module APIs live in the sister-package skills.
tags: [scitex-python-api]
---

# Python API — scitex umbrella

The umbrella surface is intentionally thin: it exposes sub-modules and a
small set of top-level helpers. Look at the sister-package skill for
full method-level docs.

## Top-level helpers

| Name | Kind | Purpose |
|------|------|---------|
| `scitex.__version__` | str | Umbrella version |
| `scitex.session` | decorator + module | `@scitex.session` wraps `main()` for reproducible runs; also accessible as `scitex.session.start(...)` etc. |
| `scitex.INJECTED` | sentinel | Marker for `@scitex.session` parameters that should be auto-injected (`CONFIG`, `plt`, `logger`, ...). |

## Sub-module map

External standalones (re-exported lazily — see `_EXTERNAL_REEXPORTS` in
`src/scitex/__init__.py`):

```text
scitex.io          → scitex_io
scitex.plt         → scitex_plt
scitex.stats       → scitex_stats
scitex.scholar     → scitex_scholar
scitex.writer      → scitex_writer
scitex.cloud       → scitex_cloud
scitex.container   → scitex_container
scitex.notebook    → scitex_notebook
scitex.notification → scitex_notification
scitex.audio       → scitex_audio
scitex.dataset     → scitex_dataset
scitex.app         → scitex_app
scitex.audit       → scitex_security
scitex.compat      → scitex_compat
scitex.repro       → scitex_repro
scitex.dict        → scitex_dict
scitex.str         → scitex_str
scitex.logging     → scitex_logging
scitex.browser     → scitex_browser
scitex.parallel    → scitex_parallel
scitex.path        → scitex_path
scitex.db          → scitex_db
scitex.types       → scitex_types
scitex.template    → scitex_template
scitex.benchmark   → scitex_benchmark
scitex.context     → scitex_context
scitex.cv          → scitex_cv
scitex.introspect  → scitex_introspect
scitex.msword      → scitex_msword
scitex.os          → scitex_os
scitex.security    → scitex_security
scitex.tex         → scitex_tex
scitex.etc         → scitex_etc
scitex.gists       → scitex_gists
```

Native sub-modules (live under `src/scitex/<name>/`):

```text
scitex.gen scitex.config scitex.decorators scitex.dsp scitex.gen
scitex.linalg scitex.module scitex.nn scitex.pd scitex.project
... (see src/scitex/ for the full list)
```

## Lazy loading

Every sub-module is wrapped by `_LazyModule` or `importlib.util.LazyLoader`.
`import scitex` is sub-second; sub-module bodies execute only on first
attribute access. Missing optional deps raise a friendly `ImportError`.

## Per-module documentation

Load the sister-package skill — e.g. `scitex-io`, `scitex-plt`,
`scitex-stats`, `scitex-scholar`, `scitex-writer`, `scitex-cloud`. The
umbrella does not duplicate that content.
