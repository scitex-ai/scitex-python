---
description: Shell injection prevention model — why string commands are rejected, what validate_command checks, and how quote() safely escapes arguments.
---

# Security Model

## Design Principle

All commands must be passed as a **list of strings**, never as a plain string. This mirrors `subprocess.Popen(shell=False)` directly: each list element is passed as a literal argument to `execvp`, so shell metacharacters (`;`, `|`, `&`, `$`, backticks, redirects) are never interpreted.

```python
# WRONG — raises TypeError immediately
stx.sh.sh("ls -la | grep .py")

# CORRECT — each token is a separate element
stx.sh.sh(["ls", "-la"])
filtered = [l for l in result["stdout"].split("\n") if ".py" in l]
```

---

## validate_command

Called automatically before every execution. Also callable directly for pre-flight checks.

```python
validate_command(command_str_or_list: Union[str, List[str]]) -> None
```

**Checks performed**

| Check | Raises | Reason |
|-------|--------|--------|
| Input is a `str` | `TypeError` | String commands pass through the shell; list format does not |
| Any argument contains `\0` | `ValueError` | Null bytes are a common shell injection vector |

**Examples**

```python
from scitex.sh import validate_command

# Passes silently
validate_command(["git", "commit", "-m", "Add feature"])

# Raises TypeError
try:
    validate_command("git commit -m 'Add feature'")
except TypeError as e:
    print(e)
# String commands are not allowed for security reasons.
# Use list format: ['command', 'arg1', 'arg2'].

# Raises ValueError
try:
    validate_command(["echo", "test\0injected"])
except ValueError as e:
    print(e)
# Command argument contains null byte - potential shell injection attempt
```

**Note on dangerous characters:** Characters like `;`, `|`, `&`, `$` are NOT explicitly blocked in list arguments because they are harmless when passed as literals to a non-shell process. The real protection is `shell=False` in the underlying `subprocess.Popen`.

---

## quote

Safely shell-quote a single string so it can be embedded in a command argument.

```python
quote(arg: str) -> str
```

Thin wrapper over `shlex.quote`. Wraps the string in single quotes and escapes any embedded single quotes, producing a string safe to pass through a POSIX shell.

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `arg` | `str` | The raw argument string to quote |

**Returns** `str` — quoted string (e.g., `'value'` or `'value'"'"'s'`)

**Examples**

```python
from scitex.sh import quote

# Spaces in filenames
safe = quote("my file.txt")
# "'my file.txt'"

# Shell metacharacters neutralised
safe = quote("file; rm -rf /")
# "'file; rm -rf /'"

# Use when building args that will pass through a shell (e.g., ssh)
host = "server.example.com"
remote_path = "/data/my project/"
stx.sh.sh(["ssh", host, f"ls {quote(remote_path)}"])
```

**When to use:** `quote` is mainly needed when constructing an argument that will itself be interpreted by a subordinate shell (e.g., the command string for `ssh`, `bash -c`). For direct subprocess list calls with `shell=False`, quoting is unnecessary — just pass raw strings as list elements.
