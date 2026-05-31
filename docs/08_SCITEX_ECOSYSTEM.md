<!-- ---
!-- Timestamp: 2026-01-29 22:43:42
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-python/docs/08_SCITEX_ECOSYSTEM.md
!-- --- -->

# SciTeX Ecosystem

<p align="center">
    <img src="../scripts/assets/workflow_out/workflow.png" alt="SciTeX Ecosystem" width="800">
</p>

SciTeX integrates standalone packages that can be used independently or through the unified `scitex` interface.

## Packages

| Package                                                           | scitex Module                    | Description                              | Status     |
|-------------------------------------------------------------------|----------------------------------|------------------------------------------|------------|
| [figrecipe](https://github.com/ywatanabe1989/figrecipe)           | `scitex.plt`                     | Publication-ready matplotlib figures     | Integrated |
| [crossref-local](https://github.com/ywatanabe1989/crossref-local) | `scitex.scholar.crossref_scitex` | Local CrossRef database (167M+ papers)   | Integrated |
| [openalex-local](https://github.com/ywatanabe1989/openalex-local) | `scitex.scholar.openalex_scitex` | Local OpenAlex database (250M+ papers)   | Integrated |
| [socialia](https://github.com/ywatanabe1989/socialia)             | `scitex.social`                  | Social media posting (Twitter, LinkedIn) | Integrated |
| [scitex-writer](https://github.com/ywatanabe1989/scitex-writer)   | `scitex.writer`                  | LaTeX manuscript compilation             | Integrated |
| [scitex-dataset](https://github.com/ywatanabe1989/scitex-dataset) | `scitex.dataset`                 |                                          |            |

## Architecture

```
scitex (umbrella)
├── scitex.plt      ← figrecipe
├── scitex.social   ← socialia
├── scitex.scholar  ← crossref-local + openalex-local
└── scitex.writer   ← scitex-writer
```

### Integration Pattern

- **Thin Wrapper**: Delegate without modification
- **Single Source of Truth**: Downstream packages are authoritative
- **Branding**: Apply `scitex.*` namespace via environment variables

### Usage

```python
# Via scitex (recommended)
import scitex as stx
fig, ax = stx.plt.subplots()

# Standalone (also works)
import figrecipe as fr
fig, ax = fr.subplots()
```

### CLI

```bash
# Via scitex
scitex writer compile manuscript
scitex social post "Hello"

# Standalone
scitex-writer compile manuscript
socialia post "Hello"
```

## Port Scheme

SciTeX uses `3129X` (sa-i-te-ku-su = 3-1-2-9):

| Port | Service |
|------|---------|
| 31290 | scitex-cloud |
| 31291 | crossref-local |
| 31292 | openalex |
| 31293 | scitex-audio |

# SciTeX Family

SciTeX integrates standalone packages that can be used independently or through the unified `scitex` interface.

## Packages

| Package | scitex Module | Integration | API Items |
|---------|---------------|-------------|-----------|
| [figrecipe](https://github.com/ywatanabe1989/figrecipe) | `scitex.plt` | Enhanced | 14 → 3881 |
| [crossref-local](https://github.com/ywatanabe1989/crossref-local) | `scitex.scholar.crossref_scitex` | Enhanced | 98 → 2063 |
| [openalex-local](https://github.com/ywatanabe1989/openalex-local) | `scitex.scholar.openalex_scitex` | Enhanced | - |
| [socialia](https://github.com/ywatanabe1989/socialia) | `scitex.social` | Thin | 2907 → 12 |
| [scitex-writer](https://github.com/ywatanabe1989/scitex-writer) | `scitex.writer` | Thin | 37 → 37 |

## Architecture

```
scitex (umbrella)
├── scitex.plt      ← figrecipe + matplotlib + local features
├── scitex.scholar  ← crossref-local + openalex-local + local features
├── scitex.social   ← socialia (thin wrapper)
└── scitex.writer   ← scitex-writer (thin wrapper)
```

## Integration Patterns

### Thin Wrapper (scitex.writer, scitex.social)

Re-export downstream package as-is, without modifications.

**Python API:**
```python
# scitex/writer/__init__.py
from scitex_writer import bib, compile, figures, guidelines, project, prompts, tables

# scitex/social/__init__.py
from socialia import Twitter, LinkedIn, Reddit, YouTube, GoogleAnalytics, BasePoster
```

**MCP Tools:**
```python
# scitex/_mcp/__init__.py — ONE registry-mounting entrypoint.
# Each peer's FastMCP server is auto-mounted under a brand-prefixed
# namespace by iterating scitex_dev._ecosystem.ECOSYSTEM. No per-package
# "register_<pkg>_tools" bridge files; new peer tools appear automatically.
def register_all_tools(mcp):
    for _pip, import_name, namespace in _iter_registry():
        peer_mcp = _resolve_peer_mcp(import_name)   # e.g. scitex_writer._mcp.server
        if peer_mcp is not None:
            safe_mount(mcp, peer_mcp, namespace=namespace)  # -> writer_*, socialia_*
```

- Single source of truth: the ecosystem registry + each downstream package
- API parity: `scitex.writer` ≈ `scitex_writer`, `scitex.social` ≈ `socialia`
- MCP tools auto-mounted from each peer's `_mcp_server` — no umbrella maintenance
- Use `scitex introspect api` to verify consistency

### Enhanced Wrapper (scitex.plt, scitex.scholar)

Integrate downstream package with scitex-specific features.

```python
# scitex/plt/__init__.py
from figrecipe import compose, crop, save, subplots  # Core from figrecipe
from . import ax, color, gallery, styles             # Local scitex features
```

- Downstream as foundation
- Local features added (color palettes, gallery, etc.)
- API larger than standalone package

## CLI

```bash
# Via scitex (hyphen or underscore both work)
scitex introspect api scitex-writer  # → 37 items
scitex introspect api scitex.writer  # → 37 items

# Standalone
scitex-writer --help
socialia --help
```

## Branding

Set environment variables before importing to apply scitex namespace:

```python
os.environ.setdefault("SCITEX_WRITER_BRAND", "scitex.writer")
os.environ.setdefault("FIGRECIPE_BRAND", "scitex.plt")
```

## Port Scheme

SciTeX uses `3129X` (sa-i-te-ku-su = 3-1-2-9):

| Port | Service |
|------|---------|
| 31290 | scitex-cloud |
| 31291 | crossref-local |
| 31292 | openalex |
| 31293 | scitex-audio |

<!-- EOF -->
