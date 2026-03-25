---
name: project-mcp-files
description: MCP tools for project-scoped file reading, writing, listing, searching, and code execution — available to AI agents via the SciTeX MCP server.
---

# MCP File Operations

These are MCP tools exposed by the SciTeX server. They operate relative to the configured project root.

## project_read_file

Read a file from the project.

```
mcp__scitex__project_read_file(path: str) -> str
```

## project_write_file

Write content to a file in the project.

```
mcp__scitex__project_write_file(path: str, content: str) -> dict
```

## project_list_files

List files in a project directory.

```
mcp__scitex__project_list_files(directory: str = ".") -> list[str]
```

## project_search_files

Search for files by name pattern or content.

```
mcp__scitex__project_search_files(query: str, directory: str = ".") -> list[str]
```

## project_exec_python

Execute a Python script within the project context.

```
mcp__scitex__project_exec_python(script: str, timeout: int = 30) -> dict
```

Returns `{'stdout': ..., 'stderr': ..., 'exit_code': ...}`.

## project_exec_shell

Execute a shell command in the project root.

```
mcp__scitex__project_exec_shell(command: str, timeout: int = 30) -> dict
```

## Usage by AI agents

```python
# Example: AI agent reads and modifies a config file
content = mcp__scitex__project_read_file("config/settings.yaml")
updated = content.replace("lr: 0.001", "lr: 0.0001")
mcp__scitex__project_write_file("config/settings.yaml", updated)

# Run tests and check output
result = mcp__scitex__project_exec_shell("pytest tests/ -x -q")
print(result["stdout"])
```
