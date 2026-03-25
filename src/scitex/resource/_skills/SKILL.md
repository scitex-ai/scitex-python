---
name: stx.resource
description: System resource monitoring — one-shot CPU/RAM/GPU snapshots, time-series logging, and full hardware spec collection.
---

# stx.resource — Skills Index

Monitor system resources during scientific computations. Covers real-time usage snapshots, CSV time-series logging, and complete hardware/software specification collection.

## Sub-skills

| File | Description |
|------|-------------|
| [monitor.md](monitor.md) | get_processor_usages (CPU/RAM/GPU/VRAM DataFrame), log_processor_usages (CSV logging, background process) |
| [specs.md](specs.md) | get_specs (full dict or YAML), component helpers (_cpu_info, _memory_info, etc.) |

## Quick Reference

```python
from scitex.resource import get_processor_usages, get_specs, log_processor_usages

df = get_processor_usages()       # One-row DataFrame: CPU/RAM/GPU/VRAM
specs = get_specs(yaml=True)      # Full system specs as YAML string
log_processor_usages(
    "/tmp/usage.csv", limit_min=10, interval_s=1, background=True
)
```
