#!/usr/bin/env python3
# Timestamp: 2026-01-24
# File: src/scitex/_env_loader.py

"""
Environment variable loader for SCITEX_ENV_SRC.

Parses and loads bash-compatible .src files containing environment variable definitions.
Supports both directory paths (all *.src files) and single file paths.
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)

# Pattern to match: export VAR=value or VAR=value (with optional quotes)
_ENV_PATTERN = re.compile(r"^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=(.*)$")


def _parse_value(value: str) -> str:
    """Parse a bash-style value, handling quotes and escapes."""
    value = value.strip()

    # Handle double-quoted strings
    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
        # Unescape common bash escapes
        value = value.replace('\\"', '"')
        value = value.replace("\\$", "$")
        value = value.replace("\\\\", "\\")
    # Handle single-quoted strings (no escaping in bash single quotes)
    elif value.startswith("'") and value.endswith("'"):
        value = value[1:-1]

    # Expand $VAR and ${VAR} references
    def expand_var(match):
        var_name = match.group(1) or match.group(2)
        return os.environ.get(var_name, "")

    value = re.sub(r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)", expand_var, value)

    return value


def parse_src_file(filepath: Path) -> Dict[str, str]:
    """
    Parse a bash-compatible .src file and extract environment variables.

    Parameters
    ----------
    filepath : Path
        Path to the .src file.

    Returns
    -------
    dict
        Dictionary of variable names to values.
    """
    env_vars = {}

    try:
        with open(filepath) as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                match = _ENV_PATTERN.match(line)
                if match:
                    name, value = match.groups()
                    env_vars[name] = _parse_value(value)

    except Exception as e:
        logger.warning(f"Failed to parse {filepath}: {e}")

    return env_vars


def load_env_from_path(path: str) -> Dict[str, str]:
    """
    Load environment variables from a file or directory.

    Parameters
    ----------
    path : str
        Path to a .src file or directory containing .src files.

    Returns
    -------
    dict
        All loaded environment variables.
    """
    loaded = {}
    path_obj = Path(path).expanduser()

    if not path_obj.exists():
        logger.warning(f"SCITEX_ENV_SRC path does not exist: {path}")
        return loaded

    files_to_load: List[Path] = []

    if path_obj.is_dir():
        # Load all .src files in directory
        files_to_load = sorted(path_obj.glob("*.src"))
    elif path_obj.is_file():
        files_to_load = [path_obj]
    else:
        logger.warning(f"SCITEX_ENV_SRC is not a file or directory: {path}")
        return loaded

    for src_file in files_to_load:
        env_vars = parse_src_file(src_file)
        if env_vars:
            logger.info(f"Loaded {len(env_vars)} vars from {src_file.name}")
            loaded.update(env_vars)

    return loaded


def load_scitex_env() -> int:
    """
    Load environment variables from SCITEX_ENV_SRC if set.

    This function should be called early in the MCP server startup.

    Returns
    -------
    int
        Number of environment variables loaded.
    """
    env_src = os.environ.get("SCITEX_ENV_SRC")

    if not env_src:
        return 0

    loaded = load_env_from_path(env_src)

    # Apply to current process environment
    for name, value in loaded.items():
        os.environ[name] = value

    if loaded:
        logger.info(f"SCITEX_ENV_SRC: Loaded {len(loaded)} environment variables")

    return len(loaded)


# EOF
