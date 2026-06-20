#!/usr/bin/env python3
"""scitex.gen — FAIL-LOUD deprecation shim (umbrella-only).

``scitex.gen`` was the mngs-era kitchen-sink namespace. Its utilities have all
moved into focused standalone packages (scitex-math, scitex-linalg,
scitex-datetime, scitex-io, scitex-context, scitex-os, scitex-sh, scitex-str,
scitex-introspect, scitex-stats). The umbrella no longer re-exports the
standalone ``scitex_gen``: every attribute access on ``scitex.gen`` now raises
a clear ``AttributeError`` naming the new home. Fail fast, fail loud, NO
fallback — so stale ``scitex.gen.<x>`` callsites surface immediately at the
exact line, instead of silently resolving to a soon-to-be-retired package.

This shim is intentionally umbrella-only. The standalone ``scitex_gen`` package
itself is untouched; only the ``scitex.gen`` umbrella surface fails loud.

Mechanism: this is a real on-disk module (not a ``_LazyModule`` proxy to
``scitex_gen``). Module-level ``__getattr__`` (PEP 562) looks the requested
name up in ``_DEPRECATIONS`` and raises an ``AttributeError`` pointing at the
umbrella target. Unmapped names get a generic fail-loud deprecation error.
"""

from __future__ import annotations

# Nothing is publicly exported — every name fails loud via __getattr__.
__all__: list = []


# symbol -> umbrella target module shown in the deprecation message.
# Keep this in sync with the migration audit; ONLY map names whose canonical
# home is known. Unmapped names fall through to the generic fail-loud error.
_DEPRECATIONS: dict = {
    # → scitex.math
    "to_even": "scitex.math",
    "to_odd": "scitex.math",
    # → scitex.linalg
    "to_z": "scitex.linalg",
    "to_nanz": "scitex.linalg",
    "to_01": "scitex.linalg",
    "to_nan01": "scitex.linalg",
    "unbias": "scitex.linalg",
    "clip_perc": "scitex.linalg",
    "to_rank": "scitex.linalg",
    "transpose": "scitex.linalg",
    "symlog": "scitex.linalg",
    "DimHandler": "scitex.linalg",
    # → scitex.datetime
    "TimeStamper": "scitex.datetime",
    # → scitex.io
    "xml2dict": "scitex.io",
    "XmlDictConfig": "scitex.io",
    "XmlListConfig": "scitex.io",
    "mat2npy": "scitex.io",
    "mat2dict": "scitex.io",
    "mat2npa": "scitex.io",
    "dir2npy": "scitex.io",
    "keys2npa": "scitex.io",
    "save_npa": "scitex.io",
    # → scitex.context
    "get_notebook_path": "scitex.context",
    "get_notebook_name": "scitex.context",
    "get_notebook_directory": "scitex.context",
    "get_output_directory": "scitex.context",
    "detect_environment": "scitex.context",
    "is_notebook": "scitex.context",
    # → scitex.path
    "symlink": "scitex.path",
    "src": "scitex.path",
    "title2path": "scitex.path",
    # → scitex.os
    "check_host": "scitex.os",
    "is_host": "scitex.os",
    "verify_host": "scitex.os",
    # → scitex.sh
    "run_shellcommand": "scitex.sh",
    "run_shellscript": "scitex.sh",
    # → scitex.str
    "title_case": "scitex.str",
    # → scitex.introspect
    "list_api": "scitex.introspect",
    "list_packages": "scitex.introspect",
    # → scitex.stats
    "ci": "scitex.stats",
}

# The focused packages that absorbed scitex.gen — named in the generic error so
# users know where to look even for an unmapped symbol.
_TARGET_PACKAGES = "math/linalg/datetime/io/context/os/sh/str/introspect/stats"


def __getattr__(name: str):
    """PEP 562 hook: every attribute access on scitex.gen fails loud.

    Mapped names point at the specific umbrella target; unmapped names get a
    generic deprecation error. No fallback, no proxy to scitex_gen.
    """
    target = _DEPRECATIONS.get(name)
    if target is not None:
        raise AttributeError(
            f"scitex.gen.{name} was deprecated and removed. "
            f"Use {target}.{name} instead — scitex.gen is being retired; "
            f"its utilities moved to focused packages."
        )
    raise AttributeError(
        f"scitex.gen.{name}: scitex.gen is deprecated and being retired; "
        f"its utilities moved to focused scitex packages "
        f"({_TARGET_PACKAGES}). Import from the specific package instead."
    )


def __dir__() -> list:
    """Surface the deprecated names for tab-completion/introspection so users
    discover them (and then hit the fail-loud error explaining the move).
    """
    return sorted(_DEPRECATIONS)


# EOF
