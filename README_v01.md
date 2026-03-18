<!-- ---
!-- Timestamp: 2026-03-18 14:40:10
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-python/README.md
!-- --- -->

# SciTeX (<code>scitex</code>)

<p align="center">
  <a href="https://scitex.ai">
    <img src="docs/assets/images/scitex-logo-blue-cropped.png" alt="SciTeX" width="400">
  </a>
</p>

<p align="center"><b>Modular Python Toolkit for AI and Humans</b></p>

<p align="center">
  <a href="https://badge.fury.io/py/scitex"><img src="https://badge.fury.io/py/scitex.svg" alt="PyPI version"></a>
  <a href="https://pypi.org/project/scitex/"><img src="https://img.shields.io/pypi/pyversions/scitex.svg" alt="Python Versions"></a>
  <a href="https://github.com/ywatanabe1989/scitex-python/blob/main/LICENSE"><img src="https://img.shields.io/github/license/ywatanabe1989/scitex-python" alt="License"></a>
  <img src="https://img.shields.io/badge/uv-recommended-blue" alt="uv recommended">
</p>

<p align="center">
  <a href="https://scitex-python.readthedocs.io">Full Documentation</a> · <code>pip install scitex</code>
</p>

---

## Problem

Researchers face a fragmented toolchain -- literature search, statistical analysis, figure creation, and manuscript writing each require separate tools with incompatible formats. AI agents can automate these steps, but lack a unified interface that connects them into a coherent pipeline.

## Solution

SciTeX provides a **modular Python toolkit** that unifies the research workflow from raw data to manuscript. This repository hosts the main orchestration package is the `scitex` Python package. Each module (e.g., io, scholar, stats, plt, writer) works standalone (e.g., `scitex_io`) or together (e.g., `scitex.io`), accessible through Python API, CLI, and MCP (Model Context Protocol) for AI agents.

<p align="center">
    <img src="scripts/assets/workflow_out/workflow.png" alt="SciTeX Ecosystem" width="800">
</p>

<p align="center"><sub><b>Figure 1.</b> SciTeX research pipeline -- AI agents orchestrate the full workflow from literature search to manuscript compilation.</sub></p>

## Demo

**40 min, minimal human intervention** -- AI agent conducts full research pipeline:

> Literature search -> Data analysis -> Statistics -> Figures -> 21-page manuscript -> Peer review simulation

<p align="center">
  <a href="https://scitex.ai/demos/watch/scitex-automated-research/" title="Watch full demo at scitex.ai/demos/">
    <img src="docs/assets/images/scitex-demo.gif" alt="SciTeX Demo" width="800">
  </a>
</p>

## Installation

``` bash
pip install scitex[all]                # Recommended: Full installation
pip install scitex                     # Core (minimal)
pip install scitex[plt,stats,scholar]  # Typical research setup
```

## Quick Start

### Python API

<details>
<summary><strong>**`@scitex.session`** -- Reproducible Experiment Tracking</strong></summary>

A single `@scitex.session` decorator enables:

1. Automatic CLI command support without `argparser`
2. Loading parameters from `./config/*yaml` files - No hard-coded parameters in scripts
3. Automatic fixation of random seeds and generation of random seed generators
4. Colored logging
5. Allocate timestamp and runtime ID
6. Log standard input/output, parameters, into predefined output structure

