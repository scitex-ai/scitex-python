# Contributing to SciTeX

## Module Structure

```
src/scitex/{module}/
├── __init__.py          # Public API exports
├── _core.py             # Core implementation
├── _mcp/                # MCP handlers (if applicable)
│   ├── __init__.py
│   └── handlers.py
└── README.md            # Module documentation
```

## Before Committing

1. Run focused tests: `pytest tests/scitex/{module}/ -v`
2. Verify no regressions in related modules
3. Update version if needed

## Version Consistency

- [ ] `pyproject.toml` version
- [ ] `src/scitex/__init__.py` `__version__`
- [ ] Git tag matches version
- [ ] GitHub release created
- [ ] PyPI published

## MCP Handler Pattern

```python
async def {tool}_handler(**kwargs) -> dict:
    """Return dict with 'success' key."""
    try:
        result = _core_function(**kwargs)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

## Branding for Family Packages

Set environment variables before importing:

```python
import os
os.environ.setdefault("{PACKAGE}_BRAND", "scitex.{module}")
os.environ.setdefault("{PACKAGE}_ALIAS", "{alias}")
from {package} import *
```

## See Also

- [CLI Reference](01_CLI_COMMANDS.md)
- [MCP Tools](02_MCP_TOOLS.md)
- [Environment Variables](03_ENV_VARIABLES.md)
- [SciTeX Family](05_SCITEX_FAMILY.md)
