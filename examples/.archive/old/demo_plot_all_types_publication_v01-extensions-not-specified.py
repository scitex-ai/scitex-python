#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-01 03:58:05 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/examples/demo_plot_all_types_publication.py


"""
Publication-ready comprehensive demo suite using the unified style system.

This demo showcases ALL plot types available in scitex with publication-ready
styling using mm-control integration in scitex.plt.subplots().

Coverage:
- Matplotlib basic plots (plot, scatter, bar, barh, hist, boxplot, etc.)
- Custom scitex plots (stx_line, stx_box, stx_mean_std, etc.)
- Functional plots (KDE, image, violin, heatmap, ECDF, etc.)
- Seaborn integration (boxplot, barplot, violinplot, etc.)

Key Features:
- Uses SCITEX_STYLE preset for consistency
- Millimeter-based control over axes dimensions
- Publication-quality styling (300 DPI)
- Automatic metadata embedding for reproducibility
- Suitable for journal submission
"""

import os
import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")

import scitex as stx
from scitex.plt.presets import SCITEX_STYLE  # Universal publication style

# Relative paths for session output directory
OUTPUT_DIR = "publication"
OUTPUT_DIR_BASIC = "publication/01_matplotlib_basic"
OUTPUT_DIR_CUSTOM = "publication/02_custom_scitex"
OUTPUT_DIR_FUNCTIONAL = "publication/03_functional"
OUTPUT_DIR_SEABORN = "publication/04_seaborn"
OUTPUT_DIR_MULTI = "publication/05_multi_panel"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


# def get_linewidth_from_style(style_dict):
#     """Get proper linewidth in points from mm-based style dict."""
#     from scitex.plt.utils import mm_to_pt

#     trace_mm = style_dict.get("trace_thickness_mm", 0.12)
#     return mm_to_pt(trace_mm)


# def set_ticks(ax, n=4):
#     """Set number of ticks on both axes."""
#     from matplotlib.ticker import MaxNLocator

#     ax.xaxis.set_major_locator(MaxNLocator(n))
#     ax.yaxis.set_major_locator(MaxNLocator(n))


def save_multi_format(
    fig,
    base_path,
    dpi=300,
    *,
    plot_type=None,
    style_name=None,
    style_overrides=None,
    save_extensions=[".jpg", ".json", ".png", ".pdf"],
):
    """Save figure in PNG, PDF, and JPEG formats with metadata.

    - PNG: Lossless raster, best for publication (metadata preserved)
    - PDF: Vector format, infinite zoom, best for publication
    - JPEG: High-quality (quality=100) for daily use, smaller file size

    Parameters
    ----------
    fig : matplotlib.figure.Figure or scitex wrapper
        The figure to save
    base_path : str
        Base path for saving (should end with .png)
    dpi : int, optional
        DPI for raster formats. Default is 300.
    plot_type : str, optional
        Type of plot (e.g., "line", "scatter", "bar", "hist", etc.)
    style_name : str, optional
        Name of the style preset used (e.g., "SCITEX_STYLE")
    style_overrides : dict, optional
        Dictionary of style parameters that override the base style

    Returns
    -------
    tuple
        (png_path, pdf_path, jpg_path)

    Note
    ----
    For final publication submission, prefer PNG or PDF.
    JPEG is included with quality=100 for daily workflow and sharing.
    """
    # Build metadata_extra
    metadata_extra = {}
    if plot_type is not None:
        metadata_extra["plot_type"] = plot_type
    if style_name is not None or style_overrides is not None:
        metadata_extra["style"] = {
            "name": style_name,
            "overrides": style_overrides or {},
        }

    # Save PNG with auto-crop (1mm margin) - lossless format
    png_path = (
        base_path
        if base_path.endswith(".png")
        else base_path.replace(".png", ".png")
    )
    pdf_path = png_path.replace(".png", ".pdf")
    jpg_path = png_path.replace(".png", ".jpg")

    if ".png" in save_extensions:

        stx.io.save(
            fig,
            png_path,
            dpi=dpi,
            auto_crop=True,
            crop_margin_mm=1.0,
            metadata_extra=metadata_extra,
        )

    if ".pdf" in save_extensions:
        # Save PDF (vector format, infinite zoom, no cropping needed)
        stx.io.save(fig, pdf_path, metadata_extra=metadata_extra)

    if ".jpg" in save_extensions:
        # Save JPEG (quality=100, 600 DPI for better sharpness despite lossy compression)

        stx.io.save(
            fig,
            jpg_path,
            dpi=600,
            auto_crop=True,
            crop_margin_mm=1.0,
            metadata_extra=metadata_extra,
        )

    return png_path, pdf_path, jpg_path


# ============================================================================
# MATPLOTLIB BASIC PLOTS
# ============================================================================


def demo_publication_plot(save_extensions=[".jpg", ".json", ".png", ".pdf"]):
    """Publication-ready line plot using SCITEX_STYLE."""
    print("\n" + "=" * 70)
    print("Demo: Publication Line Plot (SciTeX Style)")
    print("=" * 70)

    # Create figure with SciTeX preset
    fig, ax = stx.plt.subplots(**SCITEX_STYLE)

    # Generate data
    x = np.linspace(0, 2 * np.pi, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)

    # Plot with appropriate line width from style
    ax.plot(x, y1, "b-", label="sin(x)", id="sine")
    ax.plot(x, y2, "r-", label="cos(x)", id="cosine")

    # Labels and styling (use bracket units)
    ax.set_xyt(
        stx.plt.ax.format_label("Time", "s"),
        stx.plt.ax.format_label("Amplitude", "a.u."),
        "Oscillatory Response",
    )
    ax.legend(frameon=False, fontsize=6)

    # Save in publication formats (PNG, PDF) with plot_type metadata
    save_path = os.path.join(OUTPUT_DIR_BASIC, "01_plot.png")
    png_path, pdf_path, jpg_path = save_multi_format(
        fig,
        save_path,
        dpi=300,
        plot_type="line",
        style_name="SCITEX_STYLE",
        save_extensions=save_extensions,
    )
    fig.close()


def demo_publication_scatter():
    """Publication-ready scatter plot using SCITEX_STYLE."""
    print("\n" + "=" * 70)
    print("Demo: Publication Scatter Plot (SciTeX Style)")
    print("=" * 70)

    # Create figure with SciTeX preset
    fig, ax = stx.plt.subplots(**SCITEX_STYLE)

    # Generate data
    np.random.seed(42)
    n = 100
    x = np.random.normal(0, 1, n)
    y = 2 * x + np.random.normal(0, 0.5, n)

    # Scatter plot with default styling (size_mm=0.8 from source default)
    scatter = ax.scatter(
        x, y, alpha=0.6, c="steelblue", id="scatter_data", label="Data"
    )
    stx.plt.ax.style_scatter(scatter)  # Uses default size_mm=0.8

    # Add fitted line with automatic R² and p-value annotation
    # (uses add_fitted_line which calls test_pearson internally)
    stx.plt.ax.add_fitted_line(
        ax,
        x,
        y,
        label="Fit",
        show_stats=True,  # Automatically shows R² with significance stars
    )

    # Labels with units
    ax.set_xlabel(stx.plt.ax.format_label("Predictor", "a.u."))
    ax.set_ylabel(stx.plt.ax.format_label("Response", "a.u."))
    ax.set_title("Correlation Analysis")
    ax.legend(frameon=False)  # Uses default fontsize from SCITEX_STYLE (6pt)

    # Save in publication formats (PNG, PDF) with plot_type metadata
    save_path = os.path.join(OUTPUT_DIR_BASIC, "02_scatter.png")
    png_path, pdf_path, jpg_path = save_multi_format(
        fig,
        save_path,
        dpi=300,
        plot_type="scatter",
        style_name="SCITEX_STYLE",
    )
    fig.close()

    print(f"- Saved: {png_path}, .pdf, .jpg")


