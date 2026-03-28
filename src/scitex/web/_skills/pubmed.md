---
description: Search PubMed for papers matching a query with search_pubmed() and retrieve Crossref citation counts with get_crossref_metrics().
---

# PubMed Search

## search_pubmed

Query PubMed and return structured results including abstracts, authors, and DOIs.

```python
search_pubmed(
    query: str,
    max_results: int = 20,
    email: str | None = None,
) -> list[dict]
```

```python
import scitex as stx

papers = stx.web.search_pubmed("EEG epilepsy deep learning", max_results=10)
for p in papers:
    print(p["title"], p.get("doi"))
```

Each result dict contains: `pmid`, `title`, `abstract`, `authors`, `journal`, `year`, `doi`.

---

## get_crossref_metrics

Retrieve citation count and journal impact factor for a DOI via the Crossref API.

```python
get_crossref_metrics(doi: str) -> dict
```

```python
import scitex as stx

metrics = stx.web.get_crossref_metrics("10.1038/s41586-021-03819-2")
print(metrics)
# {'cited_by': 523, 'journal': 'Nature', 'type': 'journal-article'}
```
