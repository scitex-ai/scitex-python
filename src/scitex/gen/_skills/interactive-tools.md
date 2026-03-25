---
name: gen-interactive-tools
description: Interactive and filesystem utilities in stx.gen — less (pager), src (source viewer), paste (clipboard exec), embed (IPython shell), symlink, and title2path (string-to-path conversion).
---

# Interactive and Filesystem Tools

---

## less

Displays long text using the system `less` pager from within an IPython session.

```python
less(output: str) -> None
```

Writes `output` to a temporary file and opens it with `get_ipython().system("less <tmpfile>")`. Cleans up the temporary file afterwards.

> **Requires:** IPython / Jupyter environment. Will raise if called outside an IPython session.

```python
import scitex as stx

if stx.gen.is_ipython():
    stx.gen.less(long_string)
```

---

## src

Displays the source code of any Python object using the system `less` pager.

```python
src(obj: Any) -> None
```

If `obj` is a class instance (not a class, function, or method), it inspects `obj.__class__` automatically. Pipes the source code returned by `inspect.getsource(obj)` to a `less` subprocess.

```python
import scitex as stx

stx.gen.src(stx.gen.TimeStamper)   # Shows TimeStamper source
stx.gen.src(stx.gen.to_z)          # Shows to_z source

ts = stx.gen.TimeStamper()
stx.gen.src(ts)  # Also works with instances
```

Handles errors gracefully:
- `OSError` when source is unavailable (compiled extensions)
- `TypeError` for unsupported object types
- Prints error message without raising

---

## paste

Executes the current clipboard content as Python code in the calling scope.

```python
paste() -> None
```

Uses `pyperclip` to read the clipboard and `textwrap.dedent` to strip leading indentation, then calls `exec()`. Prints an error message without raising if clipboard access fails or the code errors.

> **Requires:** `pyperclip`

```python
# Copy Python code to clipboard first, then:
stx.gen.paste()
```

**Interactive use:** Useful in IPython sessions to run code copied from documentation or a browser.

---

## embed

Opens an IPython shell with optional clipboard content execution.

```python
embed() -> None
```

1. Reads clipboard via `pyperclip`
2. Asks interactively whether to execute the clipboard content (`y/n`)
3. Starts an IPython shell via `IPython.embed`
4. If confirmed, executes the clipboard content in the IPython session

> **Requires:** `IPython`, `pyperclip`. Available only when torch is installed (wrapped in try/except in `__init__.py`).

```python
stx.gen.embed()
# Opens IPython — press Ctrl-D to exit
```

---

## symlink

Creates a symbolic link using a relative path.

```python
symlink(tgt: str, src: str, force: bool = False) -> None
```

| Parameter | Description |
|-----------|-------------|
| `tgt` | Target (the file/directory to link to) |
| `src` | Source (the path where the symlink is created) |
| `force` | If `True`, remove an existing file at `src` before creating the symlink |

The symlink is created as a **relative** path (computed from `src`'s directory to `tgt`), so it remains valid if the directory tree is moved.

Prints a yellow-colored confirmation message on success.

```python
import scitex as stx

stx.gen.symlink(
    tgt="/data/raw/session_001.mat",
    src="/project/data/session_001.mat",
)
# Symlink was created: /project/data/session_001.mat -> ../../data/raw/session_001.mat

# Overwrite an existing symlink:
stx.gen.symlink(tgt="/data/raw/v2.mat", src="/project/data/session_001.mat", force=True)
```

---

## title2path

Converts a title string (or dict) to a filesystem-safe, lowercase path component.

```python
title2path(title: str | dict) -> str
```

Transformations applied in order:
1. If `title` is a dict, converts to string via `scitex.dict.to_str`
2. Removes characters: `:`, `;`, `=`, `[`, `]`
3. Replaces `_-_` with `-`
4. Replaces spaces with `_`
5. Collapses consecutive `__` to `_`
6. Lowercases the result

```python
import scitex as stx

stx.gen.title2path("Subject 03: EEG [Alpha Band]")
# "subject_03_eeg_alpha_band"

stx.gen.title2path("session_1_-_run_2")
# "session_1-run_2"
```

**Use case:** Generate consistent output directory names from plot titles or experiment labels.

```python
title = "Condition A vs B: p=0.001"
out_dir = f"./results/{stx.gen.title2path(title)}/"
# "./results/condition_a_vs_b_p0.001/"
```
