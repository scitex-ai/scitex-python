#!/usr/bin/env python3
# Time-stamp: "2025-06-05 12:00:00 (ywatanabe)"
# File: ./src/scitex/tex/_to_vec.py

"""
LaTeX vector notation with fallback mechanisms.

Functionality:
    - Convert strings to LaTeX vector notation with automatic fallback
    - Handle LaTeX rendering failures gracefully
Input:
    String representation of vector
Output:
    LaTeX vector notation with fallback support
Prerequisites:
    scitex.str._latex_fallback
"""

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
def to_vec(v_str, enable_fallback=True, fallback_strategy="auto"):
    r"""
    Convert a string to LaTeX vector notation with automatic fallback.

    Parameters
    ----------
    v_str : str
        String representation of the vector
    enable_fallback : bool, optional
        Whether to enable LaTeX fallback mechanisms, by default True
    fallback_strategy : str, optional
        Fallback strategy: "auto", "mathtext", "unicode", "plain", by default "auto"

    Returns
    -------
    str
        LaTeX representation of the vector with automatic fallback

    Examples
    --------
    >>> vector = to_vec("AB")
    >>> print(vector)  # LaTeX: \overrightarrow{\mathrm{AB}}

    >>> vector = to_vec("AB")  # Falls back to unicode if LaTeX fails
    >>> print(vector)  # Unicode: A⃗B or AB⃗

    Notes
    -----
    If LaTeX rendering fails, this function automatically falls back to:
    - mathtext: Uses matplotlib's built-in math rendering
    - unicode: Uses Unicode vector symbols (⃗)
    - plain: Returns plain text with "vec()" notation
    """
    if not v_str:
        return ""

    # Create LaTeX vector notation
    latex_vector = f"\\overrightarrow{{\\mathrm{{{v_str}}}}}"

    if enable_fallback and FALLBACK_AVAILABLE:
        # Custom fallback handling for vectors
        if fallback_strategy == "auto":
            # Try mathtext first, then unicode
            try:
                mathtext_result = safe_latex_render(f"${latex_vector}$", "mathtext")
                return mathtext_result
            except Exception:
                # Fall back to unicode vector notation
                return f"{v_str}⃗"  # Unicode combining right arrow above
        elif fallback_strategy == "unicode":
            return f"{v_str}⃗"  # Unicode combining right arrow above
        elif fallback_strategy == "plain":
            return f"vec({v_str})"
        else:
            return safe_latex_render(f"${latex_vector}$", fallback_strategy)
    else:
        return latex_vector


def safe_to_vec(v_str, fallback_strategy="auto"):
    """
    Safe version of to_vec with explicit fallback control.

    Parameters
    ----------
    v_str : str
        String representation of the vector
    fallback_strategy : str, optional
        Explicit fallback strategy: "auto", "mathtext", "unicode", "plain"

    Returns
    -------
    str
        Vector notation with specified fallback behavior
    """
    return to_vec(v_str, enable_fallback=True, fallback_strategy=fallback_strategy)


# Backward compatibility
vector_notation = to_vec

# EOF
