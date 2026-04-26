"""Compat shim: moved to scitex.helpers._env_loader."""

from .helpers._env_loader import *  # noqa: F401,F403
from .helpers._env_loader import (  # noqa: F401
    _ENV_PATTERN,
    _parse_value,
    load_env_from_path,
    load_scitex_env,
    parse_src_file,
)
