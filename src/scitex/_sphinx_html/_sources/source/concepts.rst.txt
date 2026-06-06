Core Concepts
=============

This page explains the design patterns behind SciTeX. Understanding
these patterns will help you use the toolkit effectively and extend it
for your own workflows.


Modular Architecture
--------------------

SciTeX is not a monolith. Each module is backed by an independent
package that can be installed and used on its own:

.. code-block:: bash

   pip install scitex-io       # Use standalone: import scitex_io
   pip install scitex-stats    # Use standalone: import scitex_stats
   pip install figrecipe       # Use standalone: import figrecipe

When you install ``scitex``, these packages are available under a
unified namespace:

.. code-block:: python

   import scitex as stx

   stx.io.save(data, "out.csv")     # scitex-io
   stx.stats.run_test(...)          # scitex-stats
   stx.plt.subplots()               # figrecipe

**Lazy loading** ensures that importing ``scitex`` does not pull in every
dependency. Modules are loaded only when first accessed. If you never
touch ``stx.scholar``, its dependencies are never imported and startup
remains fast.

The main ``scitex`` package itself contains no runtime logic for I/O,
statistics, or plotting. It is an orchestrator: it re-exports
sub-package APIs, provides the CLI entry point, hosts the MCP server,
and owns the session decorator.


Session Decorator
-----------------

The ``@stx.session`` decorator converts a plain Python function into a
reproducible, CLI-enabled experiment.

.. code-block:: python

   import scitex as stx

   @stx.session
   def main(
       n_epochs=50,
       learning_rate=0.001,
       CONFIG=stx.session.INJECTED,
       logger=stx.session.INJECTED,
   ):
       logger.info(f"Training for {n_epochs} epochs at lr={learning_rate}")
       return 0

   if __name__ == "__main__":
       main()

**Why it exists.** Research scripts tend to accumulate boilerplate:
argument parsing, output directory creation, logging setup, random seed
management, config file loading. The session decorator handles all of
these so that the function body contains only experiment logic.

**What it provides:**

1. **Automatic CLI.** Function parameters become command-line arguments.
   ``n_epochs=50`` becomes ``--n-epochs 50`` with no argparse code.

