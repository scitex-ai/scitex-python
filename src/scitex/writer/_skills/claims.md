---
name: claims
description: Traceable scientific assertions — add, list, get, remove, render to LaTeX, format for display.
---

# Claims

The `claim` submodule provides a system for registering traceable scientific assertions (claims). Each claim links a statement to supporting evidence: statistical results, figures, citations. Claims can be rendered into LaTeX for inclusion in the manuscript.

## What is a claim?

A claim is a structured scientific assertion:
- **statement** — the scientific finding ("Treatment significantly reduced X")
- **evidence** — linked stats, figure keys, citation keys
- **context** — which section/paragraph it belongs to

## Module-level access

```python
import scitex as stx

stx.writer.claim.add(project_dir, statement, evidence=None, section=None)
stx.writer.claim.list(project_dir)
stx.writer.claim.get(project_dir, claim_id)
stx.writer.claim.remove(project_dir, claim_id)
stx.writer.claim.render(project_dir)       # -> LaTeX string
stx.writer.claim.format(claim_dict)        # -> formatted string
```

## claim.add

```python
claim.add(
    project_dir,     # str or Path
    statement,       # str — the scientific claim
    evidence=None,   # dict | None — supporting evidence
    section=None,    # str | None — manuscript section (e.g., 'results')
) -> str            # returns claim_id
```

Evidence dict may include:
- `stats` — statistical test results (p-value, effect size, CI)
- `figures` — list of figure keys
- `citations` — list of BibTeX keys

```python
claim_id = stx.writer.claim.add(
    "my_paper",
    statement="Treatment significantly reduced response time.",
    evidence={
        "stats": {"p": 0.003, "d": 0.82, "test": "t-test"},
        "figures": ["fig_rt_comparison"],
        "citations": ["Smith2024"],
    },
    section="results",
)
```

## claim.list

```python
claim.list(
    project_dir,      # str or Path
    section=None,     # str | None — filter by section
) -> list[dict]
```

Returns all registered claims, optionally filtered by section.

```python
claims = stx.writer.claim.list("my_paper")
for c in claims:
    print(c["id"], c["statement"])

# Filter by section
results_claims = stx.writer.claim.list("my_paper", section="results")
```

## claim.get

```python
claim.get(
    project_dir,   # str or Path
    claim_id,      # str
) -> dict | None
```

Returns the claim dict for the given ID, or `None` if not found.

## claim.remove

```python
claim.remove(
    project_dir,   # str or Path
    claim_id,      # str
) -> bool
```

Removes the claim with the given ID.

## claim.render

```python
claim.render(
    project_dir,         # str or Path
    section=None,        # str | None — render only this section
    output_file=None,    # str | None — write to file if given
) -> str
```

Renders all claims (or those in `section`) as LaTeX. Returns the LaTeX string. If `output_file` is given, also writes to that file.

```python
latex = stx.writer.claim.render("my_paper")
# => \begin{itemize}
#    \item Treatment significantly reduced response time...
#    ...
```

## claim.format

```python
claim.format(
    claim_dict,     # dict — a single claim as returned by get/list
) -> str
```

Formats one claim dict as a human-readable string (for display, not LaTeX).

## MCP

```
writer_add_claim      project_dir=./my-paper  statement="..."  section=results
writer_get_claim      project_dir=./my-paper  claim_id=abc123
writer_list_claims    project_dir=./my-paper
writer_remove_claim   project_dir=./my-paper  claim_id=abc123
writer_render_claims  project_dir=./my-paper
writer_format_claim   claim_id=abc123
```
