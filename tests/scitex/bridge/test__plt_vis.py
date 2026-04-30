#!/usr/bin/env python3
# File: ./tests/scitex/bridge/test__plt_vis.py
# Time-stamp: "2024-12-09 10:30:00 (ywatanabe)"
"""Tests for scitex.bridge._plt_vis module."""

import pytest


class TestFigureToVisModel:
    """Tests for figure_to_vis_model function."""

    @pytest.fixture
    def mpl_figure(self):
        """Create a matplotlib figure."""
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [4, 5, 6], label="test")
        ax.set_xlabel("X Label")
        ax.set_ylabel("Y Label")
        ax.set_title("Test Title")
        yield fig
        plt.close(fig)

    def test_converts_to_figure_model(self, mpl_figure):
        """Test conversion to FigureModel."""
        from scitex.bridge import figure_to_vis_model
        from scitex.io.bundle.kinds._plot._models import FigureModel

        model = figure_to_vis_model(mpl_figure)

        assert isinstance(model, FigureModel)
        assert model.width_mm > 0
        assert model.height_mm > 0

    def test_captures_dimensions(self, mpl_figure):
        """Test that dimensions are captured correctly."""
        from scitex.bridge import figure_to_vis_model

        model = figure_to_vis_model(mpl_figure)

        # Default matplotlib figure is 6.4 x 4.8 inches
        expected_width_mm = 6.4 * 25.4  # ~162.56 mm
        expected_height_mm = 4.8 * 25.4  # ~121.92 mm

        assert abs(model.width_mm - expected_width_mm) < 1
        assert abs(model.height_mm - expected_height_mm) < 1

    def test_captures_axes_properties(self, mpl_figure):
        """Test that axes properties are captured."""
        from scitex.bridge import figure_to_vis_model

        model = figure_to_vis_model(mpl_figure)

        assert len(model.axes) == 1
        axes_dict = model.axes[0]
        assert axes_dict.get("xlabel") == "X Label"
        assert axes_dict.get("ylabel") == "Y Label"
        assert axes_dict.get("title") == "Test Title"


class TestAxesToVisAxes:
    """Tests for axes_to_vis_axes function."""

    @pytest.fixture
    def mpl_axes(self):
        """Create matplotlib axes."""
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 100)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        yield ax
        plt.close(fig)

    def test_creates_axes_model(self, mpl_axes):
        """Test creation of AxesModel."""
        from scitex.bridge import axes_to_vis_axes
        from scitex.io.bundle.kinds._plot._models import AxesModel

        model = axes_to_vis_axes(mpl_axes)

        assert isinstance(model, AxesModel)
        assert model.xlabel == "X"
        assert model.ylabel == "Y"

    def test_captures_limits(self, mpl_axes):
        """Test that axis limits are captured."""
        from scitex.bridge import axes_to_vis_axes

        model = axes_to_vis_axes(mpl_axes)

        assert model.xlim == [0, 10]
        assert model.ylim == [0, 100]


class TestTrackingToPlotConfigs:
    """Tests for tracking_to_plot_configs function."""

    def test_converts_plot_history(self):
        """Test conversion of plot tracking history."""
        import numpy as np

        from scitex.bridge import tracking_to_plot_configs

        history = {
            "plot_0": (
                "plot_0",
                "plot",
                {"args": (np.array([1, 2, 3]), np.array([4, 5, 6]))},
                {"color": "blue", "label": "test"},
            ),
        }

        plots = tracking_to_plot_configs(history)

        assert len(plots) == 1
        assert plots[0].plot_type == "line"
        assert plots[0].plot_id == "plot_0"

    def test_handles_scatter(self):
        """Test conversion of scatter plot history."""
        import numpy as np

        from scitex.bridge import tracking_to_plot_configs

        history = {
            "scatter_0": (
                "scatter_0",
                "scatter",
                {"args": (np.array([1, 2, 3]), np.array([4, 5, 6]))},
                {"marker": "o"},
            ),
        }

        plots = tracking_to_plot_configs(history)

        assert len(plots) == 1
        assert plots[0].plot_type == "scatter"


class TestCollectFigureData:
    """Tests for collect_figure_data function."""

    @pytest.fixture
    def mpl_figure(self):
        """Create a matplotlib figure."""
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [4, 5, 6])
        yield fig
        plt.close(fig)

    def test_returns_dict(self, mpl_figure):
        """Test that function returns dict."""
        from scitex.bridge import collect_figure_data

        data = collect_figure_data(mpl_figure)

        assert isinstance(data, dict)
        assert "figure" in data
        assert "axes" in data

    def test_captures_figure_info(self, mpl_figure):
        """Test that figure info is captured."""
        from scitex.bridge import collect_figure_data

        data = collect_figure_data(mpl_figure)

        assert "width_mm" in data["figure"]
        assert "height_mm" in data["figure"]
        assert data["figure"]["width_mm"] > 0