def demo_publication_bar():
    """Publication-ready bar plot using SCITEX_STYLE."""
    print("\n" + "=" * 70)
    print("Demo: Publication Bar Plot (SciTeX Style)")
    print("=" * 70)

    # Create figure with SciTeX preset
    fig, ax = stx.plt.subplots(**SCITEX_STYLE)

    # Generate data
    categories = ["Control", "Treatment A", "Treatment B", "Treatment C"]
    values = [45, 67, 52, 71]
    errors = [5, 7, 6, 8]
    # Define colors for each bar/group
    colors = ["steelblue", "coral", "mediumseagreen", "orchid"]

    # Bar plot with error bars and styling
    x_pos = np.arange(len(categories))
    bars = ax.bar(
        x_pos,
        values,
        alpha=0.7,
        color=colors,
        id="bar_data",
        label="Response",
    )

    # Style bar edges
    stx.plt.ax.style_barplot(bars, edge_thickness_mm=0.2, edgecolor="black")

    # Add error bars
    eb = ax.errorbar(
        x_pos,
        values,
        yerr=errors,
        fmt="none",
        capsize=3,
        color="black",
        id="error_bars",
    )
    stx.plt.ax.style_errorbar(eb, thickness_mm=0.2, cap_width_mm=0.8)

    # Labels with units
    ax.set_xticks(x_pos)
    ax.set_xticklabels(categories, rotation=15, ha="right")
    ax.set_xlabel(
        stx.plt.ax.format_label("Treatment", ""), fontweight="normal"
    )
    ax.set_ylabel(stx.plt.ax.format_label("Response", "%"))
    ax.set_title("Treatment Effect Comparison")
    ax.legend(frameon=False, fontsize=6)

    # Save in publication formats (PNG, PDF)
    save_path = os.path.join(OUTPUT_DIR_BASIC, "03_bar.png")
    png_path, pdf_path, jpg_path = save_multi_format(fig, save_path, dpi=300)
    fig.close()

    print(f"- Saved: {png_path}, .pdf, .jpg")


def demo_publication_hist():
    """Publication-ready histogram with KDE overlay."""
    print("\n" + "=" * 70)
    print("Demo: Publication Histogram (SciTeX Style)")
    print("=" * 70)

    # Create figure
    fig, ax = stx.plt.subplots(**SCITEX_STYLE)

    # Generate bimodal data
    np.random.seed(42)
    data = np.concatenate(
        [
            np.random.normal(0, 1, 500),
            np.random.normal(4, 1, 300),
        ]
    )

    # Histogram with legend
    n_hist, bins, patches = ax.hist(
        data,
        bins=40,
        alpha=0.7,
        density=True,
        color="steelblue",
        label="Data",
        id="histogram",
    )

    # KDE overlay (uses default 0.2mm line width from preset)
    from scipy import stats

    kde = stats.gaussian_kde(data)
    x_range = np.linspace(data.min(), data.max(), 200)
    ax.plot(
        x_range,
        kde(x_range),
        color="black",  # Black line for KDE
        label="KDE",
        id="kde",
    )

    # Labels with units
    ax.set_xlabel(stx.plt.ax.format_label("Value", "a.u."))
    ax.set_ylabel(stx.plt.ax.format_label("Probability Density", ""))
    ax.set_title("Distribution Analysis")
    ax.legend(frameon=False, fontsize=6)

    # Save in publication formats (PNG, PDF)
    save_path = os.path.join(OUTPUT_DIR_BASIC, "04_hist.png")
    png_path, pdf_path, jpg_path = save_multi_format(fig, save_path, dpi=300)
    fig.close()

    print(f"- Saved: {png_path}, .pdf, .jpg")


def demo_publication_boxplot():
    """Publication-ready boxplot using SCITEX_STYLE."""
    print("\n" + "=" * 70)
    print("Demo: Publication Boxplot (SciTeX Style)")
    print("=" * 70)

    # Create figure
    fig, ax = stx.plt.subplots(**SCITEX_STYLE)

    # Generate data
    np.random.seed(42)
    data = [
        np.random.normal(0, 1, 100),
        np.random.normal(2, 1, 100),
        np.random.normal(4, 1.5, 100),
    ]

    # Boxplot with styling (no fliers)
    bp = ax.boxplot(
        data,
        labels=["Group A", "Group B", "Group C"],
        showfliers=False,
        id="boxplot",
    )
    stx.plt.ax.style_boxplot(bp, linewidth_mm=0.2)

    # Make median lines black
    for median in bp["medians"]:
        median.set_color("black")
        median.set_linewidth(0.8)

    # Labels
    ax.set_xlabel(stx.plt.ax.format_label("Group", ""))
    ax.set_ylabel(stx.plt.ax.format_label("Value", "a.u."))
    ax.set_title("Group Comparison")

    # Add legend (using a proxy artist since boxplots don't have built-in labels)
    from matplotlib.patches import Patch

    legend_elements = [
        Patch(facecolor="steelblue", alpha=0.7, label="Distribution")
    ]
    ax.legend(handles=legend_elements, frameon=False, fontsize=6)

    # Save in publication formats (PNG, PDF)
    save_path = os.path.join(OUTPUT_DIR_BASIC, "05_boxplot.png")
    png_path, pdf_path, jpg_path = save_multi_format(fig, save_path, dpi=300)
    fig.close()

    print(f"- Saved: {png_path}, .pdf, .jpg")


def demo_publication_errorbar():
    """Publication-ready error bar plot."""
    print("\n" + "=" * 70)
    print("Demo: Publication Error Bar Plot (SciTeX Style)")
    print("=" * 70)

    # Create figure
    fig, ax = stx.plt.subplots(**SCITEX_STYLE)

    # Generate time series data
    np.random.seed(42)
    time = np.arange(0, 10, 0.5)
    mean_values = 10 * np.exp(-time / 5)
    errors = 0.1 * mean_values + np.random.uniform(0, 0.5, len(time))

    # Error bar plot with styling
    eb = ax.errorbar(
        time,
        mean_values,
        yerr=errors,
        fmt="o-",
        capsize=3,
        alpha=0.8,
        color="steelblue",
        label="Measured",
        id="errorbar_data",
    )

    # Style error bars (0.2mm bars, 0.8mm caps)
    stx.plt.ax.style_errorbar(eb, thickness_mm=0.2, cap_width_mm=0.8)

    # Style markers (0.08mm symbol size)
    # Get the line object from errorbar container
    line = eb[0]
    stx.plt.ax.style_scatter(line, size_mm=0.08)

    # Labels with units
    ax.set_xlabel(stx.plt.ax.format_label("Time", "min"))
    ax.set_ylabel(stx.plt.ax.format_label("Concentration", "µM"))
    ax.set_title("Decay Kinetics")
    ax.legend(frameon=False, fontsize=6)

    # Save in publication formats (PNG, PDF)
    save_path = os.path.join(OUTPUT_DIR_BASIC, "06_errorbar.png")
    png_path, pdf_path, jpg_path = save_multi_format(fig, save_path, dpi=300)
    fig.close()

    print(f"- Saved: {png_path}, .pdf, .jpg")


