---
description: MCP tool interface for stx.introspect — async handlers that wrap every Python API function. Use when calling introspect capabilities through the MCP protocol.
---

# MCP Tools

Every Python API function in `stx.introspect` has a corresponding async MCP handler in `scitex.introspect._mcp.handlers`. All handlers accept the same parameters as the Python function and return the same dict structure.

---

## Available MCP Tools

All tools are prefixed `introspect_` in the MCP namespace.

| MCP tool | Python function | Description |
|----------|----------------|-------------|
| `introspect_signature` | `q` | Signature + parameters + return annotation |
| `introspect_source` | `qq` | Full source code |
| `introspect_dir` | `dir` | Member listing with filtering |
| `introspect_api` | `list_api` | Recursive module API tree |
| `introspect_docstring` | `get_docstring` | Docstring (raw / parsed / summary) |
| `introspect_exports` | `get_exports` | Module's `__all__` contents |
| `introspect_examples` | `find_examples` | Usage examples found in tests |
| `introspect_class_hierarchy` | `get_class_hierarchy` | MRO + subclass tree |
| `introspect_type_hints` | `get_type_hints_detailed` | Per-parameter type breakdown |
| `introspect_imports` | `get_imports` | All import statements (with categories) |
| `introspect_dependencies` | `get_dependencies` | Top-level deps + optional tree |
| `introspect_call_graph` | `get_call_graph` | Outgoing calls + callers + module graph |

---

## Handler signatures

```python
# introspect_signature
async def q_handler(
    dotted_path: str,
    include_defaults: bool = True,
    include_annotations: bool = True,
) -> dict

# introspect_source
async def qq_handler(
    dotted_path: str,
    max_lines: int | None = None,
    include_decorators: bool = True,
) -> dict

# introspect_dir
async def dir_handler(
    dotted_path: str,
    filter: Literal["all", "public", "private", "dunder"] = "public",
    kind: Literal["all", "functions", "classes", "data", "modules"] | None = None,
    include_inherited: bool = False,
) -> dict

# introspect_api
async def list_api_handler(
    dotted_path: str,
    max_depth: int = 5,
    docstring: bool = False,
    root_only: bool = False,
) -> dict
# Returns: {"success": bool, "api": list[dict], "count": int}
# Each dict in "api" has: Type, Name, Docstring, Depth

# introspect_docstring
async def docstring_handler(
    dotted_path: str,
    format: Literal["raw", "parsed", "summary"] = "raw",
) -> dict

# introspect_exports
async def exports_handler(dotted_path: str) -> dict

# introspect_examples
async def examples_handler(
    dotted_path: str,
    search_paths: list[str] | None = None,
    max_results: int = 10,
) -> dict

# introspect_class_hierarchy
async def class_hierarchy_handler(
    dotted_path: str,
    include_builtins: bool = False,
    max_depth: int = 10,
) -> dict

# introspect_type_hints
async def type_hints_handler(
    dotted_path: str,
    include_extras: bool = True,
) -> dict

# introspect_imports
async def imports_handler(
    dotted_path: str,
    categorize: bool = True,
) -> dict

# introspect_dependencies
async def dependencies_handler(
    dotted_path: str,
    recursive: bool = False,
    max_depth: int = 3,
) -> dict

# introspect_call_graph
async def call_graph_handler(
    dotted_path: str,
    max_depth: int = 2,
    timeout_seconds: int = 10,
    internal_only: bool = True,
) -> dict
```

---

## list_api_handler vs list_api

`list_api_handler` serialises the DataFrame returned by `list_api` into a list of dicts using `df.to_dict(orient="records")` before returning, so the MCP result is JSON-serialisable.

```python
# MCP response shape
{
    "success": True,
    "api": [
        {"Type": "M", "Name": "scitex.io", "Docstring": "", "Depth": 0},
        {"Type": "F", "Name": "scitex.io.save", "Docstring": "", "Depth": 1},
        ...
    ],
    "count": 42,
}
```

---

## Error handling

All handlers catch any exception and return:

```python
{"success": False, "error": "<exception message>"}
```

This means MCP callers always receive a dict with a `"success"` key rather than an unhandled exception propagating through the transport.
