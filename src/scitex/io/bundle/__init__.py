#!/usr/bin/env python3
"""``scitex.io.bundle`` — thin re-export of ``scitex_io.bundle``.

The bundle dispatcher, plumbing, dataclasses, and kind handlers live in
the ``scitex_io.bundle`` standalone package. This module preserves the
``scitex.io.bundle.{Bundle, load, save, …}`` import path for downstream
code so the standalone migration is invisible at the call site.

The public surface is delegated to ``scitex_io.bundle.__all__`` so it
stays in sync automatically — no hand-maintained name list to drift.
"""

import scitex_io.bundle as _bundle
from scitex_io.bundle import *  # noqa: F401,F403

__all__ = list(_bundle.__all__)
