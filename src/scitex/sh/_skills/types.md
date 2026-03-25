---
name: sh-types
description: Type definitions used by stx.sh — ShellResult TypedDict, CommandInput, and ReturnFormat.
---

# Type Definitions

All types are defined in `scitex.sh._types` and re-exported from `scitex.sh`.

---

## ShellResult

A `TypedDict` returned by every execution function.

```python
class ShellResult(TypedDict):
    stdout: str       # Decoded, stripped stdout from the process
    stderr: str       # Decoded, stripped stderr from the process
    exit_code: int    # Process return code (0 = success)
    success: bool     # True when exit_code == 0
```

**Field notes**

- `stdout` and `stderr` are decoded as UTF-8 and stripped of leading/trailing whitespace.
- `success` is exactly `exit_code == 0`.
- On timeout, the timeout message is appended to `stderr` and `success` is `False`.

**Example usage**

```python
result = stx.sh.sh(["git", "log", "--oneline", "-5"])

# Type-safe field access
stdout: str  = result["stdout"]
stderr: str  = result["stderr"]
code:   int  = result["exit_code"]
ok:     bool = result["success"]
```

---

## CommandInput

```python
CommandInput = List[str]
```

The accepted type for all command arguments. A plain `str` is explicitly rejected — pass a list of strings.

---

## ReturnFormat

```python
ReturnFormat = Literal["dict", "str"]
```

Controls what `sh()` returns:

| Value | Return type | Content |
|-------|-------------|---------|
| `"dict"` | `ShellResult` | Full result with stdout, stderr, exit_code, success |
| `"str"` | `str` | stdout on success; stderr on failure |
