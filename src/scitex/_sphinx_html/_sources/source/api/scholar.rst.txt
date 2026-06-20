Scholar Module (``stx.scholar``)
=================================

Literature management: search papers, download PDFs, enrich BibTeX,
and organize a local library across multiple projects.

Quick Reference
---------------

.. code-block:: python

   from scitex.scholar import Scholar

   scholar = Scholar(project="my_research")

   # Load and enrich BibTeX
   papers = scholar.load_bibtex("references.bib")
   enriched = scholar.enrich_papers(papers)
   # Adds: DOIs, abstracts, citation counts, impact factors

   # Save to library and export
   scholar.save_papers_to_library(enriched)
   scholar.save_papers_as_bibtex(enriched, "enriched.bib")

   # Search your library
   results = scholar.search_library("neural oscillations")

   # Download PDFs
   scholar.download_pdfs(dois, output_dir)

CLI Usage
---------

.. code-block:: bash

   # Full pipeline from BibTeX
   scitex scholar bibtex refs.bib --project myresearch --num-workers 8

   # Search papers
   scitex scholar search "deep learning EEG"

   # Download PDFs
   scitex scholar download --doi 10.1038/nature12373

   # Institutional authentication
   scitex scholar auth --method openathens
   scitex scholar auth --method shibboleth --institution "MIT"

Data Sources
------------

Searches and enriches from:

- **CrossRef** (167M+ papers) -- DOI resolution, citation counts
- **Semantic Scholar** -- Abstracts, references, influence scores
- **PubMed** -- Biomedical literature
- **arXiv** -- Preprints
- **OpenAlex** (284M+ works) -- Open metadata

Key Classes
-----------

- ``Scholar`` -- Main entry point (search, enrich, download, organize)
- ``Paper`` -- Type-safe metadata container (Pydantic model)
- ``Papers`` -- Collection with filtering, sorting, and export
- ``ScholarConfig`` -- YAML-based configuration
- ``ScholarLibrary`` -- Local library storage and caching

Paper Metadata
--------------

Each ``Paper`` contains structured metadata sections:

.. code-block:: python

   paper.metadata.basic          # title, authors, year, abstract, keywords
   paper.metadata.id             # DOI, arXiv, PMID, Semantic Scholar ID
   paper.metadata.publication    # journal, impact factor, volume, issue
   paper.metadata.citation_count # total + yearly breakdown (2015--2024)
   paper.metadata.url            # DOI URL, publisher, arXiv, PDFs
   paper.metadata.access         # open access status, license

Filtering and Sorting
---------------------

.. code-block:: python

   # Criteria-based filtering
   recent = papers.filter(year_min=2020, has_doi=True)
   elite = papers.filter(min_impact_factor=10, min_citations=500)

   # Lambda filtering
   custom = papers.filter(lambda p: "EEG" in (p.metadata.basic.title or ""))

   # Sorting
   papers.sort_by("year", reverse=True)
   papers.sort_by("citation_count", reverse=True)

   # Chaining
   top_recent = papers.filter(year_min=2020).sort_by("citation_count", reverse=True)

Project Organization
--------------------

.. code-block:: python

   scholar = Scholar(project="review_paper")
   scholar.list_projects()
   papers = scholar.load_project()

   # Export to multiple formats
   scholar.save_papers_as_bibtex(papers, "output.bib")
   papers.to_dataframe()  # pandas DataFrame

Storage Architecture
--------------------

.. code-block:: text

   ~/.scitex/scholar/library/
   +-- MASTER/                     # Centralized master storage
   |   +-- 8DIGIT01/              # Hash-based unique ID from DOI
   |   |   +-- metadata.json
   |   |   +-- paper.pdf
   +-- project_name/               # Project-specific symlinks
       +-- Author-Year-Journal -> ../MASTER/8DIGIT01

API Reference
-------------

.. automodule:: scitex.scholar
   :members:
   :show-inheritance:
