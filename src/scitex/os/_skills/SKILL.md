---
name: stx.os
description: OS-level utilities for hostname-based guards and file moving. Use when scripts must run only on a specific machine or when moving files to auto-created destination directories.
user-invocable: false
---

# stx.os — OS Utilities

Thin OS-level helpers that complement Python's standard `os` module. Accessed via `import scitex as stx` then `stx.os.<function>`.

**Public API**

```python
from scitex.os import check_host, is_host, verify_host, mv
```

## Sub-skills

### Host Checking
- [check-host.md](check-host.md) — `check_host`, `is_host`, `verify_host`: substring-match the current hostname and optionally exit the process on mismatch

### File Moving
- [mv.md](mv.md) — `mv`: move a file or directory to a destination, auto-creating the destination directory tree
