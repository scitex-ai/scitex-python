---
name: scitex
description: |
  [WHAT] Python umbrella that delegates scientific functionality to specialized installed packages and provides CLI/MCP integration entry points.
  [WHEN] Use when the user wants the all-in-one entry point, or asks for `import scitex`, `scitex.io`, `scitex.plt`, `@scitex.session`, or any `scitex.<sub>` access; defer to the relevant sister-package skill for sub-module specifics.
  [HOW] Inspect the installed version and command help, use `import scitex`, and consult the owning leaf package for detailed APIs and requirements.
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

# scitex — Python umbrella

Use SciTeX for shared entry points across installed scientific packages. The
umbrella delegates domain logic; the owning leaf's version and configuration
control the actual capability. Python API, CLI, MCP, skills and Hub Web APIs are
complementary ecosystem interfaces, not a promise that every leaf exposes all five.

## Start with the installed environment

```bash
scitex --version
scitex --help
scitex mcp --help
```

Help describes the command surface; runtime requirements need separate checks.
Use the selected leaf's guidance before running a business operation. Retrieve
only the skill/tool groups relevant to the task instead of injecting the whole
catalog into an agent's context.

## Reference pages

- [Installation](01_installation.md) — environments, extras and compatibility.
- [Quick start](02_quick-start.md) — a complete synthetic plotting example.
- [Python API](03_python-api.md) — selected entry points and source ownership.
- [CLI and MCP](04_cli-reference.md) — discovery and server configuration.

## Domain ownership

| Topic | Owning package |
|---|---|
| File I/O | scitex-io |
| Figures and recipes | figrecipe |
| Statistics | scitex-stats |
| Literature | scitex-scholar |
| Manuscripts | scitex-writer |
| Experiment lifecycle | scitex-session |
| Provenance | scitex-clew |
| Discovery, checks and skill tooling | scitex-dev |
| App primitives / GUI hosting | scitex-sdk / scitex-hub |

Source maps live in `scitex.re_export`, with facade setup in `scitex.__init__`.
Some older aliases remain for compatibility. Do not infer a supported CLI or
Web endpoint merely from a Python alias or installed distribution name.
