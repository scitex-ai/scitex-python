Template Module (``stx.template``)
====================================

Project scaffolding and code snippet templates for quick starts.
Create fully structured research projects, Python packages, or
academic papers with a single command.

Project Templates
-----------------

.. code-block:: bash

   # Preview first; --yes creates the project
   scitex dev template clone research my_project

   # Create a project template
   scitex dev template clone research my_project --yes
   scitex dev template clone pip-project my_package --yes
   scitex dev template clone paper my_paper --yes
   scitex dev template clone singularity my_container --yes

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Template
     - Description
   * - ``research``
     - Full scientific workflow (scripts, data, docs, config, session scaffolding)
   * - ``minimal``
     - Minimal SciTeX project
   * - ``pip-project``
     - Distributable Python package for PyPI (``pyproject.toml``, tests, CI)
   * - ``paper``
     - Academic paper with LaTeX/BibTeX structure, SciTeX writer integration
   * - ``singularity``
     - Reproducible containerized environment (Singularity/Apptainer definition)

What You Get
^^^^^^^^^^^^

A ``research`` template creates:

.. code-block:: text

   my_project/
   +-- config/
   |   +-- EXPERIMENT.yaml       # Experiment parameters
   +-- scripts/
   |   +-- main.py               # @stx.session entry point
   +-- data/                     # Raw data directory
   +-- docs/                     # Documentation
   +-- tests/                    # Test suite
   +-- Makefile                  # Common tasks
   +-- pyproject.toml            # Package metadata

Git Strategies
--------------

Control how git is initialized in the cloned template:

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

.. code-block:: python

   from scitex.template import clone_template

   clone_template("research", "my_project", git_strategy="child")

Code Templates
--------------

Ready-to-use code snippets for common SciTeX patterns. Each snippet
is a complete, runnable script.

.. code-block:: bash

   # List available code templates
   scitex dev template list-code-templates

   # Get a template (prints to stdout)
   scitex dev template get session           # Full @stx.session script
   scitex dev template get session-minimal   # Lightweight session
   scitex dev template get session-plot      # Figure-focused session
   scitex dev template get session-stats     # Statistics-focused session
   scitex dev template get io                # I/O operations
   scitex dev template get plt               # Plotting patterns
   scitex dev template get stats             # Statistical analysis
   scitex dev template get scholar           # Literature management

   # Save to a file
   scitex dev template get session --output analyze.py

Python API
----------

.. code-block:: python

   from scitex.template import clone_template, get_code_template

   # Preview first; --yes creates the project
   scitex dev template clone research my_project

   # Create a project template
   clone_template("research", "my_experiment", git_strategy="child")

   # Get a code snippet as a string
   code = get_code_template("session")
   print(code)

   # Get a code snippet and write to file
   code = get_code_template("session", filepath="analyze.py")

MCP Interface
-------------

Code templates are also available to AI agents via MCP tools:

.. code-block:: python

   # List templates
   template_list_code_templates()

   # Get a specific template
   template_get_code_template(name="session-plot")

   # Clone a project
   template_clone_template(template_type="research", name="my_project")

API Reference
-------------

.. automodule:: scitex.template
   :members:
