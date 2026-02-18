#!/usr/bin/env python3
# File: /home/ywatanabe/proj/scitex-python/src/scitex/io/_save_modules/_figure_utils.py

"""Utility functions for extracting figure data for CSV export."""


class _RecordingFigureDataProxy:
    """Proxy providing export_as_csv() from a figrecipe RecordingFigure."""

    def __init__(self, fig):
        self._fig = fig

    def export_as_csv(self):
        """Extract recorded plot data as a flat DataFrame."""
        try:
            import pandas as pd

            rec = self._fig._recorder.figure_record
            columns = {}
            for ax_key, ax_rec in rec.axes.items():
                for call in ax_rec.calls:
                    for arg in call.args:
                        # args are dicts: {'name': ..., '_array': ..., ...}
                        if isinstance(arg, dict):
                            arr = arg.get("_array")
                            name = arg.get("name", "val")
                        else:
                            arr = getattr(arg, "_array", None)
                            name = getattr(arg, "name", "val")
                        if arr is not None:
                            col_name = f"{ax_key}_{call.id}_{name}"
                            data = arr.tolist() if hasattr(arr, "tolist") else list(arr)
                            columns[col_name] = data

            if not columns:
                return None

            max_len = max(len(v) for v in columns.values())
            padded = {
                k: list(v) + [float("nan")] * (max_len - len(v))
                for k, v in columns.items()
            }
            return pd.DataFrame(padded)
        except Exception:
            return None


def get_figure_with_data(obj):
    """Return a proxy with export_as_csv() if the object has figrecipe recording data.

    Returns
    -------
    _RecordingFigureDataProxy or None
    """
    # figrecipe RecordingFigure directly
    if hasattr(obj, "_recorder") and hasattr(obj._recorder, "figure_record"):
        return _RecordingFigureDataProxy(obj)

    # figrecipe RecordingFigure via .fig attribute (e.g. bundle objects)
    if hasattr(obj, "fig") and hasattr(getattr(obj, "fig", None), "_recorder"):
        return _RecordingFigureDataProxy(obj.fig)

    return None


# EOF
