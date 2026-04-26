#!/usr/bin/env python3
# File: ./tests/scitex/bridge/test__helpers.py
# Time-stamp: "2024-12-09 11:00:00 (ywatanabe)"
"""Tests for scitex.bridge._helpers module."""

import pytest


class TestAddStatsFromResults:
    """Tests for add_stats_from_results helper."""

    @pytest.fixture
    def stat_results(self):
        """Create test StatResults."""
        from scitex.schema import create_stat_result

        return [
            create_stat_result("pearson", "r", 0.85, 0.001),
            create_stat_result("t-test", "t", 2.5, 0.02),
        ]

    def test_auto_detect_matplotlib_axes(self, stat_results):
        """Test auto-detection works with matplotlib axes."""
        import matplotlib.pyplot as plt

        from scitex.bridge import add_stats_from_results

        fig, ax = plt.subplots()

        # Should auto-detect plt backend
        result = add_stats_from_results(ax, stat_results)

        # Should return the axes (for chaining)
        assert result is ax

        # Should have added text annotations
        assert len(ax.texts) == 2

        plt.close(fig)

    def test_auto_detect_figure_model(self, stat_results):
        """Test auto-detection works with FigureModel."""
        from scitex.bridge import add_stats_from_results
        from scitex.io.bundle.kinds._plot._models import FigureModel

        model = FigureModel(
            width_mm=170,
            height_mm=120,
            axes=[{"row": 0, "col": 0, "plots": []}],
        )

        # Should auto-detect vis backend
        result = add_stats_from_results(model, stat_results)

        # Should return the model (for chaining)
        assert result is model

        # Should have added annotations
        assert len(model.axes[0].get("annotations", [])) == 2

    def test_explicit_plt_backend(self, stat_results):
        """Test explicit plt backend."""
        import matplotlib.pyplot as plt

        from scitex.bridge import add_stats_from_results

        fig, ax = plt.subplots()

        add_stats_from_results(ax, stat_results, backend="plt")
        assert len(ax.texts) == 2

        plt.close(fig)

    def test_explicit_vis_backend(self, stat_results):
        """Test explicit vis backend."""
        from scitex.bridge import add_stats_from_results
        from scitex.io.bundle.kinds._plot._models import FigureModel

        model = FigureModel(
            width_mm=170,
            height_mm=120,
            axes=[{"row": 0, "col": 0, "plots": []}],
        )

        add_stats_from_results(model, stat_results, backend="vis")
        assert len(model.axes[0].get("annotations", [])) == 2

    def test_single_stat_result(self):
        """Test with single StatResult (not list)."""
        import matplotlib.pyplot as plt

        from scitex.bridge import add_stats_from_results
        from scitex.schema import create_stat_result

        fig, ax = plt.subplots()
        stat = create_stat_result("pearson", "r", 0.85, 0.001)

        # Should accept single StatResult
        add_stats_from_results(ax, stat)
        assert len(ax.texts) == 1

        plt.close(fig)

    def test_format_style_applied(self):
        """Test format_style is passed through."""
        import matplotlib.pyplot as plt

        from scitex.bridge import add_stats_from_results
        from scitex.schema import create_stat_result

        fig, ax = plt.subplots()
        stat = create_stat_result("pearson", "r", 0.85, 0.001)

        add_stats_from_results(ax, stat, format_style="compact")

        # Text should be in compact format
        text_content = ax.texts[0].get_text()
        assert "r = 0.850" in text_content

        plt.close(fig)

    def test_chaining_support(self, stat_results):
        """Test method chaining works."""
        import matplotlib.pyplot as plt

        from scitex.bridge import add_stats_from_results, extract_stats_from_axes

        fig, ax = plt.subplots()

        # Should support chaining
        extracted = extract_stats_from_axes(add_stats_from_results(ax, stat_results))

        assert len(extracted) == 2

        plt.close(fig)

    def test_invalid_backend_raises(self, stat_results):
        """Test invalid backend raises ValueError."""
        import matplotlib.pyplot as plt

        from scitex.bridge import add_stats_from_results

        fig, ax = plt.subplots()

        with pytest.raises(ValueError, match="Unknown backend"):
            add_stats_from_results(ax, stat_results, backend="invalid")

        plt.close(fig)


