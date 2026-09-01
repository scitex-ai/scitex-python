IO Module (``stx.io``)
======================

Universal file I/O through ``stx.io.save()`` and ``stx.io.load()``.
Format is determined by file extension.

Quick Reference
---------------

.. code-block:: python

    import scitex as stx

    # Save
    stx.io.save(data, "output.csv")       # DataFrame → CSV
    stx.io.save(arr, "output.npy")        # ndarray → NumPy
    stx.io.save(fig, "output.png")        # Figure → PNG + CSV + YAML recipe
    stx.io.save(obj, "output.pkl")        # any object → pickle
    stx.io.save(d, "output.yaml")         # dict → YAML
    stx.io.save(d, "output.json")         # dict → JSON

    # Load
    data = stx.io.load("input.csv")       # → DataFrame
    arr = stx.io.load("input.npy")        # → ndarray
    obj = stx.io.load("input.pkl")        # → original object
    d = stx.io.load("input.yaml")         # → dict

Supported Formats
-----------------

.. list-table::
   :header-rows: 1

   * - Extension
     - Save Type
     - Load Return
   * - ``.csv``
     - DataFrame, dict, ndarray
     - DataFrame
   * - ``.npy``
     - ndarray
     - ndarray
   * - ``.npz``
     - dict of ndarrays
     - NpzFile
   * - ``.pkl`` / ``.pickle``
     - any Python object
     - original object
   * - ``.yaml`` / ``.yml``
     - dict
     - dict
   * - ``.json``
     - dict, list
     - dict or list
   * - ``.png`` / ``.jpg`` / ``.svg`` / ``.pdf`` / ``.tiff``
     - matplotlib Figure
     - ndarray (image) or Figure
   * - ``.hdf5`` / ``.h5``
     - dict, ndarray
     - dict or ndarray
   * - ``.mat``
     - dict
     - dict
   * - ``.pth`` / ``.pt``
     - PyTorch state_dict
     - dict
   * - ``.parquet``
     - DataFrame
     - DataFrame
   * - ``.txt``
     - str
     - str

Figure Saving
-------------

When saving a matplotlib Figure, ``stx.io.save`` automatically:

1. Saves the image file (``.png``, ``.svg``, etc.)
2. Exports a ``.csv`` with the plotted data extracted from axes
3. Exports a ``.yaml`` recipe for reproducing the figure

.. code-block:: python

    fig, ax = stx.plt.subplots()
    ax.plot_line(x, y, label="signal")
    stx.io.save(fig, "results/plot.png")
    # Creates:
    #   results/plot.png       (the figure)
    #   results/plot.csv       (x, y data)
    #   results/plot.yaml      (recipe for stx.plt.reproduce)

Provenance Tracking
-------------------

Inside ``@stx.session``, every ``save`` and ``load`` records file hashes
to a local provenance database for reproducibility verification.

.. code-block:: python

    @stx.session
    def main(logger=stx.INJECTED, **kw):
        data = stx.io.load("input.csv")    # hash recorded as input
        stx.io.save(result, "output.csv")   # hash recorded as output

Other Functions
---------------

- ``stx.io.glob(pattern)`` -- Find files matching a glob pattern
- ``stx.io.load_configs(config_dir)`` -- Load and merge YAML config files

API Reference
-------------

See :doc:`/api/scitex.io` for the auto-generated Python API.
