#!/usr/bin/env python3
# Timestamp: 2025-12-19
# File: /home/ywatanabe/proj/scitex-code/src/scitex/io/_save_modules/_legends.py

"""Save separate legend files if ax.legend('separate') was used."""

import os

from scitex.path import getsize
from scitex.str._color_text import color_text
from scitex.str._readable_bytes import readable_bytes

# Optional: plotly-dependent save_image
try:
    from ._image import save_image
except ImportError:
    save_image = None


def save_separate_legends(obj, spath, symlink_from_cwd=False, dry_run=False, **kwargs):
    """Save separate legend files if ax.legend('separate') was used."""
    if dry_run:
        return

    import matplotlib.figure
    import matplotlib.pyplot as plt

    # Get the matplotlib figure object
    fig = None
    if isinstance(obj, matplotlib.figure.Figure):
        fig = obj
    elif hasattr(obj, "_fig_mpl"):
        fig = obj._fig_mpl
    elif hasattr(obj, "figure"):
        if isinstance(obj.figure, matplotlib.figure.Figure):
            fig = obj.figure
        elif hasattr(obj.figure, "_fig_mpl"):
            fig = obj.figure._fig_mpl

    if fig is None:
        return

    # Check if there are separate legend parameters stored
    if not hasattr(fig, "_separate_legend_params"):
        return

    # Save each legend as a separate file
    base_path = os.path.splitext(spath)[0]
    ext = os.path.splitext(spath)[1]

    for legend_params in fig._separate_legend_params:
        # Create a new figure for the legend
        legend_fig = plt.figure(figsize=legend_params["figsize"])
        legend_ax = legend_fig.add_subplot(111)

        # Create the legend
        legend = legend_ax.legend(
            legend_params["handles"],
            legend_params["labels"],
            loc="center",
            frameon=legend_params["frameon"],
            fancybox=legend_params["fancybox"],
            shadow=legend_params["shadow"],
            **legend_params["kwargs"],
        )

        # Remove axes
        legend_ax.axis("off")

        # Adjust layout to fit the legend
        legend_fig.tight_layout()

        # Save the legend figure
        legend_filename = f"{base_path}_{legend_params['axis_id']}_legend{ext}"
        save_image(legend_fig, legend_filename, **kwargs)

        # Close the legend figure to free memory
        plt.close(legend_fig)

        if not dry_run and os.path.exists(legend_filename):
            file_size = getsize(legend_filename)
            file_size = readable_bytes(file_size)
            print(
                color_text(
                    f"\nSaved legend to: {legend_filename} ({file_size})",
                    c="yellow",
                )
            )


# EOF
