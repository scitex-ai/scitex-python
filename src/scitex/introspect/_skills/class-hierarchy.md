---
description: Inspect inheritance trees — MRO (parent classes in resolution order) and all known subclasses. Use when you need to understand a class's ancestry or find classes that extend it.
---

# Class Hierarchy Analysis

---

## get_class_hierarchy

```python
stx.introspect.get_class_hierarchy(
    dotted_path: str,
    include_builtins: bool = False,
    max_depth: int = 10,
) -> dict
```

Returns both the upward chain (MRO) and the downward tree (subclasses) for any class.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dotted_path` | `str` | required | Dotted path to a class, e.g. `"pandas.DataFrame"` |
| `include_builtins` | `bool` | `False` | Include builtin classes (`object`, `type`, etc.) from `builtins` module |
| `max_depth` | `int` | `10` | Maximum depth for recursive subclass traversal |

**Returns**

```python
{
    "success": bool,
    "class": str,         # The dotted_path as given
    "mro": [
        {
            "name": str,       # Short class name
            "module": str,     # Module where the class lives
            "qualname": str,   # "module.ClassName"
        },
        ...
    ],
    "mro_count": int,
    "subclasses": [
        {
            "name": str,
            "module": str,
            "qualname": str,
            "subclasses": [...],  # Only present if the class has further subclasses
        },
        ...
    ],
    "subclass_count": int,   # Total including nested
    "type_info": dict,
}
```

Returns `{"success": False, "error": "..."}` if the path does not resolve to a class.

**Example**

```python
import scitex as stx

result = stx.introspect.get_class_hierarchy("collections.abc.Mapping")
print("Parents:")
for cls in result["mro"]:
    print(f"  {cls['qualname']}")

print(f"Known subclasses: {result['subclass_count']}")
for sub in result["subclasses"]:
    print(f"  {sub['qualname']}")
```

---

## get_mro

```python
stx.introspect.get_mro(
    dotted_path: str,
    include_builtins: bool = False,
) -> dict
```

Simplified version that returns only the Method Resolution Order — parent classes in the order Python uses to resolve attribute lookup.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dotted_path` | `str` | required | Dotted path to a class |
| `include_builtins` | `bool` | `False` | Include `object` and other builtins |

**Returns**

```python
{
    "success": bool,
    "class": str,
    "mro": list[str],   # Qualified names: ["module.ClassName", ...]
}
```

**Example**

```python
import scitex as stx

result = stx.introspect.get_mro("pandas.Series")
for cls in result["mro"]:
    print(cls)
# pandas.core.series.Series
# pandas.core.base.IndexOpsMixin
# pandas.core.arraylike.OpsMixin
# ...
```

---

## Difference between the two functions

| | `get_mro` | `get_class_hierarchy` |
|---|---|---|
| Parents (MRO) | Yes — flat list of strings | Yes — list of dicts with name/module |
| Subclasses | No | Yes — recursive tree |
| Return size | Small | Potentially large for widely-subclassed base classes |

Use `get_mro` for a quick ancestry check. Use `get_class_hierarchy` when you also need to find all classes that extend a given base.
