---
description: Read, write, and watch manuscript sections. Project directory layout and DocumentSection API.
---

# Section Editing

## Project directory layout

A writer project uses this directory structure:

```
my_paper/
├── 00_shared/
│   ├── title.tex
│   ├── authors.tex
│   ├── bibliography.bib
│   ├── figures/
│   └── tables/
├── 01_manuscript/
│   ├── main.tex
│   └── sections/
│       ├── abstract.tex
│       ├── introduction.tex
│       ├── methods.tex
│       ├── results.tex
│       ├── discussion.tex
│       └── conclusion.tex
├── 02_supplementary/
│   ├── main.tex
│   └── sections/
└── 03_revision/
    ├── main.tex
    └── sections/
```

Create a new project from template:

```bash
scitex template clone paper my_paper
```

or in Python:

```python
from scitex.writer import Writer
writer = Writer("my_paper")   # clones template if directory absent
```

## read_section

```python
Writer.read_section(
    section_name,            # str — 'abstract', 'introduction', etc.
    doc_type='manuscript',   # 'shared' | 'manuscript' | 'supplementary' | 'revision'
) -> str
```

Returns section file content as a string. Returns empty string if the file is empty or missing (does not raise).

```python
writer = Writer(Path("my_paper"))

abstract = writer.read_section("abstract")
title    = writer.read_section("title", "shared")
supp     = writer.read_section("methods", "supplementary")
```

## write_section

```python
Writer.write_section(
    section_name,            # str — section name
    content,                 # str — full content to write
    doc_type='manuscript',   # 'shared' | 'manuscript' | 'supplementary' | 'revision'
) -> bool
```

Overwrites the section file. Returns `True` on success.

```python
ok = writer.write_section("abstract", "We present a novel method...")
ok = writer.write_section("title", "My Paper Title", "shared")
```

## get_section

```python
Writer.get_section(
    section_name,            # str
    doc_type='manuscript',   # str
) -> DocumentSection
```

Returns a `DocumentSection` object. Raises `ValueError` if `doc_type` or `section_name` is unknown.

`DocumentSection` interface:

```python
sec = writer.get_section("introduction")
sec.read()            # -> str  (current content)
sec.write(content)    # -> bool (write new content)
sec.commit(msg=None)  # commit to git if git_strategy is set
sec.history()         # list of git commits for this file
sec.diff(ref="HEAD")  # diff against git ref
```

## watch

```python
Writer.watch(
    on_compile=None,   # callable(CompilationResult) — called after each recompile
) -> None
```

Starts a file-system watcher. Recompiles the manuscript automatically whenever any file in the project changes. Blocking — runs until interrupted.

```python
def on_done(result):
    if result.success:
        print(f"Recompiled: {result.output_pdf}")

writer.watch(on_compile=on_done)
```

## get_pdf

```python
Writer.get_pdf(
    doc_type='manuscript',  # 'manuscript' | 'supplementary' | 'revision'
) -> Optional[Path]
```

Returns the path to the last compiled PDF for the given document type. Returns `None` if not yet compiled.

```python
pdf = writer.get_pdf()
pdf = writer.get_pdf("supplementary")
```

## delete

```python
Writer.delete() -> bool
```

Deletes the entire project directory. Use with caution.
