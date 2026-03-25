---
description: Run a function in parallel across a list of argument tuples using ThreadPoolExecutor, with automatic CPU detection, ordered results, and a tqdm progress bar.
---

# stx.parallel.run

Execute a callable concurrently across many argument tuples. Results are returned in the same order as the input list regardless of completion order.

## Signature

```python
stx.parallel.run(
    func: Callable,
    args_list: List[tuple],
    n_jobs: int = -1,
    desc: str = "Processing",
) -> List[Any]
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `func` | `Callable` | required | Function to call for each item |
| `args_list` | `List[tuple]` | required | Each tuple is unpacked as positional arguments for one call |
| `n_jobs` | `int` | `-1` | Worker threads. `-1` = all CPUs. Must be `>= 1` or `-1` |
| `desc` | `str` | `"Processing"` | Label shown in the `tqdm` progress bar |

## Return value

- **Single-value functions** — returns `List[Any]`, one element per input tuple.
- **Multi-value functions** (function returns a `tuple`) — returns a `tuple` of lists, one list per return-value position (transposed). This makes it easy to unpack parallel outputs into separate variables.

## Constraints and error conditions

| Condition | Behaviour |
|-----------|-----------|
| `args_list` is empty | raises `ValueError("Args list cannot be empty")` |
| `func` is not callable | raises `ValueError("Func must be callable")` |
| `n_jobs == 0` or `n_jobs < -1` | raises `ValueError("n_jobs must be >= 1 or -1")` |
| `n_jobs > cpu_count` | emits `warnings.warn(...)` but continues |

## Backend

Uses `concurrent.futures.ThreadPoolExecutor`. This is well-suited for I/O-bound work (file reading, network calls). For CPU-bound work, Python's GIL limits true parallelism; consider splitting work explicitly or using `multiprocessing` outside this helper.

## Examples

### Basic: single-value function

```python
import scitex as stx

def add(x, y):
    return x + y

args_list = [(1, 4), (2, 5), (3, 6)]
results = stx.parallel.run(add, args_list)
# [5, 7, 9]
```

### Using all CPUs (default)

```python
import scitex as stx

def process_file(path, threshold):
    import pandas as pd
    df = pd.read_csv(path)
    return df[df["value"] > threshold]

args_list = [
    ("data/a.csv", 0.5),
    ("data/b.csv", 0.5),
    ("data/c.csv", 0.5),
]
dataframes = stx.parallel.run(process_file, args_list, n_jobs=-1)
```

### Fixed worker count with custom progress label

```python
results = stx.parallel.run(
    my_func,
    args_list,
    n_jobs=4,
    desc="Computing features",
)
```

### Multi-value return: automatic transpose

When the function returns a tuple, `run` transposes the results so each return position becomes its own list.

```python
import scitex as stx

def compute(x):
    return x * 2, x ** 2        # returns (doubled, squared)

args_list = [(1,), (2,), (3,)]
doubled, squared = stx.parallel.run(compute, args_list)
# doubled = [2, 4, 6]
# squared = [1, 4, 9]
```

### Single-argument functions

Even for single-argument functions, each element of `args_list` must be a tuple.

```python
import scitex as stx

def square(x):
    return x * x

# Correct — each item is a 1-tuple
results = stx.parallel.run(square, [(1,), (2,), (3,)])
# [1, 4, 9]
```
