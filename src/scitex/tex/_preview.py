#!/usr/bin/env python3
# Time-stamp: "2025-06-05 12:00:00 (ywatanabe)"
# File: ./src/scitex/tex/_preview.py

"""
LaTeX preview functionality with fallback mechanisms.

Functionality:
    - Generate previews of LaTeX strings with automatic fallback
    - Handle LaTeX rendering failures gracefully
Input:
    List of LaTeX strings
Output:
    Matplotlib figure with previews
Prerequisites:
    matplotlib, numpy, scitex.plt, scitex.str._latex_fallback
"""

import numpy as np

try:
    from scitex.str import latex_fallback_decorator, safe_latex_render

    FALLBACK_AVAILABLE = True
except ImportError:
    FALLBACK_AVAILABLE = False

    def latex_fallback_decorator(fallback_strategy="auto", preserve_math=True):
        def decorator(func):
            return func

        return decorator

    def safe_latex_render(text, fallback_strategy="auto", preserve_math=True):
        return text


@latex_fallback_decorator(fallback_strategy="auto", preserve_math=True)
def preview(tex_str_list, enable_fallback=True):
    r"""
    Generate a preview of LaTeX strings with automatic fallback.

    Parameters
    ----------
    tex_str_list : list of str
        List of LaTeX strings to preview
    enable_fallback : bool, optional
        Whether to enable LaTeX fallback mechanisms, by default True

    Returns
    -------
    matplotlib.figure.Figure
        Figure containing the previews

    Examples
    --------
    >>> tex_strings = ["x^2", r"\sum_{i=1}^n i", r"\alpha + \beta"]
    >>> fig = preview(tex_strings)
    >>> scitex.plt.show()

    Notes
    -----
    If LaTeX rendering fails, this function automatically falls back to
    mathtext or unicode alternatives while preserving the preview layout.
    """
    from scitex.plt import subplots

    if not isinstance(tex_str_list, (list, tuple)):
        tex_str_list = [tex_str_list]

    fig, axes = subplots(
        nrows=len(tex_str_list), ncols=1, figsize=(10, 3 * len(tex_str_list))
    )
    axes = np.atleast_1d(axes)

    for ax, tex_string in zip(axes, tex_str_list):
        try:
            # Original LaTeX string (raw)
            if enable_fallback and FALLBACK_AVAILABLE:
                safe_raw = safe_latex_render(tex_string, "unicode", preserve_math=False)
                ax.text(0.5, 0.7, safe_raw, size=20, ha="center", va="center")
            else:
                ax.text(0.5, 0.7, tex_string, size=20, ha="center", va="center")

            # LaTeX-formatted string
            latex_formatted = (
                f"${tex_string}$"
                if not (tex_string.startswith("$") and tex_string.endswith("$"))
                else tex_string
            )

            if enable_fallback and FALLBACK_AVAILABLE:
                safe_latex = safe_latex_render(latex_formatted, preserve_math=True)
                ax.text(0.5, 0.3, safe_latex, size=20, ha="center", va="center")
            else:
                ax.text(0.5, 0.3, latex_formatted, size=20, ha="center", va="center")

        except Exception as e:
            # Fallback for individual preview failures
            ax.text(0.5, 0.7, f"Raw: {tex_string}", size=16, ha="center", va="center")
            ax.text(
                0.5,
                0.3,
                f"Error: {str(e)[:50]}...",
                size=12,
                ha="center",
                va="center",
                color="red",
            )

        ax.hide_spines()

    fig.tight_layout()
    return fig


# EOF
