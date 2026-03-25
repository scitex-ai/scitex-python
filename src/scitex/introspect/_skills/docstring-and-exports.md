---
description: Extract docstrings (raw, parsed sections, or summary only) and retrieve a module's __all__ exports list. Use when you need documentation text or the official public API of a module.
---

# Docstring Extraction and Module Exports

---

## get_docstring

```python
stx.introspect.get_docstring(
    dotted_path: str,
    format: Literal["raw", "parsed", "summary"] = "raw",
) -> dict
```

Extracts the docstring from any Python object using `inspect.getdoc` (which strips leading indentation).

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dotted_path` | `str` | required | Dotted path to any Python object |
| `format` | `str` | `"raw"` | `"raw"` — full text as-is; `"parsed"` — split into named sections; `"summary"` — first paragraph only |

**Returns (format="raw")**

```python
{
    "success": bool,
    "docstring": str,     # Full cleaned docstring text
    "type_info": dict,
}
```

**Returns (format="parsed")**

```python
{
    "success": bool,
    "docstring": str,     # Full text (also available)
    "sections": {
        "summary": str,
        "description": str,
        "parameters": str,
        "returns": str,
        "examples": str,
        "notes": str,
        # Additional keys: "raises", "see_also" if present
    },
    "type_info": dict,
}
```

**Returns (format="summary")**

```python
{
    "success": bool,
    "docstring": str,     # First paragraph only (up to first blank line)
    "type_info": dict,
}
```

**Docstring parsing rules**

The parser recognises numpy/google-style section headers of the form:

```
Parameters
----------
```

or

```
Returns
-------
```

Sections detected: `Parameters`, `Returns`, `Examples`, `Notes`, `Raises`, `See Also`.

**Examples**

```python
import scitex as stx

# Quick one-line summary
doc = stx.introspect.get_docstring("scitex.io.save", format="summary")
print(doc["docstring"])

# Full structured parse
doc = stx.introspect.get_docstring("scitex.stats.test_ttest_ind", format="parsed")
print(doc["sections"]["parameters"])
print(doc["sections"]["returns"])

# Raw text
doc = stx.introspect.get_docstring("pandas.DataFrame")
print(doc["docstring"])
```

---

## get_exports

```python
stx.introspect.get_exports(dotted_path: str) -> dict
```

Returns a module's `__all__` list. If `__all__` is not defined, falls back to all public names (no leading `_`).

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dotted_path` | `str` | required | Dotted path to a module (not a function or class) |

**Returns**

```python
{
    "success": bool,
    "exports": list[str],   # Names in __all__ (or all public names)
    "has_all": bool,        # True if __all__ was explicitly defined
    "count": int,
    "type_info": dict,
}
```

Returns `{"success": False, "error": "..."}` if the path resolves to something other than a module.

**Examples**

```python
import scitex as stx

result = stx.introspect.get_exports("scitex.introspect")
print(result["has_all"])     # True
print(result["exports"])
# ['q', 'qq', 'dir', 'list_api', 'get_docstring', ...]

# Module without __all__
result = stx.introspect.get_exports("scitex.io")
print(result["has_all"])     # depends on whether __all__ is defined
```

---

## find_examples

```python
stx.introspect.find_examples(
    dotted_path: str,
    search_paths: list[str] | None = None,
    max_results: int = 10,
) -> dict
```

Searches test and example directories for source files that call the named function or class. Performs a simple string search on the object's `__name__` and returns file + line + surrounding context.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dotted_path` | `str` | required | Object whose name to search for |
| `search_paths` | `list[str] \| None` | `None` | Directories to search; if `None`, auto-detects `tests/`, `test/`, `examples/`, `example/` relative to the module's package root |
| `max_results` | `int` | `10` | Stop after this many matches |

**Returns**

```python
{
    "success": bool,
    "examples": [
        {
            "file": str,     # Absolute path to the file
            "line": int,     # 1-based line number of the match
            "context": str,  # 2 lines before + match line + 2 lines after
        },
        ...
    ],
    "count": int,
    "search_paths": list[str],
    # "message": str  — present when no directories found
}
```

**Example**

```python
import scitex as stx

result = stx.introspect.find_examples("scitex.io.save")
for ex in result["examples"]:
    print(f"{ex['file']}:{ex['line']}")
    print(ex["context"])
    print("---")

# Search a custom directory
result = stx.introspect.find_examples(
    "scitex.stats.test_anova",
    search_paths=["/my/project/tests"],
    max_results=5,
)
```

**Notes**

- Search is purely lexical (no import resolution). A hit means the object's `__name__` string appears on that line — it may include false positives from comments or unrelated identifiers.
- Context window is fixed at 2 lines before and 2 lines after the match line.
