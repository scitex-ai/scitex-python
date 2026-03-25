---
name: stx.scholar — Citation Formatting and Export
---

# stx.scholar — Citation Formatting and Export

All formatting functions work on plain Python dicts using the standard paper
dict schema. They have no ORM or database dependencies.

## Standard Paper Dict Schema

```python
{
    "title": str,
    "authors_str": str,        # "Smith, J. and Doe, A."
    "journal": str,
    "year": str,
    "doi": str,
    "pmid": str,
    "arxiv_id": str,
    "url": str,
    "abstract": str,
    "document_type": str,      # "article" | "preprint" | "book" | "chapter" |
                               # "conference" | "thesis" | "report" | "dataset"
    "citation_count": int,
    "impact_factor": float,
    "is_open_access": bool,
    "source": str,
    "volume": str,
    "number": str,
    "pages": str,
    "cite_key": str,           # optional; auto-generated if absent
}
```

---

## BibTeX

```python
from scitex.scholar import to_bibtex, papers_to_format

bibtex = to_bibtex(paper_dict)
# @article{smith2024,
#   title = {Deep Learning for EEG},
#   author = {Smith, John and Doe, Alice},
#   journal = {Nature Neuroscience},
#   year = {2024},
#   doi = {10.1038/xxx},
#   abstract = {We propose...},
# }

# Multiple papers
bibtex_block = papers_to_format(list_of_paper_dicts, fmt="bibtex")
```

### Document type → BibTeX entry type mapping

| document_type | BibTeX type |
|---|---|
| article | @article |
| preprint | @misc |
| book | @book |
| chapter | @inbook |
| conference | @inproceedings |
| thesis | @phdthesis |
| report | @techreport |
| dataset | @misc |

### arXiv-compatible cleaning

```python
from scitex.scholar import clean_bibtex_for_arxiv  # via __getattr__

clean = clean_bibtex_for_arxiv(bibtex_entry)
# Converts biblatex fields: journaltitle->journal, location->address, date->year
# Removes unsupported fields: url, urldate, file, abstract
```

---

## RIS Format

```python
from scitex.scholar import to_ris

ris = to_ris(paper_dict)
# TY  - JOUR
# TI  - Deep Learning for EEG
# AU  - Smith, John
# JO  - Nature Neuroscience
# PY  - 2024
# DO  - 10.1038/xxx
# ER  -

bibtex_block = papers_to_format(list_of_paper_dicts, fmt="ris")
```

---

## EndNote Format

```python
from scitex.scholar import to_endnote

enw = to_endnote(paper_dict)
# %0 Journal Article
# %T Deep Learning for EEG
# %A Smith, John
# %J Nature Neuroscience
# %D 2024
# %R 10.1038/xxx

bibtex_block = papers_to_format(list_of_paper_dicts, fmt="endnote")
```

---

## Text Citation Styles

```python
from scitex.scholar import to_text_citation

# APA (default)
citation = to_text_citation(paper_dict, style="apa")
# Smith, John (2024). Deep Learning for EEG. Nature Neuroscience, 15(3), 100-110. 10.1038/xxx

# MLA
citation = to_text_citation(paper_dict, style="mla")

# Chicago
citation = to_text_citation(paper_dict, style="chicago")

# Vancouver
citation = to_text_citation(paper_dict, style="vancouver")

# Dataset citation
citation = to_text_citation(paper_dict, style="apa", doc_type="dataset")
```

Supported styles: `apa`, `mla`, `chicago`, `vancouver`.

---

## CSV Row Export

```python
from scitex.scholar.formatting import to_csv_row  # internal, via __getattr__

row = to_csv_row(paper_dict)
# {"Title": "...", "Authors": "...", "Journal": "...", "Year": "...",
#  "DOI": "...", "PMID": "...", "URL": "...", "Abstract": "..."}
```

---

## Citation Key Generation

```python
from scitex.scholar import generate_cite_key, make_citation_key

# From paper dict (uses authors_str + year)
key = generate_cite_key(paper_dict)      # e.g. "smith2024"

# From components
key = make_citation_key("Smith", year=2024)   # "smith2024"
key = make_citation_key("van der Berg", year=2023)  # "vanderberg2023"
key = make_citation_key("Smith")              # "smith" (no year)
```

---

## Paper Dict Normalization

```python
from scitex.scholar.formatting import paper_normalize  # via __getattr__

# Normalize a raw API result to standard paper dict
normalized = paper_normalize({
    "title": "...",
    "authors": "Smith, J.",      # alias for authors_str
    "DOI": "10.xxx",             # alias for doi
    "snippet": "We show...",     # alias for abstract
    "externalUrl": "https://...", # alias for url
    "citations": 42,             # alias for citation_count
})
# Returns dict with canonical keys: title, authors_str, doi, abstract, url, citation_count, ...
```

---

## Format Extensions

```python
from scitex.scholar.formatting import FORMAT_EXTENSIONS

FORMAT_EXTENSIONS
# {"bibtex": ".bib", "endnote": ".enw", "ris": ".ris", "csv": ".csv", "json": ".json"}
```
