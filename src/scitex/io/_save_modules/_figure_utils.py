#!/usr/bin/env python3
# File: /home/ywatanabe/proj/scitex-python/src/scitex/io/_save_modules/_figure_utils.py

"""Utility functions for extracting figure data for CSV export."""


class _RecordingFigureDataProxy:
    """Proxy providing export_as_csv() from a figrecipe RecordingFigure."""

    def __init__(self, fig, spath=None):
        self._fig = fig
        self._spath = spath

    def export_as_csv(self):
        """Extract recorded plot data as a flat DataFrame.

        Handles two states:
        - Pre-savefig: args have '_array' with in-memory data
        - Post-savefig: args reference CSV files in <stem>_data/ directory
        """
        try:
            import pandas as pd

            rec = self._fig._recorder.figure_record
            columns = {}
            for ax_key, ax_rec in rec.axes.items():
                for call in ax_rec.calls:
                    for arg in call.args:
                        arr = (
                            arg.get("_array")
                            if isinstance(arg, dict)
                            else getattr(arg, "_array", None)
                        )
                        name = (
                            arg.get("name")
                            if isinstance(arg, dict)
                            else getattr(arg, "name", None)
                        ) or "val"
                        data_path = (
                            arg.get("data")
                            if isinstance(arg, dict)
                            else getattr(arg, "data", None)
                        )

                        col_name = f"{ax_key}_{call.id}_{name}"

                        if arr is not None:
                            # Pre-savefig: use in-memory array
                            columns[col_name] = (
                                arr.tolist() if hasattr(arr, "tolist") else list(arr)
                            )
                        elif (
                            isinstance(data_path, str)
                            and data_path.endswith(".csv")
                            and self._spath
                        ):
                            # Post-savefig: data was serialized to a CSV file
                            import os

                            stem = os.path.splitext(os.path.basename(self._spath))[0]
                            data_dir = os.path.join(
                                os.path.dirname(self._spath), f"{stem}_data"
                            )
                            full_path = os.path.join(
                                data_dir, os.path.basename(data_path)
                            )
                            if os.path.exists(full_path):
                                sub_df = pd.read_csv(full_path, header=None)
                                columns[col_name] = sub_df.iloc[:, 0].tolist()

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


def get_figure_with_data(obj, spath=None):
    """Return a proxy with export_as_csv() if the object has figrecipe recording data.

    Returns
    -------
    _RecordingFigureDataProxy or None
    """
    # figrecipe RecordingFigure directly
    if hasattr(obj, "_recorder") and hasattr(obj._recorder, "figure_record"):
        return _RecordingFigureDataProxy(obj, spath=spath)

    # figrecipe RecordingFigure via .fig attribute (e.g. bundle objects)
    if hasattr(obj, "fig") and hasattr(getattr(obj, "fig", None), "_recorder"):
        return _RecordingFigureDataProxy(obj.fig, spath=spath)

    return None


# EOF
