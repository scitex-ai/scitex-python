.. SciTeX documentation master file

SciTeX -- Modular Python Toolkit for Researchers and AI Agents
=============================================================

A Python framework for reproducible scientific research.

.. image:: _static/workflow.png
   :alt: SciTeX Ecosystem
   :align: center
   :width: 800px

Role in SciTeX Ecosystem
------------------------

``scitex`` is the **unified orchestrator** package. It re-exports from sub-packages
so users have a single import (``import scitex``). It does not contain runtime logic
itself -- it delegates to sub-packages.

.. code-block:: text

   scitex (this package) -- orchestrator, templates, CLI, MCP server
     |-- scitex.app  <-  scitex-app   (runtime SDK: file I/O, config, validation)
     |-- scitex.ui   <-  scitex-ui    (React/TS components: workspace, data-table)
     +-- scitex.plt  <-  figrecipe    (figures: plotting, diagrams, recipes)

- **scitex-app** (`docs <https://scitex-app.readthedocs.io/>`_): Runtime SDK that apps import at execution time
- **scitex-ui** (`docs <https://scitex-ui.readthedocs.io/>`_): Shared React/TypeScript component library
- **figrecipe** (`docs <https://figrecipe.readthedocs.io/>`_): Reference app -- figures, diagrams, recipes

Four Freedoms for Research
--------------------------

0. The freedom to **run** your research anywhere -- your machine, your terms.
1. The freedom to **study** how every step works -- from raw data to final manuscript.
2. The freedom to **redistribute** your workflows, not just your papers.
3. The freedom to **modify** any module and share improvements with the community.

AGPL-3.0 -- because research infrastructure deserves the same freedoms as the software it runs on.

.. code-block:: python

   import scitex as stx

   @stx.session
   def main(n_samples=100, plt=stx.INJECTED):
       import numpy as np
       x = np.linspace(0, 2 * np.pi, n_samples)
       y = np.sin(x) + np.random.normal(0, 0.1, n_samples)

       fig, ax = plt.subplots()
       ax.plot_line(x, y)
       stx.io.save(fig, "sine.png")       # PNG + CSV + YAML recipe
       return 0

- ``@stx.session`` -- Reproducible runs with CLI, config, and provenance tracking
- ``stx.io`` -- Save/load 30+ formats through a single interface
- ``stx.plt`` -- Publication figures with auto CSV data export
- ``stx.stats`` -- 23 statistical tests with effect sizes and CI
- ``stx.scholar`` -- Search, download, and enrich papers
- 120+ MCP tools for AI-assisted research workflows

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   modules/index
   installation
   quickstart
   core_concepts
   gallery

.. toctree::
   :maxdepth: 1
   :caption: API Reference
   :hidden:

   api/index
