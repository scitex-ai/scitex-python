---
name: export
description: Export and migration — arXiv-ready export, Overleaf import/export, AI2 Asta prompts, project cloning.
---

# Export and Migration

## arXiv export

```python
import scitex.writer as sw

result = sw.export.manuscript(
    project_dir,      # str or Path
    output_dir=None,  # str | None — defaults to {project_dir}/export/arxiv/
)
# Returns path to the export archive
```

Produces a clean submission package: flattened `.tex` file, all figures in required formats, `.bib` file, no internal `.log` or `.aux` files.

MCP:
```
writer_export_manuscript  project_dir=./my-paper
```

CLI:
```bash
scitex writer export manuscript ./my-paper
```

## Overleaf export

```python
sw.migration.export_overleaf(
    project_dir,      # str or Path
    output_zip=None,  # str | None — path to output .zip; defaults to {project_dir}/overleaf.zip
) -> Path
```

Packages the project as a `.zip` file compatible with Overleaf's import format.

```python
import scitex as stx

path = stx.writer.migration.export_overleaf("my_paper")
print(f"Upload this to Overleaf: {path}")
```

MCP:
```
writer_export_overleaf  project_dir=./my-paper
```

CLI:
```bash
scitex writer export overleaf ./my-paper
```

## Overleaf import

```python
sw.migration.import_overleaf(
    zip_path,          # str or Path — Overleaf .zip download
    project_dir,       # str or Path — destination project directory
    git_strategy='child',
) -> Path
```

Imports an Overleaf project download (`.zip`) into the scitex-writer project layout. Reorganizes files into the `00_shared/`, `01_manuscript/` structure.

```python
stx.writer.migration.import_overleaf(
    "overleaf_download.zip",
    "my_paper",
)
```

MCP:
```
writer_import_overleaf  zip_path=overleaf_download.zip  project_dir=./my-paper
```

## Project cloning and updates

### project.clone

```python
sw.project.clone(
    project_dir,          # str or Path
    git_strategy='child', # str
    branch=None,          # str | None
    tag=None,             # str | None
) -> Path
```

Clones the scitex-writer template into `project_dir`. This is what `Writer(project_dir)` calls internally when the directory does not yet exist.

MCP:
```
writer_clone_project  project_dir=./new-paper
```

### project.update

```python
sw.project.update(
    project_dir,   # str or Path
) -> bool
```

Pulls the latest version of the template scripts (shell scripts, Makefile) without overwriting user content (`.tex` files, figures, tables, bibliography).

MCP:
```
writer_update_project  project_dir=./my-paper
```

### project.info

```python
sw.project.info(
    project_dir,   # str or Path
) -> dict
```

Returns metadata about the project: template version, sections found, last compile time, etc.

MCP:
```
writer_get_project_info  project_dir=./my-paper
```

## AI2 Asta prompts

```python
sw.prompts.asta(
    project_dir,   # str or Path
    section=None,  # str | None — specific section or all
) -> str
```

Generates structured writing prompts compatible with the AI2 Asta interface. Combines the current draft text with section-specific IMRAD guidelines.

MCP:
```
writer_prompts_asta  project_dir=./my-paper  section=discussion
```

## ensure_workspace

```python
stx.writer.ensure_workspace(
    project_dir,           # str or Path — root project directory
    git_strategy='child',  # str
    **kwargs,              # forwarded to Writer (branch, tag)
) -> pathlib.Path
```

Idempotent: creates `{project_dir}/scitex/writer/` if it does not exist, returns the path without modification if it already does.

Intended for use in `@stx.session`-decorated scripts that need a writer workspace alongside their output directory:

```python
@stx.session
def main(CONFIG=stx.INJECTED, ...):
    ws = stx.writer.ensure_workspace("~/research/paper1")
    writer = stx.writer.Writer(ws)
    result = writer.compile_manuscript()
```
