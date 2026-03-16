Writer Module (``stx.writer``)
==============================

LaTeX manuscript compilation, figure/table management, bibliography
handling, and IMRAD writing guidelines.

.. note::

   ``stx.writer`` wraps the standalone
   `scitex-writer <https://github.com/ywatanabe1989/scitex-writer>`_ package.
   Install with: ``pip install scitex-writer``.

Quick Reference
---------------

.. code-block:: python

   from scitex.writer import Writer
   from pathlib import Path

   writer = Writer(Path("my_paper"))

   # Compile manuscript → PDF
   result = writer.compile_manuscript()
   if result.success:
       print(f"PDF: {result.output_pdf}")

   # Compile supplementary materials
   result = writer.compile_supplementary()

   # Compile revision with change tracking
   result = writer.compile_revision(track_changes=True)

CLI Usage
---------

.. code-block:: bash

   # Compile
   scitex writer compile manuscript ./my-paper
   scitex writer compile supplementary ./my-paper
   scitex writer compile revision ./my-paper --track-changes

   # Bibliography
   scitex writer bib list ./my-paper
   scitex writer bib add ./my-paper "@article{...}"

   # Tables and figures
   scitex writer tables add ./my-paper data.csv
   scitex writer figures list ./my-paper

   # Writing guidelines
   scitex writer guidelines get abstract

Project Structure
-----------------

A writer project follows this layout:

.. code-block:: text

   my_paper/
   +-- 00_shared/
   |   +-- bibliography.bib
   |   +-- figures/
   |   +-- tables/
   +-- 01_manuscript/
   |   +-- main.tex
   |   +-- sections/
   +-- 02_supplementary/
   |   +-- main.tex
   +-- 03_revision/
       +-- main.tex

Create a new project:

.. code-block:: bash

   scitex template clone paper my_paper

Key Classes
-----------

- ``Writer`` -- Main entry point for compilation and project management
- ``CompilationResult`` -- Compilation outcome (success, output path, logs)
- ``ManuscriptTree`` -- Document tree for the main manuscript
- ``SupplementaryTree`` -- Document tree for supplementary materials
- ``RevisionTree`` -- Document tree for revision responses

Document Management
-------------------

**Figures:**

.. code-block:: python

   # Add figure (copies image + creates caption file)
   writer.add_figure("fig1", "plot.png", caption="Results")

   # List figures
   writer.list_figures()

   # Convert between formats
   writer.convert_figure("figure.pdf", "figure.png", dpi=300)

**Tables:**

.. code-block:: python

   # Add table from CSV
   writer.add_table("tab1", csv_content, caption="Demographics")

   # CSV ↔ LaTeX conversion
   writer.csv_to_latex("data.csv", "table.tex")
   writer.latex_to_csv("table.tex", "data.csv")

**Bibliography:**

.. code-block:: python

   # Add BibTeX entry
   writer.add_bibentry('@article{key, title={...}, ...}')

   # Merge multiple .bib files
   writer.merge_bibfiles(output_file="bibliography.bib")

Writing Guidelines
------------------

IMRAD guidelines for each manuscript section:

.. code-block:: bash

   scitex writer guidelines list
   scitex writer guidelines get introduction

.. code-block:: python

   from scitex.writer import guidelines

   # Get guideline for a section
   guide = guidelines.get("methods")

   # Build editing prompt: guideline + draft
   prompt = guidelines.build("discussion", draft_text)

Compilation Options
-------------------

.. code-block:: python

   result = writer.compile_manuscript(
       timeout=300,        # Max compilation time (seconds)
       no_figs=False,      # Exclude figures
       no_tables=False,    # Exclude tables
       draft=False,        # Draft mode (fast, lower quality)
       dark_mode=False,    # Dark color scheme
       quiet=False,        # Suppress output
   )

API Reference
-------------

.. automodule:: scitex.writer
   :members:
   :show-inheritance:
