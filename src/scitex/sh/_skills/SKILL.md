---
name: stx.sh
description: Safe shell command execution. Enforces list-format commands to prevent shell injection. Supports timeout, real-time streaming, and flexible return formats.
user-invocable: false
---

# stx.sh — Shell Command Execution

`stx.sh` executes subprocesses safely. String commands are rejected by design; only list format is accepted. All execution goes through `subprocess.Popen(shell=False)`.

## Quick Reference

```python
import scitex as stx

# Basic — returns ShellResult dict
result = stx.sh.sh(["ls", "-la"])
print(result["stdout"])
print(result["exit_code"])   # 0 on success
print(result["success"])     # True/False

# Return stdout as plain string
output = stx.sh.sh(["echo", "hello"], return_as="str")

# Timeout after 5 seconds
result = stx.sh.sh(["sleep", "30"], timeout=5)

# Stream output live (e.g., long builds)
result = stx.sh.sh(["make", "all"], stream_output=True)

# Silent execution
result = stx.sh.sh(["git", "status"], verbose=False)

# Always-dict convenience wrapper
result = stx.sh.sh_run(["git", "log", "--oneline", "-5"])
```

## Sub-skills

### Execution
- [execution.md](execution.md) — `sh()` and `sh_run()`: parameters, return values, buffered vs streaming modes, timeout behavior

### Security
- [security.md](security.md) — injection model, `validate_command()`, `quote()`: why strings are rejected, what is validated, when to use quoting

### Types
- [types.md](types.md) — `ShellResult` TypedDict, `CommandInput`, `ReturnFormat`: field meanings and edge cases

### Legacy
- [legacy.md](legacy.md) — `run_shellcommand()`, `run_shellscript()`: backward-compat functions from the gen module, differences from `sh()`, migration guide

## Public API

| Symbol | Source | Description |
|--------|--------|-------------|
| `sh` | `__init__` | Execute command; returns dict or str |
| `sh_run` | `__init__` | Execute command; always returns `ShellResult` dict |
| `quote` | `_security` | Shell-quote a single argument via `shlex.quote` |
| `validate_command` | `_security` | Pre-flight security check (also called internally) |
| `run_shellcommand` | `_shell_legacy` | Legacy: run command + args |
| `run_shellscript` | `_shell_legacy` | Legacy: run a shell script, auto-chmod if needed |
| `ShellResult` | `_types` | TypedDict with stdout, stderr, exit_code, success |
| `CommandInput` | `_types` | Type alias for `List[str]` |
| `ReturnFormat` | `_types` | `Literal["dict", "str"]` |

## Key Constraints

- **No string commands.** `sh("ls -la")` raises `TypeError`. Pass `["ls", "-la"]`.
- **No pipes/redirects in command list.** Filter in Python instead: `[l for l in result["stdout"].split("\n") if ".py" in l]`
- **`exit_code`, not `returncode`.** The result key is `exit_code`. (`returncode` does not exist on `ShellResult`.)
