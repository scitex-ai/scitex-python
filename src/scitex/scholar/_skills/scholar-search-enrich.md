---
name: stx.scholar — Search, Enrichment, and Loading
---

# stx.scholar — Search, Enrichment, and Loading

## Search

`Scholar.search_library()` searches papers already stored in the local library.
For discovering new papers, the recommended workflow is to use
[AI2 Scholar QA](https://scholarqa.allen.ai/chat/) and then load the exported
BibTeX with `scholar.load_bibtex()`.

```python
scholar = Scholar(project="eeg_2024")

# Search local library
papers = scholar.search_library("seizure detection")

# Search across all projects
papers = scholar.search_across_projects("EEG classification")

# Search in specific projects only
papers = scholar.search_across_projects(
    "deep learning",
    projects=["eeg_2024", "neural_nets"]
)
```

### search_library signature

```python
Scholar.search_library(
    query: str,
    project: Optional[str] = None,   # defaults to self.project
) -> Papers
```

The search scans `metadata.basic.title`, `metadata.basic.abstract`, and
`metadata.basic.authors` fields from stored `metadata.json` files.

---

## Loading Papers

### From BibTeX file

```python
papers = scholar.load_bibtex("papers.bib")     # file path
papers = scholar.load_bibtex(Path("~/data/papers.bib"))

# Works with raw BibTeX content too
bibtex_str = "@article{smith2024, title={...}, ...}"
papers = scholar.load_bibtex(bibtex_str)
```

`BibTeXHandler.papers_from_bibtex()` auto-detects whether the input is a path
or raw content. Validates syntax before loading when `validate=True` (default).

### From a project directory

```python
papers = scholar.load_project("eeg_2024")
# Loads all papers whose metadata.json files are in the project's symlink tree
```

### From Connected Papers export

```python
from scitex.scholar import from_connected_papers, to_connected_papers

# Import a Connected Papers graph by paper ID
result = from_connected_papers("649def34f8be52c8b66281af98ae884c09aef38b")
# result is a CitationGraph or Papers collection

# Export back for Connected Papers web UI
to_connected_papers(result, output="./export")
```

---

## Metadata Enrichment

`scholar.enrich_papers()` queries `ScholarEngine` (CrossRef, Semantic Scholar,
OpenAlex, PubMed, arXiv) to fill in missing fields. It also populates
impact factors using the embedded JCR data from the `impact_factor` package.

```python
papers = scholar.load_bibtex("papers.bib")
enriched = scholar.enrich_papers(papers)

# Or async
enriched = await scholar.enrich_papers_async(papers)
```

### What gets enriched

- `metadata.basic.abstract` — from Semantic Scholar / CrossRef
- `metadata.citation_count.total` — from Semantic Scholar
- `metadata.citation_count.y20xx` — yearly breakdown from Semantic Scholar
- `metadata.publication.impact_factor` — from JCR data via `ImpactFactorEngine`
- `metadata.id.doi` — resolved from title when missing
- `metadata.access.is_open_access` — from OA detection
- All fields record their source in the corresponding `*_engines` list

### Enrichment config

```python
# Disable impact factor enrichment
config = ScholarConfig()
config.cascade.set("enrich_impact_factors", False)
scholar = Scholar(config=config)

# Auto-enrich is on by default when enable_auto_enrich=True (default)
```

### ScholarEngine (internal)

`Scholar._scholar_engine` is a `ScholarEngine` instance that searches across
multiple databases. It is lazy-loaded (created on first access).

Individual engine files live in:
`src/scitex/scholar/metadata_engines/individual/`

---

## Open Access Detection (standalone)

```python
from scitex.scholar.core import (
    check_oa_status,
    check_oa_status_async,
    detect_oa_from_identifiers,
    is_arxiv_id,
    is_open_access_journal,
    is_open_access_source,
    OAResult,
    OAStatus,
)

result: OAResult = check_oa_status(
    doi="10.1038/s41598-017-02626-y",
    arxiv_id=None,
    pmcid=None,
    source=None,
    journal="Scientific Reports",
    is_open_access_flag=None,
    use_unpaywall=True,
)

# OAStatus values: gold, green, bronze, hybrid, closed
print(result.is_open_access)  # bool
print(result.status)           # OAStatus enum
print(result.oa_url)           # URL to OA version or None
print(result.license)          # e.g. "CC-BY"
print(result.source)           # which detection method was used

# Quick detection without API
result = detect_oa_from_identifiers(
    doi="10.48550/arXiv.1706.03762",
    arxiv_id="1706.03762",
    journal="arXiv",
)
```

---

## Journal Normalization

```python
from scitex.scholar.core import (
    JournalNormalizer,
    normalize_journal_name,
    get_journal_issn_l,
    is_same_journal,
    refresh_journal_cache,
)

# Normalize a journal name to canonical form
canonical = normalize_journal_name("Nat. Neurosci.")
# -> "Nature Neuroscience"

# Check if two names refer to the same journal
same = is_same_journal("J. Neurosci.", "The Journal of Neuroscience")

# Get ISSN-L for a journal
issn_l = get_journal_issn_l("Nature")

# Using the class directly
normalizer = JournalNormalizer()
canonical = normalizer.normalize("PNAS")
```
