---
description: |
  [TOPIC] Quick start — scitex umbrella
  [DETAILS] Minimal `@scitex.session` script showing CONFIG / plt / logger injection and `scitex.io.save` auto-CSV export.
tags: [scitex-quick-start]
---

# Quick start — scitex

Analysis parameters live in `config/*.yaml`, not in `main()` defaults or
the CLI. The file stem is the namespace and keys are upper-cased:

```yaml
# config/ANALYSIS.yaml
N_POINTS: 100
X_MAX: 10
```

```python
import scitex
import numpy as np

@scitex.session
def main(
    CONFIG=scitex.INJECTED,              # ./config/*.yaml
    plt=scitex.INJECTED,                 # pre-styled matplotlib
    logger=scitex.INJECTED,
):
    """Quick-start demo. Docstring becomes --help text."""
    x = np.linspace(0, CONFIG.ANALYSIS.X_MAX, CONFIG.ANALYSIS.N_POINTS)
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
python script.py        # run from the directory that holds config/
# Outputs land in ./script_out/FINISHED_SUCCESS/<session_id>/
```

`./config/` is resolved against the working directory. Keep `main()`
arguments for non-numeric inputs (`data_path: str = "data.csv"`,
subject ids). There is no CLI override for `CONFIG` values; edit the YAML.
Each run freezes the values it used in `CONFIGS/CONFIG.yaml`. In
`project-type: research` projects, `scitex-dev` >= 0.64.0 rule STX-S008
warns on numeric `main()` defaults and other hard-coded parameters.

For the per-module APIs, see the relevant sister-package skill
(`scitex-io`, `scitex-plt`, `scitex-stats`, ...).
