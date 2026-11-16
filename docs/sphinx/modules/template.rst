Template Module (``stx.template``)
====================================

Project scaffolding and code snippet templates for quick starts.

Project Templates
-----------------

.. code-block:: bash

   # Preview first; --yes creates the project
   scitex dev template clone research my_project

   # Create a project template
   scitex dev template clone research my_project --yes
   scitex dev template clone pip-project my_package --yes
   scitex dev template clone paper my_paper --yes

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Template
     - Description
   * - ``research``
     - Full scientific workflow (scripts, data, docs, config)
   * - ``minimal``
     - Minimal SciTeX project
   * - ``pip-project``
     - Distributable Python package for PyPI
   * - ``singularity``
     - Reproducible containerized environment
   * - ``paper``
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
   * - ``none``
     - No git initialization

Code Templates
--------------

.. code-block:: bash

   # List available code templates
   scitex dev template list-code-templates

   # Get a template
   scitex dev template get session           # Full @stx.session script
   scitex dev template get session-minimal   # Lightweight session
   scitex dev template get session-plot      # Figure-focused session
   scitex dev template get session-stats     # Statistics-focused session
   scitex dev template get io                # I/O operations
   scitex dev template get plt               # Plotting patterns
   scitex dev template get stats             # Statistical analysis
   scitex dev template get scholar           # Literature management

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

See :doc:`/api/scitex.template` for the auto-generated Python API.
