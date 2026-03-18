Ecosystem
=========

SciTeX is a modular toolkit composed of standalone packages. Each package
can be installed and used independently, or accessed through the unified
``import scitex`` interface.

Delegation Pattern
------------------

The ``scitex`` package itself contains no runtime logic. It acts as an
orchestrator that re-exports functionality from sub-packages via lazy
imports. When you write ``scitex.io.load("data.csv")``, the call is
delegated to the ``scitex_io`` package under the hood.

This means:

- **Standalone use**: ``pip install scitex-io`` then ``import scitex_io``
- **Unified use**: ``pip install scitex[io]`` then ``import scitex; scitex.io.load(...)``

Both paths execute the same code. The ``scitex`` package simply provides
the namespace glue.

.. code-block:: python

   # These are equivalent:
   import scitex_io
   scitex_io.load("data.csv")

   import scitex
   scitex.io.load("data.csv")

Package Reference
-----------------

.. list-table::
   :header-rows: 1
   :widths: 20 18 22 40

   * - Package
     - scitex Module
     - PyPI
     - Description
   * - scitex-io
     - ``scitex.io``
     - ``pip install scitex-io``
     - Unified file I/O for 30+ formats
   * - scitex-stats
     - ``scitex.stats``
     - ``pip install scitex-stats``
     - Publication-ready statistics (23+ tests)
   * - figrecipe
     - ``scitex.plt``
     - ``pip install figrecipe``
     - Publication-ready matplotlib figures
   * - scitex-writer
     - ``scitex.writer``
     - ``pip install scitex-writer``
     - LaTeX manuscript compilation
   * - scitex-scholar
     - ``scitex.scholar``
     - ``pip install scitex-scholar``
     - Literature search and management
   * - scitex-audio
     - ``scitex.audio``
     - ``pip install scitex-audio``
     - Text-to-speech and audio
   * - scitex-dev
     - ``scitex.dev``
     - ``pip install scitex-dev``
     - Developer tools, ecosystem management
   * - scitex-clew
     - ``scitex.clew``
     - ``pip install scitex-clew``
     - Hash-based reproducibility verification
   * - scitex-linter
     - ``scitex.linter``
     - ``pip install scitex-linter``
     - AST-based code pattern checking
   * - scitex-dataset
     - ``scitex.dataset``
     - ``pip install scitex-dataset``
     - Scientific dataset access (DANDI, OpenNeuro, PhysioNet)
   * - crossref-local
     - ``scitex.scholar.crossref``
     - ``pip install crossref-local``
     - Local CrossRef database (167M+ papers)
   * - openalex-local
     - ``scitex.scholar.openalex``
     - ``pip install openalex-local``
     - Local OpenAlex database (250M+ papers)
   * - socialia
     - ``scitex.social``
     - ``pip install socialia``
     - Social media posting (Twitter, LinkedIn)
   * - scitex-app
     - ``scitex.app``
     - ``pip install scitex-app``
     - Runtime SDK for SciTeX apps
   * - scitex-cloud
     - ``scitex.cloud``
     - ``pip install scitex-cloud``
     - Cloud platform integration
   * - scitex-notification
     - ``scitex.notify``
     - ``pip install scitex-notification``
     - Multi-backend notifications

Installation
------------

Install individual packages or use extras through the main package:

.. code-block:: bash

   # Full installation (all packages)
   pip install scitex[all]

   # Typical research setup
   pip install scitex[plt,stats,scholar]

   # Individual standalone package
   pip install figrecipe
