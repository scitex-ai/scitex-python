---
description: Secure project file operations (list, read, write, search, exec) exposed as MCP tools with path traversal protection.
---

# stx.project — MCP File Operations

`stx.project._mcp.handlers` provides async handlers that back the MCP tools `project_list_files`, `project_read_file`, `project_write_file`, `project_search_files`, `project_exec_python`, and `project_exec_shell`.

All operations are sandboxed to paths under `ALLOWED_DATA_ROOT` (default `/app/data/users`, overridable via `SCITEX_PROJECT_DATA_ROOT` environment variable).

## Security model

Every handler calls `_resolve_safe(root_path, relative_path)` which:
1. Verifies `root_path` is under `ALLOWED_DATA_ROOT`
2. Verifies the resolved target is under `root_path` (no `../` traversal)
3. Raises `ValueError` on any violation (never silently allows)

## list_files_handler

List files and directories as a tree.

```python
from scitex.project._mcp.handlers import list_files_handler
import asyncio

result = asyncio.run(list_files_handler(
    root_path="/app/data/users/alice/myproject",
    relative_path=".",
    max_depth=3,           # 1–6, default 3
))
# {
#   "success": True,
#   "path": ".",
#   "tree": [
#     {"name": "data", "type": "dir", "children": [...]},
#     {"name": "analysis.py", "type": "file", "size": 1234},
#   ]
# }
```

Skips hidden files, `__pycache__`, `.git`, `node_modules`.

## read_file_handler

Read text file content (UTF-8, with `errors="replace"`).

```python
result = asyncio.run(read_file_handler(
    root_path="/app/data/users/alice/myproject",
    relative_path="results/summary.csv",
    max_bytes=65536,       # default 64 KiB
))
# {
#   "success": True,
#   "path": "results/summary.csv",
#   "content": "...",
#   "size_bytes": 1200,
#   "truncated": False,
# }
```

## write_file_handler

Write a text file, creating parent directories as needed.

```python
result = asyncio.run(write_file_handler(
    root_path="/app/data/users/alice/myproject",
    relative_path="notes/todo.md",
    content="# TODO\n- Check results\n",
))
# {"success": True, "path": "notes/todo.md", "size_bytes": 22}
```

## search_files_handler

Search by filename glob and/or content substring.

```python
result = asyncio.run(search_files_handler(
    root_path="/app/data/users/alice/myproject",
    name_pattern="*.py",
    content_pattern="import scitex",
    relative_path=".",
    max_results=50,
))
# {
#   "success": True,
#   "matches": [
#     {"path": "analysis.py", "line": 3, "preview": "import scitex as stx"},
#   ],
#   "count": 1,
#   "truncated": False,
# }
```

At least one of `name_pattern` or `content_pattern` must be provided.

## exec_python_handler

Execute Python code as a subprocess with `cwd=root_path`. Detects new/deleted/moved files.

```python
result = asyncio.run(exec_python_handler(
    root_path="/app/data/users/alice/myproject",
    code="import scitex as stx; stx.io.save([1,2,3], 'test.npy')",
    timeout=30,            # 5–60 s, default 30
))
# {
#   "success": True,
#   "exit_code": 0,
#   "stdout": "",
#   "stderr": "",
#   "new_files": ["test.npy"],
#   "moved_files": [],
#   "deleted_files": [],
# }
```

## exec_shell_handler

Execute a shell command via `/bin/bash -c` with `cwd=root_path`.

```python
result = asyncio.run(exec_shell_handler(
    root_path="/app/data/users/alice/myproject",
    command="ls -la results/",
    timeout=30,
))
```

Response format is identical to `exec_python_handler`.

## MCP tool names

| Handler | MCP tool |
|---|---|
| `list_files_handler` | `project_list_files` |
| `read_file_handler` | `project_read_file` |
| `write_file_handler` | `project_write_file` |
| `search_files_handler` | `project_search_files` |
| `exec_python_handler` | `project_exec_python` |
| `exec_shell_handler` | `project_exec_shell` |
