---
name: introspect-type-hints
description: Detailed type annotation analysis — per-parameter hint breakdown (origin, args, Optional/Union flags) and full class-level annotation inventory. Use when you need to understand or validate type signatures programmatically.
---

# Type Hint Analysis

---

## get_type_hints_detailed

```python
stx.introspect.get_type_hints_detailed(
    dotted_path: str,
    include_extras: bool = True,
) -> dict
```

Calls `typing.get_type_hints` on a callable or class and decomposes each annotation into structured metadata: the raw string, the generic origin, type arguments, and flags for `Optional`/`Union`.

For classes, the analysis targets `__init__` automatically.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dotted_path` | `str` | required | Dotted path to a function, method, or class |
| `include_extras` | `bool` | `True` | Pass `include_extras=True` to `typing.get_type_hints` (preserves `Annotated` metadata) |

**Returns**

```python
{
    "success": bool,
    "hints": {
        "param_name": {
            "raw": str,            # Type as a readable string, e.g. "list[int]"
            "origin": str | None,  # Generic origin, e.g. "list", "Union"
            "args": list[str],     # Type arguments, e.g. ["int"] for list[int]
            "is_optional": bool,   # True when the type is Union[X, None]
            "is_union": bool,      # True when the type uses Union
            "is_generic": bool,    # True when origin is not None
        },
        ...
    },
    "return_hint": {               # Same structure; None if no return annotation
        "raw": str,
        "origin": str | None,
        "args": list[str],
        "is_optional": bool,
        "is_union": bool,
        "is_generic": bool,
    } | None,
    "hint_count": int,             # Number of parameter hints (excludes return)
    "type_info": dict,
}
```

Falls back to `__annotations__` if `get_type_hints` raises (e.g., forward references that cannot be resolved). Returns `{"success": False, ...}` if no hints are obtainable.

**Example**

```python
import scitex as stx

result = stx.introspect.get_type_hints_detailed("scitex.introspect.get_docstring")
for name, hint in result["hints"].items():
    print(f"{name}: {hint['raw']}", end="")
    if hint["is_optional"]:
        print("  [optional]", end="")
    print()

# Check the return type
if result["return_hint"]:
    print("returns:", result["return_hint"]["raw"])
```

---

## get_class_annotations

```python
stx.introspect.get_class_annotations(dotted_path: str) -> dict
```

Inventories all annotations on a class: class-level variable annotations (`__annotations__`) and per-method type hints.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dotted_path` | `str` | required | Dotted path to a class |

**Returns**

```python
{
    "success": bool,
    "class": str,
    "class_vars": {
        "var_name": {
            "raw": str, "origin": str | None, "args": list[str],
            "is_optional": bool, "is_union": bool, "is_generic": bool,
        },
        ...
    },
    "methods": {
        "method_name": {
            "param_name": { <same hint structure> },
            ...
            # includes "return" key for return annotation
        },
        ...
    },
    "class_var_count": int,
    "method_count": int,
}
```

Returns `{"success": False, "error": "..."}` if path is not a class.

Methods with no annotations are omitted from `methods`.

**Example**

```python
import scitex as stx

result = stx.introspect.get_class_annotations("pandas.DataFrame")
print(f"Class-level annotations: {result['class_var_count']}")
for var, hint in result["class_vars"].items():
    print(f"  {var}: {hint['raw']}")

print(f"Annotated methods: {result['method_count']}")
```

---

## Hint structure reference

Both functions return the same per-hint dict structure:

| Field | Type | Meaning |
|-------|------|---------|
| `raw` | `str` | Human-readable type string (`"list[int]"`, `"Optional[str]"`) |
| `origin` | `str \| None` | Generic base before specialisation (`"list"`, `"Union"`) |
| `args` | `list[str]` | Type parameters (`["int"]` for `list[int]`) |
| `is_optional` | `bool` | `True` when `None` is one of the Union arms |
| `is_union` | `bool` | `True` when the type is a `Union` |
| `is_generic` | `bool` | `True` when `origin` is not `None` |
