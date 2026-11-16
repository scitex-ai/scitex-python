---
description: Selected SciTeX provider CLI paths with installed-owner discovery and safe help examples; leaf help remains authoritative for operations and flags.
---

# Provider workflows

Use selected help to learn the owning package's actual commands and flags:

```bash
scitex io --help
scitex stats --help
scitex scholar --help
scitex writer --help
scitex sdk --help
scitex cards --help
scitex clew --help
scitex ssh tunnel --help
```

These are conditional provider paths, not a promise that every package is
installed or operational. The leaf's implementation and skill are authoritative
for its operations. Research verification belongs under `clew`; developer and
security auditing belong under `scitex dev`.

```bash
scitex dev audit --help
scitex dev linter --help
scitex dev pkg --help
scitex dev template --help
scitex dev resource --help
```

Only eligible providers are exposed. A Python-only utility such as `dict` or
`types` remains a Python API without a fabricated module-named command.
CLI-only declines leave other independently provided interfaces unchanged.
