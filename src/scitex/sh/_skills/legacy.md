---
description: Legacy shell helpers (run_shellcommand, run_shellscript) carried over from the gen module for backward compatibility.
---

# Legacy Functions

These functions were moved from the `gen` module and are preserved for backward compatibility. New code should prefer `sh()` or `sh_run()`.

---

## run_shellcommand

Run a command with positional arguments. Uses `subprocess.run` directly.

```python
run_shellcommand(command: str, *args: str) -> dict
```

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `command` | `str` | The executable name or path |
| `*args` | `str` | Additional positional arguments |

**Returns** a plain dict (not `ShellResult`):

```python
{
    "stdout": str,   # raw stdout text (NOT stripped)
    "stderr": str,   # raw stderr text
    "exit_code": int,
}
```

**Differences from sh()**

- Does NOT validate against string injection (no `validate_command` call)
- Always prints success/failure message to stdout (not suppressible via `verbose`)
- Returns a plain `dict` — no `success` key
- stdout/stderr are NOT stripped

**Example**

```python
from scitex.sh import run_shellcommand

result = run_shellcommand("ls", "-la")
print(result["stdout"])
```

---

## run_shellscript

Execute a shell script file, auto-granting execute permission if needed.

```python
run_shellscript(lpath_sh: str, *args: str) -> dict
```

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `lpath_sh` | `str` | Path to the shell script file |
| `*args` | `str` | Arguments forwarded to the script |

**Behavior**

1. Checks if the file is executable with `os.access(lpath_sh, os.X_OK)`.
2. If not executable, runs `chmod +x <path>` via `subprocess.run`.
3. Runs `[lpath_sh] + list(args)` via `run_shellcommand`.

**Returns** the same dict as `run_shellcommand`.

**Example**

```python
from scitex.sh import run_shellscript

# Script does not need to be pre-chmod'd
result = run_shellscript("./scripts/build.sh", "--release")
```

---

## Migration to sh()

```python
# Legacy
run_shellcommand("git", "status")

# Modern equivalent
stx.sh.sh(["git", "status"])

# Legacy
run_shellscript("./build.sh", "--release")

# Modern equivalent
stx.sh.sh(["./build.sh", "--release"])
```
