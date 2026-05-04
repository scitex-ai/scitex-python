---
description: |
  [TOPIC] Quick start — scitex umbrella
  [DETAILS] Minimal `@scitex.session` script showing CONFIG / plt / logger injection and `scitex.io.save` auto-CSV export.
tags: [scitex-quick-start]
---

# Quick start — scitex

```python
import scitex
import numpy as np

@scitex.session
def main(
    n_points: int = 100,                 # auto-CLI: --n-points
    CONFIG=scitex.INJECTED,              # ./config/*.yaml
    plt=scitex.INJECTED,                 # pre-styled matplotlib
    logger=scitex.INJECTED,
):
    """Quick-start demo. Docstring becomes --help text."""
    x = np.linspace(0, 10, n_points)
    y = np.sin(x)

    fig, ax = plt.subplots()
    ax.plot_line(x, y)                   # data tracked for CSV export
    ax.set_xyt("X", "sin(X)", "demo")

    scitex.io.save(fig, "sine.png")      # writes sine.png + sine.csv
    scitex.io.save({"x": x, "y": y}, "data.pkl")
    logger.info("done")
    return 0


if __name__ == "__main__":
    main()
```

Run it:

```bash
python script.py --n-points 500
# Outputs land in ./script_out/FINISHED_SUCCESS/<session_id>/
```

For the per-module APIs, see the relevant sister-package skill
(`scitex-io`, `scitex-plt`, `scitex-stats`, ...).
