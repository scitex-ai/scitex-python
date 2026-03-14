PD Module (``stx.pd``)
======================

Pandas DataFrame helper functions for common transformations.

Quick Reference
---------------

.. code-block:: python

    import scitex as stx
    import pandas as pd

    df = pd.DataFrame({
        "subject": ["A", "A", "B", "B"],
        "condition": ["ctrl", "exp", "ctrl", "exp"],
        "score": [10, 15, 12, 18],
    })

    # Find individual (unique) values
    subjects = stx.pd.find_indi(df, "subject")

    # Convert to long format
    melted = stx.pd.melt_cols(df, id_vars=["subject"])

    # Merge columns
    merged = stx.pd.merge_cols(df, cols=["subject", "condition"], sep="_")

    # Force to DataFrame
    stx.pd.force_df({"a": [1, 2], "b": [3, 4]})

Available Functions
-------------------

- ``find_indi(df, col)`` -- Find unique individual identifiers
- ``find_pval(df)`` -- Find p-value columns in a DataFrame
- ``force_df(data)`` -- Convert any data to a DataFrame
- ``melt_cols(df, id_vars)`` -- Melt columns to long format
- ``merge_cols(df, cols, sep)`` -- Merge multiple columns into one
- ``to_xyz(df, x, y, z)`` -- Reshape to x, y, z pivot format

API Reference
-------------

.. automodule:: scitex.pd
   :members:
