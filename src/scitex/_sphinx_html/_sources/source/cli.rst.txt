CLI Reference
=============

SciTeX provides a unified command-line interface. All commands follow the
pattern:

.. code-block:: bash

   scitex <module> <command> [options]

Run ``scitex --help-recursive`` to see every available command.

General
-------

.. code-block:: bash

   scitex --help-recursive        # Show all commands across all modules
   scitex list-python-apis        # List all Python APIs (210 items)
   scitex mcp list-tools          # List all MCP tools (120+ tools)

Scholar
-------

Literature search, PDF management, and metadata enrichment.

.. code-block:: bash

   scitex scholar fetch <DOI>     # Download paper by DOI
   scitex scholar bibtex <file>   # Enrich BibTeX file with metadata
   scitex scholar search <query>  # Search for papers

Stats
-----

Statistical testing with automatic test recommendation.

.. code-block:: bash

   scitex stats recommend         # Suggest appropriate statistical tests
   scitex stats run <test> <data> # Run a specific test on data

Audio
-----

Text-to-speech and audio playback.

.. code-block:: bash

   scitex audio speak <text>      # Convert text to speech
   scitex audio play <file>       # Play an audio file

Capture
-------

Screen capture and monitoring.

.. code-block:: bash

   scitex capture snap            # Take a screenshot
   scitex capture monitor         # Start screen monitoring

Template
--------

Project scaffolding from built-in templates.

.. code-block:: bash

   scitex template clone <type> <name>

Available template types:

- ``research`` -- Research project with session tracking
- ``pip`` -- Python pip package
- ``paper`` -- LaTeX manuscript project
- ``app`` -- SciTeX app with bridge integration
- ``singularity`` -- Singularity container definition

Introspect
----------

Python code introspection for exploring APIs.

.. code-block:: bash

   scitex introspect api <module>       # List APIs for a module
   scitex introspect source <function>  # View source code of a function

Dev
---

Ecosystem development and version management.

.. code-block:: bash

   scitex dev versions            # Show versions of all installed packages
   scitex dev ecosystem           # Manage ecosystem packages
