---

# stx.scholar — CLI Interface

Invoked as `python -m scitex.scholar`. Provides four subcommands.

## Subcommands at a Glance

```
python -m scitex.scholar <command> [options]

Commands:
  single    Process one paper by DOI or title
  parallel  Process multiple papers from a file of DOIs/titles
  bibtex    Process papers from a BibTeX file
  mcp       Start MCP server for LLM integration
```

---

## single — Process one paper

Full pipeline: DOI resolve → URL find → PDF download → library storage.

```bash
python -m scitex.scholar single \
    --doi 10.1038/s41598-017-02626-y \
    --project eeg_seizure

python -m scitex.scholar single \
    --title "Attention Is All You Need" \
    --project transformers
```

---

## parallel — Process multiple papers

```bash
python -m scitex.scholar parallel \
    --dois-file dois.txt \
    --project eeg_seizure \
    --max-concurrent 1
```

`dois.txt` — one DOI per line.

---

## bibtex — Process a BibTeX file

The most common workflow. Load → filter → enrich → download → save.

```bash
# Step 1: Enrich BibTeX (adds abstracts, citation counts, impact factors)
python -m scitex.scholar bibtex \
    --bibtex papers.bib \
    --project eeg_seizure \
    --enrich \
    --output papers_enriched.bib

# Step 2: Download PDFs for enriched papers
python -m scitex.scholar bibtex \
    --bibtex papers_enriched.bib \
    --project eeg_seizure \
    --download

# Force re-download (clears URL finder cache)
python -m scitex.scholar bibtex \
    --bibtex papers_enriched.bib \
    --project eeg_seizure \
    --download-force
```

### Filter flags for bibtex command

```bash
--year-min 2018          # Papers from 2018 onwards
--year-max 2024          # Papers up to 2024
--min-citations 50       # Minimum citation count
--min-impact-factor 3.0  # Minimum journal impact factor
--has-pdf                # Only papers that have a PDF URL
```

### Recommended two-step workflow

Running `--enrich` and `--download` in the same call works but is less
reliable. Preferred approach:

```bash
# Step 1: enrich only
python -m scitex.scholar bibtex --bibtex input.bib --project proj --enrich --output enriched.bib

# Step 2: download only
python -m scitex.scholar bibtex --bibtex enriched.bib --project proj --download
```

---

## mcp — Start MCP server

```bash
python -m scitex.scholar mcp
# Starts FastMCP server exposing scholar tools to AI agents
```

MCP tools exposed:
- `scholar_search_papers`, `scholar_fetch_papers`
- `scholar_parse_bibtex`, `scholar_enrich_bibtex`
- `scholar_resolve_dois`, `scholar_resolve_openurls`
- `scholar_download_pdfs_batch`, `scholar_validate_pdfs`
- `scholar_parse_pdf_content`
- `scholar_create_project`, `scholar_list_projects`, `scholar_add_papers_to_project`
- `scholar_export_papers`
- `scholar_authenticate`, `scholar_check_auth_status`, `scholar_logout`
- `scholar_get_library_status`
- `scholar_start_job`, `scholar_get_job_status`, `scholar_get_job_result`,
  `scholar_list_jobs`, `scholar_cancel_job`

---

## DOI operations (CLI)

```bash
# Resolve DOIs for papers with titles
python -m scitex.scholar --doi 10.1038/xxx --project proj --enrich

# Multiple DOIs
python -m scitex.scholar --dois 10.1038/aaa 10.1002/bbb --project proj --download
```

---

## Project operations (CLI)

```bash
# List projects
python -m scitex.scholar project list

# Create a project
python -m scitex.scholar project create --name new_project --description "..."
```

---

## Environment variables affecting CLI behaviour

| Variable | Default | Effect |
|---|---|---|
| `SCITEX_DIR` | `~/.scitex` | Scholar data root |
| `SCITEX_SCHOLAR_PROJECT` | `default` | Default project name |
| `SCITEX_SCHOLAR_USE_CACHE_DOWNLOAD` | `true` | Cache URL finder results |
| `SCITEX_SCHOLAR_2CAPTCHA_API_KEY` | — | CAPTCHA solving key |
