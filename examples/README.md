# SciTeX Examples

| # | File | Module | Description |
|---|------|--------|-------------|
| 01 | `01_session.py` | `@stx.session` | Reproducible experiment tracking with auto-CLI |
| 02 | `02_io.ipynb` | `stx.io` | Unified file I/O for 30+ formats |
| 03 | `03_clew.ipynb` | `stx.clew` | Cryptographic verification DAG |
| 04 | `04_stats.ipynb` | `stx.stats` | Publication-ready statistics (23+ tests) |
| 05 | `05_plt.ipynb` | `stx.plt` | Reproducible, restylable figures |
| 06 | `06_scholar.ipynb` | `stx.scholar` | Literature search and management |
| 07 | `07_writer.ipynb` | `stx.writer` | LaTeX manuscript compilation |
| 08 | `08_notification.ipynb` | `stx.notification` | Multi-backend notifications |
| 09 | `09_dev.ipynb` | `stx.dev` | Ecosystem development tools |
| 10 | `10_app.ipynb` | `stx.app` | Building and sharing custom research apps |

## Running

```bash
pip install scitex[all]

# Session example (script)
python 01_session.py input.csv --n-samples 200

# Notebooks
jupyter notebook 02_io.ipynb
```

## Legacy Examples

Previous examples are preserved in `_legacy/` for reference.
