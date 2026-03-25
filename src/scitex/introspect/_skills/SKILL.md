---
name: stx.introspect
description: IPython-style introspection for Python packages — signatures, source code, API trees, docstrings, type hints, class hierarchies, import analysis, and call graphs.
---

# stx.introspect

The `stx.introspect` module provides runtime and static inspection of any Python object or module. It mirrors the IPython `?` / `??` experience but returns structured dicts suitable for programmatic use, and exposes every function as an MCP tool.

All functions accept a **dotted path string** (e.g. `"scitex.io.save"`) and internally resolve it to the live Python object.

## Sub-skills

### IPython-style shortcuts and API tree
- [ipython-shortcuts.md](ipython-shortcuts.md) — `q` (signature), `qq` (source), `dir` (member listing), `list_api` (recursive module DataFrame)

### Documentation extraction
- [docstring-and-exports.md](docstring-and-exports.md) — `get_docstring` (raw/parsed/summary), `get_exports` (__all__), `find_examples` (usage search in test files)

### Class hierarchy
- [class-hierarchy.md](class-hierarchy.md) — `get_class_hierarchy` (MRO + subclass tree), `get_mro` (parent chain only)

### Type hint analysis
- [type-hints.md](type-hints.md) — `get_type_hints_detailed` (per-parameter breakdown), `get_class_annotations` (class vars + method hints)

### Import and dependency analysis
- [imports-and-dependencies.md](imports-and-dependencies.md) — `get_imports` (AST-extracted import statements), `get_dependencies` (top-level deps + optional recursive tree)

### Call graph analysis
- [call-graph.md](call-graph.md) — `get_call_graph` (outgoing calls + callers + module graph, with timeout), `get_function_calls` (simplified outgoing-only)

### Object resolution
- [resolve.md](resolve.md) — `resolve_object` (dotted path → live object), `get_type_info` (kind classification)

### MCP interface
- [mcp-tools.md](mcp-tools.md) — async handler signatures, `introspect_*` tool names, serialisation notes

---

## Quick reference

```python
import scitex as stx

# --- IPython shortcuts ---
stx.introspect.q("scitex.io.save")         # signature dict
stx.introspect.qq("scitex.io.save")        # source dict
stx.introspect.dir("scitex.io")            # members dict
stx.introspect.list_api(stx.stats)         # pd.DataFrame of full API tree

# --- Documentation ---
stx.introspect.get_docstring("scitex.io.save", format="parsed")
stx.introspect.get_exports("scitex.introspect")
stx.introspect.find_examples("scitex.io.save")

# --- Class hierarchy ---
stx.introspect.get_class_hierarchy("collections.abc.Mapping")
stx.introspect.get_mro("pandas.Series")

# --- Type hints ---
stx.introspect.get_type_hints_detailed("scitex.introspect.get_docstring")
stx.introspect.get_class_annotations("pandas.DataFrame")

# --- Imports & dependencies ---
stx.introspect.get_imports("scitex.introspect._call_graph")
stx.introspect.get_dependencies("scitex.io", recursive=True, max_depth=2)

# --- Call graph ---
stx.introspect.get_call_graph("scitex.introspect._call_graph.get_call_graph")
stx.introspect.get_function_calls("scitex.introspect._call_graph._analyze_call_graph")

# --- Resolution ---
obj, err = stx.introspect.resolve_object("scitex.io.save")
info = stx.introspect.get_type_info(obj)
```

## All exported names

```
q, qq, dir, list_api
get_docstring, get_exports, find_examples
get_class_hierarchy, get_mro
get_type_hints_detailed, get_class_annotations
get_imports, get_dependencies
get_call_graph, get_function_calls
resolve_object, get_type_info
```
