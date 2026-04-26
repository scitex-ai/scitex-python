---
name: readme-organization
description: Canonical README.md template for every SciTeX package — required section order (one-liner → install → quickstart → interfaces → status/CI badges → links → licence → Four-Freedoms footer), badge set (PyPI version, CI, coverage, RTD, licence), collapsible blocks for long examples, `import scitex` (never `as stx`) in all snippets, absence of the ywatanabe@ signature, and the intra-README link contract that external RTD/Sphinx builds depend on. Use when scaffolding a new repo's README or auditing one for ecosystem drift.
canonical-location: scitex-python/src/scitex/_skills/general/04_docs_01_readme.md
tags: [scitex-python, scitex-general, scitex-package, meta]
---

# README Organization (SciTeX)

## Standard Section Order

Every SciTeX package README follows this structure:

```markdown
# package-name

[Centered SciTeX logo]

**One-line tagline**

[Badges: PyPI, Docs, Tests, License — centered]

[Quick links: Documentation · pip install — centered]

---

## Problem
## Solution
<details><summary>Supported Formats / Feature Table</summary></details>
## Installation
## Quickstart
## Five Interfaces (HTTP optional)
## Lint Rules (if applicable)
## Part of SciTeX
[Four Freedoms blockquote]

---

[Centered SciTeX icon footer]

```

## Badge Row (SciTeX Style)

```markdown
<p align="center">
  <a href="https://badge.fury.io/py/PACKAGE"><img src="https://badge.fury.io/py/PACKAGE.svg" alt="PyPI version"></a>
  <a href="https://PACKAGE.readthedocs.io/"><img src="https://readthedocs.org/projects/PACKAGE/badge/?version=latest" alt="Documentation"></a>
  <a href="https://github.com/ywatanabe1989/PACKAGE/actions/workflows/ci.yml"><img src="https://github.com/ywatanabe1989/PACKAGE/actions/workflows/ci.yml/badge.svg" alt="Tests"></a>
  <a href="https://www.gnu.org/licenses/agpl-3.0"><img src="https://img.shields.io/badge/License-AGPL--3.0-blue.svg" alt="License: AGPL-3.0"></a>
</p>
```

## Five Interfaces, HTTP optional (Collapsible)

Each interface in its own `<details>` block:

```markdown
<details>
<summary><strong>Python API</strong></summary>
[Code examples]
</details>

<details>
<summary><strong>CLI Commands</strong></summary>
[Command examples]
</details>

<details>
<summary><strong>MCP Server — for AI Agents</strong></summary>
[Tool table + start command]
</details>

<details>
<summary><strong>Skills — for AI Agent Discovery</strong></summary>
[Skill table + CLI commands]
</details>
```

## Four Freedoms Footer

```markdown
## Part of SciTeX

PACKAGE is part of [**SciTeX**](https://scitex.ai).

>Four Freedoms for Research
>
>0. The freedom to **run** your research anywhere — your machine, your terms.
>1. The freedom to **study** how every step works — from raw data to final manuscript.
>2. The freedom to **redistribute** your workflows, not just your papers.
>3. The freedom to **modify** any module and share improvements with the community.
>
>AGPL-3.0 — because we believe research infrastructure deserves the same freedoms as the software it runs on.

---

<p align="center">
  <a href="https://scitex.ai" target="_blank"><img src="docs/scitex-icon-navy-inverted.png" alt="SciTeX" width="40"/></a>
</p>

```

## SciTeX-Specific Rules

- **No `ywatanabe@scitex.ai`** in footer — community project
- **Use `import scitex`** in examples, not `import scitex as stx`
- **Verify all format/feature claims** against actual `_builtin_handlers.py` or source code
- **Match quickstart.rst** — README Quickstart and Sphinx quickstart should show the same examples
- **Add Logo and Icon** docs/assets/images/{scitex-logo-blue-cropped.png,scitex-icon-navy-inverted.png}

---

## Project README.md Examples

### Header

``` markdown
# SciTeX (<code>scitex</code>)

<p align="center">
  <a href="https://scitex.ai">
    <img src="docs/assets/images/scitex-logo-blue-cropped.png" alt="SciTeX" width="400">
  </a>
</p>

<p align="center"><b>Python Library for Science. For AI and Human Researchers</b></p>

<p align="center">
  <a href="https://badge.fury.io/py/scitex"><img src="https://badge.fury.io/py/scitex.svg" alt="PyPI version"></a>
  <a href="https://pypi.org/project/scitex/"><img src="https://img.shields.io/pypi/pyversions/scitex.svg" alt="Python Versions"></a>
  <a href="https://scitex-python.readthedocs.io"><img src="https://readthedocs.org/projects/scitex-python/badge/?version=latest" alt="Documentation"></a>
  <a href="https://github.com/ywatanabe1989/scitex-python/blob/main/LICENSE"><img src="https://img.shields.io/github/license/ywatanabe1989/scitex-python" alt="License"></a>
</p>

<p align="center">
  <a href="https://scitex-python.readthedocs.io">Docs</a> &middot;
  <a href="https://scitex-python.readthedocs.io/en/latest/quickstart.html">Quick Start</a> &middot;
  <a href="https://scitex-python.readthedocs.io/en/latest/api/index.html">API</a> &middot;
  <code>pip install scitex[all]</code>
</p>

---
```

