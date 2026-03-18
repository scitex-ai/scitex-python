SciTeX Documentation
====================

SciTeX is a modular Python toolkit for research automation. It provides a
unified interface across the full scientific workflow: from data loading and
statistical analysis, through publication-ready plotting and manuscript
compilation, to AI-assisted literature review. Every module is installable
independently, and the entire surface area is exposed to AI agents through
an MCP (Model Context Protocol) server.

Key Features
------------

- **Session decorator** -- wrap any experiment function with ``@stx.session``
  to get automatic directory management, reproducibility logging, and
  error-safe cleanup.

- **Unified I/O** -- ``stx.io.save`` / ``stx.io.load`` handle 40+ formats
  (CSV, HDF5, YAML, images, PDFs, ...) through a single call.

- **Statistics** -- ``stx.stats`` provides hypothesis testing, effect sizes,
  power analysis, and multiple-comparison correction with APA-formatted
  output.

- **Plotting** -- ``stx.plt`` produces publication-ready figures via
  `figrecipe <https://github.com/ywatanabe1989/figrecipe>`_, with
  millimetre-based layouts, journal style presets, and automatic CSV data
  export alongside every saved figure.

- **Manuscript writing** -- ``stx.writer`` compiles LaTeX manuscripts,
  manages BibTeX, and exports to Overleaf.

- **Literature management** -- ``stx.scholar`` searches CrossRef, OpenAlex,
  and Google Scholar; downloads and parses PDFs; and maintains a local
  citation database.

- **MCP for AI agents** -- every capability above is available as a
  tool call through the built-in MCP server, so LLM agents can run
  statistics, create figures, and compile papers programmatically.

Getting Started
---------------

1. :doc:`installation` -- install the core package and choose the extras you
   need.
2. :doc:`quickstart` -- a five-minute walkthrough of the session decorator,
   I/O, and plotting.
3. :doc:`api/index` -- full API reference generated from docstrings.


.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart


.. toctree::
   :maxdepth: 2
   :caption: Guides

   concepts
   gallery
   ecosystem


.. toctree::
   :maxdepth: 2
   :caption: Interfaces

   cli
   mcp


.. toctree::
   :maxdepth: 2
   :caption: Reference

   api/index


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
