---
description: |
  [TOPIC] Installation — scitex umbrella
  [DETAILS] Create an isolated environment, install declared dependencies normally, and select extras for the task. Verify installed versions and runtime capabilities separately.
tags: [scitex-installation]
---

# Installation — scitex

```bash
uv venv .venv
source .venv/bin/activate
uv pip install scitex
scitex --version
scitex --help
```

Use your shell's activation equivalent. Python and optional-provider requirements
are declared in package metadata; install an environment compatible with the
selected release. Select task extras from that release's `pyproject.toml`, for
example `uv pip install "scitex[scholar,writer]"`.

The base umbrella already declares several leaf dependencies. An extra adds its
own requirements; it does not imply that every leaf is optional or that every
integration is configured. Keep normal dependency resolution enabled.

## Compatibility and verification

The published 2.30.8 dependency set and the 2.30.9 source dependency set were
checked separately. Both provide the plotting quick start and MCP statistics
metadata discovery; their legacy skills CLI import of `scitex_dev.skills` fails.
Read installed skill files directly until using a release with compatible skill
dispatch. Do not assume a successful `--help` means the callback works.

No fixed installation duration or full `[all]` environment qualification is
claimed here. External services, credentials, browsers, compilers and container
runtimes follow the owning leaf's setup instructions.
