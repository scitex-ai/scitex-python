---
name: bib
description: BibTeX bibliography management — add, get, list, remove entries, merge .bib files.
---

# Bibliography Management

The `bib` submodule manages BibTeX entries stored in `00_shared/bibliography.bib` (and any additional `.bib` files) inside the project directory.

## Module-level access

```python
import scitex as stx

# Via stx.writer.bib module directly
stx.writer.bib.add(project_dir, bibtex_str)
stx.writer.bib.list(project_dir)
stx.writer.bib.get(project_dir, key)
stx.writer.bib.remove(project_dir, key)
stx.writer.bib.merge_files(project_dir, output_file="bibliography.bib")
```

## Via Writer convenience methods

```python
from scitex.writer import Writer
from pathlib import Path

writer = Writer(Path("my_paper"))

# Add entry (full BibTeX string)
writer.add_bibentry('@article{Smith2024, title={...}, author={Smith, J.}, year={2024}, ...}')

# Merge all .bib files in the project into one
writer.merge_bibfiles(output_file="bibliography.bib")
```

## bib.add

```python
bib.add(
    project_dir,     # str or Path
    bibtex_str,      # str — complete BibTeX entry (@article{...})
) -> bool
```

Appends the entry to `00_shared/bibliography.bib`. Duplicate keys are not validated by default.

```python
entry = """
@article{Smith2024,
  title   = {A Novel Method},
  author  = {Smith, John},
  journal = {Nature},
  year    = {2024},
  doi     = {10.1038/...},
}
"""
stx.writer.bib.add("my_paper", entry)
```

## bib.get

```python
bib.get(
    project_dir,   # str or Path
    key,           # str — BibTeX key (e.g., 'Smith2024')
) -> Optional[str]
```

Returns the full BibTeX entry string for the given key, or `None` if not found.

## bib.list

```python
bib.list(
    project_dir,   # str or Path
) -> list[dict]
```

Returns a list of dicts, each representing one bibliography entry:

```python
entries = stx.writer.bib.list("my_paper")
for e in entries:
    print(e["key"], e["type"], e.get("title"))
```

## bib.remove

```python
bib.remove(
    project_dir,   # str or Path
    key,           # str — BibTeX key to remove
) -> bool
```

Removes the entry with the given key from the `.bib` file.

## bib.merge_files

```python
bib.merge_files(
    project_dir,                    # str or Path
    output_file="bibliography.bib", # str — output filename inside 00_shared/
) -> Path
```

Finds all `.bib` files in the project and merges them into `output_file`, deduplicating entries by key. Returns the output path.

```python
path = stx.writer.bib.merge_files("my_paper")
```

## list_bibfiles

```python
bib.list_files(
    project_dir,   # str or Path
) -> list[Path]
```

Returns paths of all `.bib` files found in the project.

## MCP

```
writer_add_bibentry    project_dir=./my-paper  bibtex="@article{...}"
writer_get_bibentry    project_dir=./my-paper  key=Smith2024
writer_list_bibentries project_dir=./my-paper
writer_list_bibfiles   project_dir=./my-paper
writer_remove_bibentry project_dir=./my-paper  key=Smith2024
writer_merge_bibfiles  project_dir=./my-paper  output_file=bibliography.bib
```

## CLI

```bash
scitex writer bib list ./my-paper
scitex writer bib add ./my-paper "@article{Smith2024, ...}"
scitex writer bib remove ./my-paper Smith2024
scitex writer bib merge ./my-paper
```
