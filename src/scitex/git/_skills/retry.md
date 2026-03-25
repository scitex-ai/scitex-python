---
name: git-retry
description: Retry git operations with exponential backoff when git index.lock conflicts are detected. Wraps any zero-argument callable. Non-lock errors are re-raised immediately.
---

# Retry Logic

## git_retry

Retry a git operation that may fail due to `index.lock` contention when multiple processes access the same repository concurrently.

```python
git_retry(
    operation: Callable[[], T],
    max_retries: int = 5,
    initial_delay: float = 0.1,
    max_delay: float = 2.0,
    backoff_factor: float = 2.0,
) -> T
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `operation` | `Callable[[], T]` | required | Zero-argument callable to retry |
| `max_retries` | `int` | `5` | Maximum number of attempts |
| `initial_delay` | `float` | `0.1` | Seconds to wait before the first retry |
| `max_delay` | `float` | `2.0` | Maximum seconds between retries |
| `backoff_factor` | `float` | `2.0` | Multiplier applied to the delay after each attempt |

**Returns** — Whatever `operation()` returns on success.

**Raises**

| Exception | Condition |
|-----------|-----------|
| `TimeoutError` | `index.lock` still held after all `max_retries` attempts |
| Original exception | Any `subprocess.CalledProcessError` that is **not** a lock error, or any non-subprocess exception — re-raised immediately on first occurrence |

**Retry behaviour** — Only `subprocess.CalledProcessError` with `"index.lock"` in `stderr` triggers a retry. The delay sequence (seconds) with defaults is: `0.1 → 0.2 → 0.4 → 0.8 → 1.6` (capped at `2.0`).

**Examples**

```python
import subprocess
from pathlib import Path
import scitex as stx

repo = Path("./my_project")

# Wrap a lambda
stx.git.git_retry(
    lambda: subprocess.run(
        ["git", "commit", "-m", "parallel safe commit"],
        cwd=repo,
        check=True,
    )
)

# Wrap one of the stx.git functions
stx.git.git_retry(
    lambda: stx.git.git_add_all(repo),
    max_retries=3,
)

# Custom backoff
stx.git.git_retry(
    lambda: stx.git.git_commit(repo, "msg"),
    max_retries=10,
    initial_delay=0.05,
    max_delay=5.0,
    backoff_factor=3.0,
)
```
