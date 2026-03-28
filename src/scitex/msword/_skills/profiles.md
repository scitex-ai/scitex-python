---
description: Built-in journal/conference Word profiles that control style mapping for headings, captions, columns, and double-anonymous formatting.
---

# stx.msword — Journal Profiles

A profile (`BaseWordProfile`) maps Word style names to SciTeX document elements. Pass the profile name string to `load_docx`, `save_docx`, or `convert_docx_to_tex`.

## Built-in profiles

| Profile name | Alias | Columns | Double-anon | Notes |
|---|---|---|---|---|
| `generic` | — | 1 | No | Standard Heading 1/2/3/4 + Caption |
| `mdpi-ijerph` | `mdpi` | 1 | No | MDPI IJERPH journal |
| `resna-2025` | `resna` | 2 | No | All-caps headings, 4-page limit |
| `iop-double-anonymous` | `iop` | 1 | Yes | Custom IOPH1/IOPH2/IOPH3 styles |
| `ieee` | — | 2 | No | IEEE conference/journal |
| `springer` | — | 1 | No | Springer Nature |
| `elsevier` | — | 1 | No | Elsevier |

## Listing and retrieving profiles

```python
from scitex.msword import list_profiles, get_profile

names = list_profiles()
# ['elsevier', 'generic', 'ieee', 'iop', 'iop-double-anonymous',
#  'mdpi', 'mdpi-ijerph', 'resna', 'resna-2025', 'springer']

profile = get_profile("mdpi-ijerph")
print(profile.name)           # "mdpi-ijerph"
print(profile.columns)        # 1
print(profile.heading_styles) # {1: "Heading 1", 2: "Heading 2", 3: "Heading 3"}
print(profile.double_anonymous) # False

iop = get_profile("iop")
print(iop.heading_styles)     # {1: "IOPH1", 2: "IOPH2", 3: "IOPH3"}
print(iop.double_anonymous)   # True
```

`get_profile(None)` returns the `"generic"` profile.

## Registering a custom profile

```python
from scitex.msword import BaseWordProfile, register_profile, list_profiles

custom = BaseWordProfile(
    name="my-journal",
    description="Custom journal template",
    heading_styles={1: "Section", 2: "Subsection"},
    caption_style="FigCaption",
    normal_style="Body Text",
    reference_section_titles=["Literature Cited"],
    columns=2,
    double_anonymous=False,
)
register_profile(custom)

assert "my-journal" in list_profiles()
doc = load_docx("draft.docx", profile="my-journal")
```

## BaseWordProfile fields

| Field | Type | Default | Description |
|---|---|---|---|
| `name` | str | required | Profile identifier |
| `description` | str | required | Human-readable label |
| `heading_styles` | dict[int, str] | `{}` | depth → Word style name |
| `caption_style` | str | `"Caption"` | Style for figure/table captions |
| `normal_style` | str | `"Normal"` | Default body text style |
| `reference_section_titles` | list[str] | `["References", "REFERENCES"]` | Titles that start reference section |
| `figure_caption_prefixes` | list[str] | `["Figure", "Fig.", "Fig"]` | Caption prefix detection |
| `table_caption_prefixes` | list[str] | `["Table", "Tab.", "Tab"]` | Caption prefix detection |
| `columns` | int | 1 | Layout columns |
| `double_anonymous` | bool | False | Strip author-identifying info |
| `post_import_hooks` | list[Callable] | `[]` | Called after `load_docx` |
| `pre_export_hooks` | list[Callable] | `[]` | Called before `save_docx` |