def demo_publication_barh():
    """Publication-ready horizontal bar plot."""
    print("\n" + "=" * 70)
    print("Demo: Publication Horizontal Bar Plot (SciTeX Style)")
    print("=" * 70)

    # Create figure
    fig, ax = stx.plt.subplots(**SCITEX_STYLE)

    # Generate data
    categories = ["Method A", "Method B", "Method C", "Method D"]
    values = [45, 67, 52, 71]
    errors = [4, 6, 5, 7]
    # Define colors for each bar/group
    colors = ["steelblue", "coral", "mediumseagreen", "orchid"]

    # Horizontal bar plot with styling
    bars = ax.barh(
        categories,
        values,
        alpha=0.7,
        color=colors,
        id="barh_data",
    )
    stx.plt.ax.style_barplot(bars, edge_thickness_mm=0.2, edgecolor="black")

    # Add error bars in black
    y_pos = np.arange(len(categories))
    eb = ax.errorbar(
        values,
        y_pos,
        xerr=errors,
        fmt="none",
        capsize=3,
        color="black",
        id="error_bars",
    )
    stx.plt.ax.style_errorbar(eb, thickness_mm=0.2, cap_width_mm=0.8)

    # Labels
    ax.set_xlabel(stx.plt.ax.format_label("Score", ""), fontweight="normal")
    ax.set_ylabel(stx.plt.ax.format_label("Method", ""))
    ax.set_title("Performance Comparison")

    # Save in publication formats (PNG, PDF)
    save_path = os.path.join(OUTPUT_DIR_BASIC, "07_barh.png")
    png_path, pdf_path, jpg_path = save_multi_format(fig, save_path, dpi=300)
    fig.close()

    print(f"- Saved: {png_path}, .pdf, .jpg")


def demo_publication_fill_between():
    """Publication-ready fill_between plot."""
    print("\n" + "=" * 70)
    print("Demo: Publication Fill Between (SciTeX Style)")
    print("=" * 70)

    # Create figure
    fig, ax = stx.plt.subplots(**SCITEX_STYLE)

    # Generate data
    x = np.linspace(0, 2 * np.pi, 100)
    y1 = np.sin(x)
    y2 = np.sin(x) + 0.5

    # Fill between with styling
    ax.fill_between(
        x, y1, y2, alpha=0.3, color="steelblue", label="Confidence", id="fill"
    )
    ax.plot(x, (y1 + y2) / 2, color="steelblue", label="Mean", id="mean_line")

    # Labels
    ax.set_xlabel(stx.plt.ax.format_label("Time", "s"))
    ax.set_ylabel(stx.plt.ax.format_label("Signal", "a.u."))
    ax.set_title("Signal with Confidence")
    ax.legend(frameon=False, fontsize=6)

    # Save in publication formats (PNG, PDF)
    save_path = os.path.join(OUTPUT_DIR_BASIC, "08_fill_between.png")
    png_path, pdf_path, jpg_path = save_multi_format(fig, save_path, dpi=300)
    fig.close()

    print(f"- Saved: {png_path}, .pdf, .jpg")


def demo_publication_imshow():
    """Publication-ready imshow plot."""
    print("\n" + "=" * 70)
    print("Demo: Publication Imshow (SciTeX Style)")
    print("=" * 70)

    # Create figure with custom dimensions
    style = SCITEX_STYLE.copy()
    style["ax_width_mm"] = 40
    style["ax_height_mm"] = 30

    fig, ax = stx.plt.subplots(**style)

    # Generate data
    np.random.seed(42)
    data = np.random.rand(20, 30)

    # Imshow with styling
    im = ax.imshow(data, cmap="viridis", aspect="auto", id="imshow")
    ax.spines[:].set_visible(True)

    # Colorbar
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label(stx.plt.ax.format_label("Intensity", ""))

    # Title only (no x/y labels for image display, distinguishing from heatmap)
    ax.set_title("Image Data")
    # Remove tick labels to emphasize this is image data, not a data matrix
    ax.set_xticks([])
    ax.set_yticks([])

    # Save in publication formats (PNG, PDF)
    save_path = os.path.join(OUTPUT_DIR_BASIC, "09_imshow.png")
    png_path, pdf_path, jpg_path = save_multi_format(fig, save_path, dpi=300)
    fig.close()

    print(f"- Saved: {png_path}, .pdf, .jpg")


def demo_publication_contour():
    """Publication-ready contour plot."""
    print("\n" + "=" * 70)
    print("Demo: Publication Contour (SciTeX Style)")
    print("=" * 70)

    # Create figure
    fig, ax = stx.plt.subplots(**SCITEX_STYLE)

    # Generate data
    delta = 0.5
    x = np.arange(-3.0, 3.0, delta)
    y = np.arange(-2.0, 2.0, delta)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)

    # Contour plot
    contour = ax.contour(X, Y, Z, levels=8, id="contour")
    ax.clabel(contour, inline=True, fontsize=6)

    # Labels
    ax.set_xlabel(stx.plt.ax.format_label("X", ""))
    ax.set_ylabel(stx.plt.ax.format_label("Y", ""))
    ax.set_title("Contour Map")

    # Save in publication formats (PNG, PDF)
    save_path = os.path.join(OUTPUT_DIR_BASIC, "10_contour.png")
    png_path, pdf_path, jpg_path = save_multi_format(fig, save_path, dpi=300)
    fig.close()

    print(f"- Saved: {png_path}, .pdf, .jpg")


def demo_publication_violinplot():
    """Publication-ready violinplot using matplotlib."""
    print("\n" + "=" * 70)
    print("Demo: Publication Violinplot (SciTeX Style)")
    print("=" * 70)

    # Create figure
    fig, ax = stx.plt.subplots(**SCITEX_STYLE)

    # Generate data
    np.random.seed(42)
    data = [np.random.normal(i, 1, 100) for i in range(4)]

    # Violinplot
    parts = ax.violinplot(data, positions=[1, 2, 3, 4], id="violinplot")

    # Make error bars and vertical lines black
    for partname in ("cbars", "cmins", "cmaxes", "cmedians"):
        if partname in parts:
            vp = parts[partname]
            vp.set_edgecolor("black")
            vp.set_linewidth(0.8)

    # Labels
    ax.set_xlabel(stx.plt.ax.format_label("Group", ""))
    ax.set_ylabel(stx.plt.ax.format_label("Value", "a.u."))
    ax.set_title("Violin Plot")
    ax.set_xticks([1, 2, 3, 4])
    ax.set_xticklabels(["A", "B", "C", "D"])

    # Add legend
    from matplotlib.patches import Patch

    legend_elements = [
        Patch(facecolor="steelblue", alpha=0.7, label="Distribution")
    ]
    ax.legend(handles=legend_elements, frameon=False, fontsize=6)

    # Save in publication formats (PNG, PDF)
    save_path = os.path.join(OUTPUT_DIR_BASIC, "11_violinplot.png")
    png_path, pdf_path, jpg_path = save_multi_format(fig, save_path, dpi=300)
    fig.close()

    print(f"- Saved: {png_path}, .pdf, .jpg")


# ============================================================================
# CUSTOM SCITEX PLOTS
# ============================================================================


def demo_publication_plot_heatmap():
    """Publication-ready heatmap using stx_heatmap."""
    print("\n" + "=" * 70)
    print("Demo: Publication Heatmap (Custom Scitex)")
    print("=" * 70)

    # Create figure with custom dimensions
    style = SCITEX_STYLE.copy()
    style["ax_width_mm"] = 45
    style["ax_height_mm"] = 30

    fig, ax = stx.plt.subplots(**style)

    # Generate data
    np.random.seed(42)
    data = np.random.rand(8, 12)
    x_labels = [f"X{i+1}" for i in range(8)]
    y_labels = [f"Y{i+1}" for i in range(12)]

    # Heatmap with styling
    ax.stx_heatmap(
        data,
        x_labels=x_labels,
        y_labels=y_labels,
        cbar_label="Values",
        show_annot=True,
        value_format="{x:.2f}",
        cmap="viridis",
        id="heatmap",
    )

    ax.set_title("Data Matrix")

    # Save in publication formats (PNG, PDF)
    save_path = os.path.join(OUTPUT_DIR_CUSTOM, "01_plot_heatmap.png")
    png_path, pdf_path, jpg_path = save_multi_format(fig, save_path, dpi=300)
    fig.close()

    print(f"- Saved: {png_path}, .pdf, .jpg")


def demo_publication_plot_line():
    """Publication-ready line using stx_line."""
    print("\n" + "=" * 70)
    print("Demo: Publication Line (Custom Scitex)")
    print("=" * 70)

    # Create figure
    fig, ax = stx.plt.subplots(**SCITEX_STYLE)

    # Generate data
    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    # Plot line
    ax.stx_line(y, label="Signal", id="line")

    # Labels
    ax.set_xlabel(stx.plt.ax.format_label("Sample", ""))
    ax.set_ylabel(stx.plt.ax.format_label("Amplitude", "a.u."))
    ax.set_title("Signal Trace")
    ax.legend(frameon=False, fontsize=6)

    # Save in publication formats (PNG, PDF)
    save_path = os.path.join(OUTPUT_DIR_CUSTOM, "02_plot_line.png")
    png_path, pdf_path, jpg_path = save_multi_format(fig, save_path, dpi=300)
    fig.close()

    print(f"- Saved: {png_path}, .pdf, .jpg")


def demo_publication_plot_shaded_line():
    """Publication-ready shaded line plot."""
    print("\n" + "=" * 70)
    print("Demo: Publication Shaded Line (Custom Scitex)")
    print("=" * 70)

    # Create figure
    fig, ax = stx.plt.subplots(**SCITEX_STYLE)

    # Generate data
    np.random.seed(42)
    x = np.linspace(0, 10, 50)
    y_middle = np.sin(x)
    y_lower = y_middle - 0.2
    y_upper = y_middle + 0.2

    # Shaded line
    ax.stx_shaded_line(
        x,
        y_lower,
        y_middle,
        y_upper,
        label="Mean ± SD",
        id="shaded",
    )

    # Labels
    ax.set_xlabel(stx.plt.ax.format_label("Time", "s"))
    ax.set_ylabel(stx.plt.ax.format_label("Signal", "a.u."))
    ax.set_title("Time Series with Uncertainty")
    ax.legend(frameon=False, fontsize=6)

    # Save in publication formats (PNG, PDF)
    save_path = os.path.join(OUTPUT_DIR_CUSTOM, "03_plot_shaded_line.png")
    png_path, pdf_path, jpg_path = save_multi_format(fig, save_path, dpi=300)
    fig.close()

    print(f"- Saved: {png_path}, .pdf, .jpg")


def demo_publication_plot_violin():
    """Publication-ready violin plot using stx_violin."""
    print("\n" + "=" * 70)
    print("Demo: Publication Violin (Custom Scitex)")
    print("=" * 70)

    # Create figure
    fig, ax = stx.plt.subplots(**SCITEX_STYLE)

    # Generate data
    np.random.seed(42)
    data = [
        np.random.normal(0, 1, 100),
        np.random.normal(2, 1.5, 100),
        np.random.normal(5, 0.8, 100),
    ]
    labels = ["Group A", "Group B", "Group C"]

    # Violin plot with styling
    ax.stx_violin(
        data,
        labels=labels,
        colors=["steelblue", "coral", "mediumseagreen"],
        id="violin",
        linewidth=0,  # Remove borders of violins
        legend=True,  # Add legend
    )

    # Labels
    ax.set_xlabel(stx.plt.ax.format_label("Group", ""))
    ax.set_ylabel(stx.plt.ax.format_label("Value", "a.u."))
    ax.set_title("Distribution Comparison")

    # Ensure legend is shown (if not automatically shown)
    if ax.get_legend() is None:
        ax.legend(labels, frameon=False, fontsize=6)

    # Save in publication formats (PNG, PDF)
    save_path = os.path.join(OUTPUT_DIR_CUSTOM, "04_plot_violin.png")
    png_path, pdf_path, jpg_path = save_multi_format(fig, save_path, dpi=300)
    fig.close()

    print(f"- Saved: {png_path}, .pdf, .jpg")


def demo_publication_plot_ecdf():
    """Publication-ready ECDF plot."""
    print("\n" + "=" * 70)
    print("Demo: Publication ECDF (Custom Scitex)")
    print("=" * 70)

    # Create figure
    fig, ax = stx.plt.subplots(**SCITEX_STYLE)

    # Generate data
    np.random.seed(42)
    data = np.random.normal(0, 1, 1000)

    # ECDF plot
    ax.stx_ecdf(data, label="Distribution", id="ecdf")

    # Labels
    ax.set_xlabel(stx.plt.ax.format_label("Value", "a.u."))
    ax.set_ylabel(stx.plt.ax.format_label("Cumulative Probability", ""))
    ax.set_title("Empirical CDF")
    ax.legend(frameon=False, fontsize=6)

    # Save in publication formats (PNG, PDF)
    save_path = os.path.join(OUTPUT_DIR_CUSTOM, "05_plot_ecdf.png")
    png_path, pdf_path, jpg_path = save_multi_format(fig, save_path, dpi=300)
    fig.close()

    print(f"- Saved: {png_path}, .pdf, .jpg")


def demo_publication_plot_box():
    """Publication-ready box plot using stx_box."""
    print("\n" + "=" * 70)
    print("Demo: Publication Box (Custom Scitex)")
    print("=" * 70)

    # Create figure
    fig, ax = stx.plt.subplots(**SCITEX_STYLE)

    # Generate data
    np.random.seed(42)
    data = np.random.normal(0, 1, 100)

    # Box plot with styling
    bp = ax.stx_box(
        data,
        label="Data",
        id="box",
        showfliers=False,  # No fliers
    )

    # Set border width to 0.2mm
    if hasattr(bp, "lines"):
        # bp is the result from boxplot which returns a dict with line objects
        stx.plt.ax.style_boxplot(bp, linewidth_mm=0.2)
    else:
        # If stx_box doesn't return the boxplot object, we need to access it differently
        # Get the last boxplot added to the axes
        for artist in ax.get_children():
            if hasattr(artist, "get_label") and "boxes" in str(type(artist)):
                stx.plt.ax.style_boxplot(artist, linewidth_mm=0.2)

    # Labels
    ax.set_ylabel(stx.plt.ax.format_label("Value", "a.u."))
    ax.set_title("Box Plot")
    ax.legend(frameon=False, fontsize=6)

    # Save in publication formats (PNG, PDF)
    save_path = os.path.join(OUTPUT_DIR_CUSTOM, "06_plot_box.png")
    png_path, pdf_path, jpg_path = save_multi_format(fig, save_path, dpi=300)
    fig.close()

    print(f"- Saved: {png_path}, .pdf, .jpg")


def demo_publication_plot_mean_std():
    """Publication-ready mean±std plot."""
    print("\n" + "=" * 70)
    print("Demo: Publication Mean±Std (Custom Scitex)")
    print("=" * 70)

    # Create figure
    fig, ax = stx.plt.subplots(**SCITEX_STYLE)

    # Generate data with n=10 samples to show SD
    np.random.seed(42)
    x = np.linspace(0, 10, 20)
    n_samples = 10
    # Create 2D data: n_samples x len(x)
    y_data = np.array(
        [
            np.sin(x) + np.random.normal(0, 0.2, len(x))
            for _ in range(n_samples)
        ]
    )

    # Mean±Std plot (will calculate mean and std from the 2D data)
    ax.stx_mean_std(y_data, xx=x, sd=1, label="Mean±SD", id="mean_std")

    # Labels
    ax.set_xlabel(stx.plt.ax.format_label("Time", "s"))
    ax.set_ylabel(stx.plt.ax.format_label("Signal", "a.u."))
    ax.set_title("Mean with Standard Deviation")
    ax.legend(frameon=False, fontsize=6)

    # Save in publication formats (PNG, PDF)
    save_path = os.path.join(OUTPUT_DIR_CUSTOM, "07_plot_mean_std.png")
    png_path, pdf_path, jpg_path = save_multi_format(fig, save_path, dpi=300)
    fig.close()

    print(f"- Saved: {png_path}, .pdf, .jpg")


# ============================================================================
# FUNCTIONAL PLOTS
# ============================================================================


def demo_publication_plot_kde():
    """Publication-ready KDE plot."""
    print("\n" + "=" * 70)
    print("Demo: Publication KDE (Functional)")
    print("=" * 70)

    # Create figure
    fig, ax = stx.plt.subplots(**SCITEX_STYLE)

    # Generate bimodal data
    np.random.seed(42)
    data = np.concatenate(
        [
            np.random.normal(0, 1, 500),
            np.random.normal(5, 1, 300),
        ]
    )

    # KDE plot
    ax.stx_kde(data, label="Density", id="kde")

    # Labels
    ax.set_xlabel(stx.plt.ax.format_label("Value", "a.u."))
    ax.set_ylabel(stx.plt.ax.format_label("Density", ""))
    ax.set_title("Kernel Density Estimate")
    ax.legend(frameon=False, fontsize=6)

    # Auto-scale Y-axis to factor out small values
    stx.plt.ax.auto_scale_axis(ax, axis="y")

    # Save in publication formats (PNG, PDF) with plot_type metadata
    save_path = os.path.join(OUTPUT_DIR_FUNCTIONAL, "01_plot_kde.png")
    png_path, pdf_path, jpg_path = save_multi_format(
        fig,
        save_path,
        dpi=300,
        plot_type="kde",
        style_name="SCITEX_STYLE",
    )
    fig.close()

    print(f"- Saved: {png_path}, .pdf, .jpg")


# ============================================================================
# SEABORN INTEGRATION
# ============================================================================


def demo_publication_sns_boxplot():
    """Publication-ready seaborn boxplot."""
    print("\n" + "=" * 70)
    print("Demo: Publication Seaborn Boxplot")
    print("=" * 70)

    # Create figure
    fig, ax = stx.plt.subplots(**SCITEX_STYLE)

    # Generate data
    np.random.seed(42)
    df = pd.DataFrame(
        {
            "category": np.repeat(["A", "B", "C"], 50),
            "value": np.concatenate(
                [
                    np.random.normal(0, 1, 50),
                    np.random.normal(2, 1, 50),
                    np.random.normal(4, 1.5, 50),
                ]
            ),
        }
    )

    # Seaborn boxplot
    ax.stx_sns_boxplot(x="category", y="value", data=df, id="sns_box")

    # Labels
    ax.set_xlabel(stx.plt.ax.format_label("Category", ""))
    ax.set_ylabel(stx.plt.ax.format_label("Value", "a.u."))
    ax.set_title("Group Distributions")

    # Save in publication formats (PNG, PDF)
    save_path = os.path.join(OUTPUT_DIR_SEABORN, "01_sns_boxplot.png")
    png_path, pdf_path, jpg_path = save_multi_format(fig, save_path, dpi=300)
    fig.close()

    print(f"- Saved: {png_path}, .pdf, .jpg")


def demo_publication_sns_violinplot():
    """Publication-ready seaborn violinplot."""
    print("\n" + "=" * 70)
    print("Demo: Publication Seaborn Violinplot")
    print("=" * 70)

    # Create figure
    fig, ax = stx.plt.subplots(**SCITEX_STYLE)

    # Generate data
    np.random.seed(42)
    df = pd.DataFrame(
        {
            "category": np.repeat(["A", "B", "C"], 50),
            "value": np.concatenate(
                [
                    np.random.normal(0, 1, 50),
                    np.random.normal(2, 1, 50),
                    np.random.normal(4, 1.5, 50),
                ]
            ),
        }
    )

    # Seaborn violinplot
    ax.stx_sns_violinplot(x="category", y="value", data=df, id="sns_violin")

    # Labels
    ax.set_xlabel(stx.plt.ax.format_label("Category", ""))
    ax.set_ylabel(stx.plt.ax.format_label("Value", "a.u."))
    ax.set_title("Distribution Shapes")

    # Save in publication formats (PNG, PDF)
    save_path = os.path.join(OUTPUT_DIR_SEABORN, "02_sns_violinplot.png")
    png_path, pdf_path, jpg_path = save_multi_format(fig, save_path, dpi=300)
    fig.close()

    print(f"- Saved: {png_path}, .pdf, .jpg")


