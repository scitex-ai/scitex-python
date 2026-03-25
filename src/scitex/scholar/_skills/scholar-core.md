---
name: stx.scholar — Core Classes (Scholar, Paper, Papers)
---

# stx.scholar — Core Classes

## Scholar

The main entry point. Inherits from 10 mixins covering search, enrichment,
loading, saving, PDF download, URL finding, project management, library
management, pipeline, and service initialization.

```python
from scitex.scholar import Scholar, ScholarConfig

# Default initialization — config auto-discovered from ~/.scitex/scholar/
scholar = Scholar()

# With explicit project
scholar = Scholar(project="my_project", project_description="EEG papers 2024")

# With custom config
config = ScholarConfig(scholar_dir="/data/users/alice/.scitex")
scholar = Scholar(config=config)

# Disable auto-enrichment
config = ScholarConfig()
config.cascade.set("enable_auto_enrich", False)
scholar = Scholar(config=config)
```

### Scholar.__init__ signature

```python
Scholar(
    config: Optional[Union[ScholarConfig, str, Path]] = None,
    project: Optional[str] = None,
    project_description: Optional[str] = None,
    browser_mode: Optional[str] = None,   # 'stealth' | 'interactive' | 'manual'
)
```

### Internal services (lazy-loaded, private)

| Property | Type | Purpose |
|---|---|---|
| `_scholar_engine` | `ScholarEngine` | Metadata search and DOI resolution |
| `_auth_manager` | `ScholarAuthManager` | Institution login / cookie management |
| `_browser_manager` | `ScholarBrowserManager` | Playwright browser for PDF download |
| `_library_manager` | `LibraryManager` | Low-level library file operations |
| `_library` | `ScholarLibrary` | High-level library operations |

---

## Paper

Pydantic model with structured, source-tracked metadata.

```python
from scitex.scholar import Paper

paper = Paper()
paper.metadata.basic.title = "Attention Is All You Need"
paper.metadata.basic.authors = ["Vaswani, Ashish", "Shazeer, Noam"]
paper.metadata.basic.year = 2017
paper.metadata.publication.journal = "NeurIPS"
paper.metadata.publication.impact_factor = 12.3

# Setting DOI auto-syncs url.doi
paper.metadata.set_doi("10.48550/arXiv.1706.03762")
# paper.metadata.url.doi == "https://doi.org/10.48550/arXiv.1706.03762"

# Citation counts with year breakdown
paper.metadata.citation_count.total = 85000
paper.metadata.citation_count.y2024 = 15000

# Serialization
data = paper.to_dict()        # JSON-safe dict (uses aliases like "2024" not y2024)
paper2 = Paper.from_dict(data) # Reconstruct from dict
```

### Metadata sections

| Section | Key fields |
|---|---|
| `metadata.id` | `doi`, `arxiv_id`, `pmid`, `corpus_id`, `semantic_id` |
| `metadata.basic` | `title`, `authors`, `year`, `abstract`, `keywords`, `type` |
| `metadata.citation_count` | `total`, `y2024`, `y2023`, … `y2015` (aliases: `"2024"`, etc.) |
| `metadata.publication` | `journal`, `short_journal`, `impact_factor`, `issn`, `volume`, `issue`, `pages`, `publisher` |
| `metadata.url` | `doi`, `publisher`, `arxiv`, `pdfs`, `openurl_query`, `openurl_resolved` |
| `metadata.path` | `pdfs`, `supplementary_files`, `additional_files` |
| `metadata.access` | `is_open_access`, `oa_status`, `oa_url`, `license` |
| `metadata.system` | `searched_by_CrossRef`, `searched_by_OpenAlex`, etc. |
| `container` | `scitex_id`, `library_id`, `projects`, `readable_name`, `created_at` |

Every field has a parallel `*_engines` list recording which data source populated it.

### Open access detection

```python
# Quick check (no API calls, uses identifiers)
is_oa = paper.is_open_access   # property

# Full check with optional Unpaywall API
from scitex.scholar.core import OAResult
result: OAResult = paper.detect_open_access(use_unpaywall=True, update_metadata=True)
# result.is_open_access, result.status (gold/green/bronze/closed), result.oa_url
```

---

## Papers

A minimal collection of `Paper` objects. Business logic lives in `Scholar`.

```python
from scitex.scholar import Papers, Paper

papers = Papers([paper1, paper2], project="my_project")

# Iteration
for p in papers:
    print(p.metadata.basic.title)

# Indexing / slicing
first = papers[0]          # Paper
subset = papers[0:5]       # Papers

len(papers)                # int
repr(papers)               # "Papers(count=2, project=my_project)"
```

### Papers.filter()

```python
# By lambda (any Paper field)
high_if = papers.filter(lambda p: p.metadata.publication.impact_factor and
                                   p.metadata.publication.impact_factor > 10)

# By named criteria
filtered = papers.filter(
    year_min=2020,
    year_max=2024,
    has_doi=True,
    has_abstract=True,
    has_pdf=True,
    min_citations=100,
    max_citations=5000,
    min_impact_factor=3.0,
    max_impact_factor=20.0,
    journal="Nature",
    author="Smith",
    keyword="deep learning",
    publisher="Springer",
)
```

### Papers.sort_by()

```python
papers_sorted = papers.sort_by("impact_factor", reverse=True)
papers_sorted = papers.sort_by("year")
papers_sorted = papers.sort_by("citation_count", reverse=True)
```

### Papers.save()

```python
papers.save("output.bib")     # BibTeX
papers.save("output.ris")     # RIS
papers.save("output.csv")     # CSV
papers.save("output.json")    # JSON
```

### Papers collection methods

```python
papers.append(paper)              # Add one paper
papers.extend(other_papers)       # Add from list or Papers
papers.to_list()                  # List[Paper]
papers.to_dict()                  # List[dict]
papers.to_dataframe()             # pandas DataFrame
papers.summary()                  # dict with statistics
Papers.from_bibtex("file.bib")    # Class method: load from BibTeX
```
