Dataset Module (``stx.dataset``)
=================================

Unified access to public scientific datasets from major neuroscience
and biomedical repositories. Search, browse, and fetch datasets
without learning each repository's API.

Supported Sources
-----------------

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Source
     - Description
   * - `DANDI <https://dandiarchive.org>`_
     - Neurophysiology data (NWB format) -- electrophysiology, calcium imaging
   * - `OpenNeuro <https://openneuro.org>`_
     - Brain imaging data (BIDS format) -- fMRI, EEG, MEG, PET
   * - `PhysioNet <https://physionet.org>`_
     - Physiological signal data -- ECG, EEG, clinical waveforms

Quick Start
-----------

.. code-block:: python

   import scitex as stx

   # Search across all sources
   results = stx.dataset.search("epilepsy EEG")

   # Fetch a specific dataset
   data = stx.dataset.fetch("dandi", dandiset_id="000003")

   # List available sources
   sources = stx.dataset.list_sources()
   # ['dandi', 'openneuro', 'physionet']

Key Functions
-------------

``search(query, source=None)``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Search for datasets across one or all supported repositories.

.. code-block:: python

   # Search all sources
   results = stx.dataset.search("motor imagery BCI")

   # Search a specific source
   results = stx.dataset.search("sleep staging", source="physionet")

   for r in results:
       print(f"{r.source}: {r.title} ({r.id})")

``fetch(source, **kwargs)``
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Download or stream a dataset from a specific source.

.. code-block:: python

   # Fetch from DANDI
   data = stx.dataset.fetch("dandi", dandiset_id="000003")

   # Fetch from OpenNeuro
   data = stx.dataset.fetch("openneuro", dataset_id="ds000117")

   # Fetch from PhysioNet
   data = stx.dataset.fetch("physionet", database="mimic-iv", version="2.0")

``list_sources()``
^^^^^^^^^^^^^^^^^^

List all available dataset sources and their status.

.. code-block:: python

   sources = stx.dataset.list_sources()
   # ['dandi', 'openneuro', 'physionet']

Local Database
--------------

Build a local search index for faster repeated queries:

.. code-block:: python

   # Build/update the local database
   stx.dataset.db_build(sources=["dandi", "openneuro"])

   # Search the local index (fast, offline)
   results = stx.dataset.db_search("resting state fMRI")

   # Get database statistics
   stx.dataset.db_stats()

CLI Access
----------

.. code-block:: bash

   # Search datasets
   scitex dataset search "epilepsy EEG"

   # Fetch a dataset
   scitex dataset fetch dandi --dandiset-id 000003

   # List sources
   scitex dataset list-sources

   # Build local database
   scitex dataset db-build

API Reference
-------------

.. automodule:: scitex.dataset
   :members:
   :no-undoc-members:
   :show-inheritance:
