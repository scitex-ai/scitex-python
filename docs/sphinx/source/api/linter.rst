Linter Module (``stx.linter``)
===============================

AST-based Python linter enforcing SciTeX conventions for reproducible
scientific code. Uses a plugin architecture where each downstream
package contributes its own rules.

.. note::

   ``stx.linter`` wraps the standalone
   `scitex-linter <https://github.com/ywatanabe1989/scitex-linter>`_ package.
   Install with: ``pip install scitex-linter``.

Quick Start
-----------

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

47+ rules across 7 categories, contributed by multiple packages:

.. list-table::
   :header-rows: 1
   :widths: 10 20 15 55

   * - Prefix
     - Category
     - Source
     - Examples
   * - ``STX-S``
     - **Session**
     - scitex-linter
     - Missing ``@stx.session``, missing ``if __name__`` guard, missing return,
       ``load_configs()`` result not UPPER_CASE, magic numbers in module scope
   * - ``STX-I``
     - **Import**
     - scitex-linter
     - Using ``import mngs`` instead of ``import scitex``, bare ``import numpy``,
       wildcard imports
   * - ``STX-IO``
     - **I/O**
     - scitex-io
     - Using ``open()`` instead of ``stx.io``, hardcoded paths,
       using ``pd.read_csv`` directly
   * - ``STX-P``
     - **Plotting**
     - figrecipe
     - Using ``plt.show()`` instead of ``stx.io.save``, missing ``set_xyt``,
       using raw matplotlib calls
   * - ``STX-ST``
     - **Statistics**
     - scitex-stats
     - Using ``scipy.stats`` directly instead of ``stx.stats``,
       missing multiple comparison correction
   * - ``STX-PA``
     - **Path**
     - scitex-linter
     - Hardcoded absolute paths, missing ``stx.gen.mk_spath``
   * - ``STX-FM``
     - **Format**
     - figrecipe
     - Non-snake_case names, magic numbers, missing docstrings

Severity Levels
---------------

- **error** -- Must fix (breaks reproducibility or correctness)
- **warning** -- Should fix (best practice violations)
- **info** -- Suggestions for improvement

Plugin Architecture
-------------------

Each downstream package defines its own linter rules via the
``scitex_linter.plugins`` entry point. The linter discovers and
aggregates rules automatically at runtime.

.. code-block:: toml

   # In a downstream package's pyproject.toml
   [project.entry-points."scitex_linter.plugins"]
   my_package = "my_package._linter_plugin:get_plugin"

The plugin function returns a dictionary of rules, call patterns,
axes hints, and AST checker classes:

.. code-block:: python

   def get_plugin():
       from ._rules import MyRule001, MyRule002
       return {
           "rules": [MyRule001, MyRule002],
           "call_rules": {"my_func": "Use stx.my_func() instead"},
           "axes_hints": {},
           "checkers": [],
       }

Interfaces
----------

The linter is available through four interfaces:

**CLI (via scitex):**

.. code-block:: bash

   scitex linter check script.py
   scitex linter list-rules --category io --severity warning

**Standalone CLI:**

.. code-block:: bash

   scitex-linter check script.py

**Python API:**

.. code-block:: python

   from scitex_linter import check_file, check_source, list_rules

   results = check_file("script.py")
   results = check_source("import numpy as np\n...")
   rules = list_rules(category="io", severity="warning")

**Flake8 Plugin:**

.. code-block:: bash

   flake8 --select=STX script.py

**MCP Tools (for AI agents):**

.. code-block:: python

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

Example Output
--------------

.. code-block:: text

   my_script.py:3:1: STX-I001 [warning] Use 'import scitex as stx' instead of 'import mngs'
   my_script.py:15:5: STX-IO003 [error] Use 'stx.io.load()' instead of 'pd.read_csv()'
   my_script.py:22:1: STX-S001 [warning] Missing '@stx.session' decorator on main()

   3 issues found (1 error, 2 warnings)

API Reference
-------------

.. automodule:: scitex.linter
   :members:
   :show-inheritance:
