Quick Start
===========

Three Interfaces
----------------

SciTeX exposes the same capabilities through three interfaces:
Python API, CLI commands, and MCP tools for AI agents.

Python API
^^^^^^^^^^

``@stx.session`` -- Reproducible Experiment Tracking

.. code-block:: python

   import scitex as stx

   @stx.session
   def main(filename="demo.jpg"):
       fig, ax = stx.plt.subplots()
       ax.plot_line(t, signal)
       ax.set_xyt("Time (s)", "Amplitude", "Title")
       stx.io.save(fig, filename)
       return 0

Output:

.. code-block:: text

   script_out/FINISHED_SUCCESS/2025-01-08_12-30-00_AbC1/
   |-- demo.jpg                    # Figure with embedded metadata
   |-- demo.csv                    # Auto-exported plot data
   |-- CONFIGS/CONFIG.yaml         # Reproducible parameters
   +-- logs/{stdout,stderr}.log    # Execution logs

``stx.io`` -- Universal File I/O (30+ formats)

.. code-block:: python

   stx.io.save(df, "output.csv")
   stx.io.save(fig, "output.jpg")
   df = stx.io.load("output.csv")

``stx.stats`` -- Publication-Ready Statistics (23 tests)

.. code-block:: python

   result = stx.stats.test_ttest_ind(group1, group2, return_as="dataframe")
   # Includes: p-value, effect size, CI, normality check, power

``stx.plt`` -- Publication-Ready Figures

.. code-block:: python

   fig, ax = stx.plt.subplots()
   ax.plot_line(x, y, label="signal")
   ax.set_xyt("Time (s)", "Amplitude", "Sine Wave")
   stx.io.save(fig, "plot.png")
   # Creates: plot.png + plot.csv + plot.yaml (recipe for reproduction)

``stx.scholar`` -- Literature Management

.. code-block:: python

   # Enrich BibTeX with abstracts, DOIs, citation counts
   stx.scholar.enrich_bibtex("refs.bib", add_abstracts=True)

CLI Commands
^^^^^^^^^^^^

.. code-block:: bash

   scitex --help-recursive              # Show all commands
   scitex scholar fetch "10.1038/..."   # Download paper by DOI
   scitex scholar bibtex refs.bib       # Enrich BibTeX
   scitex stats recommend               # Suggest statistical tests
   scitex audio speak "Done"            # Text-to-speech
   scitex capture snap                  # Screenshot

MCP Tools (120+ tools for AI agents)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Turn AI agents into autonomous scientific researchers.

.. list-table::
   :header-rows: 1
   :widths: 20 10 70

   * - Category
     - Tools
     - Description
   * - writer
     - 28
     - LaTeX manuscript compilation
   * - scholar
     - 23
     - PDF download, metadata enrichment
   * - capture
     - 12
     - Screen monitoring and capture
   * - introspect
     - 12
     - Python code introspection
   * - audio
     - 10
     - Text-to-speech, audio playback
   * - stats
     - 10
     - Automated statistical testing
   * - plt
     - 9
     - Matplotlib figure creation
   * - diagram
     - 9
     - Mermaid and Graphviz diagrams
   * - dataset
     - 8
     - Neuroimaging/physiology datasets
   * - social
     - 7
     - Social media posting
   * - canvas
     - 7
     - Figure composition
   * - template
     - 6
     - Project scaffolding
   * - verify
     - 6
     - Reproducibility verification
   * - dev
     - 6
     - Version checking
   * - ui
     - 5
     - Notifications
   * - linter
     - 3
     - Code pattern checking

**Claude Code Setup** — add ``.mcp.json`` to your project root. Use ``SCITEX_ENV_SRC``
to load all configuration from a ``.src`` file — this keeps ``.mcp.json`` static
across environments:

.. code-block:: json

   {
     "mcpServers": {
       "scitex": {
         "command": "scitex",
         "args": ["mcp", "start"],
         "env": {
           "SCITEX_ENV_SRC": "${SCITEX_ENV_SRC}"
         }
       }
     }
   }

Switch environments via your shell profile:

.. code-block:: bash

   # Local machine
   export SCITEX_ENV_SRC=~/.scitex/scitex/local.src

   # Remote server
   export SCITEX_ENV_SRC=~/.scitex/scitex/remote.src

Generate a template ``.src`` file:

.. code-block:: bash

   scitex env-template -o ~/.scitex/scitex/local.src

Or install globally:

.. code-block:: bash

   scitex mcp install

Complete Example
----------------

A typical research script combining session, I/O, plotting, and statistics:

.. code-block:: python

   import scitex as stx

   @stx.session
   def main(
       n=200,
       noise=0.1,
       CONFIG=stx.INJECTED,
       plt=stx.INJECTED,
       logger=stx.INJECTED,
   ):
       """Analyze noisy sine wave."""
       import numpy as np

       # Generate data
       x = np.linspace(0, 4 * np.pi, n)
       y_clean = np.sin(x)
       y_noisy = y_clean + np.random.normal(0, noise, n)

       # Save raw data
       stx.io.save({"x": x, "y_clean": y_clean, "y_noisy": y_noisy}, "data.npz")

       # Visualize
       fig, ax = plt.subplots()
       ax.plot_scatter(x, y_noisy, alpha=0.3, label="Noisy")
       ax.plot_line(x, y_clean, color="red", label="True")
       ax.set_xyt("x", "y", f"Sine Wave (noise={noise})")
       stx.io.save(fig, "sine.png")

       # Correlation between noisy and clean
       result = stx.stats.test_pearson(y_clean, y_noisy)
       logger.info(f"Pearson r={result['effect_size']:.3f}, p={result['pvalue']:.1e}")

       # Save summary
       stx.io.save({"r": result["effect_size"], "p": result["pvalue"]}, "stats.yaml")

       return 0

Next Steps
----------

- :doc:`core_concepts` -- Architecture and design principles
- :doc:`modules/index` -- Detailed module documentation
- :doc:`gallery` -- Plot examples
