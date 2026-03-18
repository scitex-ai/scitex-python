# Introspect Module Examples

IPython-like introspection for any Python package.

## Examples

1. **01_basic_introspection.py** - Signatures, docstrings, source code
2. **02_module_exploration.py** - Listing members and exports
3. **03_advanced_introspection.py** - Class hierarchy, type hints, imports
4. **04_call_graph_analysis.py** - Function call graphs with timeout
5. **05_find_usage_examples.py** - Find usage in tests/examples

## Quick Start

```python
from scitex.introspect import get_signature, get_docstring, get_source

# Like IPython's func?
result = get_signature("json.dumps")
print(result["signature"])

# Like IPython's func??
result = get_source("json.dumps", max_lines=20)
print(result["source"])

# Get docstring
result = get_docstring("json.dumps", format="summary")
print(result["docstring"])
```

## CLI Usage

```bash
# Signature
scitex introspect signature json.dumps

# Docstring
scitex introspect docstring json.dumps --format parsed

# Source code
scitex introspect source scitex.plt.plot --max-lines 50

# List members
scitex introspect members json --kind functions

# Class hierarchy
scitex introspect hierarchy collections.abc.Mapping

# Imports analysis
scitex introspect imports scitex.introspect._resolve

# Call graph
scitex introspect calls scitex.introspect._resolve --timeout 30
```

## MCP Tools

When used via MCP, tools are prefixed with `introspect_`:

- `introspect_signature` - Get function/class signature
- `introspect_docstring` - Get docstring
- `introspect_source` - Get source code
- `introspect_members` - List module/class members
- `introspect_exports` - Get __all__ exports
- `introspect_examples` - Find usage examples
- `introspect_hierarchy` - Get class hierarchy
- `introspect_hints` - Get type hints
- `introspect_imports` - Get module imports
- `introspect_deps` - Get dependencies
- `introspect_calls` - Get call graph
