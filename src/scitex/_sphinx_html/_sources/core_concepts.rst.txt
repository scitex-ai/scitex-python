Core Concepts
=============

Research Workflow
-----------------

SciTeX covers the full research pipeline, from literature review to publication:

.. image:: _static/workflow.png
   :width: 100%
   :alt: Research workflow: Question → Literature → Data → Analysis → Figures → Manuscript → Verify → Publication

Each stage maps to a SciTeX module. The ``@stx.session`` decorator ties them
together, ensuring every step is reproducible and provenance-tracked.

Architecture
------------

SciTeX is organized around a simple principle: every research script should be
a reproducible, self-documenting unit of work. The ``@stx.session`` decorator
enforces this by managing outputs, logging, and configuration automatically.

.. image:: _static/architecture.png
   :width: 100%
   :alt: Module architecture: Experiment (session, config, io, logging, repro), Analysis & Visualization (stats, dsp, plt, diagram), Publication (scholar, writer, clew)

Modules are grouped into three layers -- **Experiment** infrastructure (blue),
**Analysis & Visualization** tools (orange), and **Publication** (purple).
See :doc:`modules/index` for the full module reference.

The Session Model
-----------------

``@stx.session`` is the core abstraction. It wraps a function and provides:

1. **Output directory**: ``script_out/FINISHED_SUCCESS/<session_id>/``
2. **Logging**: All stdout/stderr captured to ``script.log``
3. **Config injection**: YAML files from ``./config/`` merged and injected
4. **CLI generation**: Function parameters become ``--flags``
5. **Provenance**: File hashes recorded to SQLite for reproducibility

.. code-block:: python

    import scitex as stx

    @stx.session
    def main(
        lr=0.001,               # --lr 0.01
        epochs=100,             # --epochs 50
        CONFIG=stx.INJECTED,    # from ./config/*.yaml
        plt=stx.INJECTED,       # pre-configured matplotlib
        logger=stx.INJECTED,    # session logger
    ):
        """Train a model. Docstring becomes --help text."""
        logger.info(f"Training with lr={lr}, epochs={epochs}")

        # stx.io.save paths are relative to session output dir
        stx.io.save({"lr": lr, "epochs": epochs}, "params.yaml")

        return 0

Session output tree:

.. code-block:: text

    train_out/
    ├── RUNNING/                    # while script runs
    │   └── 20260213_143022_AB12/
    │       ├── params.yaml
    │       └── train.log
    └── FINISHED_SUCCESS/           # after successful exit
        └── 20260213_143022_AB12/   # moved here on completion
            ├── params.yaml
            └── train.log

Universal I/O
-------------

``stx.io.save`` and ``stx.io.load`` dispatch on file extension:

.. list-table::
   :header-rows: 1

   * - Extension
     - Data Type
     - Backend
   * - ``.csv``
     - DataFrame
     - pandas
   * - ``.npy``, ``.npz``
     - ndarray
     - numpy
   * - ``.pkl``, ``.pickle``
     - any object
     - pickle
   * - ``.yaml``, ``.yml``
     - dict
     - PyYAML
   * - ``.json``
     - dict/list
     - json
   * - ``.png``, ``.jpg``, ``.svg``, ``.pdf``
     - Figure
     - matplotlib
   * - ``.hdf5``, ``.h5``
     - dict/array
     - h5py
   * - ``.mat``
     - dict
     - scipy.io
   * - ``.pth``, ``.pt``
     - state_dict
     - torch
   * - ``.parquet``
     - DataFrame
     - pyarrow

When saving a matplotlib Figure, SciTeX also exports:

- A ``.csv`` with the plotted data (extracted from axes)
- A ``.yaml`` recipe for reproducing the figure

Provenance Tracking (Clew)
--------------------------

Inside ``@stx.session``, every ``stx.io.save`` and ``stx.io.load`` call
records the file's SHA-256 hash to a local SQLite database. This enables:

- **Verification**: Check if output files have been modified since creation
- **DAG reconstruction**: Trace which inputs produced which outputs
- **Cross-session linking**: If script B loads a file that script A produced,
  the parent-child relationship is recorded automatically

.. code-block:: bash

    # Check verification status
    scitex clew status

    # Verify a specific session
    scitex clew run <session_id>

    # Generate a dependency diagram
    scitex clew mermaid

Configuration
-------------

SciTeX uses a priority-based config system:

1. **CLI flags** (highest priority): ``--lr 0.01``
2. **Config files**: ``./config/*.yaml`` (merged alphabetically)
3. **Function defaults** (lowest priority): ``lr=0.001``

.. code-block:: yaml

    # config/experiment.yaml
    DATA_DIR: ./data
    MODEL:
      hidden_size: 256
      dropout: 0.1

    # config/PATH.yaml
    OUTPUT_DIR: ${HOME}/results    # env var substitution

Access in code:

.. code-block:: python

    @stx.session
    def main(CONFIG=stx.INJECTED, **kw):
        data_dir = CONFIG["DATA_DIR"]
        hidden = CONFIG["MODEL"]["hidden_size"]

Best Practices
--------------

1. **One session per script**: Each ``.py`` file should have one ``@stx.session`` function
2. **Use relative paths in save/load**: They resolve relative to the session output directory
3. **Return 0 for success**: The exit code determines the output directory name (``FINISHED_SUCCESS`` vs ``FINISHED_ERROR``)
4. **Put config in** ``./config/*.yaml``: Keeps parameters separate from code
5. **Use** ``stx.repro.fix_seeds(42)`` **for determinism**: Fixes numpy, torch, random seeds in one call
