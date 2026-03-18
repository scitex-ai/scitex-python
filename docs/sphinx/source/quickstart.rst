Quickstart
==========

This guide covers the most common SciTeX workflows with working code
examples. For design rationale, see :doc:`concepts`.


Session Decorator
-----------------

The ``@stx.session`` decorator is the recommended entry point for any
SciTeX script. It converts your function into a self-contained,
reproducible experiment with automatic CLI generation, config loading,
logging, and organized output directories.

.. code-block:: python

   import scitex as stx

   @stx.session
   def main(
       n_samples=100,
       CONFIG=stx.session.INJECTED,
       plt=stx.session.INJECTED,
       logger=stx.session.INJECTED,
   ):
       """Generate sample data and plot."""
       import numpy as np

       x = np.linspace(0, 2 * np.pi, n_samples)
       y = np.sin(x)

       fig, ax = stx.plt.subplots()
       ax.plot_line(x, y)
       ax.set_xyt("Time", "Amplitude", "Sine Wave")
       stx.io.save(fig, "sine.png")  # Saves sine.png + sine.csv
       return 0

   if __name__ == "__main__":
       main()

Run from the command line -- arguments are generated automatically from
the function signature:

.. code-block:: bash

   python script.py --n-samples 200

Parameters marked with ``stx.session.INJECTED`` are provided by the
session runtime. You never pass them yourself:

- **CONFIG** -- aggregated YAML parameters from ``./config/*.yaml``
- **plt** -- matplotlib wrapped by figrecipe
- **logger** -- colored, file-backed logger
- **COLORS** -- publication color palette
- **rngg** -- seeded random number generator

Output is organized into a timestamped directory:

.. code-block:: text

   script_out/FINISHED_SUCCESS/2026-03-18_14-30-00_AbC1/
   +-- sine.png               # Figure with embedded metadata
   +-- sine.csv               # Auto-exported plot data
   +-- CONFIGS/CONFIG.yaml    # Reproducible parameters
   +-- logs/stdout.log        # Standard output
   +-- logs/stderr.log        # Standard error


Unified File I/O
-----------------

``stx.io.save`` and ``stx.io.load`` handle 30+ formats through a single
interface. The format is inferred from the file extension.

.. code-block:: python

   import scitex as stx
   import numpy as np
   import pandas as pd

   # DataFrame -- CSV
   df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
   stx.io.save(df, "data.csv")
   df = stx.io.load("data.csv")

   # NumPy array -- NPY
   arr = np.random.randn(100, 50)
   stx.io.save(arr, "array.npy")
   arr = stx.io.load("array.npy")

   # Figure -- PNG (also generates CSV of plotted data)
   fig, ax = stx.plt.subplots()
   ax.plot_line([1, 2, 3, 4, 5])
   stx.io.save(fig, "plot.png")  # Creates plot.png AND plot.csv

   # Dictionary -- YAML
   params = {"learning_rate": 0.001, "epochs": 100}
   stx.io.save(params, "params.yaml")
   params = stx.io.load("params.yaml")

   # Dictionary -- JSON
   metadata = {"subject": "S01", "task": "rest"}
   stx.io.save(metadata, "meta.json")
   metadata = stx.io.load("meta.json")

   # Arbitrary object -- Pickle
   stx.io.save({"complex": [1, 2, 3]}, "data.pkl")
   obj = stx.io.load("data.pkl")

When saving a matplotlib figure, SciTeX automatically exports the
underlying data as a CSV file alongside the image. This ensures every
figure in a paper can be independently verified and reproduced.


Statistical Analysis
--------------------

SciTeX wraps 23 statistical tests with a consistent interface that
includes effect sizes, confidence intervals, and power analysis.

.. code-block:: python

   import scitex as stx
   import numpy as np

   group1 = np.random.randn(30) + 0.5
   group2 = np.random.randn(30)

   # Run a t-test with full reporting
   result = stx.stats.run_test(
       "ttest_ind", group1, group2, return_as="dataframe"
   )
   print(result)
   # Columns: test, statistic, p_value, effect_size, ci_lower, ci_upper, power

Not sure which test to use? Let SciTeX recommend one:

.. code-block:: python

   data = {"group_a": group1, "group_b": group2}
   recommendations = stx.stats.recommend_tests(data)
   print(recommendations)

Additional utilities:

.. code-block:: python

   # Multiple comparison correction
   corrected = stx.stats.correct_pvalues([0.01, 0.04, 0.06], method="bonferroni")

   # Effect size calculation
   d = stx.stats.effect_size(group1, group2, test="cohens_d")

   # Format results for publication
   formatted = stx.stats.format_results(result)
   # "t(58) = 2.34, p = .021, d = 0.60"


Publication-Ready Figures
-------------------------

SciTeX delegates to `figrecipe <https://github.com/ywatanabe1989/figrecipe>`_
for publication-quality matplotlib figures with a consistent API.

**Basic line plot**

.. code-block:: python

   import scitex as stx
   import numpy as np

   x = np.linspace(0, 10, 200)

   fig, ax = stx.plt.subplots()
   ax.plot_line(x, np.sin(x))
   ax.set_xyt("Time (s)", "Amplitude", "Sine Wave")
   stx.io.save(fig, "line.png")

**Multi-panel figure**

.. code-block:: python

   import scitex as stx
   import numpy as np

   fig, axes = stx.plt.subplots(1, 3)

   # Panel A: line plot
   x = np.linspace(0, 10, 200)
   axes[0].plot_line(x, np.sin(x))
   axes[0].set_xyt("Time", "Value", "Line")

   # Panel B: violin plot
   data = [np.random.randn(50) + i for i in range(3)]
   axes[1].stx_violin(data)
   axes[1].set_xyt("Group", "Value", "Violin")

   # Panel C: heatmap
   matrix = np.random.randn(10, 10)
   axes[2].stx_heatmap(matrix)
   axes[2].set_xyt("X", "Y", "Heatmap")

   stx.io.save(fig, "panels.png")

**Statistical visualization**

.. code-block:: python

   import scitex as stx
   import numpy as np

   data = np.random.randn(100, 50)

   fig, ax = stx.plt.subplots()
   ax.stx_mean_std(data)
   ax.set_xyt("Time", "Value", "Mean +/- SD")

   stx.io.save(fig, "stats_plot.png")


Literature Management
---------------------

The scholar module handles paper discovery, PDF downloads, and BibTeX
enrichment.

**CLI usage**

.. code-block:: bash

   # Enrich a BibTeX file with missing metadata (DOIs, abstracts)
   scitex scholar bibtex refs.bib

   # Fetch a paper by DOI
   scitex scholar fetch "10.1038/s41586-024-07487-w"

   # Search for papers
   scitex scholar search "deep learning EEG" --limit 20

**Python API**

.. code-block:: python

   import scitex as stx

   # Search for papers
   results = stx.scholar.search("transformer attention mechanism", limit=10)

   # Parse and enrich a BibTeX file
   entries = stx.scholar.parse_bibtex("refs.bib")
   enriched = stx.scholar.enrich_bibtex("refs.bib")


CLI Usage
---------

SciTeX provides a unified CLI that mirrors the Python module structure.

.. code-block:: bash

   # Show all available commands
   scitex --help-recursive

   # Statistics
   scitex stats recommend             # Suggest tests for your data
   scitex stats run ttest_ind         # Run a specific test

   # Scholar / Literature
   scitex scholar fetch "10.1038/..." # Download paper by DOI
   scitex scholar bibtex refs.bib     # Enrich BibTeX metadata
   scitex scholar search "query"      # Search for papers

   # Figures and diagrams
   scitex plt info                    # Show available plot types

   # Utilities
   scitex audio speak "Analysis complete"  # Text-to-speech notification
   scitex capture snap                     # Take a screenshot

   # Introspection
   scitex introspect api scitex.stats      # List APIs for a module
   scitex list-python-apis                 # List all Python APIs
   scitex mcp list-tools                   # List all MCP tools

Every CLI command corresponds to a Python function and an MCP tool.
See :doc:`concepts` for details on this three-interface design.
