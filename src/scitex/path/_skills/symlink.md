---
description: Symlink creation, inspection, resolution, listing, and repair. symlink, create_relative_symlink, is_symlink, readlink, resolve_symlinks, list_symlinks, fix_broken_symlinks, unlink_symlink.
---

# Symlink Management

---

## symlink

Create a symbolic link `dst` that points to `src`.

```python
symlink(
    src: str | Path,
    dst: str | Path,
    overwrite: bool = False,
    target_is_directory: bool | None = None,
    relative: bool = False,
) -> Path
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `src` | `str` or `Path` | required | Link target (the thing being pointed to) |
| `dst` | `str` or `Path` | required | Link path (the symlink file to create) |
| `overwrite` | `bool` | `False` | Remove `dst` if it already exists before creating the link |
| `target_is_directory` | `bool` or `None` | `None` | Windows only — whether target is a directory; auto-detected when `None` and `src` exists |
| `relative` | `bool` | `False` | Store a relative path in the symlink instead of an absolute path |

**Returns** `Path` — the created symlink path (`dst`).

**Raises**
- `FileExistsError` — if `dst` exists and `overwrite=False`.

**Notes**
- Parent directories of `dst` are created automatically.
- Creating a symlink to a non-existent target is allowed (dangling symlink).
- On failure, logs a warning rather than raising; the returned `Path` may not be a valid symlink.

**Examples**

```python
import scitex as stx

# Absolute symlink (default)
stx.path.symlink("/data/project/raw/file.csv", "/home/user/analysis/file.csv")

# Relative symlink — the stored link is relative to dst's parent
stx.path.symlink("../raw/file.csv", "/home/user/analysis/file.csv", relative=True)

# Overwrite an existing link
stx.path.symlink("/data/v2/file.csv", "/home/user/analysis/file.csv", overwrite=True)

# Symlink an entire directory
stx.path.symlink("/mnt/nas/datasets", "./datasets")
```

---

## create_relative_symlink

Convenience wrapper for `symlink(..., relative=True)`.

```python
create_relative_symlink(
    src: str | Path,
    dst: str | Path,
    overwrite: bool = False,
) -> Path
```

**Example**

```python
import scitex as stx

stx.path.create_relative_symlink("../data/file.txt", "link_to_file")
```

---

## is_symlink

Check whether a path is a symbolic link.

```python
is_symlink(path: str | Path) -> bool
```

Returns `True` if `path` is a symlink, `False` otherwise (including non-existent paths).

**Example**

```python
import scitex as stx

stx.path.is_symlink("./link")   # True or False
```

---

## readlink

Return the raw target path stored inside a symlink (without resolving further symlinks).

```python
readlink(path: str | Path) -> Path
```

**Raises** `OSError` if `path` is not a symlink.

**Example**

```python
import scitex as stx

target = stx.path.readlink("./link")
print(target)   # Path('../data/file.txt') or absolute path
```

---

## resolve_symlinks

Fully resolve all symlinks in a path, returning an absolute real path.

```python
resolve_symlinks(path: str | Path) -> Path
```

Equivalent to `Path(path).resolve()`. Follows all symlinks in every component.

**Example**

```python
import scitex as stx

real = stx.path.resolve_symlinks("./link/subdir/../file.csv")
print(real)   # Path('/absolute/real/path/file.csv')
```

---

## list_symlinks

List all symlinks in a directory.

```python
list_symlinks(
    directory: str | Path,
    recursive: bool = False,
) -> list[Path]
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `directory` | `str` or `Path` | required | Directory to search |
| `recursive` | `bool` | `False` | If `True`, search recursively via `rglob` |

**Returns** `list[Path]` — all symlinks found.

**Example**

```python
import scitex as stx

links = stx.path.list_symlinks("./outputs", recursive=True)
for link in links:
    print(f"{link} -> {stx.path.readlink(link)}")
```

---

## unlink_symlink

Remove a symbolic link.

```python
unlink_symlink(path: str | Path, missing_ok: bool = True) -> None
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `path` | `str` or `Path` | required | Symlink to remove |
| `missing_ok` | `bool` | `True` | If `True`, silently return when symlink doesn't exist |

**Raises**
- `FileNotFoundError` — if symlink doesn't exist and `missing_ok=False`.
- `OSError` — if `path` is not a symlink (regular file or directory).

**Example**

```python
import scitex as stx

stx.path.unlink_symlink("./old_link")           # silent if missing
stx.path.unlink_symlink("./old_link", missing_ok=False)  # raises if missing
```

---

## fix_broken_symlinks

Find symlinks whose targets no longer exist, then optionally remove or repoint them.

```python
fix_broken_symlinks(
    directory: str | Path,
    recursive: bool = False,
    remove: bool = False,
    new_target: str | Path | None = None,
) -> dict
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `directory` | `str` or `Path` | required | Directory to scan |
| `recursive` | `bool` | `False` | Search recursively |
| `remove` | `bool` | `False` | Delete broken symlinks if `True` |
| `new_target` | `str`, `Path`, or `None` | `None` | Repoint broken symlinks to this target if provided |

**Returns** `dict` with keys:

| Key | Content |
|-----|---------|
| `"found"` | `list[Path]` of all broken symlinks discovered |
| `"fixed"` | `list[Path]` of symlinks repointed to `new_target` |
| `"removed"` | `list[Path]` of symlinks that were deleted |

**Examples**

```python
import scitex as stx

# Audit: find broken symlinks without changing anything
result = stx.path.fix_broken_symlinks("./outputs")
print(f"Broken links: {len(result['found'])}")
for link in result['found']:
    print(f"  {link}")

# Remove broken symlinks
result = stx.path.fix_broken_symlinks("./outputs", recursive=True, remove=True)
print(f"Removed {len(result['removed'])} broken links")

# Repoint all broken links to a new location
result = stx.path.fix_broken_symlinks(
    "./outputs",
    new_target="/mnt/nas/new_location",
)
print(f"Repointed {len(result['fixed'])} links")
```