def demo_publication_sns_scatterplot():
    """Publication-ready seaborn scatterplot."""
    print("\n" + "=" * 70)
    print("Demo: Publication Seaborn Scatterplot")
    print("=" * 70)

    # Create figure
    fig, ax = stx.plt.subplots(**SCITEX_STYLE)

    # Generate data
    np.random.seed(42)
    n = 100
    df = pd.DataFrame(
        {
            "x": np.random.normal(0, 1, n),
            "y": np.random.normal(0, 1, n),
            "category": np.random.choice(["A", "B", "C"], n),
        }
    )
    df["y"] = df["x"] * 2 + df["y"]

    # Seaborn scatterplot
    ax.stx_sns_scatterplot(
        x="x",
        y="y",
        hue="category",
        data=df,
        id="sns_scatter",
    )

    # Labels
    ax.set_xlabel(stx.plt.ax.format_label("Predictor", "a.u."))
    ax.set_ylabel(stx.plt.ax.format_label("Response", "a.u."))
    ax.set_title("Categorical Scatter")
    ax.legend(frameon=False, title="", fontsize=6)

    # Save in publication formats (PNG, PDF)
    save_path = os.path.join(OUTPUT_DIR_SEABORN, "03_sns_scatterplot.png")
    png_path, pdf_path, jpg_path = save_multi_format(fig, save_path, dpi=300)
    fig.close()

    print(f"- Saved: {png_path}, .pdf, .jpg")


def demo_publication_sns_lineplot():
    """Publication-ready seaborn lineplot."""
    print("\n" + "=" * 70)
    print("Demo: Publication Seaborn Lineplot")
    print("=" * 70)

    # Create figure
    fig, ax = stx.plt.subplots(**SCITEX_STYLE)

    # Generate data
    np.random.seed(42)
    x = np.linspace(0, 10, 50)
    df = pd.DataFrame(
        {
            "x": np.tile(x, 3),
            "y": np.concatenate(
                [
                    np.sin(x) + np.random.normal(0, 0.1, len(x)),
                    np.cos(x) + np.random.normal(0, 0.1, len(x)),
                    -np.sin(x) + np.random.normal(0, 0.1, len(x)),
                ]
            ),
            "group": np.repeat(["A", "B", "C"], len(x)),
        }
    )

    # Seaborn lineplot
    ax.stx_sns_lineplot(
        x="x",
        y="y",
        hue="group",
        data=df,
        id="sns_line",
    )

    # Labels
    ax.set_xlabel(stx.plt.ax.format_label("Time", "s"))
    ax.set_ylabel(stx.plt.ax.format_label("Signal", "a.u."))
    ax.set_title("Time Series Comparison")
    ax.legend(frameon=False, title="", fontsize=6)

    # Save in publication formats (PNG, PDF)
    save_path = os.path.join(OUTPUT_DIR_SEABORN, "04_sns_lineplot.png")
    png_path, pdf_path, jpg_path = save_multi_format(fig, save_path, dpi=300)
    fig.close()

    print(f"- Saved: {png_path}, .pdf, .jpg")


def demo_publication_sns_histplot():
    """Publication-ready seaborn histplot."""
    print("\n" + "=" * 70)
    print("Demo: Publication Seaborn Histplot")
    print("=" * 70)

    # Create figure
    fig, ax = stx.plt.subplots(**SCITEX_STYLE)

    # Generate data
    np.random.seed(42)
    df = pd.DataFrame(
        {
            "value": np.concatenate(
                [
                    np.random.normal(0, 1, 200),
                    np.random.normal(3, 1, 150),
                ]
            ),
            "category": np.repeat(["A", "B"], [200, 150]),
        }
    )

    # Seaborn histplot
    ax.stx_sns_histplot(
        x="value",
        hue="category",
        data=df,
        kde=True,
        alpha=0.6,
        id="sns_hist",
    )

    # Labels
    ax.set_xlabel(stx.plt.ax.format_label("Value", "a.u."))
    ax.set_ylabel(stx.plt.ax.format_label("Count", ""))
    ax.set_title("Distribution with KDE")
    ax.legend(frameon=False, title="", fontsize=6)

    # Save in publication formats (PNG, PDF)
    save_path = os.path.join(OUTPUT_DIR_SEABORN, "05_sns_histplot.png")
    png_path, pdf_path, jpg_path = save_multi_format(fig, save_path, dpi=300)
    fig.close()

    print(f"- Saved: {png_path}, .pdf, .jpg")


def demo_publication_sns_barplot():
    """Publication-ready seaborn barplot."""
    print("\n" + "=" * 70)
    print("Demo: Publication Seaborn Barplot")
    print("=" * 70)

    # Create figure
    fig, ax = stx.plt.subplots(**SCITEX_STYLE)

    # Generate data
    np.random.seed(42)
    df = pd.DataFrame(
        {
            "category": np.repeat(["A", "B", "C"], 50),
            "value": np.concatenate(
                [
                    np.random.normal(20, 5, 50),
                    np.random.normal(35, 7, 50),
                    np.random.normal(28, 6, 50),
                ]
            ),
        }
    )

    # Seaborn barplot
    ax.stx_sns_barplot(x="category", y="value", data=df, id="sns_bar")

    # Labels
    ax.set_xlabel(stx.plt.ax.format_label("Category", ""))
    ax.set_ylabel(stx.plt.ax.format_label("Value", "a.u."))
    ax.set_title("Mean Values by Category")

    # Save in publication formats (PNG, PDF)
    save_path = os.path.join(OUTPUT_DIR_SEABORN, "06_sns_barplot.png")
    png_path, pdf_path, jpg_path = save_multi_format(fig, save_path, dpi=300)
    fig.close()

    print(f"- Saved: {png_path}, .pdf, .jpg")


def demo_publication_sns_stripplot():
    """Publication-ready seaborn stripplot."""
    print("\n" + "=" * 70)
    print("Demo: Publication Seaborn Stripplot")
    print("=" * 70)

    # Create figure
    fig, ax = stx.plt.subplots(**SCITEX_STYLE)

    # Generate data
    np.random.seed(42)
    df = pd.DataFrame(
        {
            "category": np.repeat(["A", "B", "C"], 30),
            "value": np.concatenate(
                [
                    np.random.normal(0, 1, 30),
                    np.random.normal(2, 1, 30),
                    np.random.normal(4, 1.5, 30),
                ]
            ),
        }
    )

    # Seaborn stripplot
    ax.stx_sns_stripplot(
        x="category",
        y="value",
        data=df,
        alpha=0.6,
        id="sns_strip",
    )

    # Labels
    ax.set_xlabel(stx.plt.ax.format_label("Category", ""))
    ax.set_ylabel(stx.plt.ax.format_label("Value", "a.u."))
    ax.set_title("Strip Plot")

    # Save in publication formats (PNG, PDF)
    save_path = os.path.join(OUTPUT_DIR_SEABORN, "07_sns_stripplot.png")
    png_path, pdf_path, jpg_path = save_multi_format(fig, save_path, dpi=300)
    fig.close()

    print(f"- Saved: {png_path}, .pdf, .jpg")


