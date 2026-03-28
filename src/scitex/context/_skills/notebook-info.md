---
description: Retrieve Jupyter notebook path, name, and directory from within a running notebook session.
---

# Notebook Info

## get_notebook_path

Return the absolute path to the currently-running notebook.

```python
get_notebook_path() -> str | None
```

Returns `None` when not running in a notebook.

```python
import scitex as stx

path = stx.context.get_notebook_path()
print(path)  # '/home/user/experiments/analysis.ipynb'
```

---

## get_notebook_name

Return just the filename (without `.ipynb` extension).

```python
get_notebook_name() -> str | None
```

```python
import scitex as stx

name = stx.context.get_notebook_name()
print(name)  # 'analysis'
```

---

## get_notebook_directory

Return the directory containing the current notebook.

```python
get_notebook_directory() -> str | None
```

```python
import scitex as stx

nb_dir = stx.context.get_notebook_directory()
stx.io.save(fig, f"{nb_dir}/figure.png")
```

---

## get_notebook_info_simple

Return a dict with `path`, `name`, and `directory` in one call.

```python
get_notebook_info_simple() -> dict
```

```python
import scitex as stx

info = stx.context.get_notebook_info_simple()
print(info)
# {'path': '/home/.../analysis.ipynb', 'name': 'analysis', 'directory': '/home/...'}
```
