#!/usr/bin/env python3
# Time-stamp: "2024-11-25 23:40:12 (ywatanabe)"
# File: ./scitex_repo/src/scitex/gen/_to_even.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/gen/_to_even.py"


def to_even(n):
    """Convert a number to the nearest even number less than or equal to itself.

    Parameters
    ----------
    n : int or float
        The input number to be converted.

    Returns
    -------
    int
        The nearest even number less than or equal to the input.

    Example
    -------
    >>> to_even(5)
    4
    >>> to_even(6)
    6
    >>> to_even(3.7)
    2
    >>> to_even(-2.3)
    -4
    >>> to_even(-0.1)
    -2
    """
    import math

    # Handle integers directly to avoid float conversion issues with large numbers
    # Note: bool is a subclass of int, so we need to exclude it
    if isinstance(n, int) and not isinstance(n, bool):
        if n % 2 == 0:
            return int(n)  # Ensure we return int, not bool
        else:
            return int(n - 1)  # Ensure we return int, not bool

    # Handle special float values
    if isinstance(n, float):
        if math.isnan(n):
            raise ValueError("Cannot convert NaN to even")
        if math.isinf(n):
            raise OverflowError("Cannot convert infinity to even")
        # Python can actually convert sys.float_info.max to int, so we don't need this check
        # Only infinity truly can't be converted

    # Try to handle custom objects with __int__ (but not float types)
    if hasattr(n, "__int__") and not isinstance(n, (float, bool)):
        try:
            n_int = int(n)
            if n_int % 2 == 0:
                return int(n_int)
            else:
                return int(n_int - 1)
        except:
            pass

    # Check for string type explicitly - raise TypeError
    if isinstance(n, str):
        raise TypeError(f"must be real number, not {type(n).__name__}")

    # Convert to float for all other cases. Handle 0-d numpy arrays / torch
    # tensors via .item() before float() — float(ndarray) on numpy 2+ raises
    # for non-0-dim, masking the underlying type.
    try:
        if hasattr(n, "item"):
            n_float = float(n.item())
        else:
            n_float = float(n)
    except (TypeError, ValueError):
        raise TypeError(f"must be real number, not {type(n).__name__}")

    # Use floor for float values
    floored = int(math.floor(n_float))

    # If odd, subtract 1 to get the next lower even number
    if floored % 2 != 0:
        return int(floored - 1)  # Ensure we return int, not bool
    return int(floored)  # Ensure we return int, not bool


# EOF
