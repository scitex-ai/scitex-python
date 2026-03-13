<!-- ---
!-- Timestamp: 2026-02-16 10:13:53
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-python/README.md
!-- --- -->

<p align="center">
  <a href="https://scitex.ai">
    <img src="docs/assets/images/scitex-logo-blue-cropped.png" alt="SciTeX" width="400">
  </a>
</p>

<p align="center">
  <a href="https://badge.fury.io/py/scitex"><img src="https://badge.fury.io/py/scitex.svg" alt="PyPI version"></a>
  <a href="https://pypi.org/project/scitex/"><img src="https://img.shields.io/pypi/pyversions/scitex.svg" alt="Python Versions"></a>
  <a href="https://github.com/ywatanabe1989/scitex-python/blob/main/LICENSE"><img src="https://img.shields.io/github/license/ywatanabe1989/scitex-python" alt="License"></a>
  <img src="https://img.shields.io/badge/uv-recommended-blue" alt="uv recommended">
</p>

<p align="center">
  <a href="https://scitex.ai">scitex.ai</a> · <a href="https://scitex-python.readthedocs.io">Read the Docs</a> · <code>pip install scitex</code>
</p>

---

# SciTeX — Modular Python Toolkit for Researchers and AI Agents

The SciTeX system follows the Four Freedoms for Research below, inspired by [the Free Software Definition](https://www.gnu.org/philosophy/free-sw.en.html):

>Four Freedoms for Research
>
>0. The freedom to **run** your research anywhere — your machine, your terms.
>1. The freedom to **study** how every step works — from raw data to final manuscript.
>2. The freedom to **redistribute** your workflows, not just your papers.
>3. The freedom to **modify** any module and share improvements with the community.
>
>AGPL-3.0 — because we believe research infrastructure deserves the same freedoms as the software it runs on.

<p align="center">
    <img src="scripts/assets/workflow_out/workflow.png" alt="SciTeX Ecosystem" width="800">
</p>

## 🎬 Demo

**40 min, zero human intervention** — AI agent conducts full research pipeline:

> Literature search → Data analysis → Statistics → Figures → 21-page manuscript → Peer review simulation

<p align="center">
  <a href="https://scitex.ai/demos/watch/scitex-automated-research/" title="▶ Watch full demo at scitex.ai/demos/">
    <img src="docs/assets/images/scitex-demo.gif" alt="SciTeX Demo" width="800">
  </a>
</p>

## 📦 Installation


``` bash
uv pip install scitex          # Core (minimal)
uv pip install scitex[plt,stats,scholar]  # Typical research setup
uv pip install scitex[all]     # Recommended: Full installation
```

## ⚙️ Configuration

Modular environment configuration via `.env.d/`:

<details>

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

→ **[Full configuration reference](./.env.d.examples/README.md)**

</details>

## Three Interfaces

<details>
<summary><strong>🐍 Python API for Humans and AI Agents</strong></summary>

<br>

**`@stx.session`** — Reproducible Experiment Tracking

```python
import scitex as stx

@stx.session
def main(filename="demo.jpg"):
    fig, ax = stx.plt.subplots()
    ax.plot_line(t, signal)
    ax.set_xyt("Time (s)", "Amplitude", "Title")
    stx.io.save(fig, filename)
    return 0
```

**Output**:
```
script_out/FINISHED_SUCCESS/2025-01-08_12-30-00_AbC1/
├── demo.jpg                    # Figure with embedded metadata
├── demo.csv                    # Auto-exported plot data
├── CONFIGS/CONFIG.yaml         # Reproducible parameters
└── logs/{stdout,stderr}.log    # Execution logs
```

**`stx.io`** — Universal File I/O (30+ formats)

```python
stx.io.save(df, "output.csv")
stx.io.save(fig, "output.jpg")
df = stx.io.load("output.csv")
```

**`stx.stats`** — Publication-Ready Statistics (23 tests)

```python
result = stx.stats.test_ttest_ind(group1, group2, return_as="dataframe")
# Includes: p-value, effect size, CI, normality check, power
```

→ **[Full module status](./docs/MODULE_STATUS.md)**

</details>

<details>
<summary><strong>🖥️ CLI Commands for Humans and AI Agents</strong></summary>

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

→ **[Full CLI reference](./docs/CLI_COMMANDS.md)**

</details>

<details>
<summary><strong>🔧 MCP Tools — 120+ tools for AI Agents</strong></summary>

<br>

Turn AI agents into autonomous scientific researchers.

**Typical workflow**: Scholar (find papers) → Stats (analyze) → Plt (visualize) → Writer (manuscript) → Capture (verify)

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

**Claude Code Setup** — add `.mcp.json` to your project root. Use `SCITEX_ENV_SRC` to load all configuration from a `.src` file — this keeps `.mcp.json` static across environments:

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

Switch environments via your shell profile:

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
scitex mcp install
```

→ **[Full MCP tool reference](./docs/MCP_TOOLS.md)**

</details>

## 🧩 Standalone Packages

SciTeX integrates several standalone packages that can be used independently:

<details>

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
pip install figrecipe        # Use independently
pip install scitex[plt]      # Or via scitex
```

</details>

## 📖 Documentation

- **[Read the Docs](https://scitex-python.readthedocs.io/)**: Complete API reference
- **[Examples](./examples/)**: Usage examples and demonstrations

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md).

---

<p align="center">
  <a href="https://scitex.ai" target="_blank"><img src="docs/assets/images/scitex-icon-navy-inverted.png" alt="SciTeX" width="40"/></a>
  <br>
  AGPL-3.0
</p>

<!-- EOF -->