#!/usr/bin/env python3
# Timestamp: "2026-02-01 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/session/_lifecycle/_utils.py
"""Utility functions for session lifecycle."""

from __future__ import annotations

import os as _os
import re
from datetime import datetime
from time import sleep
from typing import Any, Dict, Tuple

from scitex.logging import getLogger
from scitex.repro import gen_ID
from scitex.str._printc import printc as _printc

logger = getLogger(__name__)


def get_scitex_version() -> str:
    """Gets scitex version."""
    try:
        import scitex

        return scitex.__version__
    except Exception as e:
        print(e)
        return "(not found)"


def get_debug_mode() -> bool:
    """Get debug mode from configuration."""
    try:
        from scitex.io._load import load

        IS_DEBUG_PATH = "./config/IS_DEBUG.yaml"
        if _os.path.exists(IS_DEBUG_PATH):
            IS_DEBUG = load(IS_DEBUG_PATH).get("IS_DEBUG", False)
            if IS_DEBUG == "true":
                IS_DEBUG = True
        else:
            IS_DEBUG = False

    except Exception as e:
        print(e)
        IS_DEBUG = False
    return IS_DEBUG


def initialize_env(IS_DEBUG: bool) -> Tuple[str, int]:
    """Initialize environment with ID and PID.

    Parameters
    ----------
    IS_DEBUG : bool
        Debug mode flag

    Returns
    -------
    tuple
        (ID, PID) - Unique identifier and Process ID
    """
    ID = gen_ID(N=4) if not IS_DEBUG else "DEBUG_" + gen_ID(N=4)
    PID = _os.getpid()
    return ID, PID


def simplify_relative_path(sdir: str) -> str:
    """Simplify the relative path by removing specific patterns.

    Parameters
    ----------
    sdir : str
        The directory path to simplify

    Returns
    -------
    str
        Simplified relative path
    """
    base_path = _os.getcwd()
    relative_sdir = _os.path.relpath(sdir, base_path) if base_path else sdir
    simplified_path = relative_sdir.replace("scripts/", "./scripts/").replace(
        "RUNNING/", ""
    )
    # Remove date-time pattern and random string
    simplified_path = re.sub(
        r"\d{4}Y-\d{2}M-\d{2}D-\d{2}h\d{2}m\d{2}s_\w+/?$", "", simplified_path
    )
    return simplified_path


def clear_python_log_dir(log_dir: str) -> None:
    """Clear Python log directory."""
    try:
        if _os.path.exists(log_dir):
            _os.system(f"rm -rf {log_dir}")
    except Exception as e:
        print(f"Failed to clear directory {log_dir}: {e}")


def print_header(
    ID: str,
    PID: int,
    file: str,
    args: Any,
    configs: Dict[str, Any],
    verbose: bool = True,
) -> None:
    """Prints formatted header with scitex version, ID, and PID information."""
    if args is not None and hasattr(args, "_get_kwargs"):
        args_str = "Arguments:"
        for arg, value in args._get_kwargs():
            args_str += f"\n    {arg}: {value}"
    else:
        args_str = "Arguments: None"

    _printc(
        (f"SciTeX v{get_scitex_version()} | {ID} (PID: {PID})\n\n{file}\n\n{args_str}"),
        char="=",
    )

    sleep(1)
    if verbose:
        from pprint import pformat

        config_str = pformat(configs.to_dict())
        logger.info(f"\n{'-' * 40}\n\n{config_str}\n\n{'-' * 40}\n")
    sleep(1)


def format_diff_time(diff_time) -> str:
    """Format time difference as HH:MM:SS."""
    total_seconds = int(diff_time.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def process_timestamp(CONFIG, verbose=True):
    """Process session timestamps."""
    try:
        CONFIG["END_DATETIME"] = datetime.now()
        CONFIG["RUN_DURATION"] = format_diff_time(
            CONFIG["END_DATETIME"] - CONFIG["START_DATETIME"]
        )
        if verbose:
            logger.info(
                f"\nSTART TIME: {CONFIG['START_DATETIME']}\n"
                f"END TIME: {CONFIG['END_DATETIME']}\n"
                f"RUN DURATION: {CONFIG['RUN_DURATION']}\n"
            )

    except Exception as e:
        print(e)

    return CONFIG


def args_to_str(args_dict) -> str:
    """Convert args dictionary to formatted string."""
    if args_dict:
        max_key_length = max(len(str(k)) for k in args_dict.keys())
        return "\n".join(
            f"{str(k):<{max_key_length}} : {str(v)}"
            for k, v in sorted(args_dict.items())
        )
    else:
        return ""


def escape_ansi_from_log_files(log_files) -> None:
    """Remove ANSI escape sequences from log files."""
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    for f in log_files:
        with open(f, encoding="utf-8") as file:
            content = file.read()
        cleaned_content = ansi_escape.sub("", content)
        with open(f, "w", encoding="utf-8") as file:
            file.write(cleaned_content)


# EOF
