<!-- ---
!-- Timestamp: 2026-03-18 15:31:55
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-python/README.md
!-- --- -->

# SciTeX (<code>scitex</code>)

<p align="center">
  <a href="https://scitex.ai">
    <img src="docs/assets/images/scitex-logo-blue-cropped.png" alt="SciTeX" width="400">
  </a>
</p>

<p align="center"><b>Modular Python Toolkit for Scientific Research Automation</b></p>

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

## Demo

**40 min, minimal human intervention** -- AI agent conducts: literature search -> data analysis -> statistics -> figures -> 21-page manuscript -> peer review simulation

<p align="center">
  <a href="https://scitex.ai/demos/watch/scitex-automated-research/">
    <img src="docs/assets/images/scitex-demo.gif" alt="SciTeX Demo" width="800">
  </a>
</p>

## Why SciTeX?

Researchers face a fragmented toolchain -- literature search, statistical analysis, figure creation, and manuscript writing each require separate tools. AI agents can automate these steps, but lack a unified interface. And as AI-accelerated research compounds both volume and opacity, the gap between what is published and what can be verified continues to widen.

SciTeX unifies the research workflow from raw data to manuscript -- with **cryptographic verification** built into every step. Each module works standalone or together, accessible through **Python API**, **CLI**, and **MCP** for AI agents. SciTeX also serves as the computational engine behind [SciTeX Cloud](https://github.com/ywatanabe1989/scitex-cloud) ([scitex.ai](https://scitex.ai)) -- a self-hostable web platform for collaborative research.

```
                                SciTeX Ecosystem
      ┌─────────────────────────────────────────────────────────────┐
      │  SciTeX Cloud (scitex.ai) -- self-hosted research platform  │
      │    Writer | Scholar | FigRecipe | Clew | Hub | Apps         |
      ├─────────────────────────────────────────────────────────────┤
      │  scitex (this package) -- Python engine & orchestrator      │
      │    @session | io | stats | plt | scholar | writer | clew    │
      ├──────────┬──────────┬──────────┬──────────┬─────────────────┤
      │ scitex-  │ scitex-  │ fig-     │ scitex-  │  scitex-clew    │
      │ io       │ stats    │ recipe   │ writer   │  (verification) │
      │ 30+ fmt  │ 23 tests │ figures  │ LaTeX    │  SHA-256 DAG    │
      └──────────┴──────────┴──────────┴──────────┴─────────────────┘
       Each package: standalone (pip install scitex-io) or unified (scitex.io)
```

<p align="center">
    <img src="scripts/assets/workflow_out/workflow.png" alt="SciTeX Ecosystem" width="400">
</p>
<p align="center"><sub><b>Figure 1.</b> SciTeX research pipeline -- from literature search to manuscript compilation, with every step cryptographically linked.</sub></p>

## Installation

```bash
pip install scitex[all]                # Recommended: everything
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

## Quick Start

<details>
<summary><strong><code>@scitex.session</code> -- Reproducible Experiment Tracking</strong></summary>

One decorator gives you: auto-CLI, YAML config injection, random seed fixation, structured output, and logging.

```python
import scitex as stx
import numpy as np
    
@stx.session
def main(
    data_path,                       # Positional arg: python script.py data.csv
    n_samples=100,                   # Keyword arg:    python script.py data.csv --n-samples 200
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
    ax.plot_line(x, y)
    ax.set_xyt("Time", "Amplitude", "Noisy Sine Wave")
    
    # Save sine.png + sine.csv with logging message
    stx.io.save(fig, "sine.png")
    
    return 0

if __name__ == "__main__":
    main()
```

```bash
$ python script.py data.csv --n-samples 200
$ python script.py --help
# usage: script.py [-h] [--n-samples N_SAMPLES] data_path
# Analyze data. Docstring becomes --help text.
```

```
script_out/FINISHED_SUCCESS/2026-03-18_14-30-00_Z5MR/
├── sine.png, sine.csv         # Figure + auto-exported plot data
├── CONFIGS/CONFIG.yaml        # Frozen parameters
└── logs/{stdout,stderr}.log   # Execution logs
```
</details>

<details>
<summary><strong><code>scitex.clew</code> -- Cryptographic Verification for AI-Driven Science</strong></summary>

As AI agents produce research at scale, the question shifts from *"could this be reproduced?"* to *"has this been verified?"*. Clew builds a **SHA-256 hash-chain DAG** linking every manuscript claim back to source data.

```python
import scitex as stx

# Every stx.io.load/save automatically records file hashes -- zero config
stx.clew.status()                          # {'verified': 12, 'mismatched': 0, 'missing': 0}
stx.clew.chain("results/figure1.png")      # Trace one file back to source data
stx.clew.dag(claims=True)                  # Verify all manuscript claims

# Register traceable assertions
stx.clew.add_claim(
    file_path="paper/main.tex", claim_type="statistic", line_number=142,
    claim_value="t(58) = 2.34, p = .021",
    source_session="2026-03-18_14-30-00_Z5MR", source_file="results/stats.csv",
)

stx.clew.mermaid(claims=True)              # Visualize provenance DAG
```

| Mode | Function | Answers |
|------|----------|---------|
| **Project** | `clew.dag()` | Is the whole project intact? |
| **File** | `clew.chain("output.csv")` | Can I trust this specific file? |
| **Claim** | `clew.verify_claim("Fig 1")` | Is this manuscript assertion valid? |

**L1** hash comparison (ms) / **L2** sandbox re-execution (min) / **L3** registered timestamp proof (optional).

<p align="center">
  <img src="docs/assets/images/clew-dag.png" alt="Clew DAG" width="300">
</p>
<p align="center"><sub><b>Figure 2.</b> Clew verification DAG -- green nodes are verified (hash match), red nodes have mismatches. Each node shows its SHA-256 hash prefix.</sub></p>

</details>

<details>
<summary><strong><code>scitex.io</code> -- Unified File I/O (30+ Formats)</strong></summary>

```python
import scitex as stx

# Save and load -- format detected from extension
stx.io.save(df, "results.csv")
df = stx.io.load("results.csv")

stx.io.save(arr, "data.npy")
arr = stx.io.load("data.npy")

stx.io.save(fig, "figure.png")       # Also exports figure data as CSV
stx.io.save(config, "config.yaml")
stx.io.save(model, "model.pkl")

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
</details>

<details>
<summary><strong><code>scitex.plt</code> -- Reproducible, Restylable Figures</strong></summary>

Powered by [figrecipe](https://github.com/ywatanabe1989/figrecipe). Figures are **reproducible nodes** in the Clew verification DAG -- scientific data and visual style are decomposed, so figures can be restyled (fonts, colors, layout) without altering the underlying data hash. Every figure auto-exports its data as CSV + a YAML recipe for exact reproduction.

```python
import scitex as stx
fig, axes = stx.plt.subplots(1, 3)
axes[0].stx_line(x, y)
axes[0].set_xyt("Time", "Value", "Line")

axes[1].stx_violin([g1, g2, g3])
axes[1].set_xyt("Group", "Score", "Violin")

axes[2].stx_heatmap(corr_matrix)
axes[2].set_xyt("X", "Y", "Heatmap")
stx.io.save(fig, "analysis.png")  # Saves analysis.png + analysis.csv + analysis.yaml

# Restyle without changing data (hash stays valid for Clew verification)
stx.plt.reproduce("analysis.yaml", style="nature")
```
</details>

<details>
<summary><strong><code>scitex.stats</code> -- Publication-Ready Statistics (23+ Tests)</strong></summary>

```python
import scitex as stx
result = stx.stats.run_test("ttest_ind", group1, group2, return_as="dataframe")
# Returns: p-value, effect size (Cohen's d), CI, normality check, power
recommendations = stx.stats.recommend_tests(data)
stx.stats.format_results(result, style="apa")   # "t(58) = 2.34, p = .021, d = 0.60"
```
</details>

<details>
<summary><strong><code>scitex.scholar</code> -- Literature Management</strong></summary>

Search, download, enrich papers. Backed by local CrossRef (167M+) and OpenAlex (250M+) databases.

```python
import scitex as stx
papers = stx.scholar.search("neural oscillations working memory", n=20)
stx.scholar.fetch("10.1038/s41586-024-07804-3")
stx.scholar.enrich_bibtex("references.bib", output="enriched.bib")
```

```bash
scitex scholar search "neural oscillations" --n 20
scitex scholar bibtex references.bib --output enriched.bib
```
</details>

<details>
<summary><strong><code>scitex.writer</code> -- LaTeX Manuscript Compilation</strong></summary>

```python
import scitex as stx
stx.writer.compile_manuscript("paper/")
stx.writer.add_figure("paper/", "results.png", caption="Main results")
stx.writer.add_table("paper/", "stats.csv", caption="Statistical summary")
```
</details>

<details>
<summary><strong><code>scitex.notification</code> -- Multi-Backend Notifications</strong></summary>

Get notified when experiments finish -- via desktop, phone call, SMS, or email -- with automatic fallback.

```python
import scitex as stx
stx.notification.alert("Experiment complete: accuracy = 94.2%")
stx.notification.call("Training diverged -- loss is NaN")
stx.notification.sms("GPU job finished on node-42")

@stx.session(notify=True)   # Notifies on completion or failure
def main(CONFIG=stx.session.INJECTED): ...
```
</details>

> **[Full API reference](https://scitex-python.readthedocs.io/en/latest/api/index.html)** &middot; **[Module status](./docs/04_MODULE_STATUS.md)**

## Module Overview

| Category | Modules | Description |
|----------|---------|-------------|
| **Core** | `session`, `io`, `config`, `clew` | Experiment tracking, file I/O, config, cryptographic verification |
| **Analysis** | `stats`, `plt`, `dsp`, `linalg` | Statistics, plotting, signal processing, linear algebra |
| **Research** | `scholar`, `writer`, `diagram`, `canvas` | Literature, manuscripts, diagrams, figure composition |
| **ML/AI** | `ai`, `nn`, `torch`, `cv`, `benchmark` | LLM APIs, neural networks, PyTorch, computer vision |
| **Data** | `pd`, `db`, `dataset`, `schema` | Pandas utilities, databases, scientific datasets |
| **Infra** | `app`, `cloud`, `tunnel`, `container` | App SDK, cloud, SSH tunnels, containers |
| **Automation** | `browser`, `capture`, `audio`, `notification` | Web automation, screenshots, TTS, notifications |
| **Dev** | `dev`, `template`, `linter`, `introspect` | Ecosystem tools, scaffolding, code analysis |

<details>
<summary><strong>CLI Commands</strong></summary>

```bash
scitex --help-recursive                  # Show all commands
scitex scholar search "topic"            # Search literature
scitex scholar fetch "10.1038/..."       # Download paper by DOI
scitex stats recommend                   # Suggest statistical tests
scitex clew status                       # Project verification overview
scitex clew dag --claims                 # Verify all manuscript claims
scitex audio speak "Analysis complete"   # Text-to-speech
scitex notification alert "Job finished"       # Multi-backend notification
scitex template clone research my_proj   # Scaffold a project
scitex dev versions                      # Check ecosystem versions
scitex mcp list-tools                    # List all MCP tools (120+)
```

> **[Full CLI reference](./docs/01_CLI_COMMANDS.md)**
</details>

<details>
<summary><strong>MCP Server (120+ tools for AI agents)</strong></summary>

Turn AI agents into autonomous researchers via [MCP](https://modelcontextprotocol.io/).

| Category | Tools | | Category | Tools |
|----------|-------|-|----------|-------|
| writer | 28 | | stats | 10 |
| scholar | 23 | | plt | 9 |
| capture | 12 | | diagram | 9 |
| introspect | 12 | | clew | 9 |
| audio | 10 | | dataset | 8 |

```json
{"mcpServers": {"scitex": {"command": "scitex", "args": ["mcp", "start"],
  "env": {"SCITEX_ENV_SRC": "${SCITEX_ENV_SRC}"}}}}
```

> **[Full MCP reference](./docs/02_MCP_TOOLS.md)**
</details>

## SciTeX Platform

`scitex` (this package) is the Python engine. It powers the full SciTeX platform:

| Layer | Package | Role |
|-------|---------|------|
| **Cloud** | [scitex-cloud](https://github.com/ywatanabe1989/scitex-cloud) | Self-hosted Django web application ([scitex.ai](https://scitex.ai)) -- Writer, Scholar, App Store, Hub, Clew verification |
| **Frontend** | [scitex-ui](https://github.com/ywatanabe1989/scitex-ui) | React/TypeScript components -- workspace, data tables, editors |
| **App SDK** | [scitex-app](https://github.com/ywatanabe1989/scitex-app) | Runtime SDK for building and sharing custom research apps |
| **Engine** | **scitex** (this) | Python orchestrator -- `@session`, `io`, `stats`, `plt`, `clew`, CLI, MCP |

Each standalone package (`pip install scitex-io`) also works unified (`stx.io`).

<details>
<summary><strong>Full Ecosystem (17 packages)</strong></summary>

| Package | Module | Description |
|---------|--------|-------------|
| [scitex-clew](https://github.com/ywatanabe1989/scitex-clew) | `stx.clew` | SHA-256 hash-chain DAG for provenance |
| [scitex-io](https://github.com/ywatanabe1989/scitex-io) | `stx.io` | Unified file I/O (30+ formats) |
| [scitex-stats](https://github.com/ywatanabe1989/scitex-stats) | `stx.stats` | Publication-ready statistics |
| [figrecipe](https://github.com/ywatanabe1989/figrecipe) | `stx.plt` | Publication-ready matplotlib figures |
| [scitex-writer](https://github.com/ywatanabe1989/scitex-writer) | `stx.writer` | LaTeX manuscript compilation |
| [scitex-scholar](https://github.com/ywatanabe1989/scitex-scholar) | `stx.scholar` | Literature management |
| [scitex-notification](https://github.com/ywatanabe1989/scitex-notification) | `stx.notification` | Multi-backend notifications |
| [scitex-audio](https://github.com/ywatanabe1989/scitex-audio) | `stx.audio` | Text-to-speech and audio |
| [scitex-dev](https://github.com/ywatanabe1989/scitex-dev) | `stx.dev` | Developer tools, ecosystem management |
| [scitex-linter](https://github.com/ywatanabe1989/scitex-linter) | `stx.linter` | AST-based code pattern checking |
| [scitex-dataset](https://github.com/ywatanabe1989/scitex-dataset) | `stx.dataset` | Scientific datasets |
| [scitex-cloud](https://github.com/ywatanabe1989/scitex-cloud) | `stx.cloud` | Self-hosted research platform |
| [scitex-app](https://github.com/ywatanabe1989/scitex-app) | `stx.app` | Runtime SDK for research apps |
| [scitex-ui](https://github.com/ywatanabe1989/scitex-ui) | `stx.ui` | React/TS frontend components |
| [crossref-local](https://github.com/ywatanabe1989/crossref-local) | `stx.scholar` | Local CrossRef (167M+ papers) |
| [openalex-local](https://github.com/ywatanabe1989/openalex-local) | `stx.scholar` | Local OpenAlex (250M+ works) |
| [socialia](https://github.com/ywatanabe1989/socialia) | `stx.social` | Social media (Twitter, LinkedIn) |
</details>

<details>
<summary><strong>Configuration</strong></summary>

```bash
cp -r .env.d.examples .env.d  # 1. Copy examples
$EDITOR .env.d/                # 2. Edit credentials
source .env.d/entry.src        # 3. Source in shell
```

> **[Full configuration reference](./.env.d.examples/README.md)**
</details>

## Part of SciTeX

SciTeX is an open-source research automation platform at [scitex.ai](https://scitex.ai). [SciTeX Cloud](https://github.com/ywatanabe1989/scitex-cloud) provides a self-hostable web application -- GitHub for research -- with Writer, Scholar, App Store, and Clew verification built in.

>Four Freedoms for Research
>
>0. The freedom to **run** your research anywhere -- your machine, your terms.
>1. The freedom to **study** how every step works -- from raw data to final manuscript.
>2. The freedom to **redistribute** your workflows, not just your papers.
>3. The freedom to **modify** any module and share improvements with the community.
>
>AGPL-3.0 -- because research infrastructure deserves the same freedoms as the software it runs on.

---

<p align="center">
  <a href="https://star-history.com/#ywatanabe1989/scitex-python&Date">
    <img alt="Star History" src="https://api.star-history.com/svg?repos=ywatanabe1989/scitex-python&type=Date" />
  </a>
</p>

<p align="center">
  <a href="https://scitex.ai"><img src="docs/assets/images/scitex-icon-navy-inverted.png" alt="SciTeX" width="40"/></a>
</p>

<!-- EOF -->