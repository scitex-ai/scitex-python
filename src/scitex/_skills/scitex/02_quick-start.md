---
description: |
  [TOPIC] Quick start — scitex umbrella
  [DETAILS] A complete synthetic signal example using scitex.plt and scitex.io with an explicit absolute output path. Advanced session/provenance behavior belongs to its owning package.
tags: [scitex-quick-start]
---

# Quick start — scitex

After installation, run this in your project directory:

```python
from pathlib import Path

import numpy as np
import scitex

x = np.linspace(0, 2 * np.pi, 200)
y = np.sin(x)

fig, ax = scitex.plt.subplots()
ax.plot(x, y)
ax.set_xyt("Time", "Amplitude", "Synthetic signal")

output = Path("outputs/signal.png").resolve()
scitex.io.save(fig, str(output))
```

It writes `outputs/signal.png` and a FigRecipe recipe beside it. The data is
synthetic. Font rendering depends on the environment; the example does not
assert a pixel-identical style across platforms.

The same Python example is presented in the repository README. Its generated
PNG and recipe were checked in separate normal public-release and source-wheel
environments. Consult figrecipe and scitex-io for format/plugin details, and
scitex-session/scitex-clew for session injection and provenance configuration.
