---
description: Common usage patterns for stx.parallel.run — batch file processing, multi-value returns, wrapping keyword arguments, and combining with stx.io.
---

# stx.parallel — Usage Patterns

## Pattern 1: Batch file processing

Process a directory of files concurrently.

```python
import scitex as stx
from pathlib import Path

def load_and_summarize(filepath):
    df = stx.io.load(filepath)
    return df.describe()

files = list(Path("data/").glob("*.csv"))
args_list = [(str(f),) for f in files]

summaries = stx.parallel.run(
    load_and_summarize,
    args_list,
    desc="Summarizing files",
)
```

## Pattern 2: Wrapping keyword-only arguments

`run` passes only positional arguments from each tuple. To pass keyword arguments, wrap the function in a closure or `functools.partial`.

```python
import scitex as stx
import functools

def analyze(path, *, method="mean", clip=True):
    ...

# Use functools.partial to bind keyword arguments
analyze_mean = functools.partial(analyze, method="mean", clip=True)

args_list = [("data/a.csv",), ("data/b.csv",)]
results = stx.parallel.run(analyze_mean, args_list)
```

Alternatively, wrap with a lambda:

```python
args_list = [("data/a.csv", "mean", True), ("data/b.csv", "median", False)]
results = stx.parallel.run(
    lambda path, method, clip: analyze(path, method=method, clip=clip),
    args_list,
)
```

## Pattern 3: Collecting multi-value results

When the worker function returns a tuple, `run` transposes automatically.

```python
import scitex as stx

def fit_model(subject_id, data_path):
    import numpy as np
    data = stx.io.load(data_path)
    coef = data.mean().values          # example
    r2 = float(np.corrcoef(data.T)[0, 1])
    return subject_id, coef, r2

args_list = [
    ("sub-01", "data/sub-01.csv"),
    ("sub-02", "data/sub-02.csv"),
    ("sub-03", "data/sub-03.csv"),
]

subject_ids, coefficients, r2_values = stx.parallel.run(fit_model, args_list)
# subject_ids   = ["sub-01", "sub-02", "sub-03"]
# coefficients  = [array(...), array(...), array(...)]
# r2_values     = [0.82, 0.91, 0.77]
```

## Pattern 4: Combining with @stx.session for reproducible batch runs

```python
import scitex as stx

def process_subject(subject_id, cfg):
    raw = stx.io.load(f"data/{subject_id}.csv")
    result = raw * cfg["scale"]
    stx.io.save(result, f"results/{subject_id}.csv")
    return subject_id, result.mean()

@stx.session
def main(CONFIG=stx.INJECTED, logger=stx.INJECTED):
    subject_ids = CONFIG.get("subjects", ["s01", "s02", "s03"])
    args_list = [(sid, CONFIG) for sid in subject_ids]

    ids, means = stx.parallel.run(
        process_subject,
        args_list,
        desc="Processing subjects",
    )
    logger.info(f"Processed {len(ids)} subjects, mean={sum(means)/len(means):.3f}")
    return 0
```

## Pattern 5: Limiting concurrency to avoid resource exhaustion

For disk-heavy or memory-heavy tasks, fewer workers can be faster than using all CPUs.

```python
import multiprocessing
import scitex as stx

# Use half the CPUs to leave headroom
n_jobs = max(1, multiprocessing.cpu_count() // 2)

results = stx.parallel.run(heavy_func, args_list, n_jobs=n_jobs)
```

## Ordering guarantee

Results are always returned in the same order as `args_list`, regardless of which future completes first. The implementation pre-allocates `results = [None] * len(args_list)` and uses the future-to-index mapping to place each result at the correct position.
