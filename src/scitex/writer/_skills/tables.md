---
name: tables
description: Table management — add from CSV, list, remove, and CSV/LaTeX round-trip conversion.
---

# Table Management

The `tables` submodule manages LaTeX table files stored under `00_shared/tables/` in the project directory. It also provides CSV-to-LaTeX and LaTeX-to-CSV conversion utilities.

## Module-level access

```python
import scitex as stx

stx.writer.tables.add(project_dir, key, csv_content, caption="")
stx.writer.tables.list(project_dir)
stx.writer.tables.remove(project_dir, key)
stx.writer.tables.csv_to_latex(csv_path, tex_path)
stx.writer.tables.latex_to_csv(tex_path, csv_path)
```

## Via Writer convenience methods

```python
from scitex.writer import Writer
writer = Writer("my_paper")

# Add table from CSV content string
writer.add_table("tab_demographics", csv_content, caption="Participant demographics.")

# CSV ↔ LaTeX conversion
writer.csv_to_latex("data/demographics.csv", "tables/demographics.tex")
writer.latex_to_csv("tables/demographics.tex", "data/demographics.csv")
```

## tables.add

```python
tables.add(
    project_dir,    # str or Path
    key,            # str — identifier used in LaTeX \ref{tab:key}
    csv_content,    # str — CSV content (or path to .csv file)
    caption="",     # str — table caption
) -> Path
```

Converts the CSV content to a LaTeX `tabular` environment and writes it to `00_shared/tables/{key}.tex` along with a `{key}_caption.tex`. Returns the `.tex` path.

```python
import csv, io
rows = [["Group", "N", "Age (mean)"], ["Control", "30", "24.5"], ["Treatment", "28", "25.1"]]
csv_str = "\n".join(",".join(r) for r in rows)

stx.writer.tables.add(
    "my_paper",
    "tab_demographics",
    csv_str,
    caption="Participant demographics. Values are mean ± SD.",
)
```

## tables.list

```python
tables.list(
    project_dir,   # str or Path
) -> list[dict]
```

Returns a list of dicts, each with `key`, `path`, and `caption` fields.

```python
tabs = stx.writer.tables.list("my_paper")
for t in tabs:
    print(t["key"], t["path"])
```

## tables.remove

```python
tables.remove(
    project_dir,   # str or Path
    key,           # str
) -> bool
```

Removes the `.tex` file and its caption file from the project.

## tables.csv_to_latex

```python
tables.csv_to_latex(
    csv_path,      # str or Path — input CSV
    tex_path,      # str or Path — output .tex file
    caption="",    # str — optional caption to embed
    label="",      # str — optional \label{} key
) -> Path
```

Reads a CSV and writes a standalone LaTeX `tabular` (or `table` + `tabular`) environment. Column alignment is inferred (numeric columns use `r`, text uses `l`).

```python
stx.writer.tables.csv_to_latex(
    "results/stats.csv",
    "tables/stats.tex",
    caption="Summary statistics.",
    label="tab:stats",
)
```

## tables.latex_to_csv

```python
tables.latex_to_csv(
    tex_path,      # str or Path — input .tex file
    csv_path,      # str or Path — output .csv file
) -> Path
```

Parses a LaTeX `tabular` environment and writes the cell values as CSV. Handles `&` column separators and `\\` row terminators.

```python
stx.writer.tables.latex_to_csv("tables/stats.tex", "results/stats.csv")
```

## MCP

```
writer_add_table      project_dir=./my-paper  key=tab1  csv_content="A,B\n1,2"  caption="Data."
writer_list_tables    project_dir=./my-paper
writer_remove_table   project_dir=./my-paper  key=tab1
writer_csv_to_latex   csv_path=data.csv  tex_path=tables/data.tex
writer_latex_to_csv   tex_path=tables/data.tex  csv_path=data.csv
```

## CLI

```bash
scitex writer tables list ./my-paper
scitex writer tables add ./my-paper data.csv --key tab1 --caption "Data."
scitex writer tables remove ./my-paper tab1
scitex writer tables csv-to-latex data.csv tables/data.tex
scitex writer tables latex-to-csv tables/data.tex data.csv
```
