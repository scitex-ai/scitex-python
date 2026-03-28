---
description: Annotate matplotlib axes with statistical test results using add_stat_to_axes(), extract existing annotations with extract_stats_from_axes(), and format stat results for display with format_stat_for_plot().
---

# Stats to Plt Bridge

Coordinate system: **axes coordinates** (0–1 normalized).

## add_stat_to_axes

Add a statistical annotation (bracket + significance symbol) to a matplotlib `Axes`.

```python
add_stat_to_axes(
    ax,
    stat_result: dict,
    x1: float,
    x2: float,
    y: float | None = None,
) -> None
```

```python
import scitex as stx
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.bar([0, 1], [3.2, 5.1])

result = stx.stats.test_ttest_ind(group1, group2, return_as="dict")
stx.bridge.add_stat_to_axes(ax, result, x1=0, x2=1)
stx.io.save(fig, "comparison.png")
```

---

## extract_stats_from_axes

Read back statistical annotations that were previously added to an axes.

```python
extract_stats_from_axes(ax) -> list[dict]
```

```python
import scitex as stx

annotations = stx.bridge.extract_stats_from_axes(ax)
for a in annotations:
    print(a["symbol"], a["p_value"])
```

---

## format_stat_for_plot

Format a stats result dict into a display string (e.g., `"***"`, `"n.s."`, `"p=0.023"`).

```python
format_stat_for_plot(stat_result: dict, style: str = "stars") -> str
```

| `style` | Example output |
|---------|---------------|
| `"stars"` | `"***"` |
| `"p_value"` | `"p=0.001"` |
| `"both"` | `"*** (p=0.001)"` |

```python
import scitex as stx

result = stx.stats.test_mannwhitneyu(a, b, return_as="dict")
label = stx.bridge.format_stat_for_plot(result, style="both")
print(label)  # "** (p=0.012)"
```
