---
description: Automatic matplotlib integration for cloud environments — inline figure display via install_matplotlib_hook() and uninstall_matplotlib_hook().
---

# Matplotlib Hook

`scitex/cloud/_matplotlib_hook.py` patches matplotlib to display figures inline when running inside a cloud (headless) environment. It is not imported by `cloud/__init__.py` by default; it must be imported or installed explicitly.

## install_matplotlib_hook

Patches `matplotlib.figure.Figure.savefig` and `matplotlib.pyplot.show` to emit inline image markers when in a cloud environment.

```python
install_matplotlib_hook() -> None
```

**Parameters:** none

**Behavior:**
- Idempotent: calling it multiple times has no effect after the first call (guarded by `_hooked` flag).
- Hooks two entry points:
  - `Figure.savefig` — after saving, calls `emit_inline_image(fname)` if in cloud environment.
  - `plt.show` — in cloud environment, saves all open figures to `<project_root>/scitex/temp/<timestamp>/figure_<n>.png` and emits inline image markers. Does NOT call the original `plt.show()` in cloud (headless). In non-cloud environments, delegates to the original `plt.show()`.
- Safe: if `matplotlib` is not installed, the function silently returns.

```python
from scitex.cloud._matplotlib_hook import install_matplotlib_hook

install_matplotlib_hook()

import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [4, 5, 6])
plt.show()  # Saves to project_root/scitex/temp/<ts>/figure_1.png and emits inline marker
```

---

## uninstall_matplotlib_hook

Restores the original `Figure.savefig` and `plt.show` functions.

```python
uninstall_matplotlib_hook() -> None
```

**Parameters:** none

**Behavior:**
- Idempotent: no-op if hooks were not installed.
- Restores both `Figure.savefig` and `plt.show` to their pre-hook originals.
- Safe: if `matplotlib` is not installed, silently returns.

```python
from scitex.cloud._matplotlib_hook import uninstall_matplotlib_hook

uninstall_matplotlib_hook()
# matplotlib now behaves normally
```

---

## Auto-install Behavior

The module auto-installs hooks at import time if `is_cloud_environment()` returns `True`:

```python
# Bottom of _matplotlib_hook.py:
from scitex.cloud import is_cloud_environment
if is_cloud_environment():
    install_matplotlib_hook()
```

This means importing `scitex.cloud._matplotlib_hook` in a cloud session automatically enables inline figure display.

---

## Output Path

When `plt.show()` is called in cloud mode, figures are saved to:

```
<project_root>/scitex/temp/<YYYYMMDD_HHMMSS>/figure_<fignum>.png
```

The inline image marker emitted uses the project-relative path:

```
scitex/temp/20260325_142300/figure_1.png
```

---

## Notes

- `is_cloud_environment()`, `emit_inline_image()`, and `get_project_root()` are defined in `scitex_cloud` (the spoke package). They are not available when `scitex-cloud` is not installed.
- The hook is intentionally NOT auto-applied by `stx.cloud.__init__` — the user or the cloud runtime must trigger it explicitly.
- `__all__` exports only `install_matplotlib_hook` and `uninstall_matplotlib_hook`.
