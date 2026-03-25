---
name: stx.utils.yield_grids / count_grids
description: Enumerate every combination of a parameter grid for hyperparameter or condition sweeps.
---

# stx.utils — Grid Search Utilities

Two functions for exhaustive parameter-grid iteration: `yield_grids` yields each combination as a dict, `count_grids` returns the total count without iterating.

## Signatures

```python
yield_grids(params_grid: dict, random: bool = False) -> Generator[dict, None, None]

count_grids(params_grid: dict) -> int
```

### Parameters — yield_grids

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `params_grid` | dict | required | Keys are parameter names; values are lists of candidate values |
| `random` | bool | False | If True, shuffle the combination order before yielding |

### Returns — yield_grids

Generator that yields one `dict` per combination. Each dict maps every key in `params_grid` to one of its candidate values.

### Parameters — count_grids

| Parameter | Type | Description |
|-----------|------|-------------|
| `params_grid` | dict | Same structure as for `yield_grids` |

### Returns — count_grids

`int` — product of the lengths of all value lists (total number of combinations).

## Implementation detail

`yield_grids` builds the full Cartesian product via `itertools.product`, optionally shuffles with `random.shuffle`, then yields dicts constructed with `zip`. The entire combination list is materialised in memory before yielding begins.

## Examples

### Basic sweep

```python
import scitex as stx

params_grid = {
    "lr": [1e-4, 1e-3, 1e-2],
    "batch_size": [32, 64, 128],
    "dropout": [0.1, 0.3, 0.5],
}

# How many runs?
n = stx.utils.count_grids(params_grid)
print(f"Total combinations: {n}")   # 27

# Iterate in order
for params in stx.utils.yield_grids(params_grid):
    print(params)
    # {'lr': 0.0001, 'batch_size': 32, 'dropout': 0.1}
    # {'lr': 0.0001, 'batch_size': 32, 'dropout': 0.3}
    # ...
```

### Random sweep (early stopping friendly)

```python
for params in stx.utils.yield_grids(params_grid, random=True):
    result = train(**params)
    if result["val_acc"] > 0.95:
        break   # stop early — combinations were randomised so no ordering bias
```

### Large machine-learning grid

```python
params_grid = {
    "batch_size": [2**i for i in range(3, 7)],   # 8, 16, 32, 64
    "n_channels": [2**i for i in range(3, 7)],   # 8, 16, 32, 64
    "seq_len":    [2**i for i in range(8, 13)],  # 256 … 4096
    "precision":  ["fp16", "fp32"],
    "device":     ["cpu", "cuda"],
}

print(stx.utils.count_grids(params_grid))  # 320

for p in stx.utils.yield_grids(params_grid, random=True):
    benchmark(**p)
```
