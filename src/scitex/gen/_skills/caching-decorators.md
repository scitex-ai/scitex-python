---
name: gen-caching-decorators
description: Decorator and kwarg utilities in stx.gen — cache (lru_cache alias), alternate_kwarg for accepting multiple keyword names, and wrap (functools.wraps pass-through).
---

# Caching and Decorator Utilities

---

## cache

An alias for `functools.lru_cache(maxsize=None)` — an unbounded memoization decorator.

```python
cache = lru_cache(maxsize=None)
```

```python
import scitex as stx

@stx.gen.cache
def expensive_fn(n: int) -> int:
    return sum(range(n))

expensive_fn(1_000_000)  # computed
expensive_fn(1_000_000)  # cached — instant
```

Because `maxsize=None`, the cache grows without bound. For bounded caches, use `functools.lru_cache(maxsize=N)` directly.

> **Note:** Cached functions cannot have mutable (unhashable) arguments (e.g., lists, dicts, numpy arrays).

---

## alternate_kwarg

Allows a function to accept two different keyword argument names for the same parameter. If the primary key is absent or falsy, the alternate key's value is used.

```python
alternate_kwarg(kwargs: dict, primary_key: str, alternate_key: str) -> dict
```

| Parameter | Description |
|-----------|-------------|
| `kwargs` | The `**kwargs` dict to mutate |
| `primary_key` | The canonical/preferred keyword name |
| `alternate_key` | The legacy/alternative keyword name |

The `alternate_key` is **popped** from `kwargs`. If `primary_key` is already set (and truthy), `alternate_key` is discarded. If `primary_key` is absent/falsy, it is set to the `alternate_key` value.

```python
import scitex as stx

def my_func(**kwargs):
    kwargs = stx.gen.alternate_kwarg(kwargs, "learning_rate", "lr")
    lr = kwargs.get("learning_rate")
    return lr

my_func(learning_rate=0.01)  # 0.01
my_func(lr=0.001)            # 0.001  — "lr" is mapped to "learning_rate"
my_func(learning_rate=0.01, lr=0.001)  # 0.01 — primary wins
```

**Typical pattern when wrapping a library function:**

```python
def fit(X, y, **kwargs):
    kwargs = stx.gen.alternate_kwarg(kwargs, "n_estimators", "n_trees")
    kwargs = stx.gen.alternate_kwarg(kwargs, "random_state", "seed")
    return sklearn_model.fit(X, y, **kwargs)
```

---

## wrap

A minimal `functools.wraps`-based decorator factory that preserves the wrapped function's metadata.

```python
wrap(func: callable) -> callable
```

Returns a wrapper that calls `func(*args, **kwargs)` and preserves `__name__`, `__doc__`, etc. via `@functools.wraps(func)`.

```python
import scitex as stx

@stx.gen.wrap
def add(a, b):
    """Add two numbers."""
    return a + b

add.__name__   # "add"
add.__doc__    # "Add two numbers."
add(1, 2)     # 3
```

This is intentionally minimal — use it when you want to add decoration infrastructure without changing behavior yet.