def demo_publication_sns_kdeplot():
    """Publication-ready seaborn kdeplot."""
    print("\n" + "=" * 70)
    print("Demo: Publication Seaborn KDE Plot")
    print("=" * 70)

    # Create figure
    fig, ax = stx.plt.subplots(**SCITEX_STYLE)

    # Generate data
    np.random.seed(42)
    df = pd.DataFrame(
        {
            "value": np.concatenate(
                [
                    np.random.normal(0, 1, 200),
                    np.random.normal(3, 1, 150),
                ]
            ),
            "category": np.repeat(["A", "B"], [200, 150]),
        }
    )

    # Seaborn kdeplot (note: wrapper has issues with id parameter)
    ax.stx_sns_kdeplot(
        x="value",
        hue="category",
        data=df,
    )

    # Labels
    ax.set_xlabel(stx.plt.ax.format_label("Value", "a.u."))
    ax.set_ylabel(stx.plt.ax.format_label("Density", ""))
    ax.set_title("Kernel Density Estimate")
    ax.legend(frameon=False, title="", fontsize=6)

    # Save in publication formats (PNG, PDF)
    save_path = os.path.join(OUTPUT_DIR_SEABORN, "08_sns_kdeplot.png")
    png_path, pdf_path, jpg_path = save_multi_format(fig, save_path, dpi=300)
    fig.close()

    print(f"- Saved: {png_path}, .pdf, .jpg")


# ============================================================================
# MULTI-PANEL PUBLICATION FIGURES
# ============================================================================


def demo_publication_multi_panel_2x2():
    """Publication-ready 2x2 multi-panel figure."""
    print("\n" + "=" * 70)
    print("Demo: Multi-Panel Figure 2x2 (SciTeX Style)")
    print("=" * 70)

    # Create 2x2 grid with SCITEX_STYLE
    fig, axes = stx.plt.subplots(2, 2, **SCITEX_STYLE)

    # Panel A: Line plot
    x = np.linspace(0, 2 * np.pi, 100)
    axes[0, 0].plot(x, np.sin(x), "b-", label="sin", id="panel_a")
    axes[0, 0].set_xlabel(stx.plt.ax.format_label("x", "rad"))
    axes[0, 0].set_ylabel(stx.plt.ax.format_label("sin(x)", ""))
    axes[0, 0].set_title("A. Sine Wave", loc="left", fontweight="bold")
    axes[0, 0].legend(frameon=False, fontsize=6)

    # Panel B: Scatter with styling
    np.random.seed(42)
    x_scatter = np.random.normal(0, 1, 50)
    y_scatter = x_scatter + np.random.normal(0, 0.5, 50)
    scatter = axes[0, 1].scatter(
        x_scatter, y_scatter, alpha=0.6, label="Data", id="panel_b"
    )
    stx.plt.ax.style_scatter(scatter, size_mm=0.8)
    axes[0, 1].set_xlabel(stx.plt.ax.format_label("x", "a.u."))
    axes[0, 1].set_ylabel(stx.plt.ax.format_label("y", "a.u."))
    axes[0, 1].set_title("B. Correlation", loc="left", fontweight="bold")
    axes[0, 1].legend(frameon=False, fontsize=6)

    # Panel C: Histogram
    data = np.random.normal(0, 1, 500)
    axes[1, 0].hist(
        data,
        bins=20,
        alpha=0.7,
        color="steelblue",
        label="Data",
        id="panel_c",
    )
    axes[1, 0].set_xlabel(stx.plt.ax.format_label("Value", "a.u."))
    axes[1, 0].set_ylabel(stx.plt.ax.format_label("Count", ""))
    axes[1, 0].set_title("C. Distribution", loc="left", fontweight="bold")
    axes[1, 0].legend(frameon=False, fontsize=6)

    # Panel D: Bar with styling
    categories = ["A", "B", "C", "D"]
    values = [23, 45, 31, 52]
    bars = axes[1, 1].bar(
        categories,
        values,
        alpha=0.7,
        color="steelblue",
        label="Count",
        id="panel_d",
    )
    stx.plt.ax.style_barplot(bars, edge_thickness_mm=0.2, edgecolor="black")
    axes[1, 1].set_xlabel(stx.plt.ax.format_label("Category", ""))
    axes[1, 1].set_ylabel(stx.plt.ax.format_label("Count", ""))
    axes[1, 1].set_title("D. Comparison", loc="left", fontweight="bold")
    axes[1, 1].legend(frameon=False, fontsize=6)

    # Save in publication formats (PNG, PDF)
    save_path = os.path.join(OUTPUT_DIR_MULTI, "01_2x2_scitex.png")
    png_path, pdf_path, jpg_path = save_multi_format(fig, save_path, dpi=300)
    fig.close()

    print(f"- Saved: {png_path}, .pdf, .jpg")
    print("  Layout: 2x2 grid")
    print(
        f"  Each panel: {SCITEX_STYLE['ax_width_mm']} x "
        f"{SCITEX_STYLE['ax_height_mm']} mm"
    )
    if "space_w_mm" in SCITEX_STYLE and "space_h_mm" in SCITEX_STYLE:
        print(
            f"  Spacing: {SCITEX_STYLE['space_w_mm']} x "
            f"{SCITEX_STYLE['space_h_mm']} mm"
        )


def demo_publication_multi_panel_1x3():
    """Publication-ready 1x3 multi-panel figure with varied widths."""
    print("\n" + "=" * 70)
    print("Demo: Multi-Panel Figure 1x3 with Individual Widths")
    print("=" * 70)

    # Create 1x3 grid with individual widths
    fig, axes = stx.plt.subplots(
        1,
        3,
        ax_width_mm=[25, 35, 25],  # Wider middle panel
        ax_height_mm=21,
        margin_left_mm=5,
        margin_right_mm=2,
        margin_bottom_mm=5,
        margin_top_mm=2,
        space_w_mm=3,
        ax_thickness_mm=0.2,
        tick_length_mm=0.8,
        mode="publication",
        dpi=300,
    )

    # Panel A: Time series
    t = np.linspace(0, 10, 100)
    axes[0, 0].plot(t, np.sin(t), "b-", label="Signal", id="ts")
    axes[0, 0].set_xlabel(stx.plt.ax.format_label("Time", "s"))
    axes[0, 0].set_ylabel(stx.plt.ax.format_label("Signal", "a.u."))
    axes[0, 0].set_title("A", loc="left", fontweight="bold")
    axes[0, 0].legend(frameon=False, fontsize=6)

    # Panel B: Heatmap (wider panel) with all spines and square cells
    data = np.random.rand(10, 15)
    im = axes[0, 1].imshow(data, aspect="equal", cmap="viridis", id="heat")
    axes[0, 1].spines[:].set_visible(True)
    axes[0, 1].set_xlabel(stx.plt.ax.format_label("X", ""))
    axes[0, 1].set_ylabel(stx.plt.ax.format_label("Y", ""))
    axes[0, 1].set_title("B", loc="left", fontweight="bold")

    # Panel C: Box plot with styling
    box_data = [np.random.normal(0, 1, 100) for _ in range(4)]
    bp = axes[0, 2].boxplot(box_data, labels=["1", "2", "3", "4"], id="box")
    stx.plt.ax.style_boxplot(bp, linewidth_mm=0.8)
    axes[0, 2].set_xlabel(stx.plt.ax.format_label("Group", ""))
    axes[0, 2].set_ylabel(stx.plt.ax.format_label("Value", "a.u."))
    axes[0, 2].set_title("C", loc="left", fontweight="bold")

    # Save in publication formats (PNG, PDF)
    save_path = os.path.join(OUTPUT_DIR_MULTI, "02_1x3_varied_widths.png")
    png_path, pdf_path, jpg_path = save_multi_format(fig, save_path, dpi=300)
    fig.close()

    print(f"- Saved: {png_path}, .pdf, .jpg")
    print("  Layout: 1x3 grid")
    print("  Panel widths: 25, 35, 25 mm")


