---
name: bridge-stats-vis
description: Convert statistical results to vis annotation objects with stat_result_to_annotation(), add them to a FigureModel with add_stats_to_figure_model(), and position annotations with position_stat_annotation().
---

# Stats to Vis Bridge

Coordinate system: **data coordinates** (actual x/y values).

## stat_result_to_annotation

Convert a stats result dict to a vis-compatible annotation object.

```python
stat_result_to_annotation(
    stat_result: dict,
    x1: float,
    x2: float,
    y: float,
) -> dict
```

```python
import scitex as stx

result = stx.stats.test_ttest_ind(group1, group2, return_as="dict")
annotation = stx.bridge.stat_result_to_annotation(result, x1=1.0, x2=2.0, y=5.5)
```

---

## add_stats_to_figure_model

Add multiple statistical annotations to a vis FigureModel object.

```python
add_stats_to_figure_model(figure_model, annotations: list[dict]) -> None
```

```python
import scitex as stx

fm = stx.bridge.figure_to_vis_model(fig)
annotations = [
    stx.bridge.stat_result_to_annotation(r, x1=0, x2=1, y=6)
    for r in results
]
stx.bridge.add_stats_to_figure_model(fm, annotations)
```

---

## position_stat_annotation

Calculate the optimal y-position for a statistical bracket given existing plot elements.

```python
position_stat_annotation(ax, x1: float, x2: float, padding: float = 0.05) -> float
```

```python
import scitex as stx

y = stx.bridge.position_stat_annotation(ax, x1=0, x2=1)
annotation = stx.bridge.stat_result_to_annotation(result, x1=0, x2=1, y=y)
```
