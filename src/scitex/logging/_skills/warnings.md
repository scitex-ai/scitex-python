---
description: SciTeX warning system — emit, filter, and control warnings integrated with the logging infrastructure.
---

# Warnings

A warning system modelled after Python's `warnings` module but integrated with `stx.logging`. Warnings are emitted through the logging system (at `WARNING` level) rather than `sys.stderr`.

## Warning categories

```
SciTeXWarning (base, inherits UserWarning)
├── UnitWarning          — axis label unit issues (missing units, parentheses vs brackets, division vs negative exponent)
├── StyleWarning         — style/formatting issues
├── SciTeXDeprecationWarning — deprecated SciTeX features
├── PerformanceWarning   — performance issues
└── DataLossWarning      — potential data loss
```

## warn()

```python
stx.logging.warn(message, category=SciTeXWarning, stacklevel=2)
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `message` | str | required | Warning message text |
| `category` | type | `SciTeXWarning` | Warning class |
| `stacklevel` | int | `2` | Stack depth for source location tracking |

**Behavior by action**

| Action | Result |
|--------|--------|
| `"ignore"` | Silently suppressed |
| `"error"` | Raises `category(message)` as an exception |
| `"always"` | Always logs |
| `"default"` | Logs once per call site (filename + line number) |
| `"once"` | Logs once total (per message + category + location) |
| `"module"` | Logs once per source file |

Default action is `"default"`.

## filterwarnings()

```python
stx.logging.filterwarnings(action, category=SciTeXWarning, message=None)
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `action` | str | required | One of: `"ignore"`, `"error"`, `"always"`, `"default"`, `"once"`, `"module"` |
| `category` | type | `SciTeXWarning` | Warning class to apply the filter to. Subclasses are matched via `issubclass` |
| `message` | str or None | `None` | (Not yet implemented) regex pattern to match message text |

## resetwarnings()

```python
stx.logging.resetwarnings()
```

Clears all filters and the set of already-seen warnings, restoring default behavior.

## Convenience functions

```python
stx.logging.warn_deprecated(old_name, new_name, version=None)
# Emits: "{old_name} is deprecated. Use {new_name} instead. [Will be removed in version {version}.]"

stx.logging.warn_performance(operation, suggestion)
# Emits: "Performance warning in {operation}: {suggestion}"

stx.logging.warn_data_loss(operation, detail)
# Emits: "Potential data loss in {operation}: {detail}"
```

All convenience functions use `stacklevel=3` so the warning points to the caller's caller.

## Examples

```python
import scitex as stx
from scitex.logging import UnitWarning, DataLossWarning

# Emit a unit warning
stx.logging.warn("X axis label missing units", UnitWarning)
# Console: WARN: UnitWarning: X axis label missing units

# Suppress unit warnings globally
stx.logging.filterwarnings("ignore", category=UnitWarning)
stx.logging.warn("Still missing units")  # silenced

# Raise as exception for strict mode
stx.logging.filterwarnings("error", category=UnitWarning)
try:
    stx.logging.warn("Missing units", UnitWarning)
except UnitWarning as e:
    print(f"Caught: {e}")

# Reset to defaults
stx.logging.resetwarnings()

# Deprecation helper
stx.logging.warn_deprecated("stx.plt.old_func", "stx.plt.new_func", version="3.0")

# Data loss helper
stx.logging.warn_data_loss("downsampling", "reducing from 1000 to 100 samples")

# Importing categories directly
from scitex.logging import SciTeXDeprecationWarning, PerformanceWarning
stx.logging.filterwarnings("once", category=PerformanceWarning)
```