# EOF

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/bridge/_helpers.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # File: ./src/scitex/bridge/_helpers.py
# # Time-stamp: "2024-12-09 11:00:00 (ywatanabe)"
# """
# High-level helper functions for cross-module operations.
#
# These helpers provide a unified API for common workflows that span
# multiple modules, abstracting away backend-specific details.
# """
#
# from typing import Union, List, Optional, Literal
#
# # StatResult is now a dict - the GUI-specific StatResult is deprecated
# StatResult = dict
#
#
# def add_stats_from_results(
#     target,
#     stat_results: Union[StatResult, List[StatResult]],
#     backend: Literal["auto", "plt", "vis"] = "auto",
#     format_style: str = "asterisk",
#     **kwargs,
# ):
#     """
#     Add statistical results to a figure or axes, auto-detecting backend.
#
#     This is a high-level helper that works with both matplotlib axes
#     and vis FigureModel, choosing the appropriate bridge function.
#
#     Parameters
#     ----------
#     target : matplotlib.axes.Axes, scitex.plt.AxisWrapper, or FigureModel
#         The target to add statistics to
#     stat_results : StatResult or List[StatResult]
#         Statistical result(s) to add
#     backend : {"auto", "plt", "vis"}
#         Backend to use. "auto" detects from target type:
#         - matplotlib axes or scitex AxisWrapper → "plt"
#         - FigureModel → "vis"
#     format_style : str
#         Format style for stat text ("asterisk", "compact", "detailed", "publication")
#     **kwargs
#         Additional arguments passed to the backend-specific function:
#         - plt: passed to add_stat_to_axes (x, y, transform, etc.)
#         - vis: passed to add_stats_to_figure_model (axes_index, auto_position, etc.)
#
#     Returns
#     -------
#     target
#         The modified target (for chaining)
#
#     Examples
#     --------
#     >>> # With matplotlib axes
#     >>> fig, ax = plt.subplots()
#     >>> stat = create_stat_result("pearson", "r", 0.85, 0.001)
#     >>> add_stats_from_results(ax, stat)
#
#     >>> # With vis FigureModel
#     >>> model = FigureModel(width_mm=170, height_mm=120, axes=[{}])
#     >>> add_stats_from_results(model, [stat1, stat2], backend="vis")
#
#     Notes
#     -----
#     Coordinate conventions differ between backends:
#     - plt: uses axes coordinates (0-1 normalized) by default
#     - vis: uses data coordinates
#
#     For precise control, use the backend-specific functions directly:
#     - scitex.bridge.add_stat_to_axes (plt backend)
#     - scitex.bridge.add_stats_to_figure_model (vis backend)
#     """
#     # Normalize to list
#     if isinstance(stat_results, StatResult):
#         stat_results = [stat_results]
#
#     # Auto-detect backend
#     if backend == "auto":
#         backend = _detect_backend(target)
#
#     # Dispatch to appropriate function
#     if backend == "plt":
#         from scitex.bridge._stats_plt import add_stat_to_axes
#
#         for stat in stat_results:
#             add_stat_to_axes(target, stat, format_style=format_style, **kwargs)
#
#     elif backend == "vis":
#         from scitex.bridge._stats_vis import add_stats_to_figure_model
#
#         add_stats_to_figure_model(
#             target,
#             stat_results,
#             format_style=format_style,
#             **kwargs,
#         )
#
#     else:
#         raise ValueError(f"Unknown backend: {backend}. Use 'auto', 'plt', or 'vis'.")
#
#     return target
#
#
# def _detect_backend(target) -> Literal["plt", "vis"]:
#     """
#     Detect the appropriate backend from target type.
#
#     Parameters
#     ----------
#     target : any
#         The target object
#
#     Returns
#     -------
#     str
#         "plt" or "vis"
#     """
#     # Check for vis FigureModel
#     try:
#         from scitex.io.bundle.kinds._plot._models import FigureModel
#         if isinstance(target, FigureModel):
#             return "vis"
#     except ImportError:
#         pass
#
#     # Check for matplotlib axes
#     try:
#         import matplotlib.axes
#         if isinstance(target, matplotlib.axes.Axes):
#             return "plt"
#     except ImportError:
#         pass
#
#     # Check for scitex plt wrappers
#     if hasattr(target, "_axes_mpl"):
#         return "plt"
#     if hasattr(target, "_axes_scitex"):
#         return "plt"
#
#     # Default to plt (most common case)
#     return "plt"
#
#
# __all__ = [
#     "add_stats_from_results",
# ]
#
#
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/bridge/_helpers.py
# --------------------------------------------------------------------------------
