---
name: stx.writer
description: LaTeX manuscript compilation system. Manages the full paper lifecycle — compile to PDF, edit sections, manage bibliography, figures, tables, writing guidelines, and Overleaf integration. Thin wrapper over scitex-writer.
user-invocable: false
---

# stx.writer

LaTeX manuscript compilation, figure/table management, bibliography handling, and IMRAD writing guidelines.

> Requires: `pip install scitex-writer`

## Sub-skills

### Compilation
- [compile.md](compile.md) — `Writer`, `compile_manuscript`, `compile_supplementary`, `compile_revision`, `CompilationResult`

### Section Editing
- [sections.md](sections.md) — `read_section`, `write_section`, `get_section`, `watch`, project directory layout

### Bibliography
- [bib.md](bib.md) — `bib.add`, `bib.get`, `bib.list`, `bib.remove`, `bib.merge_files`, `merge_bibfiles`

### Figures
- [figures.md](figures.md) — `figures.add`, `figures.list`, `figures.remove`, `figures.convert`, `pdf_to_images`

### Tables
- [tables.md](tables.md) — `tables.add`, `tables.list`, `tables.remove`, `csv_to_latex`, `latex_to_csv`

### Writing Guidelines
- [guidelines.md](guidelines.md) — IMRAD section guidelines, `guidelines.get`, `guidelines.list`, `guidelines.build`

### Claims
- [claims.md](claims.md) — Traceable scientific assertions: `claim.add`, `claim.list`, `claim.render`, `claim.format`

### Export and Migration
- [export.md](export.md) — arXiv export, Overleaf import/export, `ensure_workspace`, `project.clone`

## MCP Tools

| Tool | Purpose |
|------|---------|
| `writer_compile_manuscript` | Compile manuscript to PDF |
| `writer_compile_supplementary` | Compile supplementary materials |
| `writer_compile_revision` | Compile revision with optional change tracking |
| `writer_compile_content` | Compile arbitrary LaTeX content |
| `writer_list_document_types` | List available document types |
| `writer_get_pdf` | Get path to compiled PDF |
| `writer_get_project_info` | Get project metadata |
| `writer_clone_project` | Clone writer project template |
| `writer_update_project` | Update project from template |
| `writer_add_bibentry` | Add BibTeX entry |
| `writer_get_bibentry` | Get a specific BibTeX entry |
| `writer_list_bibentries` | List all bibliography entries |
| `writer_list_bibfiles` | List .bib files in project |
| `writer_remove_bibentry` | Remove a BibTeX entry |
| `writer_merge_bibfiles` | Merge multiple .bib files |
| `writer_add_figure` | Register figure with caption |
| `writer_list_figures` | List all figures |
| `writer_remove_figure` | Remove figure registration |
| `writer_convert_figure` | Convert figure format (PDF/PNG/EPS, etc.) |
| `writer_pdf_to_images` | Extract PDF pages as images |
| `writer_add_table` | Add table from CSV content |
| `writer_list_tables` | List all tables |
| `writer_remove_table` | Remove a table |
| `writer_csv_to_latex` | Convert CSV file to LaTeX tabular |
| `writer_latex_to_csv` | Convert LaTeX tabular to CSV |
| `writer_guideline_get` | Get IMRAD guideline for a section |
| `writer_guideline_list` | List available guideline sections |
| `writer_guideline_build` | Build editing prompt from guideline + draft |
| `writer_add_claim` | Add traceable scientific claim |
| `writer_get_claim` | Get a specific claim |
| `writer_list_claims` | List all claims |
| `writer_remove_claim` | Remove a claim |
| `writer_render_claims` | Render claims to LaTeX |
| `writer_format_claim` | Format a single claim |
| `writer_export_manuscript` | Export manuscript for arXiv submission |
| `writer_export_overleaf` | Export to Overleaf format |
| `writer_import_overleaf` | Import from Overleaf |
| `writer_prompts_asta` | Generate AI2 Asta writing prompts |

## CLI

```bash
# Compile
scitex writer compile manuscript ./my-paper
scitex writer compile supplementary ./my-paper
scitex writer compile revision ./my-paper --track-changes

# Bibliography
scitex writer bib list ./my-paper
scitex writer bib add ./my-paper "@article{key,...}"

# Tables and figures
scitex writer tables add ./my-paper data.csv
scitex writer figures list ./my-paper

# Writing guidelines
scitex writer guidelines list
scitex writer guidelines get introduction
```
