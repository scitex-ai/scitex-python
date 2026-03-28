---
description: Persistent disk caching (cache_disk, cache_disk_async) and in-memory LRU caching (cache_mem) decorators for expensive computations.
---

# Caching Decorators

## `cache_disk`

Persistent disk caching backed by `joblib.Memory`. Cache is keyed by a content hash of the function arguments, so repeated calls with the same inputs are served from disk.

```python
from scitex.decorators import cache_disk

@cache_disk
def expensive_compute(x, n_iter=100):
    # heavy computation
    return result
```

**Signature:** `cache_disk(func: Callable) -> Callable`

No-argument decorator — applied directly without parentheses.

**Cache location:** Reads from `scitex.config.get_paths().function_cache`. This resolves to the project's configured function-cache directory (see `stx.config`). The directory is created automatically by `joblib.Memory`.

**Implementation detail:** Creates a new `joblib.Memory(cache_dir, verbose=0)` instance at decoration time. On each call, wraps `func` with `memory.cache(func)` and calls the cached version. Joblib handles serialization, cache invalidation, and sub-directory layout internally.

**Invalidation:** There is no programmatic cache-clear API on the decorator itself. Clear the cache by deleting the directory at `get_paths().function_cache` or by using `joblib.Memory` directly.

---

## `cache_disk_async`

Same as `cache_disk` but for `async def` functions. The async function is wrapped in a synchronous executor so joblib (which is synchronous) can cache it.

```python
from scitex.decorators import cache_disk_async

@cache_disk_async
async def fetch_remote_data(url: str):
    async with aiohttp.ClientSession() as session:
        ...
    return data
```

**Signature:** `cache_disk_async(func: Callable) -> Callable`

No-argument decorator.

**Mechanism:**
1. A sync wrapper (`sync_wrapper`) calls `asyncio.run(func(...))` to execute the async function synchronously.
2. `sync_wrapper` is cached by `joblib.Memory`.
3. The outer `async_wrapper` (returned to the caller) runs the cached sync version inside `loop.run_in_executor(None, ...)` to avoid blocking the event loop.

**Limitation:** `asyncio.run()` inside the sync wrapper means this will fail if called from within an already-running event loop (e.g., Jupyter notebooks with existing loops). In that context use `cache_disk` with a synchronous wrapper instead.

**Cache location:** Same as `cache_disk` — `scitex.config.get_paths().function_cache`.

---

## `cache_mem`

In-memory LRU (Least Recently Used) cache. A direct alias for Python's standard-library `functools.lru_cache(maxsize=None)`.

```python
from scitex.decorators import cache_mem

@cache_mem
def compute(x: int, y: int) -> float:
    return heavy_math(x, y)
```

**Signature:** `cache_mem` is an alias for `functools.lru_cache(maxsize=None)` — unbounded cache.

**Requirements:** All arguments must be hashable (same constraint as `functools.lru_cache`). NumPy arrays, pandas DataFrames, and torch tensors are not hashable and will raise `TypeError`. Convert to tuples or use `cache_disk` for array-valued inputs.

**Cache introspection:**

```python
# View cache statistics
compute.cache_info()
# CacheInfo(hits=3, misses=5, maxsize=None, currsize=5)

# Clear the cache manually
compute.cache_clear()
```

**Lifetime:** Cache lives as long as the decorated function object exists (i.e., for the process lifetime). Data is not persisted across restarts.

---

## Choosing Between Cache Types

| Scenario | Recommendation |
|---|---|
| Heavy CPU computation, array inputs | `cache_disk` — survives process restarts |
| Fast helper with hashable scalar args | `cache_mem` — zero overhead, no I/O |
| Async I/O fetches (network, DB) | `cache_disk_async` — avoids redundant remote calls |
| Need cache invalidation control | `cache_disk` — delete cache directory to invalidate |
| Jupyter or interactive use | `cache_mem` — `cache_disk_async` has event-loop limitations |
