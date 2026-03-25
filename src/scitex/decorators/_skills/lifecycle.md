---
name: stx.decorators — Lifecycle and Metadata
description: Decorators for function lifecycle management: timeout protection, deprecation warnings, not-implemented stubs, docstring preservation, and basic wrapping.
---

# Lifecycle and Metadata Decorators

## `timeout`

Runs a function in a child process and raises `TimeoutError` if it does not complete within the given number of seconds.

```python
from scitex.decorators import timeout

@timeout(seconds=30)
def fetch_data(url: str):
    return requests.get(url).json()

@timeout(seconds=5, error_message="Database query took too long")
def slow_query(sql: str):
    return db.execute(sql)
```

**Signature:** `timeout(seconds: int = 10, error_message: str = "Timeout") -> decorator`

Parametric decorator — called with parentheses.

**Mechanism:** Uses `multiprocessing.Process` and `multiprocessing.Queue`.
1. Spawns a child process that calls the function and puts the result in a `Queue`.
2. The parent joins the child with `join(timeout=seconds)`.
3. If the child is still alive after the timeout, `process.terminate()` is called and `TimeoutError(error_message)` is raised.
4. Otherwise, the result is retrieved from the queue with `queue.get()`.

**Caveats:**
- Spawned process means function arguments and return values must be picklable.
- Does not work with lambda functions or locally-defined classes that cannot be pickled.
- On Windows, the spawn start method requires the call to be inside `if __name__ == "__main__":`.

---

## `deprecated`

Emits a `DeprecationWarning` when the decorated function is called. Optionally forwards all calls to a new function.

```python
from scitex.decorators import deprecated

# Simple warning only
@deprecated(reason="Use new_func() instead.")
def old_func(x):
    return x * 2

# Warning + automatic call forwarding
@deprecated(
    reason="Moved to scitex.session module.",
    forward_to="scitex.session.start"
)
def start_session(*args, **kwargs):
    pass  # body never executes when forwarding succeeds
```

**Signature:** `deprecated(reason: str = None, forward_to: str = None) -> decorator`

Parametric decorator — called with parentheses.

**Parameters:**
| param | type | description |
|---|---|---|
| `reason` | `str` | Human-readable deprecation message included in the warning. |
| `forward_to` | `str` | Dotted module path to forward calls to (e.g., `"scitex.io.save"`). Supports relative notation: `"..session.start"` resolves relative to the decorated function's module. |

**Behavior with `forward_to`:**
1. Emits `DeprecationWarning` with `reason`.
2. Dynamically imports the module and retrieves the function via `importlib.import_module` + `getattr`.
3. Calls the target function with the same `*args` and `**kwargs`.
4. If import or attribute lookup fails, emits a `RuntimeWarning` and falls back to the original deprecated function body.
5. Auto-generates a docstring that combines the deprecation notice with the target function's docstring (if available).

**Behavior without `forward_to`:**
1. Emits `DeprecationWarning` with `reason`.
2. Executes the original function body normally.

---

## `not_implemented`

Marks a function as not yet implemented. When called, emits a `FutureWarning` and returns `None` (does not raise an exception and does not execute the function body).

```python
from scitex.decorators import not_implemented

@not_implemented
def future_feature(x, y):
    # This body is never executed
    pass
```

**Signature:** `not_implemented(func: Callable) -> Callable`

No-argument decorator.

**Warning category:** `FutureWarning` (not `NotImplementedError` — the call silently returns `None`).

**Message format:** `"Attempt to use unimplemented method: '<name>'. This method is not yet available."`

Use case: placeholder stubs in public APIs that should exist in the interface but are not yet coded. Allows code that calls the function to continue without crashing.

---

## `preserve_doc`

Wraps a function while explicitly preserving its docstring using `functools.wraps`.

```python
from scitex.decorators import preserve_doc

@preserve_doc
def load_csv(path: str):
    """Load a CSV file and return a DataFrame."""
    return pd.read_csv(path)
```

**Signature:** `preserve_doc(loader_func: Callable) -> Callable`

No-argument decorator.

Functionally equivalent to applying `@functools.wraps` manually. Intended for documentation tooling pipelines where an explicit named decorator makes the intent clearer in source code.

---

## `wrap`

A minimal wrapper template that preserves function metadata and exposes the original function reference.

```python
from scitex.decorators import wrap

@wrap
def my_function(x):
    return x + 1

# Access original
my_function._original_func  # the unwrapped function
my_function._is_wrapper     # True
```

**Signature:** `wrap(func: Callable) -> Callable`

No-argument decorator.

Sets two attributes on the wrapper:
- `_original_func` — reference to the unwrapped function.
- `_is_wrapper = True` — flag for decorator-stack inspection.

Use case: template for building custom decorators, or when you need to mark a function as wrapped for downstream introspection without changing behavior.
