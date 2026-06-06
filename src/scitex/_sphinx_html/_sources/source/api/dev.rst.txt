Dev Module (``stx.dev``)
========================

Development tools and ecosystem management for the SciTeX package family.

.. note::

   ``stx.dev`` delegates to the standalone
   `scitex-dev <https://github.com/ywatanabe1989/scitex-dev>`_ package.
   Install with: ``pip install scitex-dev``.

Overview
--------

The dev module provides utilities for maintaining the SciTeX ecosystem of
packages, building documentation, managing versions, and creating
MCP/CLI wrappers for scientific tools. It is primarily used by package
maintainers and contributors rather than end users.

Ecosystem Management
--------------------

The SciTeX ecosystem comprises 14+ packages. ``stx.dev`` provides a
unified registry and coordination tools.

.. code-block:: python

   import scitex as stx

   # List all ecosystem packages
   stx.dev.list_versions()

   # Check version consistency across the ecosystem
   stx.dev.check_versions()

   # Synchronize local clones
   stx.dev.ecosystem_sync()

   # Commit across multiple packages
   stx.dev.ecosystem_commit("fix: update shared constants")

.. list-table:: Ecosystem Packages
   :header-rows: 1
   :widths: 30 70

   * - Package
     - Purpose
   * - ``scitex``
     - Hub package (re-exports all modules)
   * - ``scitex-io``
     - File I/O for 30+ formats
   * - ``scitex-stats``
     - Statistical testing with auto-reporting
   * - ``scitex-linter``
     - AST-based convention checker
   * - ``scitex-clew``
     - Claim-evidence-workflow pipeline
   * - ``figrecipe``
     - Publication-quality plotting
   * - ``scitex-dev``
     - Development and ecosystem tools
   * - ``scitex-notification``
     - Multi-backend notifications
   * - ``scitex-app``
     - Runtime SDK for SciTeX applications

LLM-friendly Types
-------------------

``stx.dev`` provides structured return types designed for consumption
by both humans and AI agents:

.. code-block:: python

   from scitex.dev import Result, ErrorCode

   # Wrap function results for consistent handling
   result = Result(ok=True, data={"accuracy": 0.95})
   result = Result(ok=False, error=ErrorCode.NOT_FOUND, message="File missing")

   # Decorator to add return_as= parameter
   @stx.dev.supports_return_as
   def analyze(data):
       return {"mean": data.mean()}

   analyze(data, return_as="json")    # JSON string
   analyze(data, return_as="dict")    # Python dict

MCP and CLI Wrappers
--------------------

Convert Python functions into MCP tools or CLI commands:

.. code-block:: python

   from scitex.dev import wrap_as_mcp, wrap_as_cli

   def my_tool(path: str, threshold: float = 0.5) -> dict:
       """Analyze a data file."""
       ...

   # Register as MCP tool (for AI agent access)
   mcp_tool = wrap_as_mcp(my_tool)

   # Register as CLI command (for terminal access)
   cli_cmd = wrap_as_cli(my_tool)

Documentation
-------------

Build and search unified documentation across the ecosystem:

.. code-block:: python

   # Build Sphinx docs for a package
   stx.dev.build_docs("scitex-io")

   # Get docstring for any public function
   stx.dev.get_docs("stx.io.save")

   # Full-text search across all packages
   results = stx.dev.search("load_configs")

Hot Reload
----------

Reload modules during interactive development:

.. code-block:: python

   stx.dev.reload("scitex.io")    # Re-import scitex.io from disk

HPC Testing
-----------

Submit test suites to HPC clusters and poll results:

.. code-block:: bash

   scitex dev test-hpc --package scitex-io
   scitex dev test-hpc-poll --job-id 12345

Bulk Rename
-----------

Rename symbols across an entire codebase safely:

.. code-block:: python

   stx.dev.bulk_rename(
       root="./src",
       old="old_function_name",
       new="new_function_name",
       dry_run=True,    # Preview changes first
   )

API Reference
-------------

.. automodule:: scitex.dev
   :members:
   :no-undoc-members:
   :show-inheritance:
