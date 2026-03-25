# Stats-to-Plot Bridge (stx.bridge)

The `_stats_plt` bridge converts statistical test results into matplotlib axes annotations.

## add_stat_to_axes

```python
from scitex.bridge import add_stat_to_axes, extract_stats_from_axes
import scitex as stx

# Run a statistical test
result = stx.stats.test_ttest_ind(group1, group2)

fig, ax = stx.plt.subplots()
ax.boxplot([group1, group2])

# Annotate the axes with the statistical result
add_stat_to_axes(ax, result)
```

## extract_stats_from_axes

```python
# Retrieve previously stored statistical annotations from axes
stats = extract_stats_from_axes(ax)
# Returns list of stat annotation dicts
```

## format_stat_for_plot

```python
from scitex.bridge import format_stat_for_plot

# Format a stat result as a display-ready string
label = format_stat_for_plot(result)
ax.text(0.5, 0.95, label, transform=ax.transAxes)
```

## Coordinate convention

The stats-to-plt bridge uses **axes coordinates** (0–1 normalized), not data coordinates. Annotations positioned at `(x=0.5, y=0.95)` are centered at the top of any axes regardless of data range.

This is defined in `COORDINATE_SYSTEMS["axes"]`:

```python
from scitex.bridge import COORDINATE_SYSTEMS
print(COORDINATE_SYSTEMS["axes"])
# {"description": "Normalized axes coordinates (0-1)", "x_range": (0.0, 1.0), ...}
```
