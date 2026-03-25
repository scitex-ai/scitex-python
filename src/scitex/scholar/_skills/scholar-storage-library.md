---
name: stx.scholar — Storage, Library, and Project Management
---

# stx.scholar — Storage, Library, and Project Management

## Library Directory Structure

```
~/.scitex/scholar/library/
├── MASTER/
│   ├── A1B2C3D4/              # 8-digit hex ID
│   │   ├── metadata.json      # Full Paper model as JSON
│   │   ├── paper.pdf          # Downloaded PDF (if available)
│   │   └── attachments/       # Supplementary files
│   └── E5F6A7B8/
│       └── metadata.json
└── my_project/
    ├── info/
    │   └── project_metadata.json
    ├── A1B2C3D4 -> ../MASTER/A1B2C3D4   # Symlink to master
    └── E5F6A7B8 -> ../MASTER/E5F6A7B8
```

No paper data is duplicated. Projects hold only symlinks into `MASTER/`.

---

## Project Management

```python
scholar = Scholar()

# Create a project (auto-creates directory + project_metadata.json)
scholar._ensure_project_exists("eeg_seizure", description="EEG seizure detection papers")

# List all projects
projects = scholar.list_projects()
# [{"name": "eeg_seizure", "description": "...", "created": "...", "paper_count": 12}, ...]

# Get library-wide statistics
stats = scholar.get_library_statistics()
# {
#   "total_projects": 3,
#   "total_papers": 75,
#   "storage_mb": 412.5,
#   "library_path": "/home/user/.scitex/scholar/library",
#   "master_path": "/home/user/.scitex/scholar/library/MASTER",
#   "projects": [...]
# }

# Back up the library
info = scholar.backup_library("/backups/")
```

---

## Saving Papers to Library

```python
# Save a Papers collection to library (creates MASTER entries + project symlinks)
saved_ids = scholar.save_papers_to_library(papers)
# Returns list of 8-digit IDs: ["A1B2C3D4", "E5F6A7B8", ...]

# Save as BibTeX file with enrichment metadata
bibtex_content = scholar.save_papers_as_bibtex(papers, output_path="output.bib")
```

---

## BibTeX Validation

```python
from scitex.scholar.storage import (
    validate_bibtex_file,
    validate_bibtex_content,
    BibTeXValidator,
    ValidationResult,
    ValidationIssue,
    ValidationSeverity,
)

# Validate a file
result: ValidationResult = validate_bibtex_file("papers.bib")
result.is_valid        # bool
result.issues          # List[ValidationIssue]

# Validate content string
result = validate_bibtex_content(bibtex_string)

for issue in result.issues:
    print(issue.severity)  # ValidationSeverity.ERROR or .WARNING
    print(issue.message)
    print(issue.entry_key)

# Using class directly
validator = BibTeXValidator()
result = validator.validate_file("papers.bib")
```

---

## BibTeX Handler

`BibTeXHandler` converts between BibTeX text and `Paper` objects.
It is used internally by `scholar.load_bibtex()`.

```python
from scitex.scholar.storage import BibTeXHandler

handler = BibTeXHandler(project="my_project", config=scholar.config)

# Load papers from file or content
papers_list = handler.papers_from_bibtex("papers.bib")
papers_list = handler.papers_from_bibtex(bibtex_content_string)

# Convert Papers back to BibTeX string
bibtex_str = handler.papers_to_bibtex(papers_collection, output_path="out.bib")
```

---

## PaperIO (individual paper I/O)

`PaperIO` handles reading and writing of individual `metadata.json` files in
the library.

```python
from scitex.scholar.storage import PaperIO

paper_io = PaperIO(config=scholar.config)

# Load a paper from its MASTER directory
paper = paper_io.load_paper("A1B2C3D4")

# Save a paper to library (returns the 8-digit ID)
paper_id = paper_io.save_paper(paper, project="eeg_seizure")
```

---

## ScholarLibrary (high-level)

`ScholarLibrary` is the high-level wrapper used by `Scholar._library`.

```python
from scitex.scholar.storage import ScholarLibrary

library = ScholarLibrary(project="eeg_seizure", config=scholar.config)

# Load all papers in a project
papers_list = library.load_papers()

# Save a paper
paper_id = library.save_paper(paper)

# Parse BibTeX into Paper list
papers_list = library.papers_from_bibtex("papers.bib")
```

---

## ScholarConfig: Path Resolution

```python
from scitex.scholar import ScholarConfig

config = ScholarConfig()

# Key paths
config.path_manager.library_dir            # ~/.scitex/scholar/library
config.get_library_master_dir()            # ~/.scitex/scholar/library/MASTER
config.get_library_project_dir("proj")     # ~/.scitex/scholar/library/proj
config.path_manager.get_workspace_dir()    # ~/.scitex/scholar

# Configuration resolution (priority: direct > config file > env var > default)
config.resolve("project", direct_val=None, default="default")
config.resolve("enable_auto_enrich", None, True, type=bool)
```

### Environment variables

| Variable | Purpose |
|---|---|
| `SCITEX_DIR` | Override `~/.scitex` base directory |
| `SCITEX_SCHOLAR_PROJECT` | Default project name |
| `SCITEX_SCHOLAR_ENABLE_AUTO_ENRICH` | Enable/disable auto-enrichment |
| `SCITEX_SCHOLAR_USE_CACHE_DOWNLOAD` | Cache URL finder results |
| `SCITEX_SCHOLAR_2CAPTCHA_API_KEY` | 2captcha key for CAPTCHA solving |

---

## Filtering (standalone, dict-based)

`apply_filters` operates on plain dicts (no Paper objects required).
It is used internally by the web search interface.

```python
from scitex.scholar import apply_filters

filtered = apply_filters(
    papers=list_of_dicts,
    filters={
        "year_from": 2020,
        "year_to": 2024,
        "min_citations": 50,
        "max_citations": 10000,
        "min_impact_factor": 3.0,
        "max_impact_factor": 20.0,
        "authors": ["Smith"],        # name substring list
        "journal": "Nature",         # journal substring
        "open_access": True,
        "doc_type": "review",        # "review" | "preprint"
        "language": "english",
    },
    parsed_operators={
        "title_includes": ["deep learning"],
        "title_excludes": ["survey"],
        "author_includes": ["LeCun"],
        "journal_includes": ["science"],
        "year_min": 2019,
        "citations_min": 100,
    }
)
```
