---
name: clew-hashing
description: SHA256 file and directory hashing utilities for stx.clew — hash_file and hash_directory. Standalone functions usable independently of the tracking system.
---

# Hashing Utilities

Standalone SHA256 hashing functions. These work without any database or session and can be used anywhere you need to fingerprint files.

---

## hash_file

Compute SHA256 hash of a single file.

```python
hash_file(
    path: str | Path,
    algorithm: str = "sha256",
    chunk_size: int = 8192,
) -> str
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `path` | `str` or `Path` | required | Path to the file |
| `algorithm` | `str` | `"sha256"` | Hash algorithm (any `hashlib` name) |
| `chunk_size` | `int` | `8192` | Read chunk size in bytes |

**Returns**

First 32 characters of the hexadecimal digest. Example: `"a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"`.

**Raises**

`FileNotFoundError` if the file does not exist.

**Example**

```python
import scitex as stx

h = stx.clew.hash_file("data/raw.csv")
print(h)    # "a1b2c3d4e5f6g7h8i9j0..."  (32 chars)

# Using a non-default algorithm
h_md5 = stx.clew.hash_file("data/raw.csv", algorithm="md5")
```

---

## hash_directory

Compute SHA256 hashes for all files in a directory.

```python
hash_directory(
    path: str | Path,
    pattern: str = "*",
    recursive: bool = True,
    algorithm: str = "sha256",
) -> dict[str, str]
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `path` | `str` or `Path` | required | Directory path |
| `pattern` | `str` | `"*"` | Glob pattern for files (e.g. `"*.csv"`) |
| `recursive` | `bool` | `True` | Search subdirectories recursively |
| `algorithm` | `str` | `"sha256"` | Hash algorithm |

**Returns**

`dict[str, str]` mapping relative file paths (relative to `path`) to 32-char hashes.

**Raises**

`NotADirectoryError` if `path` is not a directory.

**Example**

```python
import scitex as stx

# Hash all files in a directory
hashes = stx.clew.hash_directory("data/")
for rel_path, h in hashes.items():
    print(f"{rel_path}: {h}")
# data/input.csv: a1b2c3d4...
# data/config.yaml: e5f6g7h8...

# Hash only CSV files
csv_hashes = stx.clew.hash_directory("data/", pattern="*.csv")

# Non-recursive (top-level only)
top_hashes = stx.clew.hash_directory("data/", recursive=False)
```

---

## Advanced: combine_hashes and verify_hash

These are advanced/internal utilities, accessible via the full module name.

### combine_hashes

Combine multiple hash values into a single deterministic hash.

```python
from scitex_clew import combine_hashes

hashes = {"input.csv": "a1b2...", "script.py": "c3d4..."}
combined = combine_hashes(hashes)
# Iterates keys in sorted order: "input.csv:a1b2c3...", "script.py:c3d4..."
```

### verify_hash

Check whether a file currently matches an expected hash.

```python
from scitex_clew import verify_hash

is_ok = verify_hash("data/raw.csv", expected_hash="a1b2c3d4...")
# Returns False (not raises) if file is missing
```

Comparison is length-aware: if `expected_hash` is shorter than 32 chars, only that many characters are compared. This allows comparing truncated hashes stored in external systems.
