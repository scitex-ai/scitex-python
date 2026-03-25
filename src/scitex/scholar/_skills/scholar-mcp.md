---
name: stx.scholar — MCP Interface (AI Agent Tools)
---

# stx.scholar — MCP Interface

The MCP server exposes Scholar functionality as tools for AI agents (Claude,
GPT, etc.) via the Model Context Protocol. Start it with:

```bash
python -m scitex.scholar mcp
```

---

## Tool Groups

### Search and Fetch

| Tool | Purpose |
|---|---|
| `scholar_search_papers` | Search academic databases by query string |
| `scholar_fetch_papers` | Fetch paper metadata by DOI list |
| `scholar_get_library_status` | Get library statistics |

### BibTeX Operations

| Tool | Purpose |
|---|---|
| `scholar_parse_bibtex` | Parse BibTeX file into paper records |
| `scholar_enrich_bibtex` | Enrich BibTeX with abstracts, citation counts, impact factors |
| `scholar_export_papers` | Export papers collection to BibTeX/RIS/CSV/JSON |

### DOI and URL Resolution

| Tool | Purpose |
|---|---|
| `scholar_resolve_dois` | Resolve DOIs for papers that only have titles |
| `scholar_resolve_openurls` | Resolve institution access URLs via OpenURL |

### PDF Handling

| Tool | Purpose |
|---|---|
| `scholar_download_pdfs_batch` | Download PDFs for a list of DOIs |
| `scholar_validate_pdfs` | Check that downloaded PDFs contain paper content |
| `scholar_parse_pdf_content` | Extract sections from a PDF file |

### Project Management

| Tool | Purpose |
|---|---|
| `scholar_create_project` | Create a new project in the library |
| `scholar_list_projects` | List all projects |
| `scholar_add_papers_to_project` | Add papers (by DOI) to an existing project |

### Authentication

| Tool | Purpose |
|---|---|
| `scholar_authenticate` | Trigger institution login (OpenAthens/EZProxy) |
| `scholar_check_auth_status` | Check if currently authenticated |
| `scholar_logout` | Clear auth cookies |

### Async Jobs

Long-running operations (e.g., batch PDF download) are handled as jobs.

| Tool | Purpose |
|---|---|
| `scholar_start_job` | Start a long-running job |
| `scholar_get_job_status` | Poll job status |
| `scholar_get_job_result` | Retrieve job result when complete |
| `scholar_list_jobs` | List all jobs |
| `scholar_cancel_job` | Cancel a running job |

---

## Example: AI agent workflow

```python
# Typical agent workflow using MCP tools:

# 1. Check if enriched BibTeX already exists
result = mcp__scitex__scholar_get_library_status()

# 2. Parse existing BibTeX
papers = mcp__scitex__scholar_parse_bibtex(bibtex_file="papers.bib", project="myproject")

# 3. Resolve missing DOIs
resolved = mcp__scitex__scholar_resolve_dois(project="myproject")

# 4. Enrich with metadata
enriched = mcp__scitex__scholar_enrich_bibtex(
    bibtex_file="papers.bib",
    project="myproject",
    output="papers_enriched.bib"
)

# 5. Download PDFs
job_id = mcp__scitex__scholar_start_job(
    operation="download_pdfs",
    project="myproject"
)
status = mcp__scitex__scholar_get_job_status(job_id=job_id)
```

---

## Crossref via MCP

Separate crossref MCP tools provide access to local Crossref database:

```
mcp__scitex__crossref_search          Search Crossref local DB
mcp__scitex__crossref_search_by_doi   Look up by DOI
mcp__scitex__crossref_enrich_dois     Bulk enrich from Crossref
mcp__scitex__crossref_check_bibtex_file   Check BibTeX against Crossref
mcp__scitex__crossref_check_citations     Validate citation keys
mcp__scitex__crossref_status          Check Crossref DB status
```

## OpenAlex via MCP

```
mcp__scitex__openalex_search          Search OpenAlex
mcp__scitex__openalex_search_by_id    Look up by OpenAlex/DOI/PMID
mcp__scitex__openalex_enrich_ids      Bulk enrich from OpenAlex
mcp__scitex__openalex_status          Check OpenAlex status
```
