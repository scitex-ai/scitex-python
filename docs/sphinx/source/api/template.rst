Template Module (``stx.template``)
====================================

Project scaffolding and code snippet templates for quick starts.
Create fully structured research projects, Python packages, or
academic papers with a single command.

Project Templates
-----------------

.. code-block:: bash

   # Clone a project template
   scitex template clone research my_project
   scitex template clone pip_project my_package
   scitex template clone paper my_paper
   scitex template clone app my_app
   scitex template clone singularity my_container

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Template
     - Description
   * - ``research``
     - Full scientific workflow (scripts, data, docs, config, session scaffolding)
   * - ``research_minimal``
     - Essential modules only for lightweight experiments
   * - ``pip_project``
     - Distributable Python package for PyPI (``pyproject.toml``, tests, CI)
   * - ``paper``
     - Academic paper with LaTeX/BibTeX structure, SciTeX writer integration
   * - ``app``
     - SciTeX application with bridge-init, MountPoint, and EventBus
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
   * - ``None``
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
   scitex template code list

   # Get a template (prints to stdout)
   scitex template code session           # Full @stx.session script
   scitex template code session-minimal   # Lightweight session
   scitex template code session-plot      # Figure-focused session
   scitex template code session-stats     # Statistics-focused session
   scitex template code io                # I/O operations
   scitex template code plt               # Plotting patterns
   scitex template code stats             # Statistical analysis
   scitex template code scholar           # Literature management

   # Save to a file
   scitex template code session --output analyze.py

Python API
----------

.. code-block:: python

   from scitex.template import clone_template, get_code_template

   # Clone a project template
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
