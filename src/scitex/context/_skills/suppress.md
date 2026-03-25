---
description: Silence stdout and stderr inside a with-block using suppress_output() and its alias quiet().
---

# Output Suppression

## suppress_output

Context manager that redirects stdout and stderr to `/dev/null`.

```python
suppress_output() -> contextmanager
```

```python
import scitex as stx

with stx.context.suppress_output():
    noisy_function()  # all prints silenced
```

---

## quiet

Alias for `suppress_output`.

```python
import scitex as stx

with stx.context.quiet():
    import_with_verbose_logging()
```
