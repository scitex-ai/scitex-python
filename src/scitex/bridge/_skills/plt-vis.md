---
name: bridge-plt-vis
description: Convert matplotlib Figure objects to vis FigureModel with figure_to_vis_model(), convert axes with axes_to_vis_axes(), collect tracked data with collect_figure_data(), and convert tracking records with tracking_to_plot_configs().
---

# Plt to Vis Bridge

## figure_to_vis_model

Convert a matplotlib `Figure` to a vis `FigureModel`.

```python
figure_to_vis_model(fig) -> dict
```

```python
import scitex as stx
import matplotlib.pyplot as plt

fig, ax = stx.plt.subplots()
ax.plot([1, 2, 3], [4, 5, 6])

model = stx.bridge.figure_to_vis_model(fig)
```

---

## axes_to_vis_axes

Convert a single matplotlib `Axes` to a vis axes dict.

```python
axes_to_vis_axes(ax) -> dict
```

---

## collect_figure_data

Collect all tracked plot data from a scitex-managed figure.

```python
collect_figure_data(fig) -> dict
```

Returns data keyed by axes index, containing the tracked arrays for each plot call.

---

## tracking_to_plot_configs

Convert scitex's internal tracking records to a list of vis plot config dicts.

```python
tracking_to_plot_configs(tracking_data: dict) -> list[dict]
```

Useful for reconstructing plot specifications from a saved CSV.
