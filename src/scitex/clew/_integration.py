#!/usr/bin/env python3
# Timestamp: "2026-02-01 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/verify/_integration.py
"""Integration hooks for session and io modules."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional, Union

from ._tracker import get_tracker, start_tracking, stop_tracking

logger = logging.getLogger(__name__)


def on_session_start(
    session_id: str,
    script_path: Optional[str] = None,
    parent_session: Optional[str] = None,
    verbose: bool = False,
    metadata: Optional[dict] = None,
) -> None:
    """
    Hook called when a session starts.

    Parameters
    ----------
    session_id : str
        Unique session identifier
    script_path : str, optional
        Path to the script being run
    parent_session : str, optional
        Parent session ID for chain tracking
    verbose : bool, optional
        Whether to log status messages
    metadata : dict, optional
        Additional metadata (e.g. notebook_path, cell_index)
    """
    try:
        start_tracking(
            session_id=session_id,
            script_path=script_path,
            parent_session=parent_session,
            metadata=metadata,
        )
    except Exception as e:
        if verbose:
            import logging

            logging.getLogger(__name__).warning(
                f"Could not start verification tracking: {e}"
            )


def on_session_close(
    status: str = "success",
    exit_code: int = 0,
    verbose: bool = False,
    register: Optional[bool] = None,
) -> None:
    """
    Hook called when a session closes.

    Parameters
    ----------
    status : str, optional
        Final status (success, failed, error)
    exit_code : int, optional
        Exit code of the script
    verbose : bool, optional
        Whether to log status messages
    register : bool, optional
        If True, register session hashes with remote Clew Registry.
        If None, checks SCITEX_AUTO_REGISTER environment variable.
    """
    try:
        tracker = get_tracker()
        stop_tracking(status=status, exit_code=exit_code)
        if _should_auto_register(register) and tracker is not None:
            _auto_register_session(tracker.session_id)
    except Exception as e:
        if verbose:
            import logging

            logging.getLogger(__name__).warning(
                f"Could not stop verification tracking: {e}"
            )


def on_io_load(
    path: Union[str, Path],
    track: bool = True,
) -> None:
    """
    Hook called when a file is loaded via stx.io.load().

    Parameters
    ----------
    path : str or Path
        Path to the loaded file
    track : bool, optional
        Whether to track this file as an input
    """
    if not track:
        return

    tracker = get_tracker()
    if tracker is not None:
        try:
            tracker.record_input(path, track=track)
        except Exception as e:
            logger.debug("clew: failed to record input %s: %s", path, e)


def on_io_save(
    path: Union[str, Path],
    track: bool = True,
) -> None:
    """
    Hook called when a file is saved via stx.io.save().

    Parameters
    ----------
    path : str or Path
        Path to the saved file
    track : bool, optional
        Whether to track this file as an output
    """
    if not track:
        return

    tracker = get_tracker()
    if tracker is not None:
        try:
            tracker.record_output(path, track=track)
        except Exception as e:
            logger.debug("clew: failed to record output %s: %s", path, e)


# ── Registry helpers ──


def _should_auto_register(register: Optional[bool]) -> bool:
    """Check whether auto-registration is enabled."""
    if register is not None:
        return register
    import os

    return os.environ.get("SCITEX_AUTO_REGISTER", "").lower() in ("1", "true", "yes")


def _auto_register_session(session_id: str) -> None:
    """Register session hashes with remote Clew Registry (fire-and-forget)."""
    try:
        from ._registry import get_registry

        get_registry().register_session(session_id)
    except Exception as e:
        logger.debug("clew: failed to auto-register session %s: %s", session_id, e)


# EOF
