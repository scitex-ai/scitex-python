MCP Server
==========

What is MCP?
------------

The `Model Context Protocol <https://modelcontextprotocol.io/>`_ (MCP) is
an open protocol that lets AI agents call external tools through a
standardized interface. Instead of generating code and hoping it works, an
agent can invoke a well-defined tool and receive structured results.

SciTeX implements an MCP server that exposes 120+ tools covering the full
research workflow. Any MCP-compatible client -- Claude Code, Cursor, or
custom agents -- can use these tools to conduct literature searches, run
statistics, create figures, and compile manuscripts.

Setup
-----

Add the following to ``.mcp.json`` in your project root:

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

Then set the environment source file in your shell profile:

.. code-block:: bash

   # Local machine
   export SCITEX_ENV_SRC=~/.scitex/scitex/local.src

   # Remote server
   export SCITEX_ENV_SRC=~/.scitex/scitex/remote.src

Generate a template ``.src`` file:

.. code-block:: bash

   scitex env-template -o ~/.scitex/scitex/local.src

Or install the MCP server globally:

.. code-block:: bash

   scitex mcp installation

Tool Categories
---------------

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
     - Scientific dataset access
   * - social
     - 7
     - Social media posting
   * - canvas
     - 7
     - Scientific figure canvas
   * - template
     - 6
     - Project scaffolding
   * - verify
     - 6
     - Reproducibility verification
   * - dev
     - 6
     - Ecosystem version management
   * - ui
     - 5
     - Notifications
   * - linter
     - 3
     - Code pattern checking

All tools accept JSON parameters and return structured results.

Example Workflow
----------------

A typical AI-driven research workflow chains tools across categories:

1. **Scholar** -- Search literature and download papers

   .. code-block:: text

      scholar_search_papers(query="neural oscillations gamma band")
      scholar_fetch_papers(dois=["10.1038/s41586-024-..."])

2. **Stats** -- Analyze experimental data

   .. code-block:: text

      stats_recommend_tests(data=[[1.2, 3.4, ...], [2.1, 4.5, ...]])
      stats_run_test(test="mann_whitney_u", groups=[[...], [...]])

3. **Plt** -- Create publication-ready figures

   .. code-block:: text

      plt_bar(data={"Control": [1,2,3], "Treatment": [4,5,6]},
              ylabel="Response", title="Figure 1")

4. **Writer** -- Compile the manuscript

   .. code-block:: text

      writer_compile_manuscript(project="my_paper")

The agent orchestrates these steps autonomously, passing outputs from one
tool as inputs to the next.
