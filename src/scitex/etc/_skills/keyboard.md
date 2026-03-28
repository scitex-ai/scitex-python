---
description: wait_key() blocks until 'q' is pressed and terminates a multiprocessing.Process; count() increments a counter every second to stdout — useful for interactive CLI demos.
---

# Keyboard Input

Requires: `pip install readchar`

## wait_key

Block until the user presses `q`, then terminate a running `multiprocessing.Process`.

```python
wait_key(p: multiprocessing.Process) -> None
```

All keypresses except `q` are printed. When `q` is pressed, `p.terminate()` is called.

```python
import multiprocessing
import scitex as stx

def background_job():
    while True:
        # ... long-running background work ...
        pass

p = multiprocessing.Process(target=background_job)
p.start()
stx.etc.wait_key(p)   # blocks until user presses 'q'
```

---

## count

Increment and print a counter every second until interrupted. Useful for demonstrating that a background process is running.

```python
count() -> None  # infinite loop
```

```python
import multiprocessing
import scitex as stx

p = multiprocessing.Process(target=stx.etc.count)
p.start()
stx.etc.wait_key(p)
# 0
# 1
# 2
# q was pressed.
```
