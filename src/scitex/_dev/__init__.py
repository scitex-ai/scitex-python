#!/usr/bin/env python3
# Timestamp: 2026-03-13
# File: scitex/_dev/__init__.py

"""SciTeX Developer Utilities — thin re-export from scitex_dev.

All functionality has been migrated to the standalone ``scitex-dev`` package.
This module re-exports everything for backward compatibility.
"""

from scitex_dev import (
    ECOSYSTEM,
    DevConfig,
    GitHubRemote,
    HostConfig,
    PackageConfig,
    PyPIAccount,
    RenameConfig,
    RenameResult,
    TestConfig,
    bulk_rename,
    check_all_hosts,
    check_all_remotes,
    check_versions,
    compare_with_local,
    config_to_dict,
    create_default_config,
    execute_rename,
    fetch_hpc_result,
    fix_mismatches,
    get_all_packages,
    get_config_path,
    get_enabled_hosts,
    get_enabled_remotes,
    get_github_latest_tag,
    get_github_release,
    get_github_tags,
    get_local_path,
    get_mismatches,
    get_remote_version,
    get_remote_versions,
    list_versions,
    load_config,
    poll_hpc_job,
    preview_rename,
    pull_local,
    remote_commit,
    remote_diff,
    run_hpc_sbatch,
    run_hpc_srun,
    run_local,
    sync_all,
    sync_host,
    sync_local,
    sync_tags,
    sync_to_hpc,
    test_host_connection,
    watch_hpc_job,
)

__all__ = [
    # Versions
    "list_versions",
    "check_versions",
    "get_mismatches",
    # Fix
    "fix_mismatches",
    # Ecosystem
    "ECOSYSTEM",
    "get_all_packages",
    "get_local_path",
    # Config
    "load_config",
    "get_config_path",
    "create_default_config",
    "get_enabled_hosts",
    "get_enabled_remotes",
    "config_to_dict",
    "DevConfig",
    "HostConfig",
    "GitHubRemote",
    "PackageConfig",
    "PyPIAccount",
    # SSH
    "check_all_hosts",
    "get_remote_version",
    "get_remote_versions",
    "test_host_connection",
    # GitHub
    "check_all_remotes",
    "compare_with_local",
    "get_github_tags",
    "get_github_latest_tag",
    "get_github_release",
    # Rename
    "bulk_rename",
    "preview_rename",
    "execute_rename",
    "RenameConfig",
    "RenameResult",
    # Sync (local → remote)
    "sync_all",
    "sync_host",
    "sync_local",
    "sync_tags",
    # Sync (remote → local)
    "remote_diff",
    "remote_commit",
    "pull_local",
    # Test
    "run_local",
    "run_hpc_srun",
    "run_hpc_sbatch",
    "poll_hpc_job",
    "fetch_hpc_result",
    "watch_hpc_job",
    "sync_to_hpc",
    "TestConfig",
]


def run_dashboard(
    host: str = "127.0.0.1",
    port: int = 5000,
    debug: bool = False,
    open_browser: bool = True,
    force: bool = False,
) -> None:
    """Run the Flask version dashboard."""
    from scitex_dev.dashboard import run_dashboard as _run

    _run(host=host, port=port, debug=debug, open_browser=open_browser, force=force)


# EOF
