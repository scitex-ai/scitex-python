---
description: Static call graph extraction via AST — which functions a function calls, which functions call it, and the call graph for an entire module. Has timeout protection for large modules.
---

# Call Graph Analysis

Both functions use static AST analysis — they parse the source file without executing any code. Timeout protection (Unix `SIGALRM`) prevents hangs on large codebases.

---

## get_call_graph

```python
stx.introspect.get_call_graph(
    dotted_path: str,
    max_depth: int = 2,
    timeout_seconds: int = 10,
    internal_only: bool = True,
) -> dict
```

Builds an outgoing/incoming call graph for a single **function** or an entire **module**.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dotted_path` | `str` | required | Dotted path to a function or module |
| `max_depth` | `int` | `2` | Maximum traversal depth (currently affects module graph; function graph is always 1-level) |
| `timeout_seconds` | `int` | `10` | Abort after this many seconds and return a partial result (`"partial": True`). Set to `0` to disable |
| `internal_only` | `bool` | `True` | For function analysis: include only calls to other functions **defined in the same source file** |

**Returns — function mode** (when `dotted_path` resolves to a function):

```python
{
    "success": bool,
    "function": str,           # Short function name
    "calls": [
        {
            "name": str,       # "other_func" or "obj.method"
            "type": str,       # "function" or "method"
            "line": int,       # Source line of the call
            # For method calls:
            "object": str,     # Object variable name (e.g. "self")
            "method": str,     # Method name
        },
        ...
    ],
    "call_count": int,
    "called_by": [
        {
            "name": str,       # Name of the function that calls this one
            "line": int,       # Line where the caller is defined
        },
        ...
    ],
    "caller_count": int,
    "type_info": dict,
}
```

**Returns — module mode** (when `dotted_path` resolves to a module):

```python
{
    "success": bool,
    "module": str,
    "graph": {
        "function_name": {
            "calls": [ { "name": str, "type": str, "line": int }, ... ],
            "line": int,    # Line where the function is defined
        },
        ...
    },
    "function_count": int,
    "type_info": dict,
}
```

**Returns — timeout**:

```python
{
    "success": False,
    "error": "Operation timed out after 10s",
    "partial": True,
}
```

**Examples**

```python
import scitex as stx

# Calls made by a specific function
result = stx.introspect.get_call_graph("scitex.introspect._call_graph.get_call_graph")
print("Calls out:")
for call in result["calls"]:
    print(f"  {call['name']} (line {call['line']})")

print("Called by:")
for caller in result["called_by"]:
    print(f"  {caller['name']}")

# All calls in a module
result = stx.introspect.get_call_graph(
    "scitex.introspect._call_graph",
    internal_only=False,
    timeout_seconds=30,
)
for func, info in result["graph"].items():
    if info["calls"]:
        print(f"{func} → {[c['name'] for c in info['calls']]}")

# Increase timeout for a big module
result = stx.introspect.get_call_graph("scitex.io", timeout_seconds=30)
```

---

## get_function_calls

```python
stx.introspect.get_function_calls(
    dotted_path: str,
    include_methods: bool = True,
    include_builtins: bool = False,
) -> dict
```

Simplified wrapper around `get_call_graph` that returns only outgoing calls as a flat list of names, with optional filtering.

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dotted_path` | `str` | required | Dotted path to a function |
| `include_methods` | `bool` | `True` | Include method calls (`obj.method()`) |
| `include_builtins` | `bool` | `False` | Include common builtins (`print`, `len`, `range`, `str`, `int`, `float`, `list`, `dict`, `set`) |

**Returns**

```python
{
    "success": bool,
    "function": str,      # dotted_path as given
    "calls": list[str],   # Names of called functions/methods
    "call_count": int,
}
```

Internally calls `get_call_graph(..., max_depth=1, internal_only=False)` then applies the filters.

**Example**

```python
import scitex as stx

result = stx.introspect.get_function_calls(
    "scitex.introspect._call_graph._analyze_call_graph",
    include_builtins=False,
)
print(result["calls"])
# ["resolve_object", "get_type_info", "_build_function_index",
#  "_get_function_calls", "_find_callers", ...]
```

---

## Implementation notes

- Analysis is purely static (AST): it detects call nodes in the parse tree but does not resolve dynamic dispatch, `getattr`-based calls, or calls through variables.
- `called_by` for a function is found by scanning all other functions in the **same source file** only — not across modules.
- On Windows, the `SIGALRM`-based timeout is silently disabled; the operation runs without a time limit.
- Method calls are recorded as `"obj.method"` when the object is a simple name (`ast.Name`), or as just `"method"` for more complex expressions.
