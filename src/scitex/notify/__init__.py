#!/usr/bin/env python3
# Timestamp: "2026-01-13 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/ui/__init__.py

"""SciTeX UI Module - User alerts and feedback.

Usage:
    import scitex

    # Simple alert - uses fallback priority (audio → emacs → desktop → ...)
    scitex.notify.alert("2FA required!")

    # Specify backend (no fallback)
    scitex.notify.alert("Error", backend="email")

    # Multiple backends (tries all)
    scitex.notify.alert("Critical", backend=["audio", "email"])

    # Use fallback explicitly
    scitex.notify.alert("Important", fallback=True)

Environment Variables:
    SCITEX_UI_DEFAULT_BACKEND: audio, email, desktop, webhook
"""

from __future__ import annotations

import asyncio
import os
from typing import Optional, Union

from ._backends import NotifyLevel as _AlertLevel
from ._backends import available_backends as _available_backends
from ._backends import get_backend as _get_backend

__all__ = ["alert", "alert_async", "available_backends"]

# Default fallback priority order
DEFAULT_FALLBACK_ORDER = [
    "audio",  # 1st: TTS audio (non-blocking, immediate)
    "emacs",  # 2nd: Emacs minibuffer (if in Emacs)
    "matplotlib",  # 3rd: Visual popup
    "playwright",  # 4th: Browser popup
    "email",  # 5th: Email (slowest, most reliable)
]


def available_backends() -> list[str]:
    """Return list of available alert backends."""
    return _available_backends()


async def alert_async(
    message: str,
    title: Optional[str] = None,
    backend: Optional[Union[str, list[str]]] = None,
    level: str = "info",
    fallback: bool = True,
    **kwargs,
) -> bool:
    """Send alert asynchronously.

    Parameters
    ----------
    message : str
        Alert message
    title : str, optional
        Alert title
    backend : str or list[str], optional
        Backend(s) to use. If None, uses default with fallback.
    level : str
        Alert level: info, warning, error, critical
    fallback : bool
        If True and backend fails, try next in priority order.
        Default True when backend=None, False when backend specified.

    Returns
    -------
    bool
        True if any backend succeeded
    """
    try:
        lvl = _AlertLevel(level.lower())
    except ValueError:
        lvl = _AlertLevel.INFO

    # Determine backends to try
    if backend is None:
        # No backend specified: use fallback priority
        default = os.getenv("SCITEX_UI_DEFAULT_BACKEND", "audio")
        if fallback:
            # Start with default, then try others in priority order
            backends = [default] + [b for b in DEFAULT_FALLBACK_ORDER if b != default]
        else:
            backends = [default]
    else:
        # Backend specified: use it (with optional fallback)
        backends = [backend] if isinstance(backend, str) else list(backend)
        if fallback and len(backends) == 1:
            # Add fallback backends after the specified one
            backends = backends + [
                b for b in DEFAULT_FALLBACK_ORDER if b not in backends
            ]

    # Try backends until one succeeds
    available = _available_backends()
    for name in backends:
        if name not in available:
            continue
        try:
            b = _get_backend(name, **kwargs)
            result = await b.send(message, title=title, level=lvl, **kwargs)
            if result.success:
                return True
        except Exception:
            pass

    return False


def alert(
    message: str,
    title: Optional[str] = None,
    backend: Optional[Union[str, list[str]]] = None,
    level: str = "info",
    fallback: bool = True,
    **kwargs,
) -> bool:
    """Send alert synchronously.

    Parameters
    ----------
    message : str
        Alert message
    title : str, optional
        Alert title
    backend : str or list[str], optional
        Backend(s) to use. If None, uses fallback priority order.
    level : str
        Alert level: info, warning, error, critical
    fallback : bool
        If True and backend fails, try next in priority order.

    Returns
    -------
    bool
        True if any backend succeeded

    Fallback Order
    --------------
    1. audio      - TTS (fast, non-blocking)
    2. emacs      - Minibuffer message
    3. matplotlib - Visual popup
    4. playwright - Browser popup
    5. email      - Email (slowest)
    """
    try:
        asyncio.get_running_loop()
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                asyncio.run,
                alert_async(message, title, backend, level, fallback, **kwargs),
            )
            return future.result(timeout=30)
    except RuntimeError:
        return asyncio.run(
            alert_async(message, title, backend, level, fallback, **kwargs)
        )


# EOF
