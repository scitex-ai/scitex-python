---
name: stx.etc
description: Miscellaneous utilities for keyboard input handling in interactive programs.
---

# stx.etc — Skills Index

The `stx.etc` module provides miscellaneous utility functions that don't fit into other categories, primarily focused on keyboard input handling for interactive scientific programs.

## Sub-skills

| File | Description |
|------|-------------|
| [wait-key.md](wait-key.md) | Block execution or count keypresses using `wait_key` and `count` |

## Quick Reference

```python
import multiprocessing
from scitex.etc import wait_key, count

p = multiprocessing.Process(target=count)
p.start()
wait_key(p)   # blocks until 'q' is pressed, then terminates p
```

## Exports

- `wait_key(p)` — block until 'q' pressed, terminate process `p`
- `count()` — infinite counter printing 0, 1, 2 … once per second
