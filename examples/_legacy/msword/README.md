# SciTeX MS Word Examples

This directory contains examples demonstrating how to use `scitex.msword` for
converting between MS Word documents and SciTeX's intermediate format.

## Prerequisites

```bash
pip install python-docx
```

## Sample Documents

The examples use Word templates from `docs/MSWORD_MANUSCTIPS/`:
- `IOP-SCIENCE-Word-template-Double-anonymous.docx` - IOP journal template
- `RESNA 2025 Scientific Paper Template.docx` - RESNA conference template
- `ijerph-template.dot` - MDPI IJERPH template

## Examples

### 01_load_docx.py
Basic document loading and structure inspection.

```python
from scitex.msword import load_docx, list_profiles

# List available journal profiles
profiles = list_profiles()  # ['generic', 'mdpi-ijerph', 'resna-2025', ...]

# Load a document
doc = load_docx("manuscript.docx", profile="resna-2025")

# Access document structure
print(doc["blocks"])      # List of content blocks
print(doc["metadata"])    # Document metadata
print(doc["images"])      # Extracted images
print(doc["references"])  # Parsed references
```

### 02_convert_to_tex.py
Convert Word documents to LaTeX.

```python
from scitex.msword import convert_docx_to_tex

# Direct conversion
convert_docx_to_tex("input.docx", "output.tex", profile="mdpi")

# Or two-step process
from scitex.msword import load_docx
from scitex.tex import export_tex

doc = load_docx("input.docx", profile="mdpi")
export_tex(doc, "output.tex")
```

### 03_save_docx.py
Save documents with different journal profiles.

```python
from scitex.msword import load_docx, save_docx

# Load with one profile, save with another
doc = load_docx("input.docx", profile="resna-2025")
save_docx(doc, "output.docx", profile="ieee")
```

### 04_custom_profile.py
Create custom journal profiles.

```python
from scitex.msword import BaseWordProfile, register_profile

custom = BaseWordProfile(
    name="my-journal",
    description="My custom journal",
    heading_styles={1: "Heading 1", 2: "Heading 2"},
    columns=2,
    double_anonymous=True,
)
register_profile(custom)
```

### 05_extract_content.py
Extract specific content (images, references, captions, tables).

```python
from scitex.msword import load_docx

doc = load_docx("manuscript.docx", extract_images=True)

# Extract images
for img in doc["images"]:
    filename = f"image_{img['hash']}{img['extension']}"
    with open(filename, "wb") as f:
        f.write(img["data"])

# Extract captions
captions = [b for b in doc["blocks"] if b.get("type") == "caption"]
```

### 06_full_pipeline.py
Complete Word to LaTeX pipeline with figure extraction.

```python
from scitex.msword import load_docx
from scitex.tex import export_tex
from pathlib import Path

# Load document
doc = load_docx("manuscript.docx", profile="resna", extract_images=True)

# Save images
for i, img in enumerate(doc["images"]):
    Path(f"figures/fig_{i+1}{img['extension']}").write_bytes(img["data"])

# Export LaTeX
export_tex(doc, "manuscript.tex")
```

## Available Profiles

| Profile | Description | Columns |
|---------|-------------|---------|
| `generic` | Standard Word with Heading 1/2/3 | 1 |
| `mdpi-ijerph` | MDPI IJERPH journal | 1 |
| `resna-2025` | RESNA 2025 conference | 2 |
| `iop-double-anonymous` | IOP double-blind review | 1 |
| `ieee` | IEEE conference/journal | 2 |
| `springer` | Springer Nature | 1 |
| `elsevier` | Elsevier journals | 1 |

## Document Structure

The intermediate format uses a block-based structure:

```python
{
    "blocks": [
        {"type": "heading", "level": 1, "text": "Introduction"},
        {"type": "paragraph", "text": "Content...", "runs": [...]},
        {"type": "caption", "caption_type": "figure", "number": 1, "caption_text": "..."},
        {"type": "table", "rows": [[...], [...]]},
        {"type": "reference-paragraph", "ref_number": 1, "ref_text": "..."},
    ],
    "metadata": {"profile": "...", "source_file": "...", ...},
    "images": [{"hash": "...", "extension": ".png", "data": b"...", ...}],
    "references": [{"number": 1, "text": "..."}, ...],
    "warnings": [],
}
```
