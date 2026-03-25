---
name: sh-execution
description: Core shell command execution — sh() and sh_run() — including buffered and streaming modes, timeout, and return format control.
---

# Shell Command Execution

## sh

Execute a shell command and return either a dict or a plain string.

```python
sh(
    command_str_or_list: List[str],
    verbose: bool = True,
    return_as: Literal["dict", "str"] = "dict",
    timeout: int = None,
    stream_output: bool = False,
) -> Union[ShellResult, str]
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `command_str_or_list` | `List[str]` | required | Command as a list of strings. String input raises `TypeError`. |
| `verbose` | `bool` | `True` | Print the command (yellow) before running. Print stdout/stderr after. |
| `return_as` | `"dict"` or `"str"` | `"dict"` | `"dict"` returns a `ShellResult` dict. `"str"` returns stdout on success, stderr on failure. |
| `timeout` | `int` or `None` | `None` | Kill the process and append a timeout message to stderr after N seconds. |
| `stream_output` | `bool` | `False` | When `True`, print output line-by-line as it is produced (real-time). When `False`, buffer and print after completion. |

**Returns**

- `return_as="dict"` — a `ShellResult` TypedDict: `{"stdout": str, "stderr": str, "exit_code": int, "success": bool}`
- `return_as="str"` — stdout string on success; stderr string on failure

**Raises**

- `TypeError` — if `command_str_or_list` is a plain string
- `ValueError` — if any argument contains a null byte (`\0`)

**Examples**

```python
import scitex as stx

# Basic usage
result = stx.sh.sh(["ls", "-la", "/home"])
print(result["stdout"])
print(result["exit_code"])  # 0 on success

# Check success before using output
result = stx.sh.sh(["git", "status"])
if result["success"]:
    print(result["stdout"])

# Return stdout as a plain string
output = stx.sh.sh(["echo", "hello"], return_as="str")
# output == "hello"

# Kill after 5 seconds if not done
result = stx.sh.sh(["sleep", "30"], timeout=5)
# result["success"] == False
# result["stderr"] contains "Command timed out after 5 seconds"

# Stream long-running process output live (e.g., pdflatex)
result = stx.sh.sh(["pdflatex", "-interaction=nonstopmode", "paper.tex"],
                   stream_output=True)

# Silent execution (no prints)
result = stx.sh.sh(["cat", "/etc/hostname"], verbose=False)
```

---

## sh_run

Convenience wrapper that always returns a `ShellResult` dict. Identical to `sh(..., return_as="dict")`.

```python
sh_run(
    command: List[str],
    verbose: bool = True,
) -> ShellResult
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `command` | `List[str]` | required | Command as a list of strings. |
| `verbose` | `bool` | `True` | Print command and output. |

**Returns** `ShellResult` dict: `{"stdout": str, "stderr": str, "exit_code": int, "success": bool}`

**Examples**

```python
from scitex.sh import sh_run

result = sh_run(["ls", "-la"])
if result["success"]:
    print(result["stdout"])
else:
    print("Failed:", result["stderr"])

# Suppress output
result = sh_run(["cat", "/nonexistent/file"], verbose=False)
print(result["success"])    # False
print(result["exit_code"])  # non-zero
print(result["stderr"])     # error message from cat
```

---

## Output Modes: Buffered vs Streaming

By default (`stream_output=False`), output is **buffered**: the subprocess runs to completion, then stdout/stderr are decoded and printed together.

With `stream_output=True`, the module uses non-blocking file descriptors and polls the process every 50 ms. Each chunk of output is printed immediately as it arrives. This is useful for long-running commands where you want live feedback.

**Streaming sets `PYTHONUNBUFFERED=1`** in the child environment so Python scripts invoked as subprocesses also emit output without internal buffering.

```python
# Buffered: waits for process to finish, then prints everything
result = stx.sh.sh(["make", "all"])

# Streaming: prints each line as produced
result = stx.sh.sh(["make", "all"], stream_output=True)
```

Both modes return the same `ShellResult` dict.

---

## Filtering Output in Python (instead of pipes)

Because string commands with pipes (`|`) are rejected, use Python to filter:

```python
result = stx.sh.sh(["ls", "-la"])
py_files = [line for line in result["stdout"].split("\n") if ".py" in line]
```
