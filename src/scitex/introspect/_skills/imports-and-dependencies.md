---
description: Static import analysis via AST — list all import statements in a module source file, categorised as stdlib/third-party/local, and build a dependency tree. Use when auditing what a module depends on.
---

# Import and Dependency Analysis

Both functions work through static AST parsing of the module's source file — no dynamic import execution.

---

## get_imports

```python
stx.introspect.get_imports(
    dotted_path: str,
    categorize: bool = True,
) -> dict
```

Reads the source file of a module, parses it with `ast`, and extracts every `import` and `from ... import` statement.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dotted_path` | `str` | required | Dotted path to a module (not a function or class) |
| `categorize` | `bool` | `True` | Group results into `stdlib`, `third_party`, `local` sub-lists |

**Returns**

```python
{
    "success": bool,
    "module": str,
    "source_file": str,
    "imports": [
        # For "import foo" or "import foo as bar":
        {
            "type": "import",
            "module": str,       # "foo"
            "alias": str | None, # "bar" or None
            "line": int,
        },
        # For "from foo import bar" or "from .foo import bar":
        {
            "type": "from",
            "module": str,       # "foo" (empty string for "from . import x")
            "name": str,         # "bar"
            "alias": str | None,
            "level": int,        # Relative import depth (0 = absolute)
            "line": int,
        },
        ...
    ],
    "import_count": int,
    # Present when categorize=True:
    "categories": {
        "stdlib": [ ... ],       # Same import dicts
        "third_party": [ ... ],
        "local": [ ... ],        # Relative imports (level > 0) end up here
    },
    "type_info": dict,
}
```

Returns `{"success": False, "error": "..."}` when:
- The path resolves to something other than a module.
- The source file cannot be found (e.g., compiled builtins).
- The source cannot be parsed.

**Stdlib detection**

Uses `sys.stdlib_module_names` (Python 3.10+) or a fallback heuristic for older Python. Common modules (`ast`, `os`, `pathlib`, etc.) are always present.

**Example**

```python
import scitex as stx

result = stx.introspect.get_imports("scitex.introspect._call_graph")
print(f"Total imports: {result['import_count']}")

cats = result["categories"]
print("stdlib:", [i["module"] for i in cats["stdlib"]])
print("third-party:", [i["module"] for i in cats["third_party"]])
print("local:", [i["module"] for i in cats["local"]])

# Find all relative imports
relative = [i for i in result["imports"] if i.get("level", 0) > 0]
```

---

## get_dependencies

```python
stx.introspect.get_dependencies(
    dotted_path: str,
    recursive: bool = False,
    max_depth: int = 3,
) -> dict
```

Builds on `get_imports` to produce a deduplicated list of top-level module names that the target module depends on. Optionally walks the dependency tree recursively.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dotted_path` | `str` | required | Dotted path to a module |
| `recursive` | `bool` | `False` | Recursively analyse each imported non-stdlib module |
| `max_depth` | `int` | `3` | Maximum recursion depth (only relevant when `recursive=True`) |

**Returns** (extends `get_imports` return with additional keys):

```python
{
    # All fields from get_imports(..., categorize=True)
    "dependencies": list[str],      # Sorted top-level module names
    "dependency_count": int,
    # Only when recursive=True:
    "tree": {
        "module": str,
        "imports": [
            {
                "module": str,
                "imports": [...],   # Nested tree; stops at max_depth or stdlib
                # "truncated": True  — present when cut off by depth/cycle guard
            },
            ...
        ],
    },
}
```

**Recursion rules:**
- Stdlib modules are not recursed into (only non-stdlib).
- A visited-set prevents infinite cycles.
- Nodes cut off by `max_depth` or already-visited carry `"truncated": True`.

**Example**

```python
import scitex as stx

# Simple: what does scitex.introspect._imports import?
result = stx.introspect.get_dependencies("scitex.introspect._imports")
print(result["dependencies"])
# ['ast', 'inspect', 'pathlib', ...]

# Deep tree for a third-party module
result = stx.introspect.get_dependencies(
    "scitex.io",
    recursive=True,
    max_depth=2,
)
import json
print(json.dumps(result["tree"], indent=2))
```

---

## Summary

| Function | Input | Output |
|----------|-------|--------|
| `get_imports` | module path | Every import statement + optional categorisation |
| `get_dependencies` | module path | Deduplicated top-level deps + optional recursive tree |
