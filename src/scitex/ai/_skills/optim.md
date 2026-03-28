---
description: Optimizer utilities — get_optimizer by name, set_optimizer for one or multiple models, with optional Ranger deep learning optimizer.
---

# Optimizer Utilities

## get_optimizer()

```python
def get_optimizer(name: str) -> type
```

Returns an optimizer **class** (not instance) by name.

### Parameters
- `name` — Optimizer name. Supported: `"adam"`, `"rmsprop"`, `"sgd"`, `"ranger"`

### Return value
Optimizer class (e.g. `torch.optim.Adam`).

### Raises
- `ValueError` — If name is not in the supported list
- `ImportError` — If `"ranger"` is requested but `pytorch-optimizer` is not installed

### Ranger availability

`"ranger"` uses `pytorch_optimizer.Ranger21` if available, falling back to a vendored `Ranger` implementation. Install with:

```bash
pip install pytorch-optimizer
```

---

## set_optimizer()

```python
def set_optimizer(
    models,
    optimizer_name: str,
    lr: float,
) -> torch.optim.Optimizer
```

Convenience function that collects parameters from one or more models and returns a configured optimizer instance.

### Parameters
- `models` — Single `nn.Module` or list of `nn.Module` instances. All learnable parameters are pooled
- `optimizer_name` — Name string (same as `get_optimizer`)
- `lr` — Learning rate

### Return value
Configured optimizer instance.

### Example

```python
import scitex as stx

# Single model
optimizer = stx.ai.set_optimizer(model, "adam", lr=1e-3)

# Multiple models (pooled parameters)
optimizer = stx.ai.set_optimizer(
    [encoder, classifier],
    "adam",
    lr=1e-4,
)

# Ranger optimizer (requires pytorch-optimizer)
optimizer = stx.ai.set_optimizer(model, "ranger", lr=1e-3)
```

---

## get_set.py (advanced)

`scitex.ai.optim._get_set` provides lower-level helpers for getting/setting optimizer state. Import directly if needed:

```python
from scitex.ai.optim._get_set import get_lr, set_lr
```
