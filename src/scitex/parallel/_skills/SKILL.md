---
name: stx.parallel
description: Parallel execution for stx — run a function across many input tuples concurrently using ThreadPoolExecutor, with ordered results and a tqdm progress bar.
user-invocable: false
---

# stx.parallel

The `stx.parallel` module exposes a single function, `run`, for concurrently executing a callable over a list of argument tuples. Results are always returned in input order.

Accessed via `import scitex as stx` then `stx.parallel.run(...)`.

## Public API

| Name | Description |
|------|-------------|
| `stx.parallel.run` | Parallel map over a list of argument tuples |

## Sub-skills

### Core function
- [run.md](run.md) — Full signature, parameters, return types, error conditions, and concrete examples for `stx.parallel.run`

### Patterns
- [patterns.md](patterns.md) — Recipes for batch file processing, keyword argument wrapping, multi-value result collection, session integration, and concurrency tuning

## Quick reference

```python
import scitex as stx

# Single-value function
results = stx.parallel.run(func, [(arg1,), (arg2,), (arg3,)])

# Multi-value function — automatic transpose
xs, ys = stx.parallel.run(func_returning_tuple, args_list)

# Control workers
results = stx.parallel.run(func, args_list, n_jobs=4, desc="My task")
```

## Key behaviours

- `n_jobs=-1` uses all available CPU cores (auto-detected via `multiprocessing.cpu_count()`)
- Results preserve input order regardless of completion order
- Functions returning a `tuple` trigger automatic transpose: one list per return position
- Backend is `ThreadPoolExecutor` — best for I/O-bound work
- Empty `args_list` or non-callable `func` raises `ValueError` immediately
- `n_jobs > cpu_count` emits a warning but proceeds normally
