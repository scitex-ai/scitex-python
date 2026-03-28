---
name: stx.scholar
description: Scientific literature management — search, enrich BibTeX, download PDFs, and manage paper libraries.
---

# stx.scholar — Index

Complete scientific literature management for SciTeX.

## Sub-Skills

| File | Contents |
|---|---|
| [scholar-core.md](scholar-core.md) | `Scholar`, `Paper`, `Papers` — class signatures, metadata structure, filtering, sorting, serialization |
| [scholar-search-enrich.md](scholar-search-enrich.md) | Library search, `load_bibtex`, `load_project`, `enrich_papers`, open access detection, journal normalization |
| [scholar-formatting.md](scholar-formatting.md) | `to_bibtex`, `to_ris`, `to_endnote`, `to_text_citation`, citation key generation, paper dict normalization |
| [scholar-storage-library.md](scholar-storage-library.md) | Library directory layout, project management, `BibTeXHandler`, `BibTeXValidator`, `PaperIO`, `ScholarLibrary`, `apply_filters` |
| [scholar-pdf-auth.md](scholar-pdf-auth.md) | Authentication (OpenAthens/EZProxy/Shibboleth), `ScholarBrowserManager`, PDF download pipeline, OpenURL resolution |
| [scholar-citation-graph.md](scholar-citation-graph.md) | `CitationGraphBuilder`, `PaperNode`, `CitationEdge`, `CitationGraph`, visualization backends |
| [scholar-cli.md](scholar-cli.md) | `python -m scitex.scholar` subcommands: `single`, `parallel`, `bibtex`, `mcp` |
| [scholar-mcp.md](scholar-mcp.md) | MCP tools for AI agents — all tool names, auth, jobs, Crossref/OpenAlex integration |

---

## Typical 5-Minute Workflow

```python
from scitex.scholar import Scholar

scholar = Scholar(project="my_pac")

# 1. Load BibTeX from AI2 Scholar QA export
papers = scholar.load_bibtex("papers.bib")          # Papers(count=75)

# 2. Enrich with metadata (abstracts, citations, impact factors)
enriched = scholar.enrich_papers(papers)

# 3. Filter to high-quality papers
good = enriched.filter(min_impact_factor=3.0, year_min=2018, has_doi=True)

# 4. Save enriched BibTeX
scholar.save_papers_as_bibtex(good, "papers_enriched.bib")

# 5. Download PDFs
results = await scholar.download_pdfs_from_dois_async(
    [p.metadata.id.doi for p in good if p.metadata.id.doi]
)
```

---

## Public API (`from scitex.scholar import ...`)

```
Scholar           — main interface
Paper             — Pydantic paper model
Papers            — collection of Paper objects
ScholarConfig     — configuration (path resolution, cascade config)
CitationGraphBuilder  — build citation networks
plot_citation_graph   — visualize citation graphs
to_bibtex         — format paper dict as BibTeX
to_ris            — format as RIS
to_endnote        — format as EndNote
to_text_citation  — APA / MLA / Chicago / Vancouver text
papers_to_format  — batch format list of dicts
generate_cite_key — BibTeX key from paper dict
make_citation_key — BibTeX key from author/year components
apply_filters     — filter list of paper dicts
from_connected_papers  — import Connected Papers graph
to_connected_papers    — export to Connected Papers format
```

### Available via `__getattr__` (internal helpers)

```
ScholarAuthManager     ScholarBrowserManager   ScholarEngine
ScholarPDFDownloader   ScholarLibrary          ScholarURLFinder
ensure_workspace       normalize_search_filename
clean_bibtex_for_arxiv clean_text              paper_normalize
paper_from_search_result  sanitize_filename    to_csv_row
```