```python
import scitex

# # Parameters
# CONFIG = scitex.io.load_configs() # For imported files using `./config/*.yaml`

# Functions and Classes
@scitex.session
def main(
    # arg1,
    # kwarg1="value1",
    CONFIG=scitex.session.INJECTED, # Aggregated parameters from ./config/*yaml files
    plt=scitex.session.INJECTED,    # FigRecipe, a matplotlib wrapper
    COLORS=scitex.session.INJECTED,
    rngg=scitex.session.INJECTED,   # Generator for random seed generators
    logger=scitex.session.INJECTED, # Logging wrapper
):
    """Help message here for `$ python __file__ --help`"""
    return 0


if __name__ == '__main__':
    main()
```

**Output**:
```
script_out/FINISHED_SUCCESS/2025-01-08_12-30-00_AbC1/
├── demo.jpg                    # Figure with embedded metadata
├── demo.csv                    # Auto-exported plot data
├── CONFIGS/CONFIG.yaml         # Reproducible parameters aggregated from ./config directory
└── logs/{stdout,stderr}.log    # Execution logs
```

</details>

<details>
<summary><strong>**`scitex.io`** -- A Unified File I/O Interface (30+ formats)</strong></summary>

scitex.io.{load,save} enables a unified interface, just like clicking files in Windows/MacOS.

```python
# Save
scitex.io.save(df, "df.csv")
df = scitex.io.load("output.csv") # Round Trip

scitex.io.save(fig, "fig.jpg")
# fig = scitex.io.save(fig, "fig.jpg")

scitex.io.save(arr, "arr.npy")
arr = scitex.io.load("outout.npy") # Round Trip

scitex.io.save(dict_for_yaml, "dict_for_yaml.yaml")
dict_for_yaml = scitex.io.load("dict_for_yaml.yaml") # Round Trip

scitex.io.save(dict_for_json, "dict_for_json.json")
dict_for_json = scitex.io.load("dict_for_json.json") # Round Trip

scitex.io.save(serializable, "serializable.pkl")
serializable = scitex.io.load("seriealizable.pkl") # Round Trip
```

</details>

<details>
<summary><strong>**`scitex.stats`** -- Publication-Ready Statistics (23 tests)</strong></summary>

```python
result = scitex.stats.test_ttest_ind(group1, group2, return_as="dataframe")
# Includes: p-value, effect size, CI, normality check, power
```

</details>

> **[Full module status](./docs/MODULE_STATUS.md)**

<details>
<summary><strong>CLI Commands</strong></summary>

<br>

```bash
scitex --help-recursive              # Show all commands
scitex scholar fetch "10.1038/..."   # Download paper by DOI
scitex scholar bibtex refs.bib       # Enrich BibTeX
scitex stats recommend               # Suggest statistical tests
scitex audio speak "Done"            # Text-to-speech
scitex capture snap                  # Screenshot

# List available APIs and tools
scitex list-python-apis              # List all Python APIs (210 items)
scitex mcp list-tools                # List all MCP tools (120+ tools)
scitex introspect api scitex.stats   # List APIs for specific module
```

> **[Full CLI reference](./docs/CLI_COMMANDS.md)**

</details>

<details>
<summary><strong>MCP Server -- for AI Agents</strong></summary>

<br>

Turn AI agents into autonomous scientific researchers via the [Model Context Protocol](https://modelcontextprotocol.io/).

**Typical workflow**: Scholar (find papers) -> Stats (analyze) -> Plt (visualize) -> Writer (manuscript) -> Capture (verify)

| Category | Tools | Description |
|----------|-------|-------------|
| writer | 28 | LaTeX manuscript compilation |
| scholar | 23 | PDF download, metadata enrichment |
| capture | 12 | Screen monitoring and capture |
| introspect | 12 | Python code introspection |
| audio | 10 | Text-to-speech, audio playback |
| stats | 10 | Automated statistical testing |
| plt | 9 | Matplotlib figure creation |
| diagram | 9 | Mermaid and Graphviz diagrams |
| dataset | 8 | Scientific dataset access |
| social | 7 | Social media posting |
| canvas | 7 | Scientific figure canvas |
| template | 6 | Project scaffolding |
| verify | 6 | Reproducibility verification |
| dev | 6 | Ecosystem version management |
| ui | 5 | Notifications |
| linter | 3 | Code pattern checking |

<sub><b>Table 1.</b> 120+ MCP tools organized by category. All tools accept JSON parameters and return structured results.</sub>

#### Claude Code Setup

Add `.mcp.json` to your project root. Use `SCITEX_ENV_SRC` to load all configuration from a `.src` file -- this keeps `.mcp.json` static across environments:

```json
{
  "mcpServers": {
    "scitex": {
      "command": "scitex",
      "args": ["mcp", "start"],
      "env": {
        "SCITEX_ENV_SRC": "${SCITEX_ENV_SRC}"
      }
    }
  }
}
```

Then switch environments via your shell profile:

```bash
# Local machine
export SCITEX_ENV_SRC=~/.scitex/scitex/local.src

# Remote server
export SCITEX_ENV_SRC=~/.scitex/scitex/remote.src
```

Generate a template `.src` file:

```bash
scitex env-template -o ~/.scitex/scitex/local.src
```

Or install globally:

```bash
scitex mcp installation
```

> **[Full MCP tool reference](./docs/MCP_TOOLS.md)**

</details>

<details>
<summary><strong>Configuration</strong></summary>

<br>

Modular environment configuration via `.env.d/`:

```bash
# 1. Copy examples
cp -r .env.d.examples .env.d

# 2. Edit with your credentials
$EDITOR .env.d/

# 3. Source in shell (~/.bashrc or ~/.zshrc)
source /path/to/.env.d/entry.src
```

**Structure:**
```
.env.d/
├── entry.src              # Single entry point
├── 00_scitex.env          # Base settings (SCITEX_DIR)
├── 00_crossref-local.env  # CrossRef database
├── 00_figrecipe.env       # Plotting config
├── 01_scholar.env         # OpenAthens, API keys
├── 01_audio.env           # TTS backends
└── ...                    # Per-module configs
```

> **[Full configuration reference](./.env.d.examples/README.md)**

</details>

## Standalone Packages

SciTeX integrates several standalone packages that can be used independently:

<details>

``` bash
(.env-3.11) (wsl) scitex-cloud $ scitex-dev ecosystem list
  scitex                    ywatanabe1989/scitex-python
  scitex-io                 ywatanabe1989/scitex-io
  scitex-stats              ywatanabe1989/scitex-stats
  scitex-clew               ywatanabe1989/scitex-clew
  scitex-cloud              ywatanabe1989/scitex-cloud
  figrecipe                 ywatanabe1989/figrecipe
  scitex-plt                ywatanabe1989/scitex-plt
  openalex-local            ywatanabe1989/openalex-local
  crossref-local            ywatanabe1989/crossref-local
  scitex-writer             ywatanabe1989/scitex-writer
  scitex-linter             ywatanabe1989/scitex-linter
  scitex-dataset            ywatanabe1989/scitex-dataset
  socialia                  ywatanabe1989/socialia
  automated-research-demo   ywatanabe1989/automated-research-demo
  scitex-research-template  ywatanabe1989/scitex-research-template
  pip-project-template      ywatanabe1989/pip-project-template
  scitex-container          ywatanabe1989/scitex-container
  scitex-tunnel             ywatanabe1989/scitex-tunnel
  scitex-ui                 ywatanabe1989/scitex-ui
  scitex-app                ywatanabe1989/scitex-app
  scitex-audio              ywatanabe1989/scitex-audio
  scitex-scholar            ywatanabe1989/scitex-scholar
  scitex-dev                ywatanabe1989/scitex-dev
  singularity-template      ywatanabe1989/singularity-template
```

| Package | scitex Module | Description |
|---------|--------------|-------------|
| [figrecipe](https://github.com/ywatanabe1989/figrecipe) | `scitex.plt` | Publication-ready matplotlib figures |
| [crossref-local](https://github.com/ywatanabe1989/crossref-local) | `scitex.scholar.crossref_scitex` | Local CrossRef database (167M+ papers) |
| [openalex-local](https://github.com/ywatanabe1989/openalex-local) | `scitex.scholar.openalex_scitex` | Local OpenAlex database (250M+ papers) |
| [socialia](https://github.com/ywatanabe1989/socialia) | `scitex.social` | Social media posting (Twitter, LinkedIn) |
| [scitex-writer](https://github.com/ywatanabe1989/scitex-writer) | `scitex.writer` | LaTeX manuscript compilation |
| [scitex-dataset](https://github.com/ywatanabe1989/scitex-dataset) | `scitex.dataset` | Scientific dataset access |

Each package works standalone or as part of scitex:

```bash
pip install scitex-io        # Use independently as import scitex_io
pip install scitex[io]       # Or via scitex as scitex.io module
```

</details>

## Role in SciTeX Ecosystem

`scitex` is the **unified orchestrator** package. It re-exports functionality from sub-packages so users have a single import (`import scitex`). It does not contain runtime logic itself -- it delegates to sub-packages.

```
scitex (this package) -- orchestrator, templates, CLI, MCP server
  |-- scitex.app  <-  scitex-app   (runtime SDK: file I/O, config, validation)
  |-- scitex.ui   <-  scitex-ui    (React/TS components: workspace, data-table)
  +-- scitex.plt  <-  figrecipe    (figures: plotting, diagrams, recipes)
```

**What this package owns:**

- All project templates (`scitex template clone app my_app`, `research`, `pip`, `paper`, `singularity`)
- CLI entry point (`scitex <module> <command>`)
- MCP server (120+ tools aggregated from sub-packages)
- Session decorator (`@scitex.session`) and reproducibility tracking

**What this package does NOT own:**

- Runtime app SDK -- see [scitex-app](https://github.com/ywatanabe1989/scitex-app)
- Frontend components -- see [scitex-ui](https://github.com/ywatanabe1989/scitex-ui)
- Figure/diagram engine -- see [figrecipe](https://github.com/ywatanabe1989/figrecipe)

## Part of SciTeX

SciTeX is an open-source research automation platform at [scitex.ai](https://scitex.ai).

- **[Read the Docs](https://scitex-python.readthedocs.io/)**: Complete API reference
- **[Examples](./examples/)**: Usage examples and demonstrations
- **[Contributing](CONTRIBUTING.md)**: We welcome contributions

The SciTeX system follows the Four Freedoms for Research below, inspired by [the Free Software Definition](https://www.gnu.org/philosophy/free-sw.en.html):

>Four Freedoms for Research
>
>0. The freedom to **run** your research anywhere -- your machine, your terms.
>1. The freedom to **study** how every step works -- from raw data to final manuscript.
>2. The freedom to **redistribute** your workflows, not just your papers.
>3. The freedom to **modify** any module and share improvements with the community.
>
>AGPL-3.0 -- because we believe research infrastructure deserves the same freedoms as the software it runs on.

---

## Star History

<a href="https://star-history.com/#ywatanabe1989/scitex-python&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=ywatanabe1989/scitex-python&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=ywatanabe1989/scitex-python&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=ywatanabe1989/scitex-python&type=Date" />
 </picture>
</a>

---

<p align="center">
  <a href="https://scitex.ai" target="_blank"><img src="docs/assets/images/scitex-icon-navy-inverted.png" alt="SciTeX" width="40"/></a>
</p>

<!-- EOF -->