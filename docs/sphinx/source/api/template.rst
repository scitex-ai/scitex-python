Template Module (``stx.template``)
====================================

Project scaffolding and code snippet templates for quick starts.

Project Templates
-----------------

.. code-block:: bash

   # Clone a project template
   scitex template clone research my_project
   scitex template clone pip_project my_package
   scitex template clone paper my_paper

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Template
     - Description
   * - ``research``
     - Full scientific workflow (scripts, data, docs, config)
   * - ``research_minimal``
     - Essential modules only
   * - ``pip_project``
     - Distributable Python package for PyPI
   * - ``singularity``
     - Reproducible containerized environment
   * - ``paper_directory``
     - Academic paper with LaTeX/BibTeX structure

Git Strategies
--------------

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Strategy
     - Behavior
   * - ``child`` (default)
     - Fresh git repo, isolated from template
   * - ``parent``
     - Use parent repo if available
   * - ``origin``
     - Preserve template's git history
   * - ``None``
     - No git initialization

Code Templates
--------------

.. code-block:: bash

   # List available code templates
   scitex template code list

   # Get a template
   scitex template code session           # Full @stx.session script
   scitex template code session-minimal   # Lightweight session
   scitex template code session-plot      # Figure-focused session
   scitex template code session-stats     # Statistics-focused session
   scitex template code io                # I/O operations
   scitex template code plt               # Plotting patterns
   scitex template code stats             # Statistical analysis
   scitex template code scholar           # Literature management

Python API
----------

.. code-block:: python

   from scitex.template import clone_template, get_code_template

   # Clone project
   clone_template("research", "my_experiment", git_strategy="child")

   # Get code snippet
   code = get_code_template("session", filepath="analyze.py")

API Reference
-------------

.. automodule:: scitex.template
   :members:
