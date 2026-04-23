#!/usr/bin/env python3
# Timestamp: 2026-03-13
# File: scitex/_mcp_tools/dev.py

"""MCP tool registration for developer utilities.

All handlers return structured Result JSON via scitex_dev.mcp_utils.
"""


def register_dev_tools(mcp) -> None:
    """Register developer tools with FastMCP server."""

    @mcp.tool()
    async def dev_ecosystem_list(
        packages: list[str] | None = None,
    ) -> str:
        """Show the version of every SciTeX package across five sources — `pyproject.toml`, installed (`importlib.metadata`), latest git tag, current git branch, and live PyPI — and flag mismatches. Drop-in replacement for `pip show` + `git describe` + `curl pypi.org/pypi/...` loops. Use when the user asks "what versions do I have?", "are any packages out of sync?", "what's on PyPI vs local?", or before a release to audit drift.

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
        """Dump the active `~/.scitex/dev_config.yaml` — tracked packages, SSH hosts, GitHub remotes, tracked branches. Drop-in replacement for `cat ~/.scitex/dev_config.yaml` + hand-parsing. Use when the user asks "show my dev config", "which hosts are set up?", "what packages am I tracking?", or is debugging why a `dev_ecosystem_*` call picked (or skipped) a particular host / package.

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
        """Run the SciTeX project's pytest suite with parallel execution, auto-detecting project root from git — one-shot replacement for `cd $(git rev-parse --show-toplevel) && pytest -n auto`. Drop-in for `pytest` + manual `-n auto`, `--cov`, `-x`, `-k`, `-m` flag wrangling. Use when the user asks to "run the tests", "check if everything passes", "run scitex.stats tests", or after a code change and wants quick feedback.

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
        """Ship the project to an HPC cluster via `rsync` and run pytest under SLURM — blocking via `srun` or fire-and-forget via `sbatch` (poll later with `dev_test_hpc_poll`). Drop-in replacement for `rsync -avz . hpc:$PWD && ssh hpc 'srun --cpus=8 --mem=16G pytest'`. Use when the user asks to "run tests on HPC", "submit this to Spartan / the cluster", "test under SLURM", "async-run the heavy GPU tests", or needs bigger resources than a laptop.

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
        """Poll a SLURM job's state via `sacct` — COMPLETED / RUNNING / PENDING / FAILED / TIMEOUT / CANCELLED — plus the tail of its stdout if finished. Drop-in replacement for `ssh hpc 'sacct -j $jobid --format=State'` + `tail` on the log. Use when the user asks "is my HPC test done?", "check job X", "what happened to that async submission?", after `dev_test_hpc` with `async_mode=True`.

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
        """Pull the complete stdout of a finished SLURM job back to local via `scp` — the full log, not just the tail from `dev_test_hpc_poll`. Use when the user asks "show me the full HPC output", "get the complete log for job X", "download the crashed job's stderr", after a `dev_test_hpc_poll` reports COMPLETED / FAILED.

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
    async def dev_ecosystem_sync(
        hosts: list[str] | None = None,
        packages: list[str] | None = None,
        install: bool = True,
        confirm: bool = False,
    ) -> str:
        """Push ecosystem packages to remote SSH hosts in parallel — `git stash` + `git pull` + `pip install -e .` per (host, package) — so every workstation / cluster runs identical code. Drop-in replacement for hand-looping `ssh $host 'cd $pkg && git pull && pip install -e .'`. Use when the user asks to "sync all hosts", "update NAS/HPC to latest", "push my changes to the cluster", "deploy the ecosystem". Two-phase safety: `confirm=False` previews, `confirm=True` executes.

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
    async def dev_ecosystem_sync_local(
        packages: list[str] | None = None,
        confirm: bool = False,
    ) -> str:
        """`pip install -e .` across every configured local SciTeX package in one shot — keeps the dev install in sync after pulls / version bumps without hand-iterating repos. Drop-in replacement for `for d in ~/proj/scitex-*; do cd $d && pip install -e .; done`. Use when the user asks to "reinstall editable", "refresh dev installs", "sync local pip installs", after big cross-repo pulls, or when imports look stale. `confirm=False` previews first.

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
    async def dev_ecosystem_fix_mismatches(
        hosts: list[str] | None = None,
        packages: list[str] | None = None,
        local: bool = True,
        remote: bool = True,
        confirm: bool = False,
    ) -> str:
        """One-shot healer — scans `dev_ecosystem_list`, identifies every package whose toml / installed / git / PyPI versions disagree, and fixes them: local `pip install -e .` where installed ≠ toml, remote `git pull + pip install` on SSH hosts. Drop-in replacement for manually reading a version dashboard then running per-row fixes. Use when the user asks to "fix version drift", "get everything back in sync", "resolve the mismatches", after a chaotic multi-repo session. `confirm=False` previews.

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
    async def dev_ecosystem_diff(
        host: str | None = None,
        packages: list[str] | None = None,
    ) -> str:
        """Read-only `git status` + `git diff` on a remote SSH host — see uncommitted work a teammate / previous session left on NAS / HPC before deciding to commit, stash, or overwrite. Drop-in replacement for `ssh $host 'cd $pkg && git status && git diff'`. Use when the user asks "what's dirty on NAS?", "show remote diff", "did I leave changes on HPC?", before `dev_ecosystem_commit` or a destructive `dev_ecosystem_sync`.

        Shows uncommitted changes (git status + git diff) on remote hosts.
        Use this to review changes before committing with dev_ecosystem_commit.

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
    async def dev_ecosystem_commit(
        host: str,
        packages: list[str] | None = None,
        message: str | None = None,
        push: bool = True,
        confirm: bool = False,
    ) -> str:
        """Commit uncommitted changes on a remote SSH host and push to origin — auto-generates the message if omitted. Drop-in replacement for `ssh $host 'cd $pkg && git add -A && git commit -m "..." && git push'`. Use when the user asks to "commit NAS changes", "push remote edits from HPC", "save whatever's dirty on host X and push it". Typical flow: `dev_ecosystem_diff` → review → `dev_ecosystem_commit(confirm=True)` → `dev_ecosystem_pull` locally.

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
    async def dev_ecosystem_pull(
        packages: list[str] | None = None,
        confirm: bool = False,
        stash: bool = True,
    ) -> str:
        """`git pull` across every configured local SciTeX repo in parallel, with automatic `git stash pop` to preserve dirty work. Drop-in replacement for `for d in ~/proj/scitex-*; do cd $d && git pull; done`. Use when the user asks to "pull latest", "sync all repos locally", "refresh from origin", after `dev_ecosystem_commit` pushed remote-host changes. `stash=True` protects uncommitted work.

        Safety: call first without confirm to preview, then with confirm=True
        to execute. Use after dev_ecosystem_commit to sync remote changes locally.

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
        """Rename a pattern everywhere — inside every file's contents, every filename, every directory name, every symlink target — in one atomic 3-step dry-run → review-skip_ids → execute flow. Django-aware by default (protects `db_table`, `related_name`, migration files). Drop-in replacement for `sed -i + find -rename + git mv + manual symlink edits` and tools like `rope`, `bowler` for the non-Python parts. Use when the user asks to "rename X to Y across the repo", "change this variable name everywhere", "rename this module and every import of it", or "bulk replace matching pattern". Pass `regex=True` for regex with backrefs; `skip_ids` drops false positives from the dry-run report.

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
