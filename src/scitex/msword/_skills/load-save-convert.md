---
name: stx.msword — Load, Save, and Convert DOCX
description: Import Word documents into SciTeX intermediate format, export back to DOCX, or convert directly to LaTeX.
---

# stx.msword — Load, Save, and Convert DOCX

`stx.msword` treats Word as a text-editing view; SciTeX is the source of truth. The internal format (a dict with `blocks`, `metadata`, `images`, `references`) travels between Word, SciTeX writer, and LaTeX.

## load_docx

Load a `.docx` file into the SciTeX intermediate document dict.

```python
from scitex.msword import load_docx

doc = load_docx("manuscript.docx")                   # default "generic" profile
doc = load_docx("manuscript.docx", profile="mdpi-ijerph")
doc = load_docx("manuscript.docx", extract_images=False)

print(doc["metadata"]["profile"])  # "mdpi-ijerph"
print(doc["blocks"])               # list of dicts: type, content, level, ...
print(doc["images"])               # list of extracted image dicts
print(doc["references"])           # list of parsed reference entries
```

`load_docx` uses `WordReader` internally. Each block has a `type` key: `"heading"`, `"paragraph"`, `"caption"`, `"list_item"`, `"table"`, etc.

## save_docx

Export a SciTeX intermediate doc back to `.docx`.

```python
from scitex.msword import save_docx

out = save_docx(doc, "submission.docx")                        # generic profile
out = save_docx(doc, "submission.docx", profile="resna-2025")
out = save_docx(doc, "submission.docx", template_path="template.dotx")
# Raises FileExistsError if file exists and overwrite=False
save_docx(doc, "out.docx", overwrite=False)
```

Returns `Path` to the written file. Backed by `WordWriter`.

## convert_docx_to_tex

One-shot pipeline: DOCX → normalize → link figures → validate → `.tex`.

```python
from scitex.msword import convert_docx_to_tex

convert_docx_to_tex(
    "RESNA_Template.docx",
    "manuscript.tex",
    profile="resna-2025",
    image_dir="figures",         # where to write extracted images
    link_mode="by-number",       # "by-number" or "by-proximity"
    normalize_headings=True,
    validate=True,
)
```

Steps performed:
1. `load_docx()` with `extract_images=True`
2. `normalize_section_headings()` (optional)
3. `link_captions_to_images()` or `link_captions_to_images_by_proximity()` (optional)
4. `validate_document()` — populates `doc["warnings"]` (optional)
5. `scitex.tex.export_tex()` — writes the `.tex` file

## Post-processing utilities

```python
from scitex.msword import (
    normalize_section_headings,
    validate_document,
    link_captions_to_images,
    link_captions_to_images_by_proximity,
)

doc = normalize_section_headings(doc)          # "intro" → "Introduction"
doc = link_captions_to_images(doc)             # Figure 1 → first image
doc = link_captions_to_images_by_proximity(doc) # document-order matching
doc = validate_document(doc)                   # adds doc["warnings"]
```
