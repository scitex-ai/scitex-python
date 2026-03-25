---
description: Save figures with figrecipe recipe metadata using save_with_recipe(), reload figures from recipe files with load_recipe(), and check figrecipe availability with has_figrecipe().
---

# FigRecipe Integration

## save_with_recipe

Save a figure alongside a figrecipe `.yaml` recipe file.

```python
save_with_recipe(fig, path: str, **kwargs) -> dict
```

```python
import scitex as stx

fig, ax = stx.plt.subplots()
ax.plot([1, 2, 3], [4, 5, 6])

# Saves both plot.png and plot.yaml (figrecipe recipe)
stx.bridge.save_with_recipe(fig, "plot.png")
```

---

## load_recipe

Load a figrecipe `.yaml` recipe file and return the metadata.

```python
load_recipe(path: str) -> dict
```

```python
import scitex as stx

recipe = stx.bridge.load_recipe("plot.yaml")
print(recipe["plots"][0]["type"])  # 'line'
```

---

## has_figrecipe / FIGRECIPE_AVAILABLE

Check whether figrecipe is installed.

```python
import scitex as stx

if stx.bridge.has_figrecipe():
    stx.bridge.save_with_recipe(fig, "plot.png")
else:
    print("Install figrecipe: pip install figrecipe")

# Or use the module-level flag
print(stx.bridge.FIGRECIPE_AVAILABLE)  # True / False
```
