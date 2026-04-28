#!/usr/bin/env python3
"""Scitex resource module.

Import discipline (todo #157):
    Importing this module must be side-effect-free — no servers, no threads,
    no dashboards. Sidecars / CLI tools shell out via
    ``python -c "from scitex.resource import get_specs; ..."`` every metrics
    tick, so import time matters and surprise listeners are unacceptable.

    To honour that, the eager imports below are limited to the lightweight
    spec/processor probes (``psutil``, ``scitex.str``).
    ``log_processor_usages`` / ``main`` pull in the heavy ``scitex.io``
    save/load chain, so they are exposed through PEP 562 module-level
    ``__getattr__`` and only imported on first access.
"""

from ._get_processor_usages import get_processor_usages
from ._get_specs import (
    _cpu_info,
    _disk_info,
    _memory_info,
    _network_info,
    _supple_nvidia_info,
    _supple_os_info,
    _supple_python_info,
    _system_info,
    get_specs,
)

__all__ = [
    "get_processor_usages",
    "get_specs",
    "log_processor_usages",
    "main",
    "_cpu_info",
    "_disk_info",
    "_memory_info",
    "_network_info",
    "_supple_nvidia_info",
    "_supple_os_info",
    "_supple_python_info",
    "_system_info",
]


# Lazy attributes — defer the scitex.io import chain (and any transitive
# dashboard / Flask machinery) until a caller actually wants the logger.
_LAZY_ATTRS = {
    "log_processor_usages": ("._log_processor_usages", "log_processor_usages"),
    "main": ("._log_processor_usages", "main"),
}


def __getattr__(name):
    if name in _LAZY_ATTRS:
        from importlib import import_module

        module_path, attr = _LAZY_ATTRS[name]
        module = import_module(module_path, package=__name__)
        value = getattr(module, attr)
        globals()[name] = value  # cache for subsequent lookups
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(set(globals()) | set(_LAZY_ATTRS) | set(__all__))
