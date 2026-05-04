---
description: |
  [TOPIC] Installation — scitex umbrella
  [DETAILS] `pip install scitex` pulls the umbrella; sister packages (`scitex_io`, `scitex_plt`, ...) install on demand via extras or transitively.
tags: [scitex-installation]
---

# Installation — scitex

```bash
pip install scitex
python -c "import scitex; print(scitex.__version__)"
```

## Extras

The umbrella exposes `pip install 'scitex[<short>]'` for sister packages
that need optional dependencies. The full mapping lives in
`pyproject.toml` and `src/scitex/__init__.py::_EXTERNAL_REEXPORTS`.

Common extras:

```bash
pip install 'scitex[plt]'        # matplotlib + figrecipe
pip install 'scitex[ai]'         # ML stack (torch, transformers, ...)
pip install 'scitex[scholar]'    # literature management
pip install 'scitex[cloud]'      # SciTeX Cloud SDK
pip install 'scitex[all]'        # everything
```

## Verify

```bash
python -c "import scitex; scitex.io"     # triggers lazy load
python -c "import scitex; scitex.plt"
```

A missing optional dep raises a friendly `ImportError` with the install
hint (`pip install scitex[<short>]`) rather than the raw upstream error.
