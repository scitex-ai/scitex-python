#!/usr/bin/env python3
# Timestamp: 2026-02-02
# File: scitex/_mcp_tools/dev.py

"""MCP tool registration for developer utilities."""

import json


def _json(obj) -> str:
    """Serialize object to JSON string."""
    return json.dumps(obj, indent=2, default=str)


def register_dev_tools(mcp) -> None:
    """Register developer tools with FastMCP server."""

    @mcp.tool()
    async def dev_versions_list(
        packages: list[str] | None = None,
    ) -> str:
        """[dev] List versions across the scitex ecosystem.

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
            JSON with version information for each package.
        """
        from scitex._dev._mcp.handlers import list_versions_handler

        result = await list_versions_handler(packages)
        return _json(result)

    @mcp.tool()
    async def dev_config_show() -> str:
        """[dev] Get current developer configuration.

        Returns the configuration from ~/.scitex/dev_config.yaml including:
        - Packages to track
        - SSH hosts
        - GitHub remotes
        - Branches to track

        Returns
        -------
        str
            JSON with current configuration.
        """
        from scitex._dev._mcp.handlers import get_config_handler

        result = await get_config_handler()
        return _json(result)

    @mcp.tool()
    async def dev_test_local(
        module: str = "",
        fast: bool = False,
        coverage: bool = False,
        exitfirst: bool = True,
        pattern: str = "",
        parallel: str = "auto",
    ) -> str:
        """[dev] Run project tests locally via pytest.

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
            JSON with {"exit_code": int}.
        """
        from scitex._dev._mcp.handlers import test_run_handler

        result = await test_run_handler(
            module, fast, coverage, exitfirst, pattern, parallel
        )
        return _json(result)

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
        """[dev] Run project tests on HPC (Spartan) via Slurm.

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
            JSON with {"exit_code": int} for srun,
            or {"job_id": str} for sbatch.
        """
        from scitex._dev._mcp.handlers import test_hpc_run_handler

        result = await test_hpc_run_handler(
            module, fast, hpc_cpus, hpc_partition, hpc_time, hpc_mem, async_mode
        )
        return _json(result)

    @mcp.tool()
    async def dev_test_hpc_poll(
        job_id: str | None = None,
    ) -> str:
        """[dev] Check HPC test job status.

        Queries sacct for the job state. If completed/failed, also fetches
        the last 20 lines of output.

        Parameters
        ----------
        job_id : str, optional
            Slurm job ID. If None, uses the last submitted job.

        Returns
        -------
        str
            JSON with {"state": str, "output": str|null, "job_id": str}.
            States: COMPLETED, RUNNING, PENDING, FAILED, TIMEOUT, CANCELLED.
        """
        from scitex._dev._mcp.handlers import test_hpc_poll_handler

        result = await test_hpc_poll_handler(job_id)
        return _json(result)

    @mcp.tool()
    async def dev_test_hpc_result(
        job_id: str | None = None,
    ) -> str:
        """[dev] Fetch full HPC test output.

        Downloads the complete stdout from a finished HPC test job via scp.

        Parameters
        ----------
        job_id : str, optional
            Slurm job ID. If None, uses the last submitted job.

        Returns
        -------
        str
            JSON with {"output": str|null, "job_id": str}.
        """
        from scitex._dev._mcp.handlers import test_hpc_result_handler

        result = await test_hpc_result_handler(job_id)
        return _json(result)

    @mcp.tool()
    async def dev_versions_sync(
        hosts: list[str] | None = None,
        packages: list[str] | None = None,
        install: bool = True,
        confirm: bool = False,
    ) -> str:
        """[dev] Sync ecosystem packages to remote hosts (git stash, pull, pip install).

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
            JSON with {host_name: {package: {status, commands|output, error}}}.
        """
        from scitex._dev._mcp.handlers import sync_handler

        result = await sync_handler(hosts, packages, install, confirm)
        return _json(result)

    @mcp.tool()
    async def dev_versions_sync_local(
        packages: list[str] | None = None,
        confirm: bool = False,
    ) -> str:
        """[dev] Install all local editable packages (pip install -e).

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
            JSON with {package: {status, output|commands}}.
        """
        from scitex._dev._mcp.handlers import sync_local_handler

        result = await sync_local_handler(packages, confirm)
        return _json(result)

    @mcp.tool()
    async def dev_versions_diff(
        host: str | None = None,
        packages: list[str] | None = None,
    ) -> str:
        """[dev] Show git diff on remote host(s). Read-only operation.

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
            JSON with {host: {package: {status, files, diff_stat, diff}}}.
        """
        from scitex._dev._mcp.handlers import remote_diff_handler

        result = await remote_diff_handler(host, packages)
        return _json(result)

    @mcp.tool()
    async def dev_versions_commit(
        host: str,
        packages: list[str] | None = None,
        message: str | None = None,
        push: bool = True,
        confirm: bool = False,
    ) -> str:
        """[dev] Commit dirty changes on a remote host and push to origin.

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
            JSON with {package: {status, commands|output}}.
        """
        from scitex._dev._mcp.handlers import remote_commit_handler

        result = await remote_commit_handler(host, packages, message, push, confirm)
        return _json(result)

    @mcp.tool()
    async def dev_versions_pull(
        packages: list[str] | None = None,
        confirm: bool = False,
        stash: bool = True,
    ) -> str:
        """[dev] Pull latest from origin to local repos.

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
            JSON with {package: {status, output|commands, stashed}}.
        """
        from scitex._dev._mcp.handlers import pull_local_handler

        result = await pull_local_handler(packages, confirm, stash)
        return _json(result)

    @mcp.tool()
    async def dev_bulk_rename(
        pattern: str,
        replacement: str,
        directory: str = ".",
        confirm: bool = False,
        django_safe: bool = True,
        extra_excludes: list[str] | None = None,
        force: bool = False,
    ) -> str:
        """[dev] Bulk rename files, contents, directories, and symlinks.

        Two-step safety: call first without confirm to preview changes,
        then with confirm=True to execute. Django-safe by default
        (protects db_table, related_name, migrations).

        Execution order:
        1. File contents (safe - doesn't change paths)
        2. Symlink targets (update to future paths)
        3. Symlink names (leaf nodes)
        4. File names (leaf nodes)
        5. Directory names (deepest first)

        Parameters
        ----------
        pattern : str
            Pattern to search for (literal string, not regex).
        replacement : str
            String to replace matches with.
        directory : str
            Target directory (default: current directory).
        confirm : bool
            If False (default), preview only (dry run).
            If True, execute the rename operation.
        django_safe : bool
            Protect Django-specific patterns (db_table, related_name, etc).
        extra_excludes : list of str, optional
            Additional path patterns to exclude.
        force : bool
            Skip uncommitted changes check (default False).

        Returns
        -------
        str
            JSON with rename results and summary.
        """
        from scitex._dev._mcp.handlers import rename_handler

        result = await rename_handler(
            pattern, replacement, directory, confirm, django_safe, extra_excludes, force
        )
        return _json(result)


# EOF
