---
description: SciTeX console entry point, metadata discovery, canonical paths and independent exposure states.
---

# Core CLI discovery

The packaging entry point is `scitex.__main__:main`, which checks CLI
dependencies and delegates to the Click group in `scitex.cli.main`.

```bash
scitex --version
scitex --help
scitex --json
scitex dev cli list --package scitex-sdk --json
```

The shared `scitex_dev.cli_providers.list_cli_providers` reader inspects the
same interpreter's installed metadata without loading provider entry points.
An owner can declare `scitex.cli` capability metadata or explicitly decline
its CLI name. Legacy canonical console evidence remains labelled unverified.
The umbrella applies naming and retirement policy to eligible declarations.

Normal help, JSON and completion use visible metadata. A requested provider
parser is loaded lazily. An ordinary declared console launcher runs in a child
only when invoked. Recursive inspection may load several parser modules.

Developer tools belong under `scitex dev`; use `scitex dev --help`. The
canonical products include `sdk`, `cards`, `clew` and `ssh`. The exact set is
environment-dependent. CLI exposure does not imply Python import availability,
MCP enablement, hosted API admission or client-loaded skill context.
