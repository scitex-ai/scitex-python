---
description: Export a SciTeX writer document dict to a .tex file. Handles document class, journal presets, package injection, image extraction, and BibTeX generation.
---

# export_tex

Convert a SciTeX writer document (dict) to a `.tex` file on disk.

```python
export_tex(
    writer_doc: dict,
    output_path: str | Path,
    document_class: str = "article",
    packages: list[str] | None = None,
    preamble: str | None = None,
    image_dir: str | Path | None = None,
    export_images: bool = True,
    journal_preset: str | None = None,
    class_options: list[str] | None = None,
    use_bibtex: bool = False,
) -> Path
```

**Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `writer_doc` | `dict` | required | SciTeX writer document with keys `"blocks"`, `"metadata"`, `"images"`, `"references"` |
| `output_path` | `str \| Path` | required | Destination `.tex` file path |
| `document_class` | `str` | `"article"` | LaTeX document class; overridden by `journal_preset` |
| `packages` | `list[str]` | `None` | Additional `\usepackage` entries (appended after defaults) |
| `preamble` | `str` | `None` | Raw string inserted into the preamble after `\usepackage` lines |
| `image_dir` | `str \| Path` | `None` | Directory to extract embedded images into; defaults to `{stem}_figures/` next to the `.tex` file |
| `export_images` | `bool` | `True` | Set `False` to skip writing image files |
| `journal_preset` | `str` | `None` | One of `"ieee"`, `"elsevier"`, `"springer"`, `"aps"`, `"mdpi"`, `"acm"` |
| `class_options` | `list[str]` | `None` | Document class options, e.g. `["12pt", "twocolumn"]` |
| `use_bibtex` | `bool` | `False` | Generate `\bibliography{}` + a `.bib` file instead of inline `thebibliography` |

**Returns** `Path` — the written `.tex` file path.

**Default packages always included**

`inputenc` (utf8), `fontenc` (T1), `amsmath`, `amssymb`, `graphicx`, `hyperref`

**Journal presets**

| Preset | Document class | Extra packages |
|--------|---------------|----------------|
| `"ieee"` | `IEEEtran` (`conference`) | `cite`, `amsmath`, `algorithmic` |
| `"elsevier"` | `elsarticle` (`preprint,12pt`) | `lineno`, `hyperref` |
| `"springer"` | `svjour3` (`smallextended`) | — |
| `"aps"` | `revtex4-2` (`aps,prl,preprint`) | — |
| `"mdpi"` | `article` | `mdpi` |
| `"acm"` | `acmart` (`sigconf`) | — |

**writer_doc structure**

```python
writer_doc = {
    "metadata": {"title": "My Paper", "author": "A. Author"},
    "blocks": [
        {"type": "heading", "level": 1, "text": "Introduction"},
        {"type": "paragraph", "text": "This study..."},
        {"type": "paragraph", "runs": [
            {"text": "Bold term", "bold": True},
            {"text": " followed by ", "bold": False},
            {"text": "italic", "italic": True},
        ]},
        {"type": "list-item", "list_type": "unordered", "text": "First point"},
        {"type": "list-item", "list_type": "unordered", "text": "Second point"},
        {"type": "equation", "latex": "E = mc^2"},
        {"type": "table", "rows": [["A", "B"], [1, 2]]},
        {"type": "image", "image_hash": "abc123", "width": "0.6\\textwidth"},
        {"type": "caption", "caption_type": "figure", "number": "1",
         "caption_text": "Results", "image_hash": "abc123"},
    ],
    "images": [
        {"hash": "abc123", "extension": ".png", "data": b"<bytes>"}
    ],
    "references": [
        {"number": 1, "text": "Author et al., Journal, 2024"}
    ],
}
```

**Block types**

| `type` | Required keys | Notes |
|--------|--------------|-------|
| `heading` | `level` (1–5), `text` | Maps to `\section` … `\subparagraph` |
| `paragraph` | `text` or `runs` | `runs` list supports `bold`, `italic`, `underline` per run |
| `list-item` | `text`, `list_type` (`"ordered"`/`"unordered"`) | Consecutive items of the same type are wrapped in one environment |
| `equation` | `latex` (preferred) or `text` | `latex` is emitted verbatim inside `equation` |
| `table` | `rows` (list of lists) | Centered, all columns `c`, full `\hline` borders |
| `image` | `image_hash`, optional `width` | `\includegraphics` without extension |
| `caption` | `caption_type` (`"figure"`/`"table"`), `number`, `caption_text`, optional `image_hash` | Figures get full `figure` environment |
| `reference-paragraph` | any | Silently skipped (handled in `references` section) |

**Examples**

```python
from scitex.msword import load_docx
from scitex.tex import export_tex

# Basic export from a DOCX
doc = load_docx("manuscript.docx")
tex_path = export_tex(doc, "manuscript.tex")
# -> PosixPath('manuscript.tex')
# -> PosixPath('manuscript_figures/') created if images present

# IEEE conference format
export_tex(doc, "ieee_paper.tex", journal_preset="ieee")

# Elsevier with explicit image directory
export_tex(
    doc,
    "elsevier_paper.tex",
    journal_preset="elsevier",
    image_dir="./figures",
    export_images=True,
)

# Custom preamble and extra packages
export_tex(
    doc,
    "custom.tex",
    document_class="report",
    class_options=["12pt", "twoside"],
    packages=["booktabs", "siunitx"],
    preamble="\\setlength{\\parindent}{0pt}\n\\setlength{\\parskip}{6pt}",
)

# Use BibTeX references
export_tex(doc, "paper.tex", use_bibtex=True)
# -> writes paper.tex AND paper.bib
```

**LaTeX escaping**

`_escape_latex()` is applied to all text content. Special characters handled:
`\`, `&`, `%`, `$`, `#`, `_`, `{`, `}`, `~`, `^`

Existing LaTeX commands (e.g. `\alpha`) are not double-escaped.