2. **Config injection.** Parameters in ``./config/*.yaml`` are aggregated
   into a single ``CONFIG`` dict and injected at runtime.

3. **Reproducibility.** Random seeds are fixed. All parameters, stdout,
   and stderr are logged to the output directory.

4. **Output organization.** Each run gets a timestamped directory under
   ``script_out/``:

   .. code-block:: text

      script_out/FINISHED_SUCCESS/2026-03-18_14-30-00_AbC1/
      +-- CONFIGS/CONFIG.yaml    # All parameters
      +-- logs/stdout.log        # Captured output
      +-- logs/stderr.log        # Captured errors

Parameters marked ``stx.session.INJECTED`` are sentinel values. The
decorator replaces them with runtime objects (logger, config, plotting
backend, color palette, random generator). You never pass these
yourself -- they signal to the decorator what to inject.


Unified I/O
------------

``stx.io.save`` and ``stx.io.load`` provide a single interface for 30+
file formats. The format is determined by the file extension:

.. code-block:: python

   stx.io.save(dataframe, "results.csv")
   stx.io.save(array, "weights.npy")
   stx.io.save(fig, "figure.png")
   stx.io.save(config, "params.yaml")

The same call pattern works for every type. No need to remember
``pd.to_csv``, ``np.save``, ``fig.savefig``, or ``yaml.dump``.

**Figure data export.** When saving a matplotlib figure, SciTeX
automatically exports the plotted data as a CSV file alongside the
image. This is a deliberate design choice: every figure in a publication
should be backed by accessible data, so that reviewers and readers can
verify the plot independently.

.. code-block:: python

   stx.io.save(fig, "plot.png")
   # Creates: plot.png  (the image)
   #          plot.csv  (the underlying data)

This behavior is powered by figrecipe's ``RecordingFigure``, which
tracks all data passed to plotting calls and serializes it on save.


Three Interfaces
-----------------

Every SciTeX feature is accessible through three interfaces:

1. **Python API** -- for scripts and notebooks
2. **CLI** -- for shell workflows and automation
3. **MCP** -- for AI agents via the Model Context Protocol

For example, running a statistical test:

.. code-block:: python

   # Python API
   result = stx.stats.run_test("ttest_ind", group1, group2)

.. code-block:: bash

   # CLI
   scitex stats run ttest_ind --data data.csv

.. code-block:: text

   # MCP tool (called by AI agents)
   stats_run_test(test="ttest_ind", data=[[1,2,3],[4,5,6]])

This three-interface design means that any workflow a human builds in
Python can be replicated by an AI agent through MCP, or scripted in a
shell pipeline through the CLI. The interfaces share the same
underlying implementation, so behavior is identical across all three.

The MCP server aggregates 120+ tools from all sub-packages. AI agents
can discover available tools, read documentation, and execute full
research pipelines -- from literature search to manuscript compilation --
without human intervention.


Delegation Pattern
-------------------

The ``scitex`` package is intentionally thin. It delegates all domain
logic to standalone packages:

.. list-table::
   :header-rows: 1
   :widths: 25 25 50

   * - scitex module
     - Standalone package
     - Responsibility
   * - ``stx.io``
     - scitex-io
     - File I/O (30+ formats)
   * - ``stx.stats``
     - scitex-stats
     - Statistical testing (23 tests)
   * - ``stx.plt``
     - figrecipe
     - Publication-ready figures
   * - ``stx.writer``
     - scitex-writer
     - LaTeX manuscript compilation
   * - ``stx.scholar``
     - scitex-scholar
     - Literature search, PDF download
   * - ``stx.dataset``
     - scitex-dataset
     - Scientific dataset access

**Why delegation?** Each sub-package has its own release cycle, test
suite, and dependency tree. A bug fix in ``scitex-io`` does not require
releasing all of ``scitex``. Users who only need file I/O can
``pip install scitex-io`` without pulling in matplotlib, LaTeX tooling,
or audio dependencies.

From the user's perspective, the delegation is invisible. A single
``import scitex as stx`` provides access to everything. The lazy loader
in ``scitex.__init__`` resolves ``stx.io`` to the ``scitex_io`` package
on first access.


Configuration
--------------

SciTeX uses a layered configuration system:

**Project-level config (YAML files)**

Place YAML files in ``./config/`` at your project root. The session
decorator aggregates all files in this directory into a single ``CONFIG``
dict:

.. code-block:: text

   config/
   +-- model.yaml      # {"hidden_size": 256, "n_layers": 4}
   +-- training.yaml   # {"epochs": 100, "batch_size": 32}

.. code-block:: python

   @stx.session
   def main(CONFIG=stx.session.INJECTED):
       print(CONFIG["hidden_size"])  # 256
       print(CONFIG["epochs"])       # 100

**Environment-level config (.env.d/)**

Credentials, API keys, and machine-specific paths live in ``.env.d/``:

.. code-block:: text

   .env.d/
   +-- entry.src            # Single entry point (source this)
   +-- 00_scitex.env        # Base paths
   +-- 01_scholar.env       # OpenAthens credentials
   +-- 01_audio.env         # TTS backend config

Source the entry point in your shell profile:

.. code-block:: bash

   # In ~/.bashrc or ~/.zshrc
   source /path/to/.env.d/entry.src

**MCP environment (.src files)**

For AI agent deployments, a single ``.src`` file bundles all environment
variables. The MCP server loads it at startup via ``SCITEX_ENV_SRC``:

.. code-block:: bash

   export SCITEX_ENV_SRC=~/.scitex/scitex/local.src

This keeps the ``.mcp.json`` configuration static across machines --
only the ``.src`` file changes between local and remote environments.

The configuration hierarchy is: CLI arguments override YAML config,
which overrides environment variables, which override built-in defaults.
