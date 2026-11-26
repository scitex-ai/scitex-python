---
description: |
  [TOPIC] Python API — scitex umbrella
  [DETAILS] Selected lazy Python facades, the session decorator and sentinel, and the owning source map. Domain APIs belong to leaf packages; availability is version-dependent.
tags: [scitex-python-api]
---

# Python API — scitex

```python
import scitex

print(scitex.__version__)
```

| Entry point | Responsibility | Owning package |
|---|---|---|
| `scitex.io` | Scientific file I/O | scitex-io |
| `scitex.plt` | Figures and recipes | figrecipe |
| `scitex.stats` | Statistical methods | scitex-stats |
| `scitex.scholar` | Literature tools | scitex-scholar |
| `scitex.writer` | Manuscript tools | scitex-writer |
| `scitex.session` | Decorator/module for experiment lifecycle | scitex-session |
| `scitex.clew` | Recorded provenance and verification | scitex-clew |

For injection into session-decorated functions, use `scitex.session.INJECTED`.
Top-level `scitex.INJECTED` is a deprecated compatibility alias. Follow the session
package's documented parameter and execution contracts.

The full source mapping is in `scitex.re_export.EXTERNAL_REEXPORTS`, with facade
initialization in `scitex.__init__`. Consult those sources instead of maintaining
a second exhaustive module list. Lazy access can import a leaf and its optional
requirements; it does not guarantee a fixed startup time or configured service.

A Python facade alone is not evidence of an installed CLI, MCP tool or Web API.
Check each interface in the actual environment before claiming availability.