### Problem and Solution

``` markdown
This repository provides `scitex`, the orchestration layer of the SciTeX ecosystem — solving key problems in scientific research:

## Problem and Solution

| # | Problem | Solution |
|---|---------|----------|
| 1 | **Fragmented tools** -- literature search, statistics, figures, and writing each require separate tools with incompatible formats | **Unified toolkit** -- `import scitex as stx` provides 73 modules under one namespace, accessible via Python API, CLI, and MCP. These modules are standalone packages but loosely coupled through a plugin registry — each works on its own, yet composes into designed synergy (save a figure → auto-exports CSV + YAML recipe → hash-tracked by Clew → citeable in scitex-writer). |
| 2 | **No verification** -- existing tools address whether work *could* be reproduced, not whether it *has* been verified | **Cryptographic verification** -- Clew builds SHA-256 hash-chain DAGs linking every manuscript claim back to source data |
| 3 | **AI agents lack context** -- general-purpose LLMs cannot operate across the full research lifecycle without domain-specific tools | **323 MCP tools** -- AI agents run statistics, create figures, search literature, and compile manuscripts through structured tool calls |
| 4 | **No custom tooling** -- every lab needs domain-specific tools, but building and sharing them requires deep infrastructure knowledge | **App Maker and Store** -- researchers create custom apps with [scitex-app](https://github.com/ywatanabe1989/scitex-app) SDK and share via [SciTeX Cloud](https://scitex.ai) |
| 5 | **Vendor lock-in** -- cloud research tools (Overleaf, Zotero, Mendeley, Colab, GitHub Copilot) keep data on third-party servers and depend on APIs that can disappear overnight or monetize tomorrow | **Open and self-hostable** -- every SciTeX package is AGPL-3.0; the full 39-package ecosystem runs on your own hardware (or SciTeX Cloud which itself is self-hostable); cloud integrations are pluggable extras, not requirements |
```

### Installation

``` markdown
## Installation

```bash
pip install scitex[all]                # Recommended: everything (may take >1 hour on first install — see Installation Tips)
```

<details>
<summary><strong>Per-module extras</strong></summary>

```bash
pip install scitex                     # Core only (minimal)
pip install scitex[plt,stats,scholar]  # Typical research setup
pip install scitex[plt]                # Publication-ready figures (figrecipe)
pip install scitex[stats]              # Statistical testing (23+ tests)
pip install scitex[scholar]            # Literature search, PDF download, BibTeX enrichment
pip install scitex[writer]             # LaTeX manuscript compilation
pip install scitex[audio]              # Text-to-speech
pip install scitex[ai]                 # LLM APIs (OpenAI, Anthropic, Google) + ML tools
pip install scitex[dataset]            # Scientific datasets (DANDI, OpenNeuro, PhysioNet)
pip install scitex[browser]            # Web automation (Playwright)
pip install scitex[capture]            # Screenshot capture and monitoring
pip install scitex[cloud]              # Cloud platform integration
```

Requires Python 3.10+. We recommend [uv](https://docs.astral.sh/uv/) for fast installs.
</details>
```

### Quick Start

``` markdown
## Quick Start

<details>
<summary><strong><code>@scitex.session</code> -- Reproducible Experiment Tracking</strong></summary>

One decorator gives you: auto-CLI, YAML config injection, random seed fixation, structured output, and logging.

```python
import scitex as stx
import numpy as np

@stx.session
def main(
    data_path: str = "./data.csv",   # --data-path data.csv
    n_samples: int = 100,            # --n-samples 200
    CONFIG=stx.session.INJECTED,     # Aggregated ./config/*.yaml
    plt=stx.session.INJECTED,        # Pre-configured matplotlib
    logger=stx.session.INJECTED,     # Session logger
):
    """Analyze data. Docstring becomes --help text."""
    
    # Load
    data = stx.io.load(data_path)
    
    # Demo data
    x = np.linspace(0, 2 * np.pi, n_samples)
    y = np.sin(x) + np.random.randn(n_samples) * 0.1
    
    # FigRecipe Plot
    fig, ax = stx.plt.subplots()
    ax.plot(x, y)
    ax.set_xyt("Time", "Amplitude", "Noisy Sine Wave")
    
    # Save sine.png + sine.csv with logging message
    stx.io.save(fig, "sine.png")
    
    return 0

