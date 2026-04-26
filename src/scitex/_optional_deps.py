"""Compat shim: moved to scitex.helpers._optional_deps."""

from .helpers import _optional_deps as _moved  # noqa: F401
from .helpers._optional_deps import *  # noqa: F401,F403

for _name in dir(_moved):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_moved, _name)
del _moved, _name
