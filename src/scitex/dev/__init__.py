#!/usr/bin/env python3
"""SciTeX Dev — development, debugging, and ecosystem management utilities.

Delegates to the standalone ``scitex-dev`` package for ecosystem-wide
tools (versions, docs, search, rename, HPC testing, LLM-friendly types).
Local utilities (reload, code-flow analysis, install guide) are kept here.
"""

# =============================================================================
# Core re-export from standalone scitex-dev
# =============================================================================

from scitex_dev import *  # noqa: F401,F403

# Explicit re-exports for IDE support
from scitex_dev import (  # noqa: F401
    # Ecosystem
    ECOSYSTEM,
    # LLM-friendly types
    RESULT_SCHEMA,
    # Config
    DevConfig,
    ErrorCode,
    GitHubRemote,
    HostConfig,
    PackageConfig,
    PyPIAccount,
    RenameConfig,
    RenameResult,
    Result,
    SideEffect,
    TestConfig,
    # CLI option factories
    add_dry_run_argument,
    add_json_argument,
    async_wrap_as_mcp,
    build_docs,
    # Rename
    bulk_rename,
    # SSH
    check_all_hosts,
    # GitHub
    check_all_remotes,
    # RTD
    check_all_rtd,
    check_rtd_status,
    check_versions,
    classify_exception,
    compare_with_local,
    config_to_dict,
    create_default_config,
    dry_run_option,
    execute_rename,
    fetch_hpc_result,
    fix_mismatches,
    get_all_packages,
    get_config_path,
    # Docs aggregation
    get_docs,
    get_enabled_hosts,
    get_enabled_remotes,
    get_github_latest_tag,
    get_github_release,
    get_github_tags,
    get_local_path,
    get_mismatches,
    get_remote_version,
    get_remote_versions,
    handle_result,
    json_option,
    # Versions
    list_versions,
    load_config,
    poll_hpc_job,
    preview_rename,
    pull_local,
    remote_commit,
    # Sync (remote -> local)
    remote_diff,
    result_to_mcp,
    # MCP / CLI wrappers
    run_as_cli,
    run_as_mcp,
    run_hpc_sbatch,
    run_hpc_srun,
    # Test runner
    run_local,
    # Unified search
    search,
    search_docs,
    supports_return_as,
    # Sync (local -> remote)
    sync_all,
    sync_host,
    sync_local,
    sync_tags,
    sync_to_hpc,
    test_host_connection,
    watch_hpc_job,
    wrap_as_cli,
    wrap_as_mcp,
)

# Installation guide utilities (moved from root scitex module)
from .._install_guide import (
    MODULE_REQUIREMENTS,
    check_module_deps,
    require_module,
    requires,
    show_install_guide,
    warn_module_deps,
)

# =============================================================================
# Local utilities (scitex-specific, not in scitex-dev)
# =============================================================================
# Pyproject utilities (lazy import to avoid tomlkit dependency)
from . import _pyproject as pyproject
from . import cv
from ._analyze_code_flow import CodeFlowAnalyzer, analyze_code_flow, main, parse_args
from ._reload import reload, reload_auto, reload_stop


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


__all__ = [
    # --- From scitex-dev ---
    # LLM-friendly types
    "Result",
    "RESULT_SCHEMA",
    "ErrorCode",
    "SideEffect",
    "classify_exception",
    "supports_return_as",
    "handle_result",
    "run_as_cli",
    "wrap_as_cli",
    "run_as_mcp",
    "wrap_as_mcp",
    "async_wrap_as_mcp",
    "result_to_mcp",
    "json_option",
    "dry_run_option",
    "add_json_argument",
    "add_dry_run_argument",
    # Docs
    "get_docs",
    "build_docs",
    "search_docs",
    # Search
    "search",
    # Versions
    "list_versions",
    "check_versions",
    "get_mismatches",
    "fix_mismatches",
    # Ecosystem
    "ECOSYSTEM",
    "get_all_packages",
    "get_local_path",
    # Config
    "DevConfig",
    "HostConfig",
    "GitHubRemote",
    "PackageConfig",
    "PyPIAccount",
    "load_config",
    "get_config_path",
    "create_default_config",
    "get_enabled_hosts",
    "get_enabled_remotes",
    "config_to_dict",
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
    # RTD
    "check_all_rtd",
    "check_rtd_status",
    # Rename
    "bulk_rename",
    "preview_rename",
    "execute_rename",
    "RenameConfig",
    "RenameResult",
    # Sync
    "sync_all",
    "sync_host",
    "sync_local",
    "sync_tags",
    "remote_diff",
    "remote_commit",
    "pull_local",
    # Test runner
    "run_local",
    "run_hpc_srun",
    "run_hpc_sbatch",
    "poll_hpc_job",
    "fetch_hpc_result",
    "watch_hpc_job",
    "sync_to_hpc",
    "TestConfig",
    # Dashboard
    "run_dashboard",
    # --- Local utilities ---
    "CodeFlowAnalyzer",
    "analyze_code_flow",
    "main",
    "parse_args",
    "reload",
    "reload_auto",
    "reload_stop",
    "pyproject",
    "cv",
    "show_install_guide",
    "check_module_deps",
    "require_module",
    "requires",
    "warn_module_deps",
    "MODULE_REQUIREMENTS",
]
