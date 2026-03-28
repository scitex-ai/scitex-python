---
skill: stats.scitex_integration
description: SciTeX-specific integration — bundle save/load, figrecipe annotations, and Stats schema conversion.
---

# stx.stats — SciTeX integration

These features are implemented in `scitex/stats/_integration.py` and
`scitex/stats/_figrecipe_integration.py`. They live in `scitex-python` (not
`scitex-stats`) because they depend on `scitex.io.bundle` and `figrecipe`.

## Stats bundle — save and load

```python
import numpy as np
import scitex as stx

g1 = np.random.randn(30)
g2 = np.random.randn(30) + 0.8

result = stx.stats.test_ttest_ind(g1, g2)

# Save one or more results as a .stats bundle
stx.stats.save_stats(
    [result],
    "analysis/comparison.stats.zip",
    as_zip=True,
)

# Load back — returns flat dict for easy inspection
data = stx.stats.load_stats("analysis/comparison.stats.zip")
# data = {
#   "comparisons": [
#     {"name": "comparison", "method": "t-test",
#      "p_value": 0.003, "effect_size": 0.8,
#      "ci95": [0.2, 1.4], "formatted": "**"}
#   ],
#   "metadata": {...}
# }
```

### Directory bundle (non-ZIP)

```python
stx.stats.save_stats([result], "analysis/comparison.stats/", as_zip=False)
data = stx.stats.load_stats("analysis/comparison.stats/")
```

## Convert result to Stats schema

`test_result_to_stats` converts a raw `scitex.stats` result dict into the
typed `Stats` schema from `scitex.io.bundle`.

```python
from scitex.stats import test_result_to_stats

stats = test_result_to_stats(result)
# Returns Stats(analyses=[Analysis(method=..., results=..., inputs=...)])

# The Stats object can be attached to a Bundle
from scitex.io.bundle import Bundle
b = Bundle("analysis.stats/", create=True, bundle_type="stats")
b.stats = stats
b.save()
```

`BUNDLE_AVAILABLE` indicates whether `scitex.io.bundle.Stats` is importable:

```python
from scitex.stats import BUNDLE_AVAILABLE
if BUNDLE_AVAILABLE:
    stats_obj = test_result_to_stats(result)
```

## figrecipe format conversion

```python
result = stx.stats.test_ttest_ind(g1, g2)

# Convert to figrecipe-compatible format
fr_stats = stx.stats.to_figrecipe(result)
# Returns {"comparisons": [...]} suitable for figrecipe.utils.annotate_from_stats

# Or convert a list of results
fr_stats = stx.stats.to_figrecipe([result1, result2, result3])
```

Requires `figrecipe >= 0.13.0`.

## Annotating plots with significance markers

```python
import scitex.plt as plt

fig, ax = plt.subplots(width_mm=80, height_mm=60)
# ... (plot data here) ...

result = stx.stats.test_ttest_ind(g1, g2)

# Add significance brackets to the plot
artists = stx.stats.annotate(
    ax,
    result,
    positions={"control": 0, "treatment": 1},  # group name -> x position
    style="stars",    # "stars", "p_value", or "both"
)
```

## Load-and-annotate workflow

When stats are pre-computed and saved as a bundle, `load_and_annotate` combines
the load and annotate steps:

```python
# Save stats first
stx.stats.save_stats([result], "analysis.stats.zip", as_zip=True)

# Later, on a different figure or in a different session
fig, ax = plt.subplots()
# ... (reproduce the plot) ...

artists = stx.stats.load_and_annotate(
    ax,
    "analysis.stats.zip",
    positions={"control": 0, "treatment": 1},
    style="stars",
)
```

This makes it possible to separate statistical analysis from figure generation —
each step can be in its own script.

## Posthoc tests

```python
# Run posthoc pairwise comparisons after an omnibus test
ph_results = stx.stats.posthoc(g1, g2, g3, method="tukey")
# Returns DataFrame with group pairs and adjusted p-values
```

## Submodule reference

| attribute | source | description |
|---|---|---|
| `stx.stats.auto` | scitex-stats | decision rules, `recommend_tests` internals |
| `stx.stats.correct` | scitex-stats | multiple comparison correction module |
| `stx.stats.descriptive` | scitex-stats | `ci`, `sem`, `iqr`, etc. |
| `stx.stats.effect_sizes` | scitex-stats | `cohen_d`, `eta_squared`, `odds_ratio` |
| `stx.stats.power` | scitex-stats | power analysis and sample size planning |
| `stx.stats.posthoc` | scitex-stats | posthoc pairwise comparison module |
| `stx.stats.tests` | scitex-stats | all 23 test functions as a namespace |
| `stx.stats.Stats` | scitex.io.bundle | typed Stats dataclass for bundle storage |
| `stx.stats.BUNDLE_AVAILABLE` | scitex-python | True if bundle schema is importable |
