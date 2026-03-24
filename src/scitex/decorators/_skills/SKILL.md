---
name: stx.decorators
description: Function decorators for type conversion, caching, batching, timeouts, and array handling.
---

# stx.decorators

The `stx.decorators` module provides a rich set of Python decorators for scientific computing workflows. Key patterns include automatic type conversion between NumPy/PyTorch/Pandas, disk/memory caching, batch processing, and timeout protection.

## Python API

```python
import scitex as stx

# Type conversion decorators (auto-convert inputs, preserve output type)
@stx.decorators.numpy_fn
def my_func(arr):  # Always receives numpy array
    return arr.mean()

@stx.decorators.torch_fn
def my_func(tensor):  # Always receives torch tensor
    return tensor.mean()

@stx.decorators.pandas_fn
def my_func(df):  # Always receives DataFrame
    return df.describe()

# Batch processing
@stx.decorators.batch_fn(batch_size=32)
def process(batch):
    return model(batch)

# Caching
@stx.decorators.cache_disk(cache_dir="~/.cache")
def expensive_compute(x):
    return slow_function(x)

@stx.decorators.cache_mem(maxsize=128)
def fast_cached(x):
    return compute(x)

# Timeout protection
@stx.decorators.timeout(seconds=30)
def slow_io():
    return fetch_data()

# Mark as not implemented
@stx.decorators.not_implemented
def future_feature():
    pass
```

## Key Features

- Type converters: `numpy_fn`, `torch_fn`, `pandas_fn`, `xarray_fn` — auto-convert inputs and preserve output types
- `batch_fn` — split inputs into batches, combine outputs
- `cache_disk` / `cache_disk_async` — persistent disk caching with hash-based keys
- `cache_mem` — in-memory LRU caching
- `timeout(seconds)` — raise `TimeoutError` if function exceeds limit
- `deprecated(new_name)` — emit `DeprecationWarning` with migration guidance
- `AutoOrderDecorator` — automatic argument ordering for broadcasting-style functions
