---
description: IMRAD writing guidelines — get section-specific tips, list available sections, build AI editing prompts from guideline + draft.
---

# Writing Guidelines

The `guidelines` submodule provides IMRAD writing tips for each manuscript section. Guidelines can be retrieved for direct reading, or used to build AI-ready editing prompts that combine the guideline with a draft text.

## Available sections

Standard IMRAD sections (verify with `guidelines.list`):

- `abstract`
- `introduction`
- `methods` / `method`
- `results`
- `discussion`
- `conclusion`
- `title`
- `keywords`

## guidelines.list

```python
from scitex.writer import guidelines

sections = guidelines.list()
# Returns: ['abstract', 'introduction', 'methods', 'results', 'discussion', 'conclusion', ...]
```

CLI:
```bash
scitex writer guidelines list
```

MCP:
```
writer_guideline_list
```

## guidelines.get

```python
guidelines.get(
    section,    # str — section name, e.g. 'methods'
) -> str
```

Returns the full guideline text for the named section.

```python
guide = guidelines.get("methods")
print(guide)
# => METHODS SECTION GUIDELINES
#    - Describe study design...
#    - Report sample sizes...
#    ...
```

CLI:
```bash
scitex writer guidelines get methods
scitex writer guidelines get introduction
```

MCP:
```
writer_guideline_get  section=methods
```

## guidelines.build

```python
guidelines.build(
    section,      # str — section name
    draft_text,   # str — draft text to improve
) -> str
```

Combines the section guideline with the draft text into a structured AI-editing prompt. The returned string is ready to be sent directly to an LLM for revision suggestions.

```python
draft = writer.read_section("discussion")
prompt = guidelines.build("discussion", draft)

# prompt is now:
# "Here are the guidelines for a Discussion section:
#  [guideline text]
#
#  Here is the current draft:
#  [draft text]
#
#  Please revise..."
```

MCP:
```
writer_guideline_build  section=discussion  draft="We found that..."
```

## Typical workflow

```python
from scitex.writer import Writer, guidelines
from pathlib import Path

writer = Writer(Path("my_paper"))

# Inspect guideline before writing
print(guidelines.get("results"))

# Read current draft
draft = writer.read_section("results")

# Build editing prompt
prompt = guidelines.build("results", draft)

# Send `prompt` to your preferred LLM, then apply the revision:
revised = call_llm(prompt)
writer.write_section("results", revised)
```
