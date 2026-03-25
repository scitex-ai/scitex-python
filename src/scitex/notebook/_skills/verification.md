---
description: Verify that a notebook's cells produce reproducible outputs with verify_notebook() and run a quick structural check with check_notebook().
---

# Notebook Verification

## verify_notebook

Run a full reproducibility verification pass on a notebook using the Clew system. Re-executes cells in DAG order and checks that outputs match.

```python
verify_notebook(path: str, **kwargs) -> dict
```

Returns a dict with `passed`, `failed`, `warnings`, and cell-level results.

```python
import scitex as stx

results = stx.notebook.verify_notebook("experiment.ipynb")
print(f"Passed: {results['passed']}, Failed: {results['failed']}")
```

---

## check_notebook

Quick structural check without re-execution. Verifies:
- All cells have been executed (non-None `execution_count`)
- No obvious broken imports
- Output directory exists

```python
check_notebook(path: str) -> dict
```

```python
import scitex as stx

status = stx.notebook.check_notebook("experiment.ipynb")
if not status["ok"]:
    print(status["warnings"])
```
