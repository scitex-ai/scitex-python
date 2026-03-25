---
name: stx.decorators — Batch Processing
description: batch_fn decorator and combined batch+type-conversion decorators for splitting large inputs into mini-batches and combining results.
---

# Batch Processing Decorators

## `batch_fn`

Splits the first positional argument along its length into fixed-size chunks, runs the function on each chunk, then concatenates results.

```python
from scitex.decorators import batch_fn

@batch_fn
def process(x, scale=1.0):
    return x * scale  # receives a slice of x each iteration

result = process(large_array, scale=2.0, batch_size=32)
```

**Signature:** `batch_fn(func: Callable) -> Callable`

The decorated function accepts one extra keyword argument:

| kwarg | type | default | description |
|---|---|---|---|
| `batch_size` | `int` | `4` | number of samples per batch |

`batch_size` is popped from kwargs before being forwarded to `func` (unless `func` explicitly accepts `batch_size` in its signature, in which case it is forwarded).

### Batching Behavior

- If `len(x) <= batch_size`, the function is called once with the whole input (no looping).
- Otherwise, iterates over `ceil(len(x) / batch_size)` batches using `tqdm` for progress display.
- Slicing: `x[start:end]` — works with any object that supports length and slicing (numpy arrays, torch tensors, lists, pandas DataFrames).

### Result Combination

| Batch result type | Combination method |
|---|---|
| `torch.Tensor` (0-D) | `torch.stack(results)` |
| `torch.Tensor` (n-D) | `torch.vstack(results)` |
| `np.ndarray` (0-D) | `np.array(results)` |
| `np.ndarray` (n-D) | `np.vstack(results)` |
| `tuple` of tensors/arrays | each element stacked individually |
| `tuple` with non-tensor elements | first batch's non-tensor elements reused |
| `int` or `float` | `np.array(results)` |
| `list` | concatenated via `sum(results, [])` |

GPU tensors are moved to CPU (`.cpu()`) before collection to avoid OOM errors during accumulation.

### Recommended Decorator Order

When combining with a type-conversion decorator, apply `batch_fn` **outermost** (written first in the decorator stack) and the type decorator **innermost** (written last):

```python
@batch_fn   # outer — splits input
@torch_fn   # inner — converts each batch to tensor
def my_func(x):
    return x.mean()
```

This ensures each mini-batch is converted to the target type individually rather than trying to convert the full dataset at once.

---

## Combined Decorators

`_combined.py` ships pre-built combinations that enforce the correct order. Use these instead of stacking manually when you need both type conversion and batching:

| Name | Equivalent to | Aliases |
|---|---|---|
| `torch_batch_fn` | `@torch_fn` + `@batch_fn` | `batch_torch_fn` |
| `numpy_batch_fn` | `@numpy_fn` + `@batch_fn` | `batch_numpy_fn` |
| `pandas_batch_fn` | `@pandas_fn` + `@batch_fn` | `batch_pandas_fn` |

```python
from scitex.decorators import torch_batch_fn, numpy_batch_fn, pandas_batch_fn

@torch_batch_fn
def model_forward(x, dim=None):
    return x.mean(dim=dim)

@numpy_batch_fn
def compute_stats(x, axis=None):
    return x.mean(axis=axis)

@pandas_batch_fn
def summarize(df):
    return df.describe()
```

All three are equivalent to writing:

```python
@wraps(func)
@torch_fn   # or numpy_fn / pandas_fn
@batch_fn
def wrapper(*args, **kwargs):
    return func(*args, **kwargs)
```

---

## Auto-Order System

`_auto_order.py` provides `AutoOrderDecorator`, which makes decorator ordering irrelevant. When enabled, `batch_fn`, `torch_fn`, `numpy_fn`, and `pandas_fn` become `AutoOrderDecorator` instances that collect applied decorators and always apply them in the correct fixed order on first call.

```python
from scitex.decorators import enable_auto_order, disable_auto_order

enable_auto_order()

# These two are now identical at runtime:
@batch_fn
@torch_fn
def func1(x):
    return x.mean()

@torch_fn
@batch_fn   # written in wrong order — auto-corrected
def func2(x):
    return x.mean()

disable_auto_order()  # restore original decorators
```

**Priority constants** (higher = applied first / innermost):

| Decorator | Priority |
|---|---|
| `torch_fn` | 100 |
| `numpy_fn` | 100 |
| `pandas_fn` | 100 |
| `batch_fn` | 10 |

Auto-ordering works via lazy application: decorators are collected into `func._pending_decorators` list, then sorted by priority and applied on the **first function call**, not at decoration time. After the first call `_pending_decorators` is replaced by `_final_func`.

`enable_auto_order()` / `disable_auto_order()` mutate `scitex.decorators` module globals in-place.
