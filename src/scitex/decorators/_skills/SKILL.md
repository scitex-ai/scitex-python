---
name: stx.decorators
description: Function decorators for automatic type conversion, batch processing, caching, timeout protection, deprecation, and lifecycle management. Use when writing scientific computing functions that need to accept multiple array types or require performance optimizations.
---

# stx.decorators

The `stx.decorators` module provides a focused set of Python decorators for scientific computing workflows. All decorators are accessible as `stx.decorators.<name>` or via direct import from `scitex.decorators`.

## Sub-skills

### Type Conversion
- [type-conversion.md](type-conversion.md) — `numpy_fn`, `torch_fn`, `pandas_fn`, `xarray_fn`, `signal_fn`: auto-convert inputs to a target array type and restore the caller's original type on output. Includes `to_numpy`, `to_torch`, `is_torch`, `is_cuda` utilities.

### Batch Processing
- [batch-processing.md](batch-processing.md) — `batch_fn`, `torch_batch_fn`, `numpy_batch_fn`, `pandas_batch_fn` (and their aliases): split large inputs into mini-batches, process each batch, and concatenate results. Includes `AutoOrderDecorator`, `enable_auto_order`, `disable_auto_order` for order-independent stacking.

### Caching
- [caching.md](caching.md) — `cache_disk`, `cache_disk_async`, `cache_mem`: persistent joblib-backed disk cache for sync and async functions; unbounded in-memory LRU cache for hashable-argument functions.

### Lifecycle and Metadata
- [lifecycle.md](lifecycle.md) — `timeout`, `deprecated`, `not_implemented`, `preserve_doc`, `wrap`: timeout protection via child process, deprecation forwarding, not-implemented stubs, and docstring preservation helpers.

## Quick Reference

```python
import scitex as stx

# --- Type conversion ---
@stx.decorators.numpy_fn
def compute(arr):          # always np.ndarray inside
    return arr.mean(axis=0)

@stx.decorators.torch_fn
def model_step(x, dim=0):  # always torch.Tensor, auto-CUDA
    return x.mean(dim=dim)

@stx.decorators.pandas_fn
def describe(df):          # always pd.DataFrame inside
    return df.describe()

@stx.decorators.signal_fn
def bandpass(signal, fs, low_hz, high_hz):
    # only signal (first arg) converted; fs etc. stay as scalars
    ...

# --- Batch processing ---
@stx.decorators.batch_fn
def process(x, scale=1.0):
    return x * scale

result = process(big_array, scale=2.0, batch_size=64)

# --- Combined: type conversion + batching ---
@stx.decorators.torch_batch_fn
def forward(x):
    return x.mean()

# --- Auto-order (decorator order no longer matters) ---
stx.decorators.enable_auto_order()

@stx.decorators.batch_fn
@stx.decorators.torch_fn   # order irrelevant — auto-corrected at first call
def func(x):
    return x.mean()

# --- Caching ---
@stx.decorators.cache_disk
def expensive(x):          # persisted to disk via joblib
    return slow_compute(x)

@stx.decorators.cache_disk_async
async def fetch(url):      # async version, cached to disk
    ...

@stx.decorators.cache_mem
def fast_helper(n: int):   # in-memory LRU, unbounded
    return compute(n)

# --- Lifecycle ---
@stx.decorators.timeout(seconds=30)
def slow_io():
    return fetch_data()

@stx.decorators.deprecated(reason="Use new_api().", forward_to="mymod.new_api")
def old_api(*args, **kwargs):
    pass

@stx.decorators.not_implemented
def future_feature():
    pass
```

## All Exported Names

```
AutoOrderDecorator    ConversionWarning     batch_fn
batch_numpy_fn        batch_pandas_fn       batch_torch_fn
cache_disk            cache_disk_async      cache_mem
deprecated            disable_auto_order    enable_auto_order
is_cuda               is_nested_decorator   is_torch
not_implemented       numpy_batch_fn        numpy_fn
pandas_batch_fn       pandas_fn             preserve_doc
session               signal_fn             timeout
to_numpy              to_torch              torch_batch_fn
torch_fn              wrap                  xarray_fn
```

(`session` is a lazy re-export of `scitex.session` to avoid circular imports.)
