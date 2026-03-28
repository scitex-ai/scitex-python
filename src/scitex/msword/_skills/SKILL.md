---
name: stx.msword
description: MS Word DOCX import/export with journal-specific profiles for scientific manuscript workflows.
---

# stx.msword — Skills Index

Import/export Word documents with journal-specific style mapping. SciTeX is the source of truth; Word is a text-editing view.

## Sub-skills

| File | Description |
|------|-------------|
| [load-save-convert.md](load-save-convert.md) | load_docx, save_docx, convert_docx_to_tex, post-processing utilities |
| [profiles.md](profiles.md) | Built-in journal profiles, get_profile, register_profile, BaseWordProfile fields |

## Quick Reference

```python
from scitex.msword import load_docx, save_docx, convert_docx_to_tex, list_profiles

doc = load_docx("manuscript.docx", profile="resna-2025")
save_docx(doc, "output.docx", profile="generic")
convert_docx_to_tex("draft.docx", "out.tex", profile="iop-double-anonymous")

list_profiles()
# ['elsevier', 'generic', 'ieee', 'iop', 'iop-double-anonymous',
#  'mdpi', 'mdpi-ijerph', 'resna', 'resna-2025', 'springer']
```
