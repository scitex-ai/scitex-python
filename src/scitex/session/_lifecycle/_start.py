#!/usr/bin/env python3
# Timestamp: "2026-02-01 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/session/_lifecycle/_start.py
"""Session start function."""

from __future__ import annotations

import inspect
import logging
import os as _os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

from scitex.dict import DotDict
from scitex.logging import getLogger
from scitex.repro import RandomStateManager
from scitex.str._clean_path import clean_path

from .._manager import get_global_session_manager
from ._config import setup_configs
from ._matplotlib import setup_matplotlib
from ._utils import (
    clear_python_log_dir,
    get_debug_mode,
    initialize_env,
    print_header,
    simplify_relative_path,
)

logger = getLogger(__name__)

# For development code flow analysis
try:
    from scitex.dev._analyze_code_flow import analyze_code_flow
except ImportError:

    def analyze_code_flow(file):
        return "Code flow analysis not available"


def start(
    sys=None,
    plt=None,
    file: Optional[str] = None,
    sdir: Optional[Union[str, Path]] = None,
    sdir_suffix: Optional[str] = None,
    args: Optional[Any] = None,
    os: Optional[Any] = None,
    random: Optional[Any] = None,
    np: Optional[Any] = None,
    torch: Optional[Any] = None,
    seed: int = 42,
    agg: bool = False,
    fig_size_mm: Tuple[int, int] = (160, 100),
    fig_scale: float = 1.0,
    dpi_display: int = 100,
    dpi_save: int = 300,
    fontsize="small",
    autolayout=True,
    show_execution_flow=False,
    hide_top_right_spines: bool = True,
    alpha: float = 0.9,
    line_width: float = 1.0,
    clear_logs: bool = False,
    verbose: bool = True,
) -> Tuple[DotDict, Any, Any, Any, Optional[Dict[str, Any]], Any]:
    """Initialize experiment session with reproducibility settings.

    Parameters
    ----------
    sys : module, optional
        Python sys module for I/O redirection
    plt : module, optional
        Matplotlib pyplot module for plotting configuration
    file : str, optional
        Script file path. If None, automatically detected
    sdir : Union[str, Path], optional
        Save directory path
    sdir_suffix : str, optional
        Suffix to append to save directory
    args : object, optional
        Command line arguments or configuration object
    seed : int, default=42
        Random seed for reproducibility
    agg : bool, default=False
        Whether to use matplotlib Agg backend
    verbose : bool, default=True
        Whether to print detailed information

    Returns
    -------
    tuple
        (CONFIGS, stdout, stderr, plt, COLORS, rng)
    """
    IS_DEBUG = get_debug_mode()
    ID, PID = initialize_env(IS_DEBUG)

    # Convert Path objects to strings for internal processing
    if sdir is not None and isinstance(sdir, Path):
        sdir = str(sdir)

    # Defines SDIR
    if sdir is None:
        # Define __file__
        if file:
            caller_file = file
        else:
            caller_file = inspect.stack()[1].filename
            if "ipython" in caller_file.lower():
                try:
                    from scitex.gen._detect_notebook_path import get_notebook_path

                    nb_path = get_notebook_path()
                    caller_file = (
                        nb_path if nb_path else f"/tmp/{_os.getenv('USER')}.py"
                    )
                except Exception:
                    caller_file = f"/tmp/{_os.getenv('USER')}.py"

        # Convert to absolute path if relative and resolve symlinks
        if not _os.path.isabs(caller_file):
            caller_file = _os.path.realpath(_os.path.abspath(caller_file))
        else:
            caller_file = _os.path.realpath(caller_file)

        # Define sdir
        sdir = clean_path(_os.path.splitext(caller_file)[0] + f"_out/RUNNING/{ID}/")

        # Optional
        if sdir_suffix:
            sdir = sdir[:-1] + f"-{sdir_suffix}/"
    else:
        caller_file = file

    if clear_logs and caller_file:
        clear_python_log_dir(sdir + caller_file + "/")
    _os.makedirs(sdir, exist_ok=True)
    relative_sdir = simplify_relative_path(sdir)

    # Setup configs - use caller_file (computed) instead of file (parameter)
    CONFIGS = setup_configs(
        IS_DEBUG, ID, PID, caller_file, sdir, relative_sdir, verbose
    )

    # Logging
    if sys is not None:
        from scitex_io._flush import flush

        from scitex.logging._Tee import tee

        flush(sys)
        sys.stdout, sys.stderr = tee(sys, sdir=sdir, verbose=verbose)
        CONFIGS["_sys"] = sys

        # Redirect logging handlers to use the tee-wrapped streams
        _redirect_logging_handlers(sys)

    # Initialize RandomStateManager
    rng = RandomStateManager(seed=seed, verbose=verbose)
    if verbose:
        logger.info(f"Initialized RandomStateManager with seed {seed}")

    # Matplotlib configurations
    plt, COLORS = setup_matplotlib(
        plt,
        agg,
        fig_size_mm=fig_size_mm,
        fig_scale=fig_scale,
        dpi_display=dpi_display,
        dpi_save=dpi_save,
        hide_top_right_spines=hide_top_right_spines,
        alpha=alpha,
        line_width=line_width,
        fontsize=fontsize,
        autolayout=autolayout,
        verbose=verbose,
    )

    # Adds argument-parsed variables
    if args is not None:
        CONFIGS["ARGS"] = vars(args) if hasattr(args, "__dict__") else args

    CONFIGS = DotDict(CONFIGS)

    # Register session
    session_manager = get_global_session_manager()
    session_manager.create_session(ID, CONFIGS)

    print_header(ID, PID, caller_file, args, CONFIGS, verbose)

    if show_execution_flow:
        from scitex.str._printc import printc as _printc

        structure = analyze_code_flow(caller_file)
        _printc(structure)

    # Start verification tracking
    _start_verification(CONFIGS)

    # Return appropriate values based on whether sys was provided
    if sys is not None:
        return CONFIGS, sys.stdout, sys.stderr, plt, COLORS, rng
    else:
        return CONFIGS, None, None, plt, COLORS, rng


def _redirect_logging_handlers(sys) -> None:
    """Redirect logging handlers to use tee-wrapped streams."""
    # Update all existing StreamHandler instances
    for logger_name in list(logging.Logger.manager.loggerDict.keys()):
        try:
            lgr = logging.getLogger(logger_name)
            for handler in lgr.handlers:
                if isinstance(handler, logging.StreamHandler):
                    if not hasattr(handler, "stream"):
                        continue
                    if handler.stream in (sys.__stderr__, sys.__stdout__):
                        handler.stream = (
                            sys.stderr
                            if handler.stream == sys.__stderr__
                            else sys.stdout
                        )
        except Exception:
            pass

    # Also update the root logger handlers
    try:
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                if not hasattr(handler, "stream"):
                    continue
                if handler.stream in (sys.__stderr__, sys.__stdout__):
                    handler.stream = (
                        sys.stderr if handler.stream == sys.__stderr__ else sys.stdout
                    )
    except Exception:
        pass


def _start_verification(CONFIG) -> None:
    """Start verification tracking for this session."""
    try:
        from scitex.clew import on_session_start

        session_id = CONFIG.get("ID", "unknown")
        file_path = CONFIG.get("FILE")
        if file_path is not None:
            file_path = str(file_path)

        metadata = None
        if file_path and file_path.endswith(".ipynb"):
            metadata = {"notebook_path": file_path}

        on_session_start(
            session_id=session_id, script_path=file_path, metadata=metadata
        )
    except Exception:
        pass


# EOF
