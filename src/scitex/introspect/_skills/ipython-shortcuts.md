---
name: introspect-ipython-shortcuts
description: IPython-style quick lookup — q (signature), qq (source), dir (members), list_api (recursive API tree). Use when you need to inspect a function, class, or module interactively.
---

# IPython-Style Shortcuts

Four functions that mirror the interactive IPython `?` / `??` / `dir()` workflow, but work as plain Python calls and return structured dicts instead of printing to stdout.

---

## q — Signature (like `func?`)

```python
stx.introspect.q(
    dotted_path: str,
    include_defaults: bool = True,
    include_annotations: bool = True,
) -> dict
```

Resolves a dotted path to any callable and returns its full signature.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dotted_path` | `str` | required | Dotted path to the callable, e.g. `"scitex.io.save"` |
| `include_defaults` | `bool` | `True` | Include default values in parameter info |
| `include_annotations` | `bool` | `True` | Include type annotations |

**Returns**

```python
{
    "success": bool,
    "name": str,                  # Function/class name
    "signature": str,             # Human-readable: "save(obj, path: str, ...) -> None"
    "parameters": [
        {
            "name": str,
            "kind": str,          # POSITIONAL_OR_KEYWORD, VAR_POSITIONAL, etc.
            "annotation": str,    # omitted if no annotation or include_annotations=False
            "default": str,       # repr() of default; omitted if no default
        },
        ...
    ],
    "return_annotation": str | None,
    "type_info": {
        "type": str, "kind": str, "module": str, "qualname": str
    },
}
```

**Example**

```python
import scitex as stx

result = stx.introspect.q("scitex.io.save")
print(result["signature"])
# save(obj, path: str, ...) -> None

# Inspect a class (resolves __init__)
result = stx.introspect.q("pandas.DataFrame")
for p in result["parameters"]:
    print(p["name"], p.get("annotation", ""))
```

---

## qq — Full Source (like `func??`)

```python
stx.introspect.qq(
    dotted_path: str,
    max_lines: int | None = None,
    include_decorators: bool = True,
) -> dict
```

Retrieves the source code of any Python object via `inspect.getsource`.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dotted_path` | `str` | required | Dotted path to the object |
| `max_lines` | `int \| None` | `None` | Truncate to first N lines (appends `... (N more lines)`) |
| `include_decorators` | `bool` | `True` | When `False`, strips leading `@decorator` lines |

**Returns**

```python
{
    "success": bool,
    "source": str,        # Full source text
    "file": str,          # Absolute path to source file
    "line_start": int,    # Line number where definition starts
    "line_count": int,    # Total lines in full source
    "type_info": dict,
}
```

**Example**

```python
result = stx.introspect.qq("scitex.io.save", max_lines=20)
print(result["source"])
print(f"Defined at {result['file']}:{result['line_start']}")
```

---

## dir — Member Listing (like `dir()`)

```python
stx.introspect.dir(
    dotted_path: str,
    filter: Literal["all", "public", "private", "dunder"] = "public",
    kind: Literal["all", "functions", "classes", "data", "modules"] | None = None,
    include_inherited: bool = False,
) -> dict
```

Lists members of a module or class with per-member metadata.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dotted_path` | `str` | required | Dotted path to the module or class |
| `filter` | `str` | `"public"` | `"all"`, `"public"` (no leading `_`), `"private"` (single `_`), `"dunder"` (`__x__`) |
| `kind` | `str \| None` | `None` | Restrict to `"functions"`, `"classes"`, `"data"`, or `"modules"` |
| `include_inherited` | `bool` | `False` | For classes, include members inherited from base classes |

**Returns**

```python
{
    "success": bool,
    "members": [
        {
            "name": str,
            "kind": str,      # "function", "class", "data", "module", "method", etc.
            "summary": str,   # First line of docstring, truncated at 100 chars
        },
        ...
    ],
    "count": int,
    "type_info": dict,
}
```

**Example**

```python
# List all public functions in stx.io
result = stx.introspect.dir("scitex.io", kind="functions")
for m in result["members"]:
    print(f"{m['name']:20s}  {m['summary']}")

# Show only dunder methods on a class
result = stx.introspect.dir("pandas.DataFrame", filter="dunder")
```

---

## list_api — Recursive Module Tree

```python
stx.introspect.list_api(
    module: str | Any,
    columns: list[str] = ["Type", "Name", "Docstring", "Depth"],
    max_depth: int = 5,
    docstring: bool = False,
    tree: bool = True,
    print_output: bool = False,
    drop_duplicates: bool = True,
    root_only: bool = False,
    skip_depwarnings: bool = True,
) -> pd.DataFrame
```

Recursively walks a module and returns its entire API as a pandas DataFrame. Only public names are included (no leading `_`). Avoids infinite cycles via a visited-set guard.

**Type column values:** `"M"` = module, `"F"` = function, `"C"` = class.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `module` | `str \| Any` | required | Module name string or already-imported module object |
| `columns` | `list[str]` | `["Type","Name","Docstring","Depth"]` | Columns to keep in the returned DataFrame |
| `max_depth` | `int` | `5` | Maximum recursion depth (0 = root module only) |
| `docstring` | `bool` | `False` | Populate the `Docstring` column |
| `tree` | `bool` | `True` | Enable tree-style console print when `print_output=True` |
| `print_output` | `bool` | `False` | Print tree to stdout |
| `drop_duplicates` | `bool` | `True` | Remove rows with duplicate `Name` values |
| `root_only` | `bool` | `False` | Show only names with at most one `.` in the path |
| `skip_depwarnings` | `bool` | `True` | Suppress DeprecationWarning and UserWarning during traversal |

**Returns:** `pd.DataFrame` with at least columns `Type`, `Name`, `Docstring`, `Depth`.

**Example**

```python
import scitex as stx

# Full API tree of scitex.stats
df = stx.introspect.list_api(stx.stats, docstring=True)
print(df[df["Type"] == "F"]["Name"].tolist())

# Top-level only
df = stx.introspect.list_api("scitex", root_only=True)

# Print tree to terminal
stx.introspect.list_api(stx.io, print_output=True)
```

**Notes**

- Strings with hyphens are normalized (e.g., `"scitex-stats"` → `"scitex_stats"`) before import.
- Only submodules whose `__name__` starts with the parent `__name__` are traversed (prevents walking sibling packages).
- Functions and classes defined in a different module (re-exports from siblings) are excluded.
