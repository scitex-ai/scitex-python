---
name: msword-import-export
description: Load a .docx file with load_docx(), save a SciTeX writer document back to Word with save_docx(), and convert directly to LaTeX with convert_docx_to_tex().
---

# MS Word Import/Export

## load_docx

Load a `.docx` file and convert it to a SciTeX writer document dict.

```python
load_docx(
    path: str | Path,
    profile: str | None = None,   # "generic" | "mdpi-ijerph" | "resna-2025" | "iop-double-anonymous"
    extract_images: bool = True,
) -> dict
```

Returns a dict with keys: `blocks`, `metadata`, `images`, `references`.

```python
from scitex.msword import load_docx

doc = load_docx("manuscript.docx", profile="resna-2025")
print(doc["metadata"]["profile"])   # 'resna-2025'
print(len(doc["blocks"]))           # number of content blocks
```

---

## save_docx

Write a SciTeX writer document dict back to a `.docx` file.

```python
save_docx(
    writer_doc: dict,
    path: str | Path,
    profile: str | None = None,
    overwrite: bool = True,
    template_path: str | Path | None = None,
) -> Path
```

```python
from scitex.msword import load_docx, save_docx

doc = load_docx("draft.docx")
# ... manipulate doc["blocks"] ...
save_docx(doc, "final.docx", profile="mdpi-ijerph")
```

---

## convert_docx_to_tex

One-step pipeline: `.docx` → LaTeX.

```python
convert_docx_to_tex(
    input_path: str | Path,
    output_path: str | Path,
    profile: str | None = None,
    image_dir: str | Path | None = None,
    link_images: bool = True,
    link_mode: str = "by-number",   # "by-number" | "by-proximity"
    normalize_headings: bool = True,
    validate: bool = True,
) -> Path
```

Steps: load DOCX → normalize headings → link figure captions to images → validate → export LaTeX.

```python
from scitex.msword import convert_docx_to_tex

convert_docx_to_tex(
    "RESNA 2025 Scientific Paper Template.docx",
    "manuscript.tex",
    profile="resna-2025",
    image_dir="figures",
)
```
