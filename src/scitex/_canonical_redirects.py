#!/usr/bin/env python3
"""Canonical-attribute redirect helpers for ``scitex.re_export``.

When ``scitex.<mod>.<attr>`` lookup fails — either because ``<mod>`` is not
installed and the extras gate raises ``ImportError``, or because ``<mod>``
IS installed but does not actually carry ``<attr>`` — and the requested
attribute has a known canonical home in a different module that is already
in the umbrella's core deps, redirect the error to name that canonical
location. This converts a baffling "scitex.gen requires additional
dependencies. Install with: pip install scitex[gen]" or AttributeError
into "scitex.gen.load_configs is unavailable; the canonical location is
scitex.io.load_configs (already installed)." Saves the user from
pip-installing torch+CUDA into their venv just to call a function that
actually lives in scitex.io.

Seed populated from proj-paper-ripple-wm's PR#4a misdirected-callsite
audit (2026-06-07): the mngs.gen kitchen-sink namespace was split across
multiple scitex peers, leaving hundreds of callsites pointing at
scitex.gen.<X> for X that now lives in scitex.io / scitex.session /
scitex.dict / scitex.str / scitex.etc / scitex.context / scitex.types.
All canonical homes here are in the umbrella's core deps — no extras
install needed for the redirect target.
"""

from __future__ import annotations

import sys


# (short_name, attr_name) → canonical short_name where attr_name actually
# lives. All values are in the umbrella's core deps (no extras needed).
CANONICAL_REDIRECTS: dict[tuple[str, str], str] = {
    # gen → io
    ("gen", "load_configs"): "io",
    ("gen", "glob"): "io",
    ("gen", "reload"): "io",
    # gen → session
    ("gen", "start"): "session",
    ("gen", "close"): "session",
    # gen → dict
    ("gen", "replace"): "dict",
    ("gen", "listed_dict"): "dict",
    # gen → str
    ("gen", "search"): "str",
    # gen → etc
    ("gen", "yield_grids"): "etc",
    ("gen", "count_grids"): "etc",
    # gen → context
    ("gen", "suppress_output"): "context",
    # gen → types
    ("gen", "is_listed_X"): "types",
}


def venv_pip_hint(extras_name: str) -> str:
    """Return a venv-correct ``pip install`` hint for ``scitex[<extras_name>]``.

    Uses ``sys.executable -m pip`` so users with an active virtualenv don't
    accidentally invoke a system-level ``pip`` and install into the wrong
    Python. Quotes the extras spec so shells that interpret square brackets
    (zsh globbing) don't choke.
    """
    return f"{sys.executable} -m pip install 'scitex[{extras_name}]'"


def missing_extras_hint(short: str, attr: str) -> str:
    """Build the actionable ``ImportError`` message for a failed
    ``scitex.<short>.<attr>`` lookup when ``<short>`` is not importable.

    If the attribute has a known canonical home in another core module,
    name it — users learn the right location and that no extra install is
    needed. Otherwise fall back to the venv-correct ``pip install`` hint.
    """
    canonical = CANONICAL_REDIRECTS.get((short, attr))
    if canonical is not None:
        return (
            f"scitex.{short}.{attr} is not available here; the canonical "
            f"location is scitex.{canonical}.{attr} (already installed by "
            f"the umbrella core — no extra needed). Change your import to "
            f"`from scitex.{canonical} import {attr}`."
        )
    return (
        f"scitex.{short} requires additional dependencies. "
        f"Install with: {venv_pip_hint(short)}"
    )


def phantom_attr_hint(short: str, attr: str) -> str | None:
    """Build the actionable ``AttributeError`` message for the phantom case:
    ``scitex.<short>`` loaded fine but doesn't carry ``<attr>``.

    Returns ``None`` if there is no canonical redirect; the caller should
    let the original ``AttributeError`` propagate. Returns a string naming
    the canonical location when a redirect exists.
    """
    canonical = CANONICAL_REDIRECTS.get((short, attr))
    if canonical is None:
        return None
    return (
        f"module 'scitex.{short}' has no attribute {attr!r}; the "
        f"canonical location is scitex.{canonical}.{attr} (already "
        f"installed by the umbrella core — no extra needed). Change "
        f"your import to `from scitex.{canonical} import {attr}`."
    )
