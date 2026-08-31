<!-- ---
!-- Timestamp: 2026-03-23 01:22:48
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-python/README.md
!-- --- -->

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
  <a href="https://codecov.io/gh/ywatanabe1989/scitex-python"><img src="https://img.shields.io/codecov/c/github/ywatanabe1989/scitex-python/develop?label=cov" alt="cov"></a>
  <a href="https://github.com/ywatanabe1989/scitex-python/blob/main/LICENSE"><img src="https://img.shields.io/github/license/ywatanabe1989/scitex-python" alt="License"></a>
</p>

<p align="center">
  <a href="https://scitex-python.readthedocs.io">Docs</a> &middot;
  <a href="https://scitex-python.readthedocs.io/en/latest/quickstart.html">Quick Start</a> &middot;
  <a href="https://scitex-python.readthedocs.io/en/latest/api/index.html">API</a> &middot;
  <code>pip install scitex[all]</code>
</p>

---

This repository provides `scitex`, the orchestration layer of the SciTeX ecosystem — solving key problems in scientific research:

## Problem and Solution

| # | Problem | Solution |
|---|---------|----------|
| 1 | **Fragmented tools** -- literature search, statistics, figures, and writing each require separate tools with incompatible formats | **Unified toolkit** -- `import scitex as stx` provides 73 modules under one namespace, accessible via Python API, CLI, and MCP. These modules are standalone packages but loosely coupled through a plugin registry — each works on its own, yet composes into designed synergy (save a figure → auto-exports CSV + YAML recipe → hash-tracked by Clew → citeable in scitex-writer). |
| 2 | **No verification** -- existing tools address whether work *could* be reproduced, not whether it *has* been verified | **Cryptographic verification** -- Clew builds SHA-256 hash-chain DAGs linking every manuscript claim back to source data |
| 3 | **AI agents lack context** -- general-purpose LLMs cannot operate across the full research lifecycle without domain-specific tools | **323 MCP tools** -- AI agents run statistics, create figures, search literature, and compile manuscripts through structured tool calls |
| 4 | **No custom tooling** -- every lab needs domain-specific tools, but building and sharing them requires deep infrastructure knowledge | **App Maker and Store** -- researchers create custom apps with [scitex-app](https://github.com/ywatanabe1989/scitex-app) SDK and share via [SciTeX Cloud](https://scitex.ai) |
| 5 | **Vendor lock-in** -- cloud research tools (Overleaf, Zotero, Mendeley, Colab, GitHub Copilot) keep data on third-party servers and depend on APIs that can disappear overnight or monetize tomorrow | **Open and self-hostable** -- every SciTeX package is AGPL-3.0; the full 39-package ecosystem runs on your own hardware (or SciTeX Cloud which itself is self-hostable); cloud integrations are pluggable extras, not requirements |

## SciTeX and Research Workflow

<p align="center">
    <img src="scripts/assets/workflow_out/workflow.png" alt="SciTeX Research Workflow" width="600">
</p>
<p align="center"><sub><b>Figure 1.</b> SciTeX research pipeline -- from literature search to manuscript compilation, with every step cryptographically linked.</sub></p>

## Demo — Automated Research from Data to Manuscript

**40 min, minimal human intervention** — an AI agent using SciTeX completed a full research cycle: literature search, statistical analysis, publication-ready figures, a 21-page manuscript, and peer review simulation. More demos are available at [https://scitex.ai/demos/](https://scitex.ai/demos/).

<p align="center">
  <a href="https://scitex.ai/demos/watch/scitex-automated-research/">
    <img src="docs/assets/images/scitex-demo.gif" alt="SciTeX Demo" width="800">
  </a>
</p>

## Installation

```bash
# Recommended — uv resolver, ~3 min (10–30× faster than pip on scitex[all])
uv pip install "scitex[all]"

# Plain pip works but expect ~30–90 min — pip's resolver backtracks
# heavily on the full extras set. See Installation Tips below.
pip install "scitex[all]"
```

> **Why uv?** `scitex[all]` pulls a large transitive set
> (numpy/pandas/torch/jax/playwright/openalex-local/sphinx-rtd-theme/…).
> pip's serial resolver walks version histories trying to satisfy
> every constraint and can spend 30+ min just downloading metadata
> before installing a single wheel. uv resolves the same set in
> parallel in 1–3 min. Install uv once with
> `pip install uv` (or `curl -LsSf https://astral.sh/uv/install.sh | sh`).

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

Requires Python 3.10+. Prefix any of the above with `uv ` (e.g. `uv pip install scitex[plt,stats,scholar]`) for a 10–30× faster resolve.
</details>

<details>
<summary><strong>Installation Tips — timeouts, mirrors, <code>[all]</code> size</strong></summary>

`scitex[all]` pulls the full 33-package ecosystem plus heavy extras (playwright browsers, torch, jax, pymupdf, Apptainer/Docker integrations, etc.). With **plain pip** this takes **30–90 minutes** because pip's resolver thrashes on the transitive set; with **uv** it takes ~3 min. Recommended order of preference:

```bash
# 1. uv (recommended) — parallel Rust resolver, 10-30× faster
pip install uv && uv pip install "scitex[all]"

# 2. pip with extended timeouts (default 15s aborts mid-wheel on slow links)
pip install --timeout 600 --retries 5 "scitex[all]"

# 3. Install in groups if a single run keeps failing
uv pip install scitex[io,stats,plt]         # core analysis layer first
uv pip install scitex[scholar,writer]       # research layer
uv pip install scitex[audio,browser,dataset,cloud]   # heavy extras last

# 4. Mirror — for networks where pypi.org is unreliable
uv pip install -i https://pypi.tuna.tsinghua.edu.cn/simple "scitex[all]"
```

If a single dep hangs, identify it with `pip install -v` and install that package alone with `--no-deps`, then resume the full install.
</details>

<details>
<summary><strong>Module Overview</strong></summary>

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

</details>

## Architecture — Packages (3-Layer Cascade)

The 33-package ecosystem follows a strict **dependency cascade**: upstream imports middle imports downstream, never the reverse. Downstream apps must work standalone; the umbrella only orchestrates.

```
Upstream (orchestration — SOC, integration tests only)
    scitex (scitex-python), scitex-cloud
        │ imports / re-exposes
        ▼
Middle (shared infrastructure — wraps, doesn't replace)
    scitex-io, scitex-stats, scitex-app, scitex-ui, scitex-audio, scitex-dev
        │ integrates / wraps via plugin registry
        ▼
Downstream (standalone apps — own IO/GUI, unit tests)
    figrecipe, scitex-writer, scitex-scholar, scitex-clew, scitex-notebook,
    scitex-dataset, scitex-ssh, scitex-container, scitex-browser, scitex-linter,
    openalex-local, crossref-local, socialia, + utility leaves
    (scitex-{path,str,dict,logging,types,db,repro,audit,parallel,compat,gists,etc,core})
```

**One-line contract**: downstream does not know upstream exists; upstream does not duplicate downstream logic. See [01_ecosystem_01_upstream-and-downstream.md](https://github.com/ywatanabe1989/scitex-dev/blob/main/src/scitex_dev/_skills/general/01_ecosystem_01_upstream-and-downstream.md) for full rules (testing, cascade, interfaces) and [01_ecosystem_02_dependency-and-version-pinning.md](https://github.com/ywatanabe1989/scitex-dev/blob/main/src/scitex_dev/_skills/general/01_ecosystem_02_dependency-and-version-pinning.md) for dep-pinning.

## Three Interfaces

Every capability in the SciTeX umbrella is reachable through three surfaces, so humans and AI agents share one toolkit:

| Interface | Entry point | Example |
|-----------|-------------|---------|
| **Python API** | `import scitex as stx` | `stx.io.save(fig, "result.png")` |
| **CLI** | `scitex <group> <command>` | `scitex io convert data.csv data.parquet` |
| **MCP** | `scitex mcp start` | 323 tools an AI agent calls directly |

The Python API is the primary surface; the CLI and MCP server expose the same logic for shells and AI agents. See the [Quick Start](#quick-start) below for runnable Python examples and the [Full MCP reference](./docs/02_MCP_TOOLS.md).

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

Use `CONFIG.SDIR_RUN / "results.csv"` to re-load a file saved earlier in the same session. A frozen copy of `CONFIG` is persisted to `CONFIG.SDIR_RUN/CONFIGS/{CONFIG.yaml,CONFIG.pkl}` so any run is fully auditable. See the [Session config docs](https://scitex-python.readthedocs.io/en/latest/api/session.html) for the full reference.
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
stx.stats.annotate(ax, test=result, style="apa")   # stars + "t(58) = 2.34, p = .021, d = 0.60" on a matplotlib Axes
```
</details>

<details>
<summary><strong><code>scitex.scholar</code> -- Literature Management</strong></summary>

Search, download, enrich papers. Backed by local CrossRef (167M+) and OpenAlex (250M+) databases.

```python
import scitex as stx
scholar = stx.scholar.Scholar()                             # lazy-load library
papers = scholar.process_papers(["neural oscillations working memory"])
scholar.download_pdfs_from_dois(["10.1038/s41586-024-07804-3"])
scholar.enrich_papers(bibtex_path="references.bib")
```

```bash
scitex scholar crossref-scitex search "neural oscillations" --abstracts
scitex scholar fetch --from-bibtex references.bib --project myproject
```
</details>

<details>
<summary><strong><code>scitex.writer</code> -- LaTeX Manuscript Compilation</strong></summary>

```python
import scitex as stx
stx.writer.compile.manuscript("paper/")                     # latexmk wrapper
stx.writer.figures.add("paper/", "results.png", caption="Main results")
stx.writer.tables.add("paper/", "stats.csv", caption="Statistical summary")
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
  <img src="docs/clew-dag.png" alt="Clew DAG" width="300">
</p>
<p align="center"><sub><b>Figure 2.</b> Clew verification DAG -- green nodes are verified (hash match), red nodes have mismatches. Each node shows its SHA-256 hash prefix.</sub></p>

</details>

<details>
<summary><strong><code>scitex.audio</code> -- Text-to-Speech (ElevenLabs / LuxTTS / gTTS / pyttsx3)</strong></summary>

```python
import scitex as stx
stx.audio.speak("Training complete. Accuracy ninety-four percent.")
stx.audio.speak("Offline only", backend="pyttsx3")                  # force offline
stx.audio.speak("Report", output_path="report.mp3", play=False)     # TTS → file
```
Backends fall back automatically: ElevenLabs (paid, highest) → LuxTTS (offline, 48 kHz, voice-cloning) → gTTS (free online) → pyttsx3 (offline espeak).
</details>

<details>
<summary><strong><code>scitex.dataset</code> -- OpenNeuro / DANDI / PhysioNet / Zenodo Fetcher</strong></summary>

```python
import scitex as stx
ds = stx.dataset.neuroscience.openneuro.fetch_all_datasets(max_datasets=10)
stx.dataset.neuroscience.dandi.fetch_all_datasets(max_datasets=10)
hits = stx.dataset.search_datasets(ds, text_query="phase-amplitude coupling")
```
Uniform API across neuroscience / biomedical / clinical-trial repositories.
</details>

<details>
<summary><strong><code>scitex.container</code> -- Apptainer / Docker Management</strong></summary>

```python
import scitex as stx
stx.container.apptainer.build(def_name="recipe")        # versioned SIF
stx.container.apptainer.switch_version("2.19.5")        # atomic active-SIF flip
stx.container.apptainer.rollback()                      # revert to previous
snap = stx.container.env_snapshot()                     # full env for papers
```
Reproducible HPC containers — build, version, rollback, env-snapshot for manuscripts.
</details>

<details>
<summary><strong><code>scitex.tunnel</code> -- Persistent SSH Reverse Tunnels</strong></summary>

```python
import scitex as stx
stx.tunnel.setup(port=8888, bastion_server="gw.example.com")
stx.tunnel.status()                                     # {"8888": "active"}
```
NAT traversal for lab machines — autossh-backed systemd service.
</details>

<details>
<summary><strong><code>scitex.linter</code> -- 47-Rule Convention Checker</strong></summary>

```python
import scitex as stx
issues = stx.linter.lint_file("src/")
for i in issues:
    print(f"{i.filepath}:{i.line} [{i.rule.id}] {i.message}")
```
Lints SciTeX projects for ecosystem conventions (`stx.io.save` usage, CONFIGS naming, matplotlib prefs, import hygiene). Complements ruff/flake8.
</details>

<details>
<summary><strong><code>scitex.repro</code> -- Seed Everything + Array Hashing</strong></summary>

```python
import scitex as stx
rng = stx.repro.RandomStateManager(seed=42)             # seeds random + numpy + torch + tf
run_id = stx.repro.gen_ID()                             # "20260423_2155_abc12345"
digest = stx.repro.hash_array(np_array)                 # deterministic SHA
```
One call seeds every RNG; generates experiment-run IDs; hashes arrays for fingerprinting.
</details>

<details>
<summary><strong><code>scitex.parallel</code> -- Threaded Map with tqdm</strong></summary>

```python
import scitex as stx
results = stx.parallel.run(download, [(u,) for u in urls], n_jobs=-1)
```
Drop-in parallel map for I/O-bound work — HTTP fetches, file reads, API calls. tqdm progress bar built-in.
</details>

<details>
<summary><strong><code>scitex.path</code> -- Project-Aware Paths &amp; Session Dirs</strong></summary>

```python
import scitex as stx
root = stx.path.find_git_root()                     # walk up for .git/
out = stx.path.get_spath("results.csv")             # → {script}_out/results.csv
stx.path.create_relative_symlink(src, dst)          # relative (portable) symlink
latest = stx.path.find_latest(".", "model_", ".pt") # model_v003.pt (highest version)
stx.path.fix_broken_symlinks("dir/", remove=True)   # cleanup dangling links
```
Auto-routes saves to `{script}_out/` and resolves session-scoped paths so `@stx.session` scripts produce dated, hash-trackable output dirs with no boilerplate.
</details>

<details>
<summary><strong><code>scitex.logging</code> -- Extended Logging + Exception Hierarchy + Tee</strong></summary>

```python
import scitex as stx
logger = stx.logging.getLogger(__name__)
logger.success("Training converged at epoch 87")    # SUCCESS level (custom)
logger.fail("Validation loss diverged")             # FAIL level (custom)

# Structured warnings with SciTeX categories
stx.logging.warn_deprecated("old_api", replacement="new_api", version="3.0")
stx.logging.warn_data_loss("NaN values dropped in column 'bp'")

# Typed exceptions (30+ subclasses of SciTeXError)
raise stx.logging.ShapeError("expected (N, 2), got (N, 3)")

# Tee stdout/stderr to a log file
with stx.logging.Tee("run.log"):
    main()                                           # prints go to screen + file
```
Extends stdlib `logging` with SUCCESS/FAIL levels, a 30+ class exception tree (`IOError`/`ShapeError`/`ConfigKeyError`/...), structured warning categories, and tee-to-file. `SCITEX_LOGGING_LEVEL` env var sets default at import.
</details>

<details>
<summary><strong><code>scitex.db</code> -- PostgreSQL with ndarray BLOB Storage</strong></summary>

```python
import scitex as stx, numpy as np

db = stx.db.PostgreSQL(dbname="experiments")
with db:                                             # context-manager transaction
    db.execute("CREATE TABLE IF NOT EXISTS runs (id TEXT, acc REAL)")
    db.save_array("weights_epoch_87", np.random.rand(1024, 1024))   # compressed BLOB

df = db.to_df("runs")                                # pandas round-trip
w = db.load_array("weights_epoch_87")                # typed ndarray back
db.check_health()                                    # integrity + schema drift
stx.db.delete_duplicates(conn, "runs", columns=["id"])
```
A PostgreSQL client with first-class compressed-ndarray BLOBs, dataframe round-trips, health checks, and duplicate removal. Drop-in replacement for hand-rolling `pickle → BLOB` storage or SQLAlchemy Core when you don't need an ORM.
</details>

<details>
<summary><strong><code>scitex.browser</code> -- Playwright Helpers for Scientific Scraping</strong></summary>

```python
import scitex as stx, asyncio

async def grab_pdf():
    async with stx.browser.SyncBrowserSession() as session:
        page = await session.new_page()
        await page.goto("https://journal.example/article/123")
        await stx.browser.click_with_fallbacks_async(
            page, ["button.download-pdf", "a[href$='.pdf']"]   # fall through selectors
        )
        await stx.browser.save_as_pdf_async(page, "article.pdf")

asyncio.run(grab_pdf())
```
Playwright wrappers with: Chrome-PDF-viewer download helper, popup/cookie dismissers (`close_popups_async`, `PopupHandler`), cursor/click/step overlays for debug video recording, console-log collectors, test-failure artifact capture. Drop-in replacement for raw Playwright scripts + stealth plugins.
</details>

<details>
<summary><strong>Utility modules — lower-level helpers</strong></summary>

| Module | Purpose | Key API |
|--------|---------|---------|
| `stx.str` | Text / LaTeX fallback / colored prints | `printc`, `safe_latex_render`, `grep` |
| `stx.dict` | `DotDict` + safe merge / flatten | `DotDict`, `safe_merge`, `flatten` |
| `stx.types` | Union type aliases + predicates | `ArrayLike`, `ColorLike`, `is_array_like` |
| `stx.audit` | Unified security scan (bandit / shellcheck / pip-audit) | `audit()` |
| `stx.compat` | Deprecation shims | `@deprecated`, `notify` legacy alias |
| `stx.etc` | Terminal keypress helpers | `wait_key`, `count` |

See [docs/05_ADDITIONAL_MODULES.md](./docs/05_ADDITIONAL_MODULES.md) for full examples.
</details>

> **[Agentic usage](./docs/06_AGENTIC_USAGE.md)** — MCP setup, example prompts, real one-shot outputs, and skill-trigger testing.

> **[Full API reference](https://scitex-python.readthedocs.io/en/latest/api/index.html)** &middot; **[Examples](./examples/)** &middot; **[Module status](./docs/04_MODULE_STATUS.md)**

<details>
<summary><strong>CLI Commands</strong></summary>

```bash
scitex --help-recursive                  # Show all commands
scitex scholar crossref-scitex search "topic"   # Search literature (CrossRef 167M+)
scitex scholar fetch "10.1038/..."       # Download paper by DOI
scitex stats recommend                   # Suggest statistical tests
scitex clew status                       # Project verification overview
scitex clew dag --claims                 # Verify all manuscript claims
scitex audio speak "Analysis complete"   # Text-to-speech
scitex notification send "Job finished"  # Multi-backend notification
scitex template clone research my_proj   # Scaffold a project
scitex dev ecosystem list                # Check ecosystem versions
scitex mcp list-tools                    # List all MCP tools (323)
```

> **[Full CLI reference](./docs/01_CLI_COMMANDS.md)**
</details>

<details>
<summary><strong>MCP Server (323 tools across 23 modules)</strong></summary>

Turn AI agents into autonomous researchers via [MCP](https://modelcontextprotocol.io/).

| Category | Tools | | Category | Tools | | Category | Tools |
|----------|-------|-|----------|-------|-|----------|-------|
| plt | 73 | | crossref | 15 | | io | 5 |
| cloud | 50 | | dev | 13 | | template | 4 |
| writer | 38 | | introspect | 12 | | openalex | 4 |
| scholar | 22 | | stats | 10 | | linter | 3 |
| clew | 9 | | dataset | 8 | | social | 3 |
| project | 6 | | notify | 5 | | tunnel | 3 |
| docs | 4 | | ui | 2 | | usage | 2 |

```json
{"mcpServers": {"scitex": {"command": "scitex", "args": ["mcp", "start"],
  "env": {"SCITEX_ENV_SRC": "${SCITEX_ENV_SRC}"}}}}
```

> **[Full MCP reference](./docs/02_MCP_TOOLS.md)**
</details>

## Configuration

```bash
cp -r .env.d.examples .env.d   # 1. Copy examples
$EDITOR .env.d/                # 2. Edit credentials
source .env.d/entry.src        # 3. Source in shell
```

> **[Full configuration reference](./.env.d.examples/README.md)**


## SciTeX Ecosystem

[`scitex-cloud`](https://github.com/ywatanabe1989/scitex-cloud) is a self-hosted web application that serves as a collaborative research workspace — with a built-in Writer, Scholar, and App Store where researchers build custom tools using [`scitex-app`](https://github.com/ywatanabe1989/scitex-app) SDK and [`scitex-ui`](https://github.com/ywatanabe1989/scitex-ui) components, then share them with the community. A live instance is hosted at [scitex.ai](https://scitex.ai).

<!-- hook-bypass: line-limit -->
<details>
<summary><strong>Full Ecosystem (37 packages, grouped by primary interface)</strong></summary>

Each package exposes the ecosystem via up to six interfaces: Python library, CLI, MCP tools, Claude Code skills, hooks, and HTTP. Ratings: ⭐⭐⭐ = primary / canonical surface, ⭐⭐ = strong secondary, ⭐ = thin, — = not provided. Packages are grouped by their *primary* interface — the one users should reach for first.

### Python-first (library API is primary)

| Package | Module | Interfaces | Description |
|---------|--------|-----------|-------------|
| [crossref-local](https://github.com/ywatanabe1989/crossref-local) | `stx.scholar` | Py ⭐⭐⭐ · CLI ⭐⭐ · MCP ⭐⭐ · Skills ⭐⭐ · Hook — · HTTP — | Offline, zero-API-key DOI lookup + full-text search over the CrossRef corpus |
| [openalex-local](https://github.com/ywatanabe1989/openalex-local) | `stx.scholar` | Py ⭐⭐⭐ · CLI ⭐⭐ · MCP ⭐⭐ · Skills ⭐⭐ · Hook — · HTTP — | Offline, zero-API-key search over the full OpenAlex academic corpus |
| [scitex-browser](https://github.com/ywatanabe1989/scitex-browser) | `stx.browser` | Py ⭐⭐⭐ · CLI — · MCP — · Skills ⭐⭐ · Hook — · HTTP — | Playwright wrappers for scientific web scraping + AI-agent browsing |
| [scitex-compat](https://github.com/ywatanabe1989/scitex-compat) | `stx.compat` | Py ⭐⭐⭐ · CLI — · MCP — · Skills ⭐ · Hook — · HTTP — | Backward-compatibility shims for deprecated SciTeX APIs |
| [scitex-core](https://github.com/ywatanabe1989/scitex-core) | `stx.core` | Py ⭐⭐⭐ · CLI — · MCP — · Skills ⭐⭐ · Hook — · HTTP — | Foundation layer for the SciTeX ecosystem |
| [scitex-dataset](https://github.com/ywatanabe1989/scitex-dataset) | `stx.dataset` | Py ⭐⭐⭐ · CLI ⭐ · MCP ⭐⭐ · Skills ⭐⭐ · Hook — · HTTP — | Unified dataset-discovery API across 7 scientific repositories |
| [scitex-db](https://github.com/ywatanabe1989/scitex-db) | `stx.db` | Py ⭐⭐⭐ · CLI ⭐ · MCP — · Skills ⭐⭐ · Hook — · HTTP — | Relational-DB wrapper for scientific Python |
| [scitex-dict](https://github.com/ywatanabe1989/scitex-dict) | `stx.dict` | Py ⭐⭐⭐ · CLI — · MCP — · Skills ⭐ · Hook — · HTTP — | Dictionary utilities for scientific Python |
| [scitex-etc](https://github.com/ywatanabe1989/scitex-etc) | `stx.etc` | Py ⭐⭐⭐ · CLI — · MCP — · Skills ⭐ · Hook — · HTTP — | Miscellaneous SciTeX utilities |
| [scitex-gists](https://github.com/ywatanabe1989/scitex-gists) | `stx.gists` | Py ⭐⭐⭐ · CLI — · MCP — · Skills ⭐ · Hook — · HTTP — | SigmaPlot v12 macro snippets as printable Python functions |
| [scitex-logging](https://github.com/ywatanabe1989/scitex-logging) | `stx.logging` | Py ⭐⭐⭐ · CLI — · MCP — · Skills ⭐⭐ · Hook — · HTTP — | Enhanced Python logging + warnings + exceptions for SciTeX |
| [scitex-parallel](https://github.com/ywatanabe1989/scitex-parallel) | `stx.parallel` | Py ⭐⭐⭐ · CLI — · MCP — · Skills ⭐ · Hook — · HTTP — | Minimal thread-pool parallel execution for scientific Python |
| [scitex-path](https://github.com/ywatanabe1989/scitex-path) | `stx.path` | Py ⭐⭐⭐ · CLI — · MCP — · Skills ⭐⭐ · Hook — · HTTP — | Project-aware path utilities for scientific Python |
| [scitex-plt](https://github.com/ywatanabe1989/scitex-plt) | `stx.plt` | Py ⭐⭐⭐ · CLI — · MCP ⭐⭐⭐ · Skills ⭐⭐ · Hook — · HTTP — | Publication-ready plotting (thin wrapper around figrecipe) |
| [scitex-repro](https://github.com/ywatanabe1989/scitex-repro) | `stx.repro` | Py ⭐⭐⭐ · CLI — · MCP — · Skills ⭐⭐ · Hook — · HTTP — | Reproducibility helpers for scientific Python experiments |
| [scitex-stats](https://github.com/ywatanabe1989/scitex-stats) | `stx.stats` | Py ⭐⭐⭐ · CLI ⭐ · MCP ⭐⭐ · Skills ⭐⭐ · Hook — · HTTP — | Publication-ready statistical testing for 23 tests |
| [scitex-str](https://github.com/ywatanabe1989/scitex-str) | `stx.str` | Py ⭐⭐⭐ · CLI — · MCP — · Skills ⭐⭐ · Hook — · HTTP — | Text-processing utilities for scientific Python |
| [scitex-types](https://github.com/ywatanabe1989/scitex-types) | `stx.types` | Py ⭐⭐⭐ · CLI — · MCP — · Skills ⭐ · Hook — · HTTP — | Type aliases and runtime type guards for scientific Python |

### CLI-first

| Package | Module | Interfaces | Description |
|---------|--------|-----------|-------------|
| [scitex-agent-container](https://github.com/ywatanabe1989/scitex-agent-container) | `stx.agent_container` | Py ⭐⭐ · CLI ⭐⭐⭐ · MCP — · Skills ⭐⭐ · Hook — · HTTP — | Declarative YAML-based AI agent lifecycle management (tmux/screen/SSH) |
| [scitex-app](https://github.com/ywatanabe1989/scitex-app) | `stx.app` | Py ⭐⭐ · CLI ⭐⭐⭐ · MCP ⭐⭐ · Skills ⭐⭐ · Hook — · HTTP — | App-developer SDK for SciTeX workspace apps |
| [scitex-audit](https://github.com/ywatanabe1989/scitex-audit) | `stx.audit` | Py ⭐ · CLI ⭐⭐⭐ · MCP ⭐ · Skills ⭐ · Hook — · HTTP — | Unified repo security scanner for scientific Python projects |
| [scitex-clew](https://github.com/ywatanabe1989/scitex-clew) | `stx.clew` | Py ⭐⭐ · CLI ⭐⭐⭐ · MCP ⭐⭐ · Skills ⭐⭐ · Hook — · HTTP — | Hash-based reproducibility verification for scientific pipelines |
| [scitex-container](https://github.com/ywatanabe1989/scitex-container) | `stx.container` | Py ⭐⭐ · CLI ⭐⭐⭐ · MCP ⭐⭐ · Skills ⭐⭐ · Hook — · HTTP — | Unified container management for Apptainer/Singularity + Docker |
| [scitex-dev](https://github.com/ywatanabe1989/scitex-dev) | `stx.dev` | Py ⭐⭐ · CLI ⭐⭐⭐ · MCP ⭐⭐ · Skills ⭐⭐ · Hook — · HTTP — | Developer utilities for maintaining the whole SciTeX ecosystem |
| [scitex-notebook](https://github.com/ywatanabe1989/scitex-notebook) | `stx.notebook` | Py ⭐⭐ · CLI ⭐⭐⭐ · MCP ⭐ · Skills ⭐⭐ · Hook — · HTTP — | Jupyter notebook reproducibility — verify, compile to DAG, convert to script |
| [scitex-ssh](https://github.com/ywatanabe1989/scitex-ssh) | `stx.tunnel` | Py ⭐ · CLI ⭐⭐⭐ · MCP ⭐⭐ · Skills ⭐⭐ · Hook — · HTTP — | SSH primitives (exec/copy/attach) plus gated, auto-reconnecting reverse tunnels for NAT traversal |

### MCP-first

| Package | Module | Interfaces | Description |
|---------|--------|-----------|-------------|
| [scitex-audio](https://github.com/ywatanabe1989/scitex-audio) | `stx.audio` | Py ⭐⭐ · CLI ⭐ · MCP ⭐⭐⭐ · Skills ⭐⭐ · Hook — · HTTP — | Unified text-to-speech with automatic backend fallback |
| [socialia](https://github.com/ywatanabe1989/socialia) | `stx.social` | Py ⭐ · CLI ⭐ · MCP ⭐⭐⭐ · Skills ⭐⭐ · Hook — · HTTP — | Unified posting + analytics client for 6 social platforms |

### Hook-first

| Package | Module | Interfaces | Description |
|---------|--------|-----------|-------------|
| [scitex-linter](https://github.com/ywatanabe1989/scitex-linter) | `stx.linter` | Py ⭐ · CLI ⭐⭐ · MCP ⭐ · Skills ⭐⭐ · Hook ⭐⭐⭐ · HTTP — | AST-based linter for reproducible-research Python (pre-commit hook) |

### Mixed (multiple equally-primary interfaces)

| Package | Module | Interfaces | Description |
|---------|--------|-----------|-------------|
| [figrecipe](https://github.com/ywatanabe1989/figrecipe) | `stx.plt` | Py ⭐⭐⭐ · CLI ⭐ · MCP ⭐⭐⭐ · Skills ⭐⭐ · Hook — · HTTP — | Publication-ready matplotlib figures with mm-precision layouts |
| [scitex-cloud](https://github.com/ywatanabe1989/scitex-cloud) | `stx.cloud` | Py ⭐ · CLI ⭐⭐⭐ · MCP ⭐⭐⭐ · Skills ⭐⭐ · Hook — · HTTP ⭐⭐ | SciTeX Cloud operational surface (55 MCP tools) |
| [scitex-io](https://github.com/ywatanabe1989/scitex-io) | `stx.io` | Py ⭐⭐⭐ · CLI ⭐ · MCP ⭐⭐ · Skills ⭐⭐⭐ · Hook — · HTTP — | Universal one-call file I/O for 30+ scientific formats |
| [scitex-notification](https://github.com/ywatanabe1989/scitex-notification) | `stx.notification` | Py ⭐⭐ · CLI ⭐ · MCP ⭐⭐⭐ · Skills ⭐⭐ · Hook — · HTTP — | One-call alerting across 9 backends (audio/desktop/email/Telegram/...) |
| [scitex-orochi](https://github.com/ywatanabe1989/scitex-orochi) | `stx.orochi` | Py ⭐⭐ · CLI ⭐⭐ · MCP ⭐⭐ · Skills ⭐⭐ · Hook — · HTTP ⭐⭐ | Agent Communication Hub — real-time WebSocket messaging between agents |
| [scitex-scholar](https://github.com/ywatanabe1989/scitex-scholar) | `stx.scholar` | Py ⭐⭐⭐ · CLI ⭐⭐⭐ · MCP ⭐⭐ · Skills ⭐⭐ · Hook — · HTTP — | End-to-end scientific-literature toolkit |
| [scitex-ui](https://github.com/ywatanabe1989/scitex-ui) | `stx.ui` | Py ⭐⭐ · CLI ⭐ · MCP ⭐⭐ · Skills ⭐⭐ · Hook — · HTTP ⭐⭐ | Shared frontend framework for SciTeX web apps |
| [scitex-writer](https://github.com/ywatanabe1989/scitex-writer) | `stx.writer` | Py ⭐ · CLI ⭐⭐⭐ · MCP ⭐⭐⭐ · Skills ⭐⭐ · Hook — · HTTP — | End-to-end LaTeX manuscript toolchain (45 MCP tools) |
</details>

## Part of SciTeX

`scitex` is part of [SciTeX](https://scitex.ai) — it is the umbrella distribution that aggregates the whole ecosystem under one `import scitex` namespace. Each peer module (`scitex.io`, `scitex.plt`, `scitex.stats`, …) is a standalone package installable on its own (`pip install scitex[io]`) yet composes into designed synergy: save a figure → auto-export CSV + YAML recipe → hash-track via Clew → cite in scitex-writer.

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