if __name__ == "__main__":
    main()
```

```bash
$ python script.py --data-path experiment.csv --n-samples 200
$ python script.py --help
# usage: script.py [-h] [--data-path DATA_PATH] [--n-samples N_SAMPLES]
# Analyze data. Docstring becomes --help text.
```

```
script_out/FINISHED_SUCCESS/2026-03-18_14-30-00_Z5MR/
├── sine.png, sine.csv         # Figure + auto-exported plot data
├── CONFIGS/CONFIG.yaml        # Frozen parameters
└── logs/{stdout,stderr}.log   # Execution logs
```

The injected `CONFIG` is a `DotDict` merging YAML user configs with session-resolved keys:

| Key | Meaning |
|-----|---------|
| `CONFIG.ID` | Session identifier, e.g. `2026-04-23T21-30-00_Z5MR` |
| `CONFIG.PID` | Python process ID |
| `CONFIG.START_DATETIME` | When the session started |
| `CONFIG.FILE` | Path to caller script |
| `CONFIG.SDIR_OUT` | Base output dir, e.g. `analysis_out/` |
| `CONFIG.SDIR_RUN` | This run's dir, e.g. `analysis_out/FINISHED_SUCCESS/<ID>/` |
| `CONFIG.ARGS` | Parsed CLI args |
| `CONFIG.MODEL.*` | Values from `./config/MODEL.yaml` (one namespace per YAML file) |

Use `CONFIG.SDIR_RUN / "results.csv"` to re-load a file saved earlier in the same session. A frozen copy of `CONFIG` is persisted to `CONFIG.SDIR_RUN/CONFIGS/{CONFIG.yaml,CONFIG.pkl}` so any run is fully auditable. See [25_session-config](./src/scitex/_skills/general/25_session-config.md) for the full reference.
</details>


<details>
<summary><strong><code>scitex.io</code> -- Unified File I/O (50+ Formats)</strong></summary>

```python
import scitex as stx

# Save and load -- format detected from extension.
# symlink_from_cwd=True drops a symlink at cwd so round-trip by filename works;
# without it, save() routes to <script>_out/ and load() must use an absolute path.
stx.io.save(df, "results.csv", symlink_from_cwd=True)
df = stx.io.load("results.csv")

stx.io.save(arr, "data.npy", symlink_from_cwd=True)
arr = stx.io.load("data.npy")

stx.io.save(fig, "figure.png")       # Also exports figure data as CSV
stx.io.save(config, "config.yaml")
stx.io.save(model, "model.pkl")

# Aggregate ./config/*.yaml into a single DotDict
CONFIG = stx.io.load_configs(config_dir="./config")
print(CONFIG.MODEL.hidden_size)      # Dot-notation access

# Register custom formats
@stx.io.register_saver(".custom")
def save_custom(obj, path, **kw):
    with open(path, "w") as f:
        f.write(str(obj))

@stx.io.register_loader(".custom")
def load_custom(path, **kw):
    with open(path) as f:
        return f.read()
```

Supports: CSV, JSON, YAML, TOML, HDF5, NPY, NPZ, PKL, PNG, JPG, SVG, PDF, Excel, Parquet, Zarr, INI, TXT, MAT, WAV, MP3, BibTeX, and more.

**Built-in features**: Auto directory creation, path resolution to `<script_name>_out/`, symlinks (`symlink_from_cwd=True`), save logging with file size, and Clew hash tracking.
</details>

...

</details>
```

### Footer

``` markdown
## Part of SciTeX

scitex-io is part of [**SciTeX**](https://scitex.ai). When used inside the SciTeX framework, I/O is seamless:

```python
import scitex

@scitex.session
def main(CONFIG=scitex.INJECTED):
    data = scitex.io.load("input.csv")     # auto-tracked by clew
    result = process(data)
    scitex.io.save(result, "output.csv")   # auto-tracked by clew
    return 0
```

`scitex.io` delegates to `scitex_io` — they share the same API and registry.

The SciTeX system follows the Four Freedoms for Research below, inspired by [the Free Software Definition](https://www.gnu.org/philosophy/free-sw.en.html):

>Four Freedoms for Research
>
>0. The freedom to **run** your research anywhere — your machine, your terms.
>1. The freedom to **study** how every step works — from raw data to final manuscript.
>2. The freedom to **redistribute** your workflows, not just your papers.
>3. The freedom to **modify** any module and share improvements with the community.
>
>AGPL-3.0 — because we believe research infrastructure deserves the same freedoms as the software it runs on.

---

<p align="center">
  <a href="https://scitex.ai" target="_blank"><img src="docs/assets/images/scitex-icon-navy-inverted.png" alt="SciTeX" width="40"/></a>
</p>

```
