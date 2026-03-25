---
name: stx.module
description: Mark functions as SciTeX workspace modules with the @module decorator and collect structured outputs. Backward-compatibility shim — new code should use scitex_cloud.module.
---

# stx.module — Skills Index

`stx.module` is a backward-compatibility shim for `scitex_cloud.module`. New code should import from `scitex_cloud.module` directly.

## Sub-skills

| File | Description |
|------|-------------|
| [module-decorator.md](module-decorator.md) | @module decorator, output/html helpers, INJECTED sentinel, ModuleManifest, CLI runner |

## Quick Reference

```python
from scitex.module import module, output, html, INJECTED

@module(label="My Analysis", category="analysis")
def run(project=INJECTED, plt=INJECTED, logger=INJECTED):
    fig, ax = plt.subplots()
    output(fig, title="Result")

# Preferred (new code)
from scitex_cloud.module import module, output, html, INJECTED
```