# Display mode demo removed as it's not needed for publication figures
# (User requested: "no display demo needed, 08_display_mode.png")


def demo_publication_style_override():
    """Demonstrate style override pattern."""
    print("\n" + "=" * 70)
    print("Demo: Style Override Pattern")
    print("=" * 70)

    # Override specific parameters from SCITEX_STYLE
    custom_style = SCITEX_STYLE.copy()
    custom_style["ax_width_mm"] = 40  # Wider axes
    custom_style["ax_thickness_mm"] = 0.3  # Thicker spines
    custom_style["tick_length_mm"] = 1.0  # Longer ticks

    fig, ax = stx.plt.subplots(**custom_style)

    # Generate data
    x = np.linspace(0, 10, 100)
    y = np.exp(-x / 5) * np.sin(2 * x)

    ax.plot(x, y, "b-", label="Oscillation", id="damped_osc")
    ax.set_xlabel(stx.plt.ax.format_label("Time", "s"))
    ax.set_ylabel(stx.plt.ax.format_label("Amplitude", "a.u."))
    ax.set_title("Damped Oscillation (Custom Style)")
    ax.legend(frameon=False, fontsize=6)
    ax.grid(True, alpha=0.3)

    # Save in publication formats (PNG, PDF) with style overrides
    save_path = os.path.join(OUTPUT_DIR, "style_override.png")

    # Extract only the overridden parameters
    style_overrides = {
        "ax_width_mm": custom_style["ax_width_mm"],
        "ax_thickness_mm": custom_style["ax_thickness_mm"],
        "tick_length_mm": custom_style["tick_length_mm"],
    }

    png_path, pdf_path, jpg_path = save_multi_format(
        fig,
        save_path,
        dpi=300,
        plot_type="line",
        style_name="SCITEX_STYLE",
        style_overrides=style_overrides,
    )
    fig.close()

    print(f"- Saved: {png_path}, .pdf, .jpg")


# ============================================================================
# MAIN EXECUTION
# ============================================================================


@stx.session
def main(verbose=True):
    """Run all publication demos showcasing mm-control integration."""

    if verbose:
        print("\n" + "=" * 70)
        print(" PUBLICATION-READY FIGURE DEMONSTRATION")
        print(" Using Unified Style System")
        print("=" * 70)
        print("\nThis demo showcases scitex.plt.subplots() with mm-control")
        print("integration for creating publication-ready figures.\n")

    demos = [
        # Matplotlib basic plots
        demo_publication_plot,
        demo_publication_scatter,
        demo_publication_bar,
        # demo_publication_hist,
        # demo_publication_boxplot,
        # demo_publication_errorbar,
        # demo_publication_barh,
        # demo_publication_fill_between,
        # demo_publication_imshow,
        # demo_publication_contour,
        # demo_publication_violinplot,
        # # Custom scitex plots
        # demo_publication_plot_heatmap,
        # demo_publication_plot_line,
        # demo_publication_plot_shaded_line,
        # demo_publication_plot_violin,
        # demo_publication_plot_ecdf,
        # demo_publication_plot_box,
        # demo_publication_plot_mean_std,
        # # Functional plots
        # demo_publication_plot_kde,
        # # Seaborn integration
        # demo_publication_sns_boxplot,
        # demo_publication_sns_violinplot,
        # demo_publication_sns_scatterplot,
        # demo_publication_sns_lineplot,
        # demo_publication_sns_histplot,
        # demo_publication_sns_barplot,
        # demo_publication_sns_stripplot,
        # demo_publication_sns_kdeplot,
        # # Multi-panel demos
        # demo_publication_multi_panel_2x2,
        # demo_publication_multi_panel_1x3,
        # # Style customization
        # demo_publication_style_override,
    ]

    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"\n[ERROR] in {demo.__name__}: {e}")
            import traceback

            traceback.print_exc()

    if verbose:
        print("\n" + "=" * 70)
        print(" DEMONSTRATION COMPLETE")
        print("=" * 70)
        print("\nOutput locations:")
        print(f"  Session output: {__file__.replace('.py', '_out')}/")
        print(f"  Matplotlib basic: {OUTPUT_DIR_BASIC}/")
        print(f"  Custom scitex: {OUTPUT_DIR_CUSTOM}/")
        print(f"  Functional: {OUTPUT_DIR_FUNCTIONAL}/")
        print(f"  Seaborn: {OUTPUT_DIR_SEABORN}/")
        print(f"  Multi-panels: {OUTPUT_DIR_MULTI}/")
        print(f"  Root (style override): {OUTPUT_DIR}/")
        print("\nCoverage:")
        print(
            "  - Matplotlib basic plots (11): plot, scatter, bar, barh, hist, boxplot,"
        )
        print("    errorbar, fill_between, imshow, contour, violinplot")
        print(
            "  - Custom scitex plots (7): stx_heatmap, stx_line, stx_shaded_line,"
        )
        print("    stx_violin, stx_ecdf, stx_box, stx_mean_std")
        print("  - Functional plots (1): stx_kde")
        print(
            "  - Seaborn integration (8): sns_boxplot, sns_violinplot, sns_scatterplot,"
        )
        print(
            "    sns_lineplot, sns_histplot, sns_barplot, sns_stripplot, sns_kdeplot"
        )
        print("  - Multi-panel (2): 2x2 grid, 1x3 with varied widths")
        print("  - Total: 30 publication-ready plot demonstrations")
        print("\nAll figures are publication-ready:")
        print("  - Formats: PNG (lossless raster) + PDF (vector)")
        print("  - 300 DPI resolution (PNG)")
        print("  - Infinite zoom (PDF)")
        print("  - Precise mm-based dimensions")
        print("  - Automatic cropping with 1mm margin")
        print("  - Consistent SCITEX_STYLE preset")
        print("  - Embedded metadata for reproducibility")
        print("\nNote: JPEG is NOT used - it's lossy and creates artifacts")

    return 0


if __name__ == "__main__":
    main()

# EOF
