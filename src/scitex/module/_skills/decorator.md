---
name: module-decorator
description: Decorate Python functions as SciTeX cloud modules with @module(), inject parameters automatically with INJECTED, and describe module metadata with ModuleManifest.
---

# Module Decorator

**Preferred import** (new code):
```python
from scitex_cloud.module import module, INJECTED, ModuleManifest
```

**Legacy import** (still works, emits DeprecationWarning):
```python
import scitex as stx
stx.module.module  # delegate to scitex_cloud.module
```

---

## @module

Decorator that registers a function as a SciTeX cloud module.

```python
from scitex_cloud.module import module, INJECTED

@module(
    name="my_analysis",
    description="Run EEG analysis pipeline",
    version="1.0.0",
)
def run(data_path: str, CONFIG=INJECTED, logger=INJECTED):
    """Analyze EEG data."""
    data = stx.io.load(data_path)
    # ... analysis ...
    return stx.module.output(result_df, "results")
```

---

## INJECTED

Sentinel value used as a default parameter to signal that the SciTeX runtime should inject the value automatically (e.g., `CONFIG`, `logger`, `rng`).

```python
from scitex_cloud.module import INJECTED

def my_func(CONFIG=INJECTED):
    print(CONFIG.learning_rate)
```

---

## ModuleManifest

Describes a module's inputs, outputs, and metadata for the SciTeX cloud registry.

```python
from scitex_cloud.module import ModuleManifest

manifest = ModuleManifest(
    name="my_analysis",
    inputs=["data_path"],
    outputs=["results"],
    version="1.0.0",
)
```
