---
description: Resolve a dotted path string to a live Python object and classify it by kind (module, class, function, method, data). Foundational utility used internally by all other introspect functions.
---

# Object Resolution

---

## resolve_object

```python
stx.introspect.resolve_object(dotted_path: str) -> tuple[Any, str | None]
```

Converts a dotted string path into the corresponding Python object by trying progressively shorter module paths and attribute access.

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dotted_path` | `str` | Dotted path such as `"scitex.io.save"`, `"pandas.DataFrame"`, or `"json"` |

**Returns**

`(object, error)` tuple:
- On success: `(resolved_object, None)`
- On failure: `(None, "Could not resolve '...': <last error>")`

**Resolution algorithm**

For path `a.b.c.d`, it tries:
1. `importlib.import_module("a.b.c.d")`
2. `importlib.import_module("a.b.c")` then `getattr(module, "d")`
3. `importlib.import_module("a.b")` then `getattr(module, "c")`, `getattr(result, "d")`
4. `importlib.import_module("a")` then attribute chain

The first successful resolution is returned.

**Example**

```python
import scitex as stx

obj, err = stx.introspect.resolve_object("scitex.io.save")
# obj is the save function, err is None

obj, err = stx.introspect.resolve_object("nonexistent.module")
# obj is None, err is "Could not resolve 'nonexistent.module': ..."

obj, err = stx.introspect.resolve_object("pandas.DataFrame")
# obj is the DataFrame class

obj, err = stx.introspect.resolve_object("json")
# obj is the json module
```

---

## get_type_info

```python
stx.introspect.get_type_info(obj: Any) -> dict
```

Classifies any Python object and returns a metadata dict. Used internally by all introspect functions but also available directly.

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `obj` | `Any` | Any Python object |

**Returns**

```python
{
    "type": str,      # type(obj).__name__
    "kind": str,      # One of: "module", "class", "function", "method",
                      #          "property", "callable", "data"
    "module": str,    # obj.__module__ (None if not available)
    "qualname": str,  # obj.__qualname__ or obj.__name__ or str(obj)
}
```

**Kind classification rules**

| `kind` value | Condition |
|-------------|-----------|
| `"module"` | `inspect.ismodule(obj)` |
| `"class"` | `inspect.isclass(obj)` |
| `"function"` | `inspect.isfunction(obj)` or `inspect.isbuiltin(obj)` |
| `"method"` | `inspect.ismethod(obj)` |
| `"property"` | `isinstance(obj, property)` |
| `"callable"` | `callable(obj)` (fallthrough, e.g. class instances with `__call__`) |
| `"data"` | everything else |

**Example**

```python
import scitex as stx
import json

info = stx.introspect.get_type_info(json.dumps)
# {"type": "builtin_function_or_method", "kind": "function",
#  "module": "json", "qualname": "dumps"}

info = stx.introspect.get_type_info(json)
# {"type": "module", "kind": "module", "module": "json", "qualname": "json"}
```

---

## Notes

- `resolve_object` and `get_type_info` are the foundation that every other `stx.introspect` function calls first. You rarely need to call them directly unless building custom introspection tooling.
- `resolve_object` will import the module as a side-effect of resolution. For modules with expensive `__init__` code this may take time.
