---
name: stx.project
description: SciTeX project file operations — secure MCP handlers for list, read, write, search, and execute within project sandboxes.
---

# stx.project — Skills Index

Provides MCP tool handlers for sandboxed project file operations. All paths are constrained to `ALLOWED_DATA_ROOT` with path traversal protection.

## Sub-skills

| File | Description |
|------|-------------|
| [mcp-file-ops.md](mcp-file-ops.md) | list_files, read_file, write_file, search_files, exec_python, exec_shell handlers; security model |

## Quick Reference

```python
# Via MCP tools (preferred)
# project_list_files, project_read_file, project_write_file,
# project_search_files, project_exec_python, project_exec_shell

# Directly (async)
from scitex.project._mcp.handlers import (
    list_files_handler, read_file_handler, write_file_handler,
    search_files_handler, exec_python_handler, exec_shell_handler,
)
import asyncio

result = asyncio.run(list_files_handler("/app/data/users/alice/proj"))
```

## Related modules

| Task | Module |
|---|---|
| Project scaffolding | `stx.template` |
| Experiment lifecycle | `stx.session` |
| File I/O | `stx.io` |
| Path management | `stx.path` |
