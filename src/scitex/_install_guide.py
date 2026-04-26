"""Compat shim: moved to scitex.helpers._install_guide."""

from .helpers import _install_guide as _moved  # noqa: F401
from .helpers._install_guide import *  # noqa: F401,F403

# Re-export every public attribute (including private-prefixed ones) so legacy
# `from scitex._install_guide import X` keeps working.
for _name in dir(_moved):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_moved, _name)
del _moved, _name
