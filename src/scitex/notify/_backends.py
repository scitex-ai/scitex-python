#!/usr/bin/env python3
# Timestamp: "2026-01-13 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/ui/_backends.py

"""Re-export from _backends package for backward compatibility."""

from ._backends import (
    BACKENDS,
    AudioBackend,
    BaseNotifyBackend,
    DesktopBackend,
    EmailBackend,
    MatplotlibBackend,
    NotifyLevel,
    NotifyResult,
    PlaywrightBackend,
    WebhookBackend,
    available_backends,
    get_backend,
)

__all__ = [
    "NotifyLevel",
    "NotifyResult",
    "BaseNotifyBackend",
    "AudioBackend",
    "EmailBackend",
    "DesktopBackend",
    "WebhookBackend",
    "MatplotlibBackend",
    "PlaywrightBackend",
    "BACKENDS",
    "get_backend",
    "available_backends",
]

# EOF
