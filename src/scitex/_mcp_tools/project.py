#!/usr/bin/env python3
# Timestamp: 2026-02-19
# File: scitex/_mcp_tools/project.py
"""MCP tool registration for project file operations."""


import json


def _json(obj) -> str:
    return json.dumps(obj, indent=2, default=str)


def register_project_tools(mcp) -> None:
    """Register project file tools with FastMCP server."""

    @mcp.tool()
    async def project_list_files(
        root_path: str,
        relative_path: str = ".",
        max_depth: int = 3,
    ) -> str:
        """[project] List files and directories in a project directory.

        Parameters
        ----------
        root_path : str
            Absolute path to the project root (provided in system context).
        relative_path : str
            Sub-path within the project to list. Default is project root.
        max_depth : int
            How many directory levels to recurse (1–6, default 3).

        Returns
        -------
        str
            JSON with {"success": bool, "tree": [...], "path": str}.
        """
        from scitex.project._mcp.handlers import list_files_handler

        result = await list_files_handler(root_path, relative_path, max_depth)
        return _json(result)

    @mcp.tool()
    async def project_read_file(
        root_path: str,
        relative_path: str,
    ) -> str:
        """[project] Read the content of a file in a project.

        Parameters
        ----------
        root_path : str
            Absolute path to the project root.
        relative_path : str
            Path to the file relative to root_path.

        Returns
        -------
        str
            JSON with {"success": bool, "content": str, "size_bytes": int,
            "truncated": bool}.
            Files larger than 64 KB are truncated.
        """
        from scitex.project._mcp.handlers import read_file_handler

        result = await read_file_handler(root_path, relative_path)
        return _json(result)

    @mcp.tool()
    async def project_write_file(
        root_path: str,
        relative_path: str,
        content: str,
    ) -> str:
        """[project] Write or create a file in a project.

        Creates any missing parent directories automatically.

        Parameters
        ----------
        root_path : str
            Absolute path to the project root.
        relative_path : str
            Path to the file relative to root_path.
        content : str
            Text content to write (overwrites existing file).

        Returns
        -------
        str
            JSON with {"success": bool, "path": str, "size_bytes": int}.
        """
        from scitex.project._mcp.handlers import write_file_handler

        result = await write_file_handler(root_path, relative_path, content)
        return _json(result)

    @mcp.tool()
    async def project_search_files(
        root_path: str,
        name_pattern: str = "",
        content_pattern: str = "",
        relative_path: str = ".",
        max_results: int = 50,
    ) -> str:
        """[project] Search project files by name glob and/or content substring.

        At least one of name_pattern or content_pattern must be provided.

        Parameters
        ----------
        root_path : str
            Absolute path to the project root.
        name_pattern : str
            Glob pattern for filename (e.g. "*.py", "main*").
        content_pattern : str
            Substring to search for inside file contents.
        relative_path : str
            Sub-directory to search within (default: project root).
        max_results : int
            Maximum matches to return (default 50).

        Returns
        -------
        str
            JSON with {"success": bool, "matches": [...], "count": int,
            "truncated": bool}.
            Each match has "path" and optionally "line"/"preview" for content hits.
        """
        from scitex.project._mcp.handlers import search_files_handler

        result = await search_files_handler(
            root_path, name_pattern, content_pattern, relative_path, max_results
        )
        return _json(result)


# EOF