# EOF

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/bridge/_plt_vis.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # File: ./src/scitex/bridge/_plt_vis.py
# # Time-stamp: "2024-12-09 10:00:00 (ywatanabe)"
# """
# Bridge module for plt ↔ vis integration.
#
# Provides adapters to:
# - Convert scitex.plt figures to vis FigureModel
# - Extract tracking data as PlotModel configurations
# - Synchronize matplotlib state with vis JSON
# """
#
# from typing import Optional, Dict, Any, List, Tuple, Union
# import warnings
#
# # Legacy model imports - may not be available (deleted module)
# try:
#     from scitex.io.bundle.kinds._plot._models import (
#         FigureModel,
#         AxesModel,
#         PlotModel,
#         AnnotationModel,
#         GuideModel,
#         PlotStyle,
#         AxesStyle,
#         TextStyle,
#     )
#     VIS_MODEL_AVAILABLE = True
# except ImportError:
#     FigureModel = None
#     AxesModel = None
#     PlotModel = None
#     AnnotationModel = None
#     GuideModel = None
#     PlotStyle = None
#     AxesStyle = None
#     TextStyle = None
#     VIS_MODEL_AVAILABLE = False
#
#
# def figure_to_vis_model(
#     fig,
#     include_data: bool = True,
#     include_style: bool = True,
# ) -> FigureModel:
#     """
#     Convert a scitex.plt figure to a vis FigureModel.
#
#     Parameters
#     ----------
#     fig : scitex.plt.FigWrapper or matplotlib.figure.Figure
#         The figure to convert
#     include_data : bool
#         Whether to include plot data in the model
#     include_style : bool
#         Whether to include style information
#
#     Returns
#     -------
#     FigureModel
#         The vis figure model
#     """
#     # Get matplotlib figure
#     mpl_fig = _get_mpl_figure(fig)
#
#     # Get figure dimensions
#     width_inch = mpl_fig.get_figwidth()
#     height_inch = mpl_fig.get_figheight()
#     dpi = mpl_fig.get_dpi()
#
#     # Convert to mm
#     width_mm = width_inch * 25.4
#     height_mm = height_inch * 25.4
#
#     # Determine layout from axes
#     axes_list = mpl_fig.axes
#     nrows, ncols = _infer_layout(axes_list, mpl_fig)
#
#     # Create figure model
#     figure_model = FigureModel(
#         width_mm=width_mm,
#         height_mm=height_mm,
#         nrows=nrows,
#         ncols=ncols,
#         dpi=int(dpi),
#         facecolor=_color_to_hex(mpl_fig.get_facecolor()),
#         edgecolor=_color_to_hex(mpl_fig.get_edgecolor()),
#     )
#
#     # Handle suptitle
#     if hasattr(mpl_fig, "_suptitle") and mpl_fig._suptitle:
#         figure_model.suptitle = mpl_fig._suptitle.get_text()
#         figure_model.suptitle_fontsize = mpl_fig._suptitle.get_fontsize()
#
#     # Convert each axes
#     scitex_axes = _get_scitex_axes(fig)
#
#     for idx, ax in enumerate(axes_list):
#         row = idx // ncols
#         col = idx % ncols
#
#         # Find corresponding scitex axis wrapper for history
#         scitex_ax = _find_scitex_axis(scitex_axes, ax)
#
#         axes_model = axes_to_vis_axes(
#             ax,
#             row=row,
#             col=col,
#             scitex_ax=scitex_ax,
#             include_data=include_data,
#             include_style=include_style,
#         )
#         figure_model.axes.append(axes_model.to_dict())
#
#     return figure_model
#
#
# def axes_to_vis_axes(
#     ax,
#     row: int = 0,
#     col: int = 0,
#     scitex_ax=None,
#     include_data: bool = True,
#     include_style: bool = True,
# ) -> AxesModel:
#     """
#     Convert a matplotlib axes to a vis AxesModel.
#
#     Parameters
#     ----------
#     ax : matplotlib.axes.Axes
#         The axes to convert
#     row : int
#         Row position in layout
#     col : int
#         Column position in layout
#     scitex_ax : AxisWrapper, optional
#         Scitex axis wrapper with tracking history
#     include_data : bool
#         Whether to include plot data
#     include_style : bool
#         Whether to include style information
#
#     Returns
#     -------
#     AxesModel
#         The vis axes model
#     """
#     # Get underlying matplotlib axes
#     mpl_ax = ax._axes_mpl if hasattr(ax, "_axes_mpl") else ax
#
#     # Extract axis properties
#     axes_model = AxesModel(
#         row=row,
#         col=col,
#         xlabel=mpl_ax.get_xlabel() or None,
#         ylabel=mpl_ax.get_ylabel() or None,
#         title=mpl_ax.get_title() or None,
#         xlim=list(mpl_ax.get_xlim()),
#         ylim=list(mpl_ax.get_ylim()),
#         xscale=mpl_ax.get_xscale(),
#         yscale=mpl_ax.get_yscale(),
#     )
#
#     # Extract tick info
#     xticks = mpl_ax.get_xticks()
#     yticks = mpl_ax.get_yticks()
#     if len(xticks) > 0:
#         axes_model.xticks = [float(t) for t in xticks]
#     if len(yticks) > 0:
#         axes_model.yticks = [float(t) for t in yticks]
#
#     # Extract style if requested
#     if include_style:
#         axes_model.style = _extract_axes_style(mpl_ax)
#
#     # Extract plots from tracking history
#     if include_data and scitex_ax and hasattr(scitex_ax, "history"):
#         plots = tracking_to_plot_configs(scitex_ax.history)
#         for plot in plots:
#             axes_model.plots.append(plot.to_dict() if hasattr(plot, "to_dict") else plot)
#
#     # Extract annotations
#     for text_obj in mpl_ax.texts:
#         annotation = _text_to_annotation(text_obj)
#         if annotation:
#             axes_model.annotations.append(annotation.to_dict())
#
#     # Extract guides (axhline, axvline, etc.)
#     guides = _extract_guides(mpl_ax)
#     for guide in guides:
#         axes_model.guides.append(guide.to_dict())
#
#     return axes_model
#
#
# def tracking_to_plot_configs(
#     history: Dict[str, Tuple],
# ) -> List[PlotModel]:
#     """
#     Convert scitex.plt tracking history to PlotModel configurations.
#
#     Parameters
#     ----------
#     history : Dict[str, Tuple]
#         Tracking history from AxisWrapper
#         Format: {id: (id, method_name, tracked_dict, kwargs)}
#
#     Returns
#     -------
#     List[PlotModel]
#         List of PlotModel configurations
#     """
#     plots = []
#
#     for plot_id, (_, method_name, tracked_dict, kwargs) in history.items():
#         plot_model = _history_entry_to_plot_model(
#             plot_id, method_name, tracked_dict, kwargs
#         )
#         if plot_model:
#             plots.append(plot_model)
#
#     return plots
#
#
# def collect_figure_data(
#     fig,
# ) -> Dict[str, Any]:
#     """
#     Collect all data from a figure for export.
#
#     This is a simpler version that just extracts data without
#     full vis model conversion.
#
#     Parameters
#     ----------
#     fig : scitex.plt.FigWrapper or matplotlib.figure.Figure
#         The figure to collect data from
#
#     Returns
#     -------
#     Dict[str, Any]
#         Dictionary with figure data organized by axes/plot
#     """
#     data = {
#         "figure": {},
#         "axes": [],
#     }
#
#     mpl_fig = _get_mpl_figure(fig)
#
#     # Figure info
#     data["figure"]["width_mm"] = mpl_fig.get_figwidth() * 25.4
#     data["figure"]["height_mm"] = mpl_fig.get_figheight() * 25.4
#     data["figure"]["dpi"] = mpl_fig.get_dpi()
#
#     # Get scitex axes for history
#     scitex_axes = _get_scitex_axes(fig)
#
#     # Collect axes data
#     for idx, ax in enumerate(mpl_fig.axes):
#         mpl_ax = ax._axes_mpl if hasattr(ax, "_axes_mpl") else ax
#         scitex_ax = _find_scitex_axis(scitex_axes, mpl_ax)
#
#         axes_data = {
#             "index": idx,
#             "xlabel": mpl_ax.get_xlabel(),
#             "ylabel": mpl_ax.get_ylabel(),
#             "title": mpl_ax.get_title(),
#             "xlim": list(mpl_ax.get_xlim()),
#             "ylim": list(mpl_ax.get_ylim()),
#             "plots": [],
#         }
#
#         # Get plot data from history
#         if scitex_ax and hasattr(scitex_ax, "history"):
#             for plot_id, (_, method, tracked, kwargs) in scitex_ax.history.items():
#                 plot_data = {
#                     "id": plot_id,
#                     "method": method,
#                     "kwargs": {k: v for k, v in kwargs.items() if _is_serializable(v)},
#                 }
#                 # Extract data arrays from tracked_dict
#                 if "args" in tracked:
#                     plot_data["args"] = [
#                         _array_to_list(a) for a in tracked["args"]
#                         if _is_array_like(a)
#                     ]
#                 axes_data["plots"].append(plot_data)
#
#         data["axes"].append(axes_data)
#
#     return data
#
#
# # =============================================================================
# # Helper Functions
# # =============================================================================
#
#
# def _get_mpl_figure(fig):
#     """Get the underlying matplotlib figure."""
#     if hasattr(fig, "_fig_mpl"):
#         return fig._fig_mpl
#     return fig
#
#
# def _get_scitex_axes(fig):
#     """Get scitex axes wrappers from figure."""
#     if hasattr(fig, "_axes_scitex"):
#         axes = fig._axes_scitex
#         if hasattr(axes, "flat"):
#             return list(axes.flat)
#         return [axes]
#     return []
#
#
# def _find_scitex_axis(scitex_axes, mpl_ax):
#     """Find the scitex axis wrapper that wraps the given mpl axis."""
#     for ax in scitex_axes:
#         if hasattr(ax, "_axes_mpl") and ax._axes_mpl is mpl_ax:
#             return ax
#     return None
#
#
# def _infer_layout(axes_list, fig) -> Tuple[int, int]:
#     """Infer nrows, ncols from axes positions."""
#     if not axes_list:
#         return 1, 1
#
#     # Check if using gridspec
#     if hasattr(fig, "_gridspecs") and fig._gridspecs:
#         gs = fig._gridspecs[0]
#         return gs.nrows, gs.ncols
#
#     # Fallback: guess from axes count
#     n = len(axes_list)
#     if n == 1:
#         return 1, 1
#     elif n == 2:
#         return 1, 2
#     elif n <= 4:
#         return 2, 2
#     else:
#         # Try to make it roughly square
#         import math
#         ncols = int(math.ceil(math.sqrt(n)))
#         nrows = int(math.ceil(n / ncols))
#         return nrows, ncols
#
#
# def _color_to_hex(color) -> str:
#     """Convert matplotlib color to hex string."""
#     try:
#         import matplotlib.colors as mcolors
#         rgb = mcolors.to_rgb(color)
#         return "#{:02x}{:02x}{:02x}".format(
#             int(rgb[0] * 255),
#             int(rgb[1] * 255),
#             int(rgb[2] * 255),
#         )
#     except (ValueError, TypeError):
#         return "#ffffff"
#
#
# def _extract_axes_style(mpl_ax) -> AxesStyle:
#     """Extract style information from matplotlib axes."""
#     # Check grid visibility
#     grid_visible = False
#     try:
#         gridlines = mpl_ax.xaxis.get_gridlines()
#         if gridlines:
#             grid_visible = gridlines[0].get_visible()
#     except (AttributeError, IndexError):
#         pass
#
#     return AxesStyle(
#         facecolor=_color_to_hex(mpl_ax.get_facecolor()),
#         grid=grid_visible,
#         spines_visible={
#             "top": mpl_ax.spines["top"].get_visible(),
#             "right": mpl_ax.spines["right"].get_visible(),
#             "bottom": mpl_ax.spines["bottom"].get_visible(),
#             "left": mpl_ax.spines["left"].get_visible(),
#         },
#     )
#
#
# def _text_to_annotation(text_obj) -> Optional[AnnotationModel]:
#     """Convert matplotlib text object to AnnotationModel."""
#     text = text_obj.get_text()
#     if not text or not text.strip():
#         return None
#
#     pos = text_obj.get_position()
#
#     style = TextStyle(
#         fontsize=text_obj.get_fontsize(),
#         color=_color_to_hex(text_obj.get_color()),
#         ha=text_obj.get_ha(),
#         va=text_obj.get_va(),
#         rotation=text_obj.get_rotation(),
#     )
#
#     return AnnotationModel(
#         annotation_type="text",
#         text=text,
#         x=pos[0],
#         y=pos[1],
#         style=style,
#     )
#
#
# def _extract_guides(mpl_ax) -> List[GuideModel]:
#     """Extract guide lines (axhline, axvline) from axes."""
#     guides = []
#
#     # Check for horizontal lines
#     for line in mpl_ax.lines:
#         data = line.get_xydata()
#         if len(data) >= 2:
#             # Check if horizontal (y values same)
#             if data[0][1] == data[-1][1] and data[0][0] != data[-1][0]:
#                 xlim = mpl_ax.get_xlim()
#                 if abs(data[0][0] - xlim[0]) < 0.01 and abs(data[-1][0] - xlim[1]) < 0.01:
#                     guides.append(GuideModel(
#                         guide_type="axhline",
#                         y=data[0][1],
#                         color=_color_to_hex(line.get_color()),
#                         linestyle=line.get_linestyle(),
#                         linewidth=line.get_linewidth(),
#                     ))
#             # Check if vertical
#             elif data[0][0] == data[-1][0] and data[0][1] != data[-1][1]:
#                 ylim = mpl_ax.get_ylim()
#                 if abs(data[0][1] - ylim[0]) < 0.01 and abs(data[-1][1] - ylim[1]) < 0.01:
#                     guides.append(GuideModel(
#                         guide_type="axvline",
#                         x=data[0][0],
#                         color=_color_to_hex(line.get_color()),
#                         linestyle=line.get_linestyle(),
#                         linewidth=line.get_linewidth(),
#                     ))
#
#     return guides
#
#
# def _history_entry_to_plot_model(
#     plot_id: str,
#     method_name: str,
#     tracked_dict: Dict,
#     kwargs: Dict,
# ) -> Optional[PlotModel]:
#     """Convert a tracking history entry to PlotModel."""
#     # Map matplotlib methods to vis plot types
#     method_to_type = {
#         "plot": "line",
#         "scatter": "scatter",
#         "bar": "bar",
#         "barh": "barh",
#         "hist": "histogram",
#         "boxplot": "boxplot",
#         "violinplot": "violin",
#         "fill_between": "fill_between",
#         "errorbar": "errorbar",
#         "imshow": "imshow",
#         "contour": "contour",
#         "contourf": "contourf",
#     }
#
#     plot_type = method_to_type.get(method_name, method_name)
#
#     # Extract data from tracked_dict
#     data = {}
#     if "args" in tracked_dict:
#         args = tracked_dict["args"]
#         if method_name in ("plot", "scatter") and len(args) >= 2:
#             data["x"] = _array_to_list(args[0])
#             data["y"] = _array_to_list(args[1])
#         elif method_name == "bar" and len(args) >= 2:
#             data["x"] = _array_to_list(args[0])
#             data["height"] = _array_to_list(args[1])
#         elif method_name == "hist" and len(args) >= 1:
#             data["x"] = _array_to_list(args[0])
#
#     # Extract style from kwargs
#     style = PlotStyle()
#     if "color" in kwargs:
#         style.color = _color_to_hex(kwargs["color"]) if kwargs["color"] else None
#     if "linewidth" in kwargs or "lw" in kwargs:
#         style.linewidth = kwargs.get("linewidth") or kwargs.get("lw")
#     if "linestyle" in kwargs or "ls" in kwargs:
#         style.linestyle = kwargs.get("linestyle") or kwargs.get("ls")
#     if "marker" in kwargs:
#         style.marker = kwargs.get("marker")
#     if "alpha" in kwargs:
#         style.alpha = kwargs.get("alpha")
#     if "label" in kwargs:
#         style.label = kwargs.get("label")
#
#     return PlotModel(
#         plot_type=plot_type,
#         plot_id=plot_id,
#         data=data,
#         style=style,
#     )
#
#
# def _array_to_list(arr) -> List:
#     """Convert array-like to list for serialization."""
#     if hasattr(arr, "tolist"):
#         return arr.tolist()
#     elif isinstance(arr, (list, tuple)):
#         return list(arr)
#     return [arr]
#
#
# def _is_array_like(obj) -> bool:
#     """Check if object is array-like."""
#     return hasattr(obj, "__len__") and not isinstance(obj, (str, dict))
#
#
# def _is_serializable(obj) -> bool:
#     """Check if object is JSON serializable."""
#     import json
#     try:
#         json.dumps(obj)
#         return True
#     except (TypeError, ValueError):
#         return False
#
#
# __all__ = [
#     "figure_to_vis_model",
#     "axes_to_vis_axes",
#     "tracking_to_plot_configs",
#     "collect_figure_data",
# ]
#
#
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/bridge/_plt_vis.py
# --------------------------------------------------------------------------------
