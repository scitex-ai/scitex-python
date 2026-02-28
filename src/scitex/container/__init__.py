#!/usr/bin/env python3
"""SciTeX container management -- delegates to scitex-container package."""

try:
    from scitex_container import env_snapshot
    from scitex_container.apptainer import (
        build,
        build_dev_pythonpath,
        build_exec_args,
        build_host_mount_binds,
        build_srun_command,
        cleanup,
        deploy,
        detect_container_cmd,
        find_containers_dir,
        freeze,
        get_active_version,
        is_sandbox,
        list_versions,
        rollback,
        sandbox_create,
        sandbox_maintain,
        sandbox_to_sif,
        status,
        switch_version,
        verify,
    )

    _BACKEND = "scitex-container"
except ImportError:
    from ._build import build
    from ._freeze import freeze
    from ._status import status
    from ._utils import detect_container_cmd, find_containers_dir
    from ._versioning import (
        cleanup,
        deploy,
        get_active_version,
        list_versions,
        rollback,
        switch_version,
    )

    _BACKEND = "local"

__all__ = [
    "build",
    "cleanup",
    "deploy",
    "freeze",
    "get_active_version",
    "list_versions",
    "rollback",
    "status",
    "switch_version",
]

# EOF
