#!/usr/bin/env python3
"""SciTeX container management (Apptainer/Singularity)."""

from ._build import build
from ._freeze import freeze
from ._status import status
from ._versioning import (
    cleanup,
    deploy,
    get_active_version,
    list_versions,
    rollback,
    switch_version,
)

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
