#!/usr/bin/env python3
# Timestamp: 2026-03-13
# File: scitex/_mcp_tools/dev.py

"""MCP tool registration for developer utilities.

All handlers return structured Result JSON via scitex_dev.mcp_utils.
"""


def register_dev_tools(mcp) -> None:
    """Register developer tools with FastMCP server."""

    @mcp.tool()
    async def dev_versions_list(
        packages: list[str] | None = None,
    ) -> str:
        """List versions across the scitex ecosystem.

        Shows version information from multiple sources:
        - pyproject.toml (local source)
        - installed package (importlib.metadata)
        - git tag (latest version tag)
        - git branch (current branch)
        - PyPI (remote published version)

        Parameters
        ----------
        packages : list[str] | None
            List of package names to check. If None, checks all ecosystem packages.
            Available packages: scitex, scitex-cloud, scitex-writer, scitex-dataset,
            figrecipe, crossref-local, openalex-local, socialia

        Returns
        -------
        str
            JSON Result with version information for each package.
        """
        from scitex_dev.dev_mcp.handlers import list_versions_handler

        return await list_versions_handler(packages)

    @mcp.tool()
    async def dev_config_show() -> str:
        """Get current developer configuration.

        Returns the configuration from ~/.scitex/dev_config.yaml including:
        - Packages to track
        - SSH hosts
        - GitHub remotes
        - Branches to track

        Returns
        -------
        str
            JSON Result with current configuration.
        """
        from scitex_dev.dev_mcp.handlers import get_config_handler

        return await get_config_handler()

    @mcp.tool()
    async def dev_test_local(
        module: str = "",
        fast: bool = False,
        coverage: bool = False,
        exitfirst: bool = True,
        pattern: str = "",
        parallel: str = "auto",
    ) -> str:
        """Run project tests locally via pytest.

        Auto-detects project root via git. Uses parallel execution by default.

        Parameters
        ----------
        module : str
            Module to test (e.g., "stats", "io", "plt"). Empty for all.
        fast : bool
            Skip @slow tests.
        coverage : bool
            Enable coverage reporting.
        exitfirst : bool
            Stop on first failure.
        pattern : str
            Test name filter (-k pattern).
        parallel : str
            Parallel workers ("auto", "0", or number).

        Returns
        -------
        str
            JSON Result with {"exit_code": int}.
        """
        from scitex_dev.dev_mcp.handlers import test_run_handler

        return await test_run_handler(
            module, fast, coverage, exitfirst, pattern, parallel
        )

    @mcp.tool()
    async def dev_test_hpc(
        module: str = "",
        fast: bool = False,
        hpc_cpus: int = 8,
        hpc_partition: str = "sapphire",
        hpc_time: str = "00:10:00",
        hpc_mem: str = "16G",
        async_mode: bool = False,
    ) -> str:
        """Run project tests on HPC (Spartan) via Slurm.

        Syncs project via rsync, then runs pytest via srun (blocking)
        or sbatch (async). Use dev_test_hpc_poll to check async job status.

        Parameters
        ----------
        module : str
            Module to test. Empty for all.
        fast : bool
            Skip @slow tests.
        hpc_cpus : int
            CPUs per task (default 8).
        hpc_partition : str
            Slurm partition (default "sapphire").
        hpc_time : str
            Time limit (default "00:10:00").
        hpc_mem : str
            Memory limit (default "16G").
        async_mode : bool
            If True, submit via sbatch and return job ID immediately.
            If False, run blocking via srun.

        Returns
        -------
        str
            JSON Result with {"exit_code": int} for srun,
            or {"job_id": str} for sbatch.
        """
        from scitex_dev.dev_mcp.handlers import test_hpc_run_handler

        return await test_hpc_run_handler(
            module, fast, hpc_cpus, hpc_partition, hpc_time, hpc_mem, async_mode
        )

    @mcp.tool()
    async def dev_test_hpc_poll(
        job_id: str | None = None,
    ) -> str:
        """Check HPC test job status.

        Queries sacct for the job state. If completed/failed, also fetches
        the last 20 lines of output.

        Parameters
        ----------
        job_id : str, optional
            Slurm job ID. If None, uses the last submitted job.

        Returns
        -------
        str
            JSON Result with {"state": str, "output": str|null, "job_id": str}.
            States: COMPLETED, RUNNING, PENDING, FAILED, TIMEOUT, CANCELLED.
        """
        from scitex_dev.dev_mcp.handlers import test_hpc_poll_handler

        return await test_hpc_poll_handler(job_id)

    @mcp.tool()
    async def dev_test_hpc_result(
        job_id: str | None = None,
    ) -> str:
        """Fetch full HPC test output.

        Downloads the complete stdout from a finished HPC test job via scp.

        Parameters
        ----------
        job_id : str, optional
            Slurm job ID. If None, uses the last submitted job.

        Returns
        -------
        str
            JSON Result with {"output": str|null, "job_id": str}.
        """
        from scitex_dev.dev_mcp.handlers import test_hpc_result_handler

        return await test_hpc_result_handler(job_id)

    @mcp.tool()
    async def dev_versions_sync(
        hosts: list[str] | None = None,
        packages: list[str] | None = None,
        install: bool = True,
        confirm: bool = False,
    ) -> str:
        """Sync ecosystem packages to remote hosts (git stash, pull, pip install).

        Safety: call first without confirm to preview, then with confirm=True
        to execute. Parallel by default across hosts and packages.

        Parameters
        ----------
        hosts : list[str] | None
            Host names to sync. None = all enabled hosts.
        packages : list[str] | None
            Package names. None = host-specific defaults from config.
        install : bool
            Pip install after pull (default True).
        confirm : bool
            If False (default), preview only (dry run).
            If True, execute the sync operation.

        Returns
        -------
        str
            JSON Result with {host_name: {package: {status, commands|output, error}}}.
        """
        from scitex_dev.dev_mcp.handlers import sync_handler

        return await sync_handler(hosts, packages, install, confirm)

    @mcp.tool()
    async def dev_versions_sync_local(
        packages: list[str] | None = None,
        confirm: bool = False,
    ) -> str:
        """Install all local editable packages (pip install -e).

        Safety: call first without confirm to preview, then with confirm=True
        to execute.

        Parameters
        ----------
        packages : list[str] | None
            Package names. None = all configured packages.
        confirm : bool
            If False (default), preview only (dry run).
            If True, execute pip install -e.

        Returns
        -------
        str
            JSON Result with {package: {status, output|commands}}.
        """
        from scitex_dev.dev_mcp.handlers import sync_local_handler

        return await sync_local_handler(packages, confirm)

    @mcp.tool()
    async def dev_fix_mismatches(
        hosts: list[str] | None = None,
        packages: list[str] | None = None,
        local: bool = True,
        remote: bool = True,
        confirm: bool = False,
    ) -> str:
        """Detect and fix version mismatches across the ecosystem.

        Detects all packages with non-ok status, then fixes them:
        - Local: pip install -e . where installed != toml
        - Remote: git pull + pip install on hosts

        Safety: call first without confirm to preview, then with confirm=True.

        Parameters
        ----------
        hosts : list[str] | None
            Host names. None = all enabled hosts.
        packages : list[str] | None
            Package names. None = all with mismatches.
        local : bool
            Fix local mismatches (default True).
        remote : bool
            Fix remote mismatches (default True).
        confirm : bool
            If False (default), preview only (dry run).

        Returns
        -------
        str
            JSON Result with {detected, local_fixes, remote_fixes, summary}.
        """
        from scitex_dev.dev_mcp.handlers import fix_mismatches_handler

        return await fix_mismatches_handler(hosts, packages, local, remote, confirm)

    @mcp.tool()
    async def dev_versions_diff(
        host: str | None = None,
        packages: list[str] | None = None,
    ) -> str:
        """Show git diff on remote host(s). Read-only operation.

        Shows uncommitted changes (git status + git diff) on remote hosts.
        Use this to review changes before committing with dev_versions_commit.

        Parameters
        ----------
        host : str | None
            Host name (e.g., "nas"). None = first enabled host.
        packages : list[str] | None
            Package names. None = host-configured defaults.

        Returns
        -------
        str
            JSON Result with {host: {package: {status, files, diff_stat, diff}}}.
        """
        from scitex_dev.dev_mcp.handlers import remote_diff_handler

        return await remote_diff_handler(host, packages)

    @mcp.tool()
    async def dev_versions_commit(
        host: str,
        packages: list[str] | None = None,
        message: str | None = None,
        push: bool = True,
        confirm: bool = False,
    ) -> str:
        """Commit dirty changes on a remote host and push to origin.

        Safety: call first without confirm to preview, then with confirm=True
        to execute. Auto-generates commit message if not provided.

        Parameters
        ----------
        host : str
            Host name (e.g., "nas"). Required.
        packages : list[str] | None
            Package names. None = host-configured defaults.
        message : str | None
            Commit message. Auto-generated if not provided.
        push : bool
            Push to origin after commit (default True).
        confirm : bool
            If False (default), preview only (dry run).
            If True, execute commit + push.

        Returns
        -------
        str
            JSON Result with {package: {status, commands|output}}.
        """
        from scitex_dev.dev_mcp.handlers import remote_commit_handler

        return await remote_commit_handler(host, packages, message, push, confirm)

    @mcp.tool()
    async def dev_versions_pull(
        packages: list[str] | None = None,
        confirm: bool = False,
        stash: bool = True,
    ) -> str:
        """Pull latest from origin to local repos.

        Safety: call first without confirm to preview, then with confirm=True
        to execute. Use after dev_versions_commit to sync remote changes locally.

        Parameters
        ----------
        packages : list[str] | None
            Package names. None = all configured packages.
        confirm : bool
            If False (default), preview only (dry run).
            If True, execute git pull.
        stash : bool
            If True (default), stash local changes before pull and pop after.
            If False and repo is dirty, pull proceeds as-is (may fail).

        Returns
        -------
        str
            JSON Result with {package: {status, output|commands, stashed}}.
        """
        from scitex_dev.dev_mcp.handlers import pull_local_handler

        return await pull_local_handler(packages, confirm, stash)

    @mcp.tool()
    async def dev_bulk_rename(
        pattern: str,
        replacement: str,
        directory: str = ".",
        confirm: bool = False,
        regex: bool = False,
        scope: str = "",
        recursive: bool = True,
        django_safe: bool = True,
        extra_excludes: list[str] | None = None,
        force: bool = False,
        skip_ids: list[str] | None = None,
        use_sudo: bool = False,
        sudo_password: str | None = None,
    ) -> str:
        """Bulk rename files, contents, directories, and symlinks.

        WORKFLOW (3-step):
        1. DRY RUN: Call with confirm=False (default). Review the output.
        2. REVIEW: Check each change. Every item has a unique ID.
           - Content changes: "c-{file_idx}-L{line}" (e.g., "c-003-L12")
           - Directory renames: "d-{idx}" (e.g., "d-001")
           - File renames: "f-{idx}"
           - Symlink updates: "st-{idx}", "sn-{idx}"
        3. EXECUTE: Call with confirm=True and skip_ids=[...] for false positives.

        Django-safe by default (protects db_table, related_name, migration files).

        Parameters
        ----------
        pattern : str
            Pattern to search for. Literal string by default, or regex if regex=True.
        replacement : str
            String to replace matches with. Supports regex backreferences
            (\\1, \\g<name>) when regex=True.
        directory : str
            Target directory (default: current directory).
        confirm : bool
            If False (default), preview only (dry run).
            If True, execute the rename operation.
        regex : bool
            If True, treat pattern as a regular expression (re.DOTALL).
            If False (default), treat as literal string.
        scope : str
            Glob pattern to restrict which files are matched (e.g., "README.md",
            "*.py", "*.md"). Empty string matches all files.
        recursive : bool
            If True (default), recurse into subdirectories.
            If False, only process files in the top-level directory.
        django_safe : bool
            Protect Django-specific patterns (db_table, related_name, etc).
        extra_excludes : list of str, optional
            Additional path patterns to exclude.
        force : bool
            Skip uncommitted changes check (default False).
        skip_ids : list of str, optional
            IDs of changes to skip (from dry-run output).
        use_sudo : bool
            Use sudo for file operations. Default False.
        sudo_password : str, optional
            Password for non-interactive sudo.

        Returns
        -------
        str
            JSON Result with rename results and summary.
        """
        from scitex_dev.dev_mcp.handlers import rename_handler

        return await rename_handler(
            pattern,
            replacement,
            directory,
            confirm,
            regex,
            django_safe,
            extra_excludes,
            force,
            skip_ids=skip_ids,
            use_sudo=use_sudo,
            sudo_password=sudo_password,
            scope=scope,
            recursive=recursive,
        )


# EOF
