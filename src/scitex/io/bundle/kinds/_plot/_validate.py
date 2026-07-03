#!/usr/bin/env python3
# Timestamp: 2026-05-28
# File: src/scitex/io/bundle/kinds/_plot/_validate.py

"""Umbrella-internal validator for .plot bundle specs.

figrecipe owns figure I/O but exposes no spec validator; this is the umbrella's
minimal stub, kept here so callers in `scitex.io.bundle` remain self-contained.
"""

from typing import Any, Dict, List

__all__ = ["validate_plot_spec"]


def validate_plot_spec(spec: Dict[str, Any]) -> List[str]:
    """Validate `.plot`-specific fields.

    Parameters
    ----------
    spec : dict
        The specification dictionary to validate.

    Returns
    -------
    list of str
        Validation error messages (empty if valid).
    """
    errors: List[str] = []

    axes = spec.get("axes")
    if axes is not None and not isinstance(axes, (dict, list)):
        errors.append("'axes' must be a dictionary or list")

    return errors


# EOF
