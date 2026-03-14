#!/usr/bin/env python3
# Timestamp: "2026-02-01 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/session/_lifecycle/_config.py
"""Configuration setup for session lifecycle."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from scitex.logging import getLogger

logger = getLogger(__name__)


def setup_configs(
    IS_DEBUG: bool,
    ID: str,
    PID: int,
    file: str,
    sdir: str,
    relative_sdir: str,
    verbose: bool,
) -> Dict[str, Any]:
    """Setup configuration dictionary with basic parameters.

    Parameters
    ----------
    IS_DEBUG : bool
        Debug mode flag
    ID : str
        Unique identifier
    PID : int
        Process ID
    file : str
        File path
    sdir : str
        Save directory path
    relative_sdir : str
        Relative save directory path
    verbose : bool
        Verbosity flag

    Returns
    -------
    dict
        Configuration dictionary
    """
    # Calculate SDIR_OUT (base output directory)
    # sdir format: /path/to/script_out/RUNNING/ID/
    sdir_path = Path(sdir) if sdir else None
    if sdir_path:
        # Remove /RUNNING/ID/ to get base output dir
        parts = sdir_path.parts
        if "RUNNING" in parts:
            running_idx = parts.index("RUNNING")
            sdir_out = Path(*parts[:running_idx])
        else:
            sdir_out = sdir_path.parent
    else:
        sdir_out = None

    # Load YAML configs from ./config/*.yaml
    from scitex.io import load_configs

    CONFIGS = load_configs(IS_DEBUG).to_dict()

    # Add session-specific config with clean structure (Path objects only)
    CONFIGS.update(
        {
            "ID": ID,
            "PID": PID,
            "START_DATETIME": datetime.now(),
            "FILE": Path(file) if file else None,
            "SDIR_OUT": sdir_out,
            "SDIR_RUN": sdir_path,
        }
    )
    return CONFIGS


def save_configs(CONFIG) -> None:
    """Save configuration to files.

    Note: track=False prevents verification tracking of CONFIG files,
    which would cause false "missing" errors since these files are saved
    in RUNNING/ but then moved to FINISHED_SUCCESS/.
    """
    from scitex.io._save import save as scitex_io_save

    # Convert to dict with all keys (including private ones) for saving
    config_dict = (
        CONFIG.to_dict(include_private=True) if hasattr(CONFIG, "to_dict") else CONFIG
    )

    # track=False: Don't track internal config files in verification DB
    scitex_io_save(
        config_dict,
        str(CONFIG["SDIR_RUN"] / "CONFIGS/CONFIG.pkl"),
        verbose=False,
        track=False,
    )
    scitex_io_save(
        config_dict,
        str(CONFIG["SDIR_RUN"] / "CONFIGS/CONFIG.yaml"),
        verbose=False,
        track=False,
    )


# EOF
