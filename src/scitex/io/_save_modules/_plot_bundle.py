#!/usr/bin/env python3
# Timestamp: 2026-05-28
# File: src/scitex/io/_save_modules/_plot_bundle.py

"""Save matplotlib/figrecipe figures as `.plt.zip` bundles via figrecipe."""

from pathlib import Path

from scitex import logging

logger = logging.getLogger()


def save_plot_bundle(obj, spath, as_zip=False, data=None, layered=True, **kwargs):
    """Save a figure as a figrecipe `.plt.zip` bundle.

    figrecipe owns figure I/O. The umbrella's `.plot` directory format is
    retired; this function now delegates to ``figrecipe.save_bundle``.

    Parameters
    ----------
    obj : RecordingFigure
        The figrecipe RecordingFigure to save. Plain matplotlib figures
        are no longer accepted on this code path; route them through
        ``scitex.io.save(fig, path)``, which dispatches via
        ``scitex.io.bundle.from_matplotlib``.
    spath : str or Path
        Output path (the `.plt.zip` suffix is enforced).
    as_zip : bool
        Ignored — figrecipe always writes a ZIP.
    data : pandas.DataFrame, optional
        Ignored on this path (data is extracted from the recording).
    layered : bool
        Ignored — figrecipe is always layered.
    **kwargs
        Forwarded to ``figrecipe.save_bundle`` (e.g. ``dpi``,
        ``image_formats``, ``save_hitmap``, ``verbose``).
    """
    from figrecipe import save_bundle as _fr_save_bundle

    path = Path(spath)

    # Enforce the .plt.zip extension figrecipe expects.
    name = path.name
    if not name.endswith(".plt.zip"):
        if name.endswith(".plot.zip"):
            name = name[: -len(".plot.zip")] + ".plt.zip"
        elif name.endswith(".plot"):
            name = name[: -len(".plot")] + ".plt.zip"
        elif name.endswith(".zip"):
            name = name[: -len(".zip")] + ".plt.zip"
        else:
            name = name + ".plt.zip"
        path = path.with_name(name)

    # Extract underlying figure from wrappers if needed.
    fig = obj
    if hasattr(obj, "figure") and not hasattr(obj, "record"):
        fig = obj.figure
    elif hasattr(obj, "fig") and not hasattr(obj, "record"):
        fig = obj.fig

    return _fr_save_bundle(fig, path, **kwargs)


# EOF
