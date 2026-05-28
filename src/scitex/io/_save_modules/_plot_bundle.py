#!/usr/bin/env python3
"""Retired ``.plot`` directory-bundle save path.

figrecipe owns figure I/O via ``.plt.zip`` (Pltz) and ``.fig.zip`` (Figz).
The umbrella's old ``.plot/`` directory bundle was a duplicate that has
now been removed. Callers should save through ``.plt.zip`` (routed via
``scitex_io``'s optional figrecipe provider) instead.

This stub stays only to surface a clear error for any code still passing
``.plot`` to ``scitex.io.save``; the underlying implementation
(``scitex.plt.io.save_layered_plot_bundle`` and the entire
``src/scitex/plt/io/`` subpackage, plus ``src/scitex/schema/``) was
deleted as part of the same migration.
"""

from __future__ import annotations

import warnings


def save_plot_bundle(
    obj, spath, as_zip: bool = False, data=None, layered: bool = True, **kwargs
):
    """No-op stub for the retired ``.plot`` directory-bundle save path.

    Raises
    ------
    NotImplementedError
        Always. The underlying implementation has been deleted. Use
        ``scitex.io.save(fig, "<name>.plt.zip")`` instead (figrecipe-routed
        via the scitex_io optional provider).
    """
    warnings.warn(
        "scitex.io.save(fig, '*.plot' | '*.plot.zip') is deprecated and has "
        "been retired. figrecipe owns figure I/O now — save a "
        "figrecipe-recorded figure (figrecipe.subplots / scitex.plt.subplots) "
        "to '*.plt.zip' or '*.fig.zip' instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    raise NotImplementedError(
        "The .plot directory-bundle save path has been retired; "
        f"got spath={spath!r}. Save to '*.plt.zip' instead — "
        "scitex.io.save will route through figrecipe."
    )


# EOF
