#!/usr/bin/env python3
# Timestamp: "2026-02-01 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/session/_lifecycle/_close.py
"""Session close functions."""

from __future__ import annotations

import os
import os as _os
import shutil
import time
from glob import glob as _glob
from pathlib import Path

from scitex.logging import getLogger
from scitex.utils._notify import notify as scitex_utils_notify

from .._manager import get_global_session_manager
from ._config import save_configs
from ._utils import args_to_str, escape_ansi_from_log_files, process_timestamp

logger = getLogger(__name__)


def running2finished(CONFIG, exit_status=None, remove_src_dir=True, max_wait=60):
    """Move session from RUNNING to FINISHED directory.

    Parameters
    ----------
    CONFIG : dict
        Session configuration dictionary
    exit_status : int, optional
        Exit status code (0=success, 1=error, None=finished)
    remove_src_dir : bool, default=True
        Whether to remove source directory after copy
    max_wait : int, default=60
        Maximum seconds to wait for copy operation

    Returns
    -------
    dict
        Updated configuration with new SDIR
    """
    if exit_status == 0:
        dest_dir = str(CONFIG["SDIR_RUN"]).replace("RUNNING/", "FINISHED_SUCCESS/")
    elif exit_status == 1:
        dest_dir = str(CONFIG["SDIR_RUN"]).replace("RUNNING/", "FINISHED_ERROR/")
    else:
        dest_dir = str(CONFIG["SDIR_RUN"]).replace("RUNNING/", "FINISHED/")

    src_dir = str(CONFIG["SDIR_RUN"])
    _os.makedirs(dest_dir, exist_ok=True)
    try:
        # Copy files individually
        for item in _os.listdir(src_dir):
            s = _os.path.join(src_dir, item)
            d = _os.path.join(dest_dir, item)
            if _os.path.isdir(s):
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)

        start_time = time.time()
        while not _os.path.exists(dest_dir) and time.time() - start_time < max_wait:
            time.sleep(0.1)
        if _os.path.exists(dest_dir):
            print()
            if exit_status == 1:
                logger.error(
                    f"Script failed: {dest_dir}",
                )
            elif exit_status == 0:
                logger.success(
                    f"Congratulations! The script completed: {dest_dir}",
                )
            else:
                logger.info(
                    f"Script finished: {dest_dir}",
                )

            if remove_src_dir:
                shutil.rmtree(src_dir)

            # Cleanup RUNNING when empty
            running_base = os.path.dirname(src_dir.rstrip("/"))
            if os.path.basename(running_base) == "RUNNING":
                try:
                    os.rmdir(running_base)
                except OSError:
                    pass

        else:
            print(f"Copy operation timed out after {max_wait} seconds")

        CONFIG["SDIR_RUN"] = Path(dest_dir)
    except Exception as e:
        print(e)

    finally:
        return CONFIG


def close(CONFIG, message=":)", notify=False, verbose=True, exit_status=None):
    """Close experiment session and finalize logging.

    Parameters
    ----------
    CONFIG : DotDict
        Configuration dictionary from start()
    message : str, default=':)'
        Completion message
    notify : bool, default=False
        Whether to send notification
    verbose : bool, default=True
        Whether to print verbose output
    exit_status : int, optional
        Exit status code (0=success, 1=error, None=finished)
    """
    # Stop verification tracking first
    _stop_verification(exit_status)

    sys = None
    try:
        CONFIG.EXIT_STATUS = exit_status
        CONFIG = CONFIG.to_dict()
        CONFIG = process_timestamp(CONFIG, verbose=verbose)
        sys = CONFIG.pop("_sys", None)

        # CRITICAL: Close matplotlib BEFORE closing streams to prevent segfault
        _cleanup_matplotlib(verbose)

        save_configs(CONFIG)

        # RUNNING to FINISHED
        CONFIG = running2finished(CONFIG, exit_status=exit_status)

        # ANSI code escape
        log_files = _glob(str(CONFIG["SDIR_RUN"]) + "logs/*.log")
        escape_ansi_from_log_files(log_files)

        if CONFIG.get("ARGS"):
            message += f"\n{args_to_str(CONFIG.get('ARGS'))}"

        if notify:
            try:
                message = (
                    "[DEBUG]\n" + str(message)
                    if CONFIG.get("DEBUG", False)
                    else str(message)
                )
                scitex_utils_notify(
                    message=message,
                    ID=CONFIG["ID"],
                    file=CONFIG.get("FILE"),
                    attachment_paths=log_files,
                    verbose=verbose,
                )
            except Exception as e:
                print(e)

        # Close session
        session_manager = get_global_session_manager()
        session_manager.close_session(CONFIG["ID"])

    finally:
        # Only close if they're custom file objects (Tee objects)
        if sys:
            _close_streams(sys)


def _cleanup_matplotlib(verbose: bool) -> None:
    """Clean up matplotlib resources."""
    try:
        import gc

        import matplotlib
        import matplotlib.pyplot as plt

        # Close all figures
        plt.close("all")

        # CRITICAL: Unregister matplotlib's atexit handlers to prevent segfault
        try:
            if hasattr(matplotlib, "_pylab_helpers"):
                matplotlib._pylab_helpers.Gcf.destroy_all()

            if hasattr(plt, "get_fignums"):
                for fignum in plt.get_fignums():
                    plt.close(fignum)

        except Exception:
            pass

        # Force garbage collection
        gc.collect()

        if verbose:
            logger.info("Matplotlib cleanup completed")

    except Exception as e:
        if verbose:
            logger.warning(f"Could not close matplotlib: {e}")


def _close_streams(sys) -> None:
    """Close tee-wrapped streams."""
    try:
        # First, flush all outputs
        if hasattr(sys, "stdout") and hasattr(sys.stdout, "flush"):
            sys.stdout.flush()
        if hasattr(sys, "stderr") and hasattr(sys.stderr, "flush"):
            sys.stderr.flush()

        # Then close Tee objects
        if hasattr(sys, "stdout") and hasattr(sys.stdout, "_log_file"):
            sys.stdout.close()
        if hasattr(sys, "stderr") and hasattr(sys.stderr, "_log_file"):
            sys.stderr.close()
    except Exception:
        pass


def _stop_verification(exit_status: int) -> None:
    """Stop verification tracking for this session."""
    try:
        from scitex.clew import on_session_close

        status = "success" if exit_status == 0 else "failed"
        on_session_close(status=status, exit_code=exit_status or 0)
    except Exception:
        pass


# EOF
