#!/usr/bin/env python3
"""Scitex gen module.

NOTE: This module is being refactored. Many functions are being moved to
more appropriate locations. For backward compatibility, they are re-exported
here with deprecation warnings.

Recommended imports:
- ci -> scitex.stats.descriptive.ci
- check_host, is_host, verify_host -> scitex.os
- detect_environment, is_notebook, is_script -> scitex.context
- list_api -> scitex.introspect
- run_shellcommand, run_shellscript -> scitex.sh
- xml2dict, XmlDictConfig, XmlListConfig -> scitex.io
- title_case -> scitex.str
- symlink -> scitex.path
"""

import warnings


def _deprecation_warning(old_path, new_path):
    warnings.warn(
        f"{old_path} is deprecated, use {new_path} instead",
        DeprecationWarning,
        stacklevel=3,
    )


# ci -> scitex_stats.descriptive.ci (with re-export for backward compat)
from scitex_stats.descriptive import ci

# Optional: DimHandler requires torch
try:
    from ._DimHandler import DimHandler
except ImportError:
    DimHandler = None
# check_host moved to scitex.os (re-export for backward compatibility)
from scitex.os import check_host, is_host, verify_host

from ._alternate_kwarg import alternate_kwarg
from ._cache import cache
from ._deprecated_close import close as _deprecated_close
from ._deprecated_close import running2finished as _deprecated_running2finished

# _start.py moved to old/ directory - functionality now in scitex.session
# BACKWARD COMPATIBILITY: Import deprecated wrappers
from ._deprecated_start import start as _deprecated_start

# _close.py moved to old/ directory - functionality now in scitex.session
# Optional: _embed requires torch
try:
    from ._embed import embed
except ImportError:
    embed = None
# list_api moved to scitex.introspect (re-export for backward compatibility)
from scitex.introspect import list_api

from ._is_ipython import is_ipython, is_script
from ._less import less
from ._list_packages import list_packages, main
from ._mat2py import (
    dir2npy,
    keys2npa,
    mat2dict,
    mat2npa,
    mat2npy,
    public_keys,
    save_npa,
)

# Optional: _norm requires torch
try:
    from ._norm import clip_perc, to_01, to_nan01, to_nanz, to_z, unbias
except ImportError:
    clip_perc = None
    to_01 = None
    to_nan01 = None
    to_nanz = None
    to_z = None
    unbias = None
# shell functions moved to scitex.sh (re-export for backward compatibility)
from scitex.sh import run_shellcommand, run_shellscript

from ._paste import paste
from ._print_config import print_config, print_config_main
from ._src import src
from ._TimeStamper import TimeStamper

# Override the imported functions with deprecated wrappers
start = _deprecated_start
close = _deprecated_close
running2finished = _deprecated_running2finished

# environment detection moved to scitex.context (re-export for backward compatibility)
from scitex.context import (
    detect_environment,
    get_notebook_directory,
    get_notebook_info_simple,
    get_notebook_name,
    get_notebook_path,
    get_output_directory,
    is_notebook,
)

# title_case moved to scitex.str (re-export for backward compatibility)
from scitex.str import title_case

from ._symlink import symlink
from ._symlog import symlog
from ._title2path import title2path
from ._to_even import to_even
from ._to_odd import to_odd

# Optional: _to_rank requires torch
try:
    from ._to_rank import to_rank
except ImportError:
    to_rank = None
from ._transpose import transpose

# Optional: _type and _var_info require torch
try:
    from ._type import ArrayLike, var_info
except ImportError:
    ArrayLike = None
    var_info = None

try:
    from ._var_info import ArrayLike, var_info
except ImportError:
    pass  # Already set to None above
from ._wrap import wrap
from ._xml2dict import XmlDictConfig, XmlListConfig, xml2dict

# Import from misc module
from .misc import connect_nums, float_linspace

__all__ = [
    "ArrayLike",
    "ArrayLike",
    "DimHandler",
    "Tee",
    "TimeStamper",
    "XmlDictConfig",
    "XmlListConfig",
    "alternate_kwarg",
    "cache",
    "check_host",
    "ci",
    "clip_perc",
    "close",
    "connect_nums",
    "dir2npy",
    "embed",
    "float_linspace",
    "list_api",
    "is_host",
    "is_ipython",
    "is_script",
    "keys2npa",
    "less",
    "list_packages",
    "mat2dict",
    "mat2npa",
    "mat2npy",
    "paste",
    "print_config",
    "print_config_main",
    "public_keys",
    "run_shellcommand",
    "run_shellscript",
    "running2finished",
    "save_npa",
    "src",
    "start",
    "symlink",
    "symlog",
    "tee",
    "title2path",
    "title_case",
    "to_01",
    "to_even",
    "to_nan01",
    "to_nanz",
    "to_odd",
    "to_rank",
    "to_z",
    "transpose",
    "unbias",
    "var_info",
    "var_info",
    "verify_host",
    "wrap",
    "xml2dict",
    "detect_environment",
    "get_output_directory",
    "is_notebook",
    "get_notebook_path",
    "get_notebook_name",
    "get_notebook_directory",
]
