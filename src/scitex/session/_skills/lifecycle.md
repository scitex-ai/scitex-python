---
name: stx.session — lifecycle
description: Manual session start/close API, output directory structure, CONFIG DotDict keys, and running2finished directory promotion.
---

# Session Lifecycle

The session lifecycle is implemented in `_lifecycle/` and consists of three
public functions: `start()`, `close()`, and `running2finished()`.

## `start()`

```python
def start(
    sys=None,
    plt=None,
    file: Optional[str] = None,
    sdir: Optional[Union[str, Path]] = None,
    sdir_suffix: Optional[str] = None,
    args: Optional[Any] = None,
    os: Optional[Any] = None,       # unused, kept for compat
    random: Optional[Any] = None,   # unused, kept for compat
    np: Optional[Any] = None,       # unused, kept for compat
    torch: Optional[Any] = None,    # unused, kept for compat
    seed: int = 42,
    agg: bool = False,
    fig_size_mm: Tuple[int, int] = (160, 100),
    fig_scale: float = 1.0,
    dpi_display: int = 100,
    dpi_save: int = 300,
    fontsize="small",
    autolayout=True,
    show_execution_flow=False,
    hide_top_right_spines: bool = True,
    alpha: float = 0.9,
    line_width: float = 1.0,
    clear_logs: bool = False,
    verbose: bool = True,
) -> Tuple[DotDict, Any, Any, Any, Optional[Dict], Any]:
```

Returns `(CONFIG, stdout, stderr, plt, COLORS, rng)`.

If `sys` is not passed, `stdout` and `stderr` are `None` (no tee-logging).

### What `start()` does

1. Reads `./config/IS_DEBUG.yaml` to set debug mode (prefix `DEBUG_` on session ID
   if true).
2. Generates a unique session `ID` via `gen_ID(N=4)`, e.g. `2025Y-11M-18D-07h53m37s_Z5MR`.
3. Determines `caller_file` — uses `file` parameter, falls back to
   `inspect.stack()[1].filename`, handles IPython/notebook detection.
4. Builds `SDIR_RUN` path:
   `<script>_out/RUNNING/<ID>/` (optionally `<ID>-<sdir_suffix>/`)
5. Calls `setup_configs()` to load `./config/*.yaml` and merge with session keys.
6. If `sys` is provided: wraps `sys.stdout`/`sys.stderr` with `Tee` (mirrors output
   to file), redirects all existing `logging.StreamHandler`s to the tee streams.
7. Creates `RandomStateManager(seed=seed)`.
8. Calls `setup_matplotlib()` to configure matplotlib and return `scitex.plt` +
   `COLORS`.
9. Stores parsed `args` in `CONFIG['ARGS']`.
10. Registers session with the global `SessionManager`.
11. Prints a formatted header with version, ID, PID, file, and args.
12. Calls `_start_verification()` to notify `scitex.clew` if available.

## CONFIG DotDict Keys

| Key | Type | Description |
|---|---|---|
| `ID` | str | Session ID, e.g. `2025Y-11M-18D-07h53m37s_Z5MR` |
| `PID` | int | Python process ID |
| `START_DATETIME` | datetime | Session start time |
| `FILE` | Path | Absolute path to script |
| `SDIR_OUT` | Path | Base output directory (`<script>_out/`) |
| `SDIR_RUN` | Path | Running session dir (`<SDIR_OUT>/RUNNING/<ID>/`) |
| `ARGS` | dict | Parsed CLI arguments |
| `DEBUG` | bool | Whether debug mode is active |
| `EXIT_STATUS` | int | Set by `close()` |
| `END_DATETIME` | datetime | Set by `close()` |
| `RUN_DURATION` | str | HH:MM:SS string, set by `close()` |
| YAML namespaces | various | e.g. `CONFIG.PARAMS.lr` from `config/PARAMS.yaml` |

Access either as `CONFIG['ID']` or `CONFIG.ID` (DotDict supports both).

## `close()`

```python
def close(
    CONFIG,
    message=":)",
    notify=False,
    verbose=True,
    exit_status=None,
) -> None:
```

### What `close()` does

1. Calls `_stop_verification(exit_status)` (notifies `scitex.clew`).
2. Sets `CONFIG.EXIT_STATUS`, `CONFIG.END_DATETIME`, `CONFIG.RUN_DURATION`.
3. Closes all matplotlib figures (`plt.close("all")`) **before** closing streams to
   prevent segfault.
4. Saves `CONFIG` to `SDIR_RUN/CONFIGS/CONFIG.pkl` and `CONFIG.yaml`.
5. Calls `running2finished(CONFIG, exit_status)` to promote the directory.
6. Strips ANSI codes from log files.
7. If `notify=True`, sends a notification via `scitex.utils.notify`.
8. Closes the global `SessionManager` entry for this session.
9. Closes the tee-wrapped streams (`sys.stdout`, `sys.stderr`).

## `running2finished()`

```python
def running2finished(
    CONFIG,
    exit_status=None,
    remove_src_dir=True,
    max_wait=60,
) -> dict:
```

Moves session output from `RUNNING/` to a final directory based on exit status:

| `exit_status` | Destination |
|---|---|
| `0` | `FINISHED_SUCCESS/<ID>/` |
| `1` | `FINISHED_ERROR/<ID>/` |
| anything else / `None` | `FINISHED/<ID>/` |

Files are copied individually (not `shutil.copytree` of the whole tree) to handle
concurrent file system cases. After a successful copy, the `RUNNING/<ID>/` source
is removed. If `RUNNING/` is now empty, it is also removed.

## Output Directory Structure

```
script_out/
    RUNNING/
        <SESSION_ID>/           # active during run
            logs/
                stdout.log
                stderr.log
            CONFIGS/
                CONFIG.pkl
                CONFIG.yaml
            <your saved files>
    FINISHED_SUCCESS/
        <SESSION_ID>/           # moved here on exit_status=0
    FINISHED_ERROR/
        <SESSION_ID>/           # moved here on exit_status=1
    FINISHED/
        <SESSION_ID>/           # moved here otherwise
```

## Manual Usage Example

```python
import sys
import matplotlib.pyplot as plt
import scitex as stx

CONFIG, sys.stdout, sys.stderr, plt, COLORS, rng = stx.session.start(
    sys=sys,
    plt=plt,
    seed=42,
    verbose=True,
)

try:
    # Experiment code
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3])
    stx.io.save(fig, "plot.png")
    exit_status = 0
except Exception:
    exit_status = 1
    raise
finally:
    stx.session.close(CONFIG, exit_status=exit_status)
```
