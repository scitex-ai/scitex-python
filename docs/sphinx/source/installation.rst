Installation
============

Requirements
------------

- **Python 3.10+**
- ``pip`` 21+ or ``uv`` (recommended for faster installs)


Core Install
------------

The base package pulls in only lightweight dependencies and gives you access
to session management, path utilities, string helpers, and the module
discovery system.

.. code-block:: bash

   pip install scitex


Recommended: Install Everything
-------------------------------

If you want the full experience (plotting, statistics, I/O, scholar, writer,
and every other module):

.. code-block:: bash

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
   * - ``ai``
     - LLM APIs (OpenAI, Anthropic, Google, Groq) and ML tools (scikit-learn)
   * - ``browser``
     - Web automation via Playwright
   * - ``capture``
     - Screenshot capture (mss, Playwright)
   * - ``dataset``
     - Scientific dataset access (DANDI, OpenNeuro, PhysioNet)
   * - ``cloud``
     - Cloud integration utilities
   * - ``app``
     - Unified file storage SDK (scitex-app)
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
significantly faster than pip:

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
