---
description: Block execution or count keypresses interactively using wait_key and count.
---

# stx.etc — Interactive Keyboard Control

`stx.etc` exposes two functions for interactive keyboard-driven control in long-running experiments or monitoring loops.

## Functions

### `wait_key(p)`

Blocks until the user presses `q`, then terminates the given process.

Implemented with the `readchar` library. The function reads characters in a loop and calls `p.terminate()` when `q` is detected.

```python
import multiprocessing
from scitex.etc import wait_key, count

# Start a background counting process
p = multiprocessing.Process(target=count)
p.start()

# Block main thread until user presses 'q'
wait_key(p)
# After 'q' is pressed: process is terminated
print("Process stopped.")
```

### `count()`

Runs an infinite counter that prints incrementing integers once per second. Intended to be used as the target of a `multiprocessing.Process` so it can be terminated by `wait_key`.

```python
import multiprocessing
from scitex.etc import wait_key, count

p = multiprocessing.Process(target=count)
p.start()
# Outputs: 0, 1, 2, 3 ... until 'q' is pressed
wait_key(p)
```

## Dependency

Requires the `readchar` package:

```bash
pip install readchar
```

## Notes

- `wait_key` only terminates when `q` is pressed; all other keys are printed and ignored.
- Both functions are most useful in terminal-based monitoring loops where you need graceful shutdown via keyboard.
- This module is intentionally minimal; for richer interactive UIs see `scitex.ui` (deprecated) or `scitex.notify`.
