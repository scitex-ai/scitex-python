---
name: pd-warnings
description: Context manager to suppress pandas SettingWithCopyWarning for a block of code.
---

# Warnings

## ignore_setting_with_copy_warning

Context manager that temporarily silences `pandas.errors.SettingWithCopyWarning` (or the equivalent `pandas.core.common.SettingWithCopyWarning` on older pandas versions).

The canonical name is `ignore_setting_with_copy_warning`. The PascalCase alias `ignore_SettingWithCopyWarning` is retained for backward compatibility but is deprecated.

```python
@contextmanager
ignore_setting_with_copy_warning()
```

**When to use**

This warning fires when pandas detects an assignment to a DataFrame slice that may or may not modify the original. If you have already verified correctness (e.g. you are intentionally modifying a view, or the slice is used as a temporary), wrapping the block suppresses noise without hiding real bugs elsewhere.

**Examples**

```python
import scitex as stx

# Suppress warning for a specific assignment block
with stx.pd.ignore_setting_with_copy_warning():
    df['column'] = new_values

# Deprecated alias (still functional)
with stx.pd.ignore_SettingWithCopyWarning():
    df['column'] = new_values
```

**Implementation note**

Uses `warnings.catch_warnings()` + `warnings.simplefilter("ignore", SettingWithCopyWarning)` internally, so warning filters are fully restored on context exit even if an exception is raised.
