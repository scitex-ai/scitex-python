---
name: scitex
description: |
  [WHAT] Umbrella package that lazy-re-exports every standalone SciTeX sister package (io, plt, stats, scholar, writer, cloud, container, ...) under one `import scitex` namespace.
  [WHEN] Use when the user wants the all-in-one entry point, or asks for `import scitex`, `scitex.io`, `scitex.plt`, `@scitex.session`, or any `scitex.<sub>` access; defer to the relevant sister-package skill for sub-module specifics.
  [HOW] `pip install scitex` then `import scitex`; sub-modules load lazily on first attribute access (see `src/scitex/__init__.py`).
tags: [scitex]
allowed-tools: mcp__scitex__*
primary_interface: python
interfaces:
  python: 3
  cli: 1
  mcp: 2
  skills: 3
  http: 0
---

# scitex — umbrella package

`scitex` is the user-facing aggregator for the SciTeX ecosystem. Each
sister package (`scitex_io`, `scitex_plt`, `scitex_stats`, ...) ships
independently on PyPI; the umbrella re-exports them lazily so a single
`import scitex` exposes the whole stack with sub-second startup.

## Mechanics

- External standalones are registered via `_EXTERNAL_REEXPORTS` and
  wrapped with `importlib.util.LazyLoader` so `scitex.io`, `scitex.plt`,
  etc. resolve to the top-level `scitex_<short>` package only on first
  attribute access.
- Native sub-modules (`scitex.gen`, `scitex.config`, ...) live under
  `src/scitex/<name>/` and are wrapped by `_LazyModule`.
- `scitex.session` is a `_CallableModuleWrapper` so `@scitex.session` works
  as both a decorator and a module.

See `src/scitex/__init__.py` for the full mapping.

## Sub-skills index

The umbrella does not duplicate sister-package documentation. For
package-specific guidance, load the corresponding skill:

| Topic | Skill |
|-------|-------|
| Universal I/O | `scitex-io` |
| Plotting | `scitex-plt` (thin shim over `figrecipe`) |
| Statistics | `scitex-stats` |
| Scholar / literature | `scitex-scholar` |
| Manuscript writer | `scitex-writer` |
| Cloud platform | `scitex-cloud` |
| Containers | `scitex-container` |
| Notebook reproducibility | `scitex-notebook` |
| Notifications | `scitex-notification` |
| Audio / TTS | `scitex-audio` |
| Datasets | `scitex-dataset` |
| Linter | `scitex-linter` |
| Dev tooling | `scitex-dev` |
| Ecosystem standards | `scitex / general` |

## Quick reference

```python
import scitex

@scitex.session
def main(CONFIG=scitex.INJECTED, plt=scitex.INJECTED, logger=scitex.INJECTED):
    fig, ax = scitex.plt.subplots()
    ax.plot_line(x, y)
    scitex.io.save(fig, "plot.png")    # auto-exports plot.csv
    return 0
```

## Mandatory leaves

- [01_installation.md](01_installation.md) — `pip install scitex` + extras
- [02_quick-start.md](02_quick-start.md) — minimal `@scitex.session` script
- [03_python-api.md](03_python-api.md) — top-level `scitex.*` surface
- [04_cli-reference.md](04_cli-reference.md) — `scitex` console entry

## MCP

Sister-package MCP tools are mounted under namespaced prefixes
(`io_*`, `plt_*`, `stats_*`, `scholar_*`, ...) on the umbrella server
exposed by `scitex.mcp_server`.
