---
description: ArrayLike protocol for type annotations and is_array_like() runtime check; ColorLike type alias for matplotlib-compatible color specifications.
---

# Array and Color Types

## ArrayLike

Protocol type covering objects that behave like arrays: `list`, `tuple`, `np.ndarray`, `pd.Series`, `torch.Tensor`.

```python
from scitex.types import ArrayLike
import numpy as np

def compute_mean(data: ArrayLike) -> float:
    import numpy as np
    return np.mean(data)
```

---

## is_array_like

Runtime check for array-like objects.

```python
is_array_like(obj) -> bool
```

```python
import scitex as stx
import numpy as np

stx.types.is_array_like([1, 2, 3])          # True
stx.types.is_array_like(np.array([1, 2]))   # True
stx.types.is_array_like("hello")             # False
stx.types.is_array_like(42)                  # False
```

---

## ColorLike

Type alias for any matplotlib-compatible color specification:
- Named color string: `"red"`, `"blue"`
- Hex string: `"#FF0000"`
- RGB tuple: `(1.0, 0.0, 0.0)`
- RGBA tuple: `(1.0, 0.0, 0.0, 0.5)`

```python
from scitex.types import ColorLike

def paint(color: ColorLike) -> None:
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.axhline(0, color=color)
```
