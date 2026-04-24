#!/usr/bin/env python3
# Timestamp: 2026-02-19
# File: scitex/_mcp_tools/project.py
"""MCP tool registration for project file operations."""


def register_project_tools(mcp) -> None:
    """Register project file tools with FastMCP server."""

    @mcp.tool()
    async def project_list_files(
        root_path: str,
        relative_path: str = ".",
        max_depth: int = 3,
    ) -> str:
        """Tree-walk a project's directory and return a nested file/dir listing bounded by `max_depth` — for agents that see a project as a remote root and need to orient before editing. Drop-in replacement for `tree -L N`, `ls -R`, and hand-rolled `os.walk` with depth tracking. Use when the agent is handed a `root_path` and needs to know what's in there before reading, or when the user asks "what's in this project?", "list the tree", "show me the layout".

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

        # Handler already called above; wrap result directly
        from scitex_dev.types import Result

        return Result(
            success=True,
            data=result,
            idempotent=True,
        ).to_json()

    @mcp.tool()
    async def project_read_file(
        root_path: str,
        relative_path: str,
    ) -> str:
        """Read a text file's contents from a project root, auto-truncating at 64 KB so big files don't blow context. Drop-in replacement for `open(path).read()` with manual size guards. Use when an agent needs the content of a specific project file — e.g. a config, source module, or README — and knows the relative path. First call `project_list_files` or `project_search_files` if the path is uncertain.

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

        # Handler already called above; wrap result directly
        from scitex_dev.types import Result

        return Result(
            success=True,
            data=result,
            idempotent=True,
        ).to_json()

    @mcp.tool()
    async def project_write_file(
        root_path: str,
        relative_path: str,
        content: str,
    ) -> str:
        """Write or overwrite a *text* file inside a project root, auto-`mkdir -p`ing any missing parent directories. Drop-in replacement for `pathlib.Path(...).write_text()` + manual `parents=True, exist_ok=True`. Use when an agent needs to create / overwrite a config, script, README, or code file at a known relative path. For binary outputs (.png, .mp3, .mp4) use `project_exec_python` or `project_exec_shell` instead.

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

        # Handler already called above; wrap result directly
        from scitex_dev.types import Result

        return Result(
            success=True,
            data=result,
            side_effects=["file_modify: writes or creates file in project"],
        ).to_json()

    @mcp.tool()
    async def project_search_files(
        root_path: str,
        name_pattern: str = "",
        content_pattern: str = "",
        relative_path: str = ".",
        max_results: int = 50,
    ) -> str:
        """Find files in a project by filename glob and/or a substring inside the file contents, capped at `max_results`. Drop-in replacement for `find . -name '*.py' | xargs grep -l foo`, ripgrep, or `pathlib.Path.rglob(...)`. Use when the agent needs to locate a file whose exact path isn't known — "find configs", "grep for FUNC_NAME across the project", "where's the test for X?", before reading with `project_read_file`.

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

        # Handler already called above; wrap result directly
        from scitex_dev.types import Result

        return Result(
            success=True,
            data=result,
            idempotent=True,
        ).to_json()

    @mcp.tool()
    async def project_exec_python(
        root_path: str,
        code: str,
        timeout: int = 30,
    ) -> str:
        """Run an arbitrary Python snippet with `cwd` pinned to the project root, capturing stdout / stderr / exit code and reporting new files created — the escape hatch when `project_write_file` (text-only) cannot produce the needed output. Drop-in replacement for `subprocess.run(['python', '-c', code], cwd=root)`. Use when the agent must produce binary artifacts (PNG via matplotlib, MP3 via pydub, `.npz` via numpy, PDFs via reportlab) or run a computation that `project_write_file` can't express.

        Use this to generate binary files (audio, video, images) that
        project_write_file cannot create (it only writes text).
        The code runs with cwd set to the project root.

        Parameters
        ----------
        root_path : str
            Absolute path to the project root.
        code : str
            Python code to execute. Use print() for output.
        timeout : int
            Max execution time in seconds (5–60, default 30).

        Returns
        -------
        str
            JSON with {"success": bool, "exit_code": int,
            "stdout": str, "stderr": str, "new_files": [...]}.
        """
        from scitex.project._mcp.handlers import exec_python_handler

        result = await exec_python_handler(root_path, code, timeout)

        # Handler already called above; wrap result directly
        from scitex_dev.types import Result

        return Result(
            success=True,
            data=result,
            side_effects=["code_exec: runs Python code in project directory"],
        ).to_json()

    @mcp.tool()
    async def project_exec_shell(
        root_path: str,
        command: str,
        timeout: int = 30,
    ) -> str:
        """Run an arbitrary `/bin/bash` command with `cwd` pinned to the project root, capturing stdout / stderr / exit code and reporting new files created. Drop-in replacement for `subprocess.run(['bash', '-c', cmd], cwd=root)`. Use when the agent needs external binaries — `ffmpeg` for audio/video transcode, `sox` for audio edits, `imagemagick convert` for image ops, `pandoc` for doc conversion, `latex`/`pdflatex` for document build, `git` for VCS ops, `ls -la` / `du -sh` for diagnostics.

        Use this to run system commands (ffmpeg, sox, imagemagick, etc.)
        for file processing. The command runs via /bin/bash with cwd
        set to the project root.

        Parameters
        ----------
        root_path : str
            Absolute path to the project root.
        command : str
            Shell command to execute.
        timeout : int
            Max execution time in seconds (5–60, default 30).

        Returns
        -------
        str
            JSON with {"success": bool, "exit_code": int,
            "stdout": str, "stderr": str, "new_files": [...]}.
        """
        from scitex.project._mcp.handlers import exec_shell_handler

        result = await exec_shell_handler(root_path, command, timeout)

        # Handler already called above; wrap result directly
        from scitex_dev.types import Result

        return Result(
            success=True,
            data=result,
            side_effects=["shell_exec: runs shell command in project directory"],
        ).to_json()


# EOF
