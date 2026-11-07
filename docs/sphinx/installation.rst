Installation
============

Requirements
------------

- **Python 3.10+**
- ``uv`` (strongly recommended) — install with ``pip install uv`` or
  ``curl -LsSf https://astral.sh/uv/install.sh | sh``
- Hub integration and ``scitex[all]`` require **Python 3.11+** in the
  upcoming 2.30.9 release. The base library retains its Python 3.10+ requirement.
- ``pip`` is also supported; resolution and download time depend on the
  selected extras, platform and package cache.


.. note::

   ``scitex[all]`` selects a large dependency set. Use a dedicated environment
   and inspect installation errors rather than falling back to fewer extras
   while claiming a complete installation. System tools needed by an integration
   (for example, a LaTeX compiler) are separate from Python package installation.


Core Install
------------

The base package installs the default scientific stack and declared leaf
providers. Extras select additional integrations; the base install is not a
promise that every app or external service is available.

.. code-block:: bash

   uv pip install scitex          # recommended
   pip install scitex              # also works, slower for [all]


Recommended: Install Everything
-------------------------------

If you want the full experience (plotting, statistics, I/O, scholar, writer,
and every other module):

.. code-block:: bash

   uv pip install "scitex[all]"
   pip install "scitex[all]"


Research Workflow
-----------------

For a typical research project you need figures, statistics, and literature
search but not audio, browser automation, or cloud tools:

.. code-block:: bash

   pip install "scitex[plt,stats,scholar]"


Per-Module Extras
-----------------

Install only what you need. Each extra maps to a self-contained capability.

.. list-table::
   :header-rows: 1
   :widths: 15 55

   * - Extra
     - Description
   * - ``plt``
     - Publication-ready figures via figrecipe (matplotlib, seaborn, Pillow)
   * - ``stats``
     - Hypothesis testing, effect sizes, power analysis (scitex-stats, scipy, statsmodels)
   * - ``io``
     - Unified I/O for 40+ formats (HDF5, Excel, YAML, PDF, images, ...)
   * - ``scholar``
     - Literature search and PDF management (CrossRef, OpenAlex, Semantic Scholar)
   * - ``writer``
     - LaTeX manuscript compilation, BibTeX management, Overleaf export
   * - ``audio``
     - Text-to-speech and audio utilities (scitex-audio)
   * - ``genai``
     - Generative-AI provider interfaces
   * - ``ml``
     - Machine-learning tools
   * - ``browser``
     - Web automation via Playwright
   * - ``capture``
     - Screenshot capture (mss, Playwright)
   * - ``dataset``
     - Scientific dataset access (DANDI, OpenNeuro, PhysioNet)
   * - ``cloud``
     - Cloud integration utilities
   * - ``app``
     - App interfaces supplied by scitex-sdk
   * - ``session``
     - Session decorator with reproducibility logging
   * - ``diagram``
     - Diagram generation (Mermaid, Graphviz)
   * - ``db``
     - Database access (SQLAlchemy, PostgreSQL)
   * - ``cv``
     - Computer vision (OpenCV, Pillow)
   * - ``dsp``
     - Digital signal processing (scipy, tensorpac)
   * - ``social``
     - Social media posting (socialia)
   * - ``tunnel``
     - SSH tunnel management (scitex-tunnel)
   * - ``all``
     - Everything above


Example combinations:

.. code-block:: bash

   # Neuroscience analysis
   pip install "scitex[plt,stats,dsp,dataset]"

   # Paper writing
   pip install "scitex[writer,scholar,plt]"

   # AI agent development
   pip install "scitex[ai,browser,capture]"


Development Install
-------------------

Clone the repository and install in editable mode with development tools:

.. code-block:: bash

   git clone https://github.com/ywatanabe1989/scitex-python.git
   cd scitex-python
   pip install -e ".[dev]"

The ``dev`` extra includes pytest, ruff, mypy, Sphinx, and build tools.

Using uv (recommended)
^^^^^^^^^^^^^^^^^^^^^^^

`uv <https://docs.astral.sh/uv/>`_ resolves and installs dependencies
in parallel from a Rust resolver — roughly 10–30× faster than pip on
``scitex[all]`` (3 min vs. 30–90 min). Install it once with
``pip install uv`` (or the standalone shell installer), then prefix
every install command on this page with ``uv``:

.. code-block:: bash

   uv pip install -e ".[dev]"


Verifying the Installation
--------------------------

.. code-block:: python

   import scitex as stx
   print(stx.__version__)

To check which optional modules are available:

.. code-block:: python

   stx.usage.list()
