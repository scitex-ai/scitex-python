---
name: stx.etc
description: Miscellaneous utilities for keyboard input handling in interactive programs.
---

# stx.etc

The `stx.etc` module provides miscellaneous utility functions that don't fit into other categories, primarily focused on keyboard input handling for interactive scientific programs.

## Python API

```python
import scitex as stx

# Wait for a keypress (blocks until key pressed)
key = stx.etc.wait_key()

# Count keypresses over a duration
n_presses = stx.etc.count(duration=5.0)
```

## Key Features

- `wait_key()` — block execution until a keyboard key is pressed, returns the key
- `count(duration)` — count keypresses over a specified time window
- Useful for interactive experiment control loops
