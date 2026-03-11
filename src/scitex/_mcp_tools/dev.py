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
            JSON with version information for each package.
        """
        from scitex._dev._mcp.handlers import list_versions_handler

        result = await list_versions_handler(packages)
        return _json(result)

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
        """Fetch full HPC test output.

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
            JSON with {package: {status, output|commands}}.
        """
        from scitex._dev._mcp.handlers import sync_local_handler

        result = await sync_local_handler(packages, confirm)
        return _json(result)

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
            JSON with {detected, local_fixes, remote_fixes, summary}.
        """
        from scitex._dev._mcp.handlers import fix_mismatches_handler

        result = await fix_mismatches_handler(hosts, packages, local, remote, confirm)
        return _json(result)

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
           Look for FALSE POSITIVES (changes that shouldn't happen) and
           FALSE NEGATIVES (protected lines that should actually change).
           Common false positives: legacy redirect URLs that should keep
           the old name, documentation describing the rename itself.
           Common false negatives: lines matching django_safe patterns
           (db_table=, related_name=) that are actually app config, not
           DB schema.
        3. EXECUTE: Call with confirm=True and skip_ids=[...] for any
           false positives. For false negatives, either set django_safe=False
           or fix manually after execution.

        SKIP_IDS: Use file-level IDs (e.g., "c-003") to skip ALL changes
        in a file, or line-level IDs (e.g., "c-003-L12") to skip a single
        line while still renaming other lines in the same file.

        Django-safe by default (protects db_table, related_name, migration
        files). Execution order: contents → symlink targets → symlink
        names → file names → directory names (deepest first).

        DJANGO APP RENAME WARNING: If renaming a Django app directory
        (e.g., old_app/ → new_app/), additional manual steps are required
        AFTER the bulk rename completes:
        1. Add explicit db_table to ALL models in the renamed app to
           preserve the old table names (e.g., db_table="old_app_mymodel").
        2. Update migration file internal references (dependencies and
           ForeignKey `to=` strings) from old_app to new_app.
        3. Run SQL to fix Django tracking tables BEFORE running migrate:
           UPDATE django_migrations SET app='new_app' WHERE app='old_app';
        4. Create a new migration that updates django_content_type rows.
        5. Fix any `related_name` values in models that reference the
           old app name — these are Python-only but affect reverse queries.
        Model class renames (e.g., UserModule → UserApp) require separate
        Django RenameModel migrations and are NOT handled by this tool.

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
        skip_ids : list of str, optional
            IDs of changes to skip (from dry-run output). Supports both
            file-level ("c-003") and line-level ("c-003-L12") granularity.
        use_sudo : bool
            Use sudo for file operations (for root-owned files). Default False.
        sudo_password : str, optional
            Password for non-interactive sudo. Required when use_sudo=True
            on systems without NOPASSWD configured.

        Returns
        -------
        str
            JSON with rename results and summary.
        """
        from scitex._dev._mcp.handlers import rename_handler

        result = await rename_handler(
            pattern,
            replacement,
            directory,
            confirm,
            django_safe,
            extra_excludes,
            force,
            skip_ids=skip_ids,
            use_sudo=use_sudo,
            sudo_password=sudo_password,
        )
        return _json(result)


# EOF
