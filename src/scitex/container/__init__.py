#!/usr/bin/env python3
"""SciTeX container management -- delegates to scitex-container package."""

try:
    # Re-export subnamespaces so umbrella users can write
    # `stx.container.apptainer.build(...)` as well as the flattened
    # `stx.container.build(...)`.
    from scitex_container import apptainer, docker, env_snapshot, host
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
    "apptainer",
    "build",
    "cleanup",
    "deploy",
    "docker",
    "env_snapshot",
    "freeze",
    "get_active_version",
    "host",
    "list_versions",
    "rollback",
    "status",
    "switch_version",
]

# EOF
