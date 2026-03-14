#!/usr/bin/env python3
# Timestamp: "2026-01-13 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/ui/_backends/__init__.py

"""Notification backend registry and utilities."""

from __future__ import annotations

from ._audio import AudioBackend
from ._desktop import DesktopBackend
from ._emacs import EmacsBackend
from ._email import EmailBackend
from ._matplotlib import MatplotlibBackend
from ._playwright import PlaywrightBackend
from ._types import BaseNotifyBackend, NotifyLevel, NotifyResult
from ._webhook import WebhookBackend

__all__ = [
    "NotifyLevel",
    "NotifyResult",
    "BaseNotifyBackend",
    "AudioBackend",
    "EmailBackend",
    "DesktopBackend",
    "EmacsBackend",
    "WebhookBackend",
    "MatplotlibBackend",
    "PlaywrightBackend",
    "BACKENDS",
    "get_backend",
    "available_backends",
]

# Registry of available backends
BACKENDS: dict[str, type[BaseNotifyBackend]] = {
    "audio": AudioBackend,
    "email": EmailBackend,
    "desktop": DesktopBackend,
    "emacs": EmacsBackend,
    "webhook": WebhookBackend,
    "matplotlib": MatplotlibBackend,
    "playwright": PlaywrightBackend,
}


def get_backend(name: str, **kwargs) -> BaseNotifyBackend:
    """Get a notification backend by name."""
    if name not in BACKENDS:
        raise ValueError(f"Unknown backend: {name}. Available: {list(BACKENDS.keys())}")
    return BACKENDS[name](**kwargs)


def available_backends() -> list[str]:
    """Return list of available notification backends."""
    available = []
    for name, cls in BACKENDS.items():
        try:
            backend = cls()
            if backend.is_available():
                available.append(name)
        except Exception:
            pass
    return available


# EOF
