Linter Module (``stx.linter``)
===============================

AST-based Python linter enforcing SciTeX conventions for reproducible
scientific code.

.. note::

   ``stx.linter`` wraps the standalone
   `scitex-linter <https://github.com/ywatanabe1989/scitex-linter>`_ package.
   Install with: ``pip install scitex-linter``.

Quick Reference
---------------

.. code-block:: bash

   # Check a file
   scitex linter check my_script.py

   # Check with specific severity
   scitex linter check my_script.py --severity warning

   # List all rules
   scitex linter list-rules

   # Filter by category
   scitex linter list-rules --category session

.. code-block:: python

   from scitex_linter import check_file, list_rules

   # Check a file
   results = check_file("my_script.py")

   # List available rules
   rules = list_rules()

Rule Categories
---------------

45 rules across 8 categories:

.. list-table::
   :header-rows: 1
   :widths: 15 25 60

   * - Prefix
     - Category
     - Examples
   * - ``STX-S``
     - **Session**
     - Missing ``@stx.session``, missing ``if __name__`` guard, missing return
   * - ``STX-I``
     - **Import**
     - Using ``import mngs`` instead of ``import scitex``, bare ``import numpy``
   * - ``STX-IO``
     - **I/O**
     - Using ``open()`` instead of ``stx.io``, hardcoded paths
   * - ``STX-P``
     - **Plotting**
     - Using ``plt.show()`` instead of ``stx.io.save``, missing ``set_xyt``
   * - ``STX-ST``
     - **Statistics**
     - Using ``scipy.stats`` directly instead of ``stx.stats``
   * - ``STX-PA``
     - **Path**
     - Hardcoded absolute paths, missing ``stx.gen.mk_spath``
   * - ``STX-FM``
     - **Format**
     - Non-snake_case names, magic numbers, missing docstrings

Severity Levels
---------------

- **error** -- Must fix (breaks reproducibility or correctness)
- **warning** -- Should fix (best practice violations)
- **info** -- Suggestions for improvement

Interfaces
----------

The linter is available through multiple interfaces:

**CLI:**

.. code-block:: bash

   scitex linter check script.py
   scitex-linter check script.py    # standalone CLI

**Python API:**

.. code-block:: python

   from scitex_linter import check_file, check_source

   results = check_file("script.py")
   results = check_source("import numpy as np\n...")

**Flake8 Plugin:**

.. code-block:: bash

   flake8 --select=STX script.py

**MCP Tools:**

.. code-block:: python

   # Available as MCP tools for AI agents
   linter_check(path="script.py", severity="warning")
   linter_list_rules(category="session")
   linter_check_source(source="...", filepath="<stdin>")

Configuration
-------------

Configure via ``pyproject.toml``:

.. code-block:: toml

   [tool.scitex-linter]
   severity = "warning"
   ignore = ["STX-S002", "STX-FM001"]

API Reference
-------------

.. automodule:: scitex.linter
   :members:
   :show-inheritance:
