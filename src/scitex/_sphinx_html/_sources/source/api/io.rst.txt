I/O Module (``stx.io``)
========================

Unified file I/O for 30+ scientific data formats. A single ``save()``
and ``load()`` interface handles format detection by file extension,
so you never need to remember which library reads ``.npy`` vs ``.h5``
vs ``.parquet``.

.. note::

   Core format handlers are provided by the standalone
   `scitex-io <https://github.com/ywatanabe1989/scitex-io>`_ package.
   ``stx.io`` adds integration with ``stx.session`` (provenance tracking),
   ``stx.clew`` (claim verification), and automatic CSV export for figures.

Supported Formats
-----------------

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Category
     - Extensions
   * - **Tabular**
     - ``.csv``, ``.tsv``, ``.xlsx``, ``.xls``, ``.parquet``, ``.feather``
   * - **Array**
     - ``.npy``, ``.npz``, ``.mat``, ``.zarr``, ``.h5`` / ``.hdf5``
   * - **Config**
     - ``.yaml``, ``.yml``, ``.json``, ``.toml``, ``.ini``, ``.conf``
   * - **Figure**
     - ``.png``, ``.jpg``, ``.jpeg``, ``.svg``, ``.pdf``, ``.tiff``
   * - **Text**
     - ``.txt``, ``.log``, ``.md``, ``.rst``
   * - **Audio**
     - ``.wav``, ``.mp3``, ``.flac``
   * - **Serialized**
     - ``.pkl``, ``.pickle``, ``.joblib``
   * - **Bibliography**
     - ``.bib``

Quick Start
-----------

.. code-block:: python

   import scitex as stx
   import pandas as pd
   import numpy as np

   # --- Save and load a DataFrame ---
   df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
   stx.io.save(df, "results.csv")
   df_loaded = stx.io.load("results.csv")

   # --- Save and load a NumPy array ---
   arr = np.random.randn(100, 3)
   stx.io.save(arr, "data.npy")
   arr_loaded = stx.io.load("data.npy")

   # --- Save a figure (PNG + CSV data export) ---
   fig, ax = stx.plt.subplots()
   ax.stx_line([1, 2, 3, 4, 5], id="my_data")
   stx.io.save(fig, "plot.png")
   # Creates: plot.png, plot.csv, plot.yaml

Key Functions
-------------

``save(obj, path, **kwargs)``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Save any supported object to a file. The format is determined by the
file extension. Built-in features beyond simple save:

- **Auto directory creation** -- no ``os.makedirs()`` needed
- **Path resolution** -- relative paths resolve to ``<script_name>_out/<path>``
- **Symlinks** -- ``symlink_from_cwd=True`` for short access paths
- **Save logging** -- prints file path and size on success
- **Clew hash tracking** -- file hashes recorded automatically for verification
- **Figure CSV export** -- saves plot data alongside image files

.. code-block:: python

   # Format detected from extension
   stx.io.save(fig, "figure.pdf")       # Also exports CSV + YAML recipe
   stx.io.save(df, "output.parquet")    # DataFrame
   stx.io.save({"lr": 0.001}, "config.yaml")  # Dict
   stx.io.save(arr, "weights.npy")      # NumPy array

   # Symlink for convenient access
   stx.io.save(df, "results/data.csv", symlink_from_cwd=True)

``load(path)``
^^^^^^^^^^^^^^

Load data from a file. Returns the appropriate Python object
(DataFrame, ndarray, dict, etc.).

.. code-block:: python

   df = stx.io.load("results.csv")          # -> pd.DataFrame
   arr = stx.io.load("weights.npy")         # -> np.ndarray
   cfg = stx.io.load("config.yaml")         # -> dict
   data = stx.io.load("experiment.h5")      # -> dict of arrays

``load_configs(pattern="./config/*.yaml")``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Load and merge multiple YAML configuration files into a single
``DotDict``. Used internally by ``@stx.session`` to build the
``CONFIG`` object.

.. code-block:: python

   CONF = stx.io.load_configs("./config/*.yaml")
   print(CONF.MODEL.hidden_size)

``list_formats()``
^^^^^^^^^^^^^^^^^^

List all registered format handlers.

.. code-block:: python

   fmts = stx.io.list_formats()
   # ['.csv', '.h5', '.hdf5', '.json', '.mat', '.npy', ...]

HDF5 and Zarr Exploration
-------------------------

For hierarchical formats, use the explorer interface:

.. code-block:: python

   # HDF5
   stx.io.explore_h5("data.h5")            # Print tree structure
   stx.io.has_h5_key("data.h5", "/group/dataset")

   # Zarr
   stx.io.explore_zarr("data.zarr")
   stx.io.has_zarr_key("data.zarr", "/group/array")

Format Registry
---------------

Register custom loaders and savers for new file extensions:

.. code-block:: python

   @stx.io.register_loader(".custom")
   def load_custom(path, **kwargs):
       with open(path) as f:
           return parse_custom(f.read())

   @stx.io.register_saver(".custom")
   def save_custom(obj, path, **kwargs):
       with open(path, "w") as f:
           f.write(serialize_custom(obj))

Caching
-------

Built-in load caching for repeated reads of the same file:

.. code-block:: python

   stx.io.configure_cache(maxsize=128)
   data = stx.io.load("big_file.h5")    # First call: reads from disk
   data = stx.io.load("big_file.h5")    # Second call: from cache

   stx.io.get_cache_info()               # Cache hit/miss statistics
   stx.io.clear_load_cache()             # Flush the cache

API Reference
-------------

.. automodule:: scitex.io
   :members:
   :no-undoc-members:
   :show-inheritance:
