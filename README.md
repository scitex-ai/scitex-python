<p align="center">
  <a href="https://scitex.ai"><img src="https://raw.githubusercontent.com/scitex-ai/.github/7dcc33cc93d44983710e5e3b19a73853766c2483/profile/assets/scitex-logo.png" alt="SciTeX" width="360"></a>
</p>

# SciTeX (`scitex`)

**A Python toolkit — AI for Science**

SciTeX connects specialized scientific packages through a shared Python namespace, command-line tools, and interfaces for AI agents. Use individual packages for a focused task, or combine them in a research workflow.

- **Deterministic research tools** for literature, data, analysis, figures, and writing.
- **Provenance-based verification** with [scitex-clew](https://github.com/scitex-ai/scitex-clew).
- **Flexible interfaces**: Python API, CLI, MCP, skills, and web API across the ecosystem.

[Documentation](https://scitex-python.readthedocs.io/) · [PyPI](https://pypi.org/project/scitex/) · [SciTeX Cloud](https://scitex.ai) · [Ecosystem](https://github.com/scitex-ai)

<p align="center"><a href="https://scitex-python.readthedocs.io/">Full Documentation</a> · <code>uv pip install scitex</code></p>

<!-- scitex-badges:start -->
<p align="center">
  <a href="https://pypi.org/project/scitex/"><img src="https://img.shields.io/pypi/v/scitex?label=pypi" alt="PyPI version"></a>
  <a href="https://pypi.org/project/scitex/"><img src="https://img.shields.io/pypi/pyversions/scitex?label=python" alt="Python versions"></a>
  <a href="https://scitex-python.readthedocs.io/"><img src="https://img.shields.io/readthedocs/scitex-python?label=docs" alt="Documentation build"></a>
</p>
<p align="center">
  <a href="https://github.com/scitex-ai/scitex-python/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/scitex-ai/scitex-python/ci.yml?label=tests&amp;branch=develop" alt="Tests"></a>
  <a href="https://codecov.io/gh/scitex-ai/scitex-python"><img src="https://img.shields.io/codecov/c/github/scitex-ai/scitex-python/develop?label=cov" alt="Coverage"></a>
</p>
<!-- scitex-badges:end -->

## Problem and Solution

| # | Problem | Solution |
|---|---|---|
| 1 | **Fragmentation** between literature, analysis, figures, and writing | **Shared entry points** backed by independent, specialized packages |
| 2 | **Traceability** gaps between reported results and their source data | **Recorded provenance** through scitex-clew and supported package integrations |
| 3 | **Interfaces** that differ across researchers and AI agents | **Access** through Python, CLI, MCP, skills, and Web APIs |

## Quick start

After [installation](#installation), create a figure from a synthetic signal and save it with its FigRecipe recipe:

```python
from pathlib import Path

import numpy as np
import scitex

x = np.linspace(0, 2 * np.pi, 200)
y = np.sin(x)

fig, ax = scitex.plt.subplots()
ax.plot(x, y)
ax.set_xyt("Time", "Amplitude", "Synthetic signal")

output = Path("outputs/signal.png").resolve()
scitex.io.save(fig, str(output))
```

Run the code in your project directory. It writes `outputs/signal.png` and the figure's recipe beside it. The absolute path makes the output location explicit.

| Task | Python entry point | Owning package |
|---|---|---|
| Scientific file I/O | `scitex.io` | [scitex-io](https://github.com/scitex-ai/scitex-io) |
| Statistics | `scitex.stats` | [scitex-stats](https://github.com/scitex-ai/scitex-stats) |
| Figures and recipes | `scitex.plt` | [figrecipe](https://github.com/scitex-ai/figrecipe) |
| Literature | `scitex.scholar` | [scitex-scholar](https://github.com/scitex-ai/scitex-scholar) |
| Manuscripts | `scitex.writer` | [scitex-writer](https://github.com/scitex-ai/scitex-writer) |
| Experiment sessions | `scitex.session` | [scitex-session](https://github.com/scitex-ai/scitex-session) |

<sub><b>Table 1.</b> Selected Python entry points and their owning packages.</sub>

The umbrella delegates implementation to the owning packages. Their documentation describes detailed APIs, dependencies, and configuration.

## Demo — SciTeX Cloud apps

SciTeX Hub provides the graphical workspace; specialized packages provide the apps. These screenshots show development builds with synthetic/demo content, not research findings.

<p>
  <a href="https://raw.githubusercontent.com/scitex-ai/.github/7dcc33cc93d44983710e5e3b19a73853766c2483/profile/assets/figrecipe-20261103-scene-768.webp"><img src="https://raw.githubusercontent.com/scitex-ai/.github/7dcc33cc93d44983710e5e3b19a73853766c2483/profile/assets/figrecipe-20261103-scene-768.webp" alt="FigRecipe development interface: multiple synthetic figures with a selected training line and its native Details pane" width="49%"></a>
  <a href="https://raw.githubusercontent.com/scitex-ai/.github/7dcc33cc93d44983710e5e3b19a73853766c2483/profile/assets/writer-20261102-768.webp"><img src="https://raw.githubusercontent.com/scitex-ai/.github/7dcc33cc93d44983710e5e3b19a73853766c2483/profile/assets/writer-20261102-768.webp" alt="Writer development interface: a LaTeX example Abstract beside its compiled section PDF preview" width="49%"></a>
</p>

<sub><b>Figure 1.</b> FigRecipe: editable figures and recipes.</sub> <sub><b>Figure 2.</b> Writer: manuscript editing and section previews.</sub> Captured November 2–3, 2026; [image sources and hashes](https://github.com/scitex-ai/.github/blob/7dcc33cc93d44983710e5e3b19a73853766c2483/profile/assets/ASSET-MANIFEST.md).

> **SciTeX Cloud is in alpha.** Features and data formats may change. Keep backups.

[Explore the apps](https://scitex.ai/landing/#overview) · [Watch the research demo and inspect its outputs](https://github.com/scitex-ai/automated-research-demo)

## Installation

Create a virtual environment and install the toolkit:

```bash
uv venv .venv
source .venv/bin/activate
uv pip install scitex
scitex --help
```

Use the equivalent activation command for your shell. Python requirements are declared on [PyPI](https://pypi.org/project/scitex/). Optional integrations may have additional runtime or platform requirements.

Choose extras for the work you need, for example:

```bash
uv pip install "scitex[scholar,writer]"
```

See the [installation guide](https://scitex-python.readthedocs.io/en/latest/installation.html) for package and environment setup.

## Architecture — Ecosystem

| Role | Package |
|---|---|
| Python umbrella and integration | **scitex** — shared namespace and user entry points |
| Development tools and dispatchers | [scitex-dev](https://github.com/scitex-ai/scitex-dev) — discovery, shared checks, hooks, and skills |
| Standalone apps and Hub plugins | [scitex-sdk](https://github.com/scitex-ai/scitex-sdk) — shared web/app primitives |
| Browser workspace and Web API hosting | [scitex-hub](https://github.com/scitex-ai/scitex-hub) |
| Domain logic and providers | Specialized leaf packages, each with its own APIs, documentation, and license |

<sub><b>Table 2.</b> Responsibilities across the ecosystem.</sub>

Leaves own their expertise; shared dispatchers discover and integrate their declared interfaces. [Browse the ecosystem](https://github.com/orgs/scitex-ai/repositories).

## Five Interfaces

| Interface | Entry point |
|---|---|
| **Python API** | `import scitex` |
| **CLI** | `scitex --help`, then the selected command's `--help` |
| **MCP tools** | `scitex mcp --help`; package tools are discovered from the installed environment |
| **Skills** | [Packaged guidance](src/scitex/_skills/scitex/SKILL.md) and each leaf package's skills |
| **Web API** | [Hub and app endpoints](https://scitex.ai/docs/web-api/), served through scitex-hub and its plugins |

<sub><b>Table 3.</b> The five ecosystem interfaces; availability depends on the installed packages.</sub>

Available interfaces depend on installed packages, their versions, and configuration. Use documentation that matches your installed release.

<details>
<summary>Connect an MCP client</summary>

For clients using an `mcpServers` configuration:

```json
{
  "mcpServers": {
    "scitex": {
      "command": "/absolute/path/to/.venv/bin/scitex",
      "args": ["mcp", "start", "--transport", "stdio"]
    }
  }
}
```

Set `command` to the executable in your SciTeX environment. Inspect only the tool groups relevant to your task, for example:

```bash
scitex mcp list-tools --module stats
```

Provider credentials and external services are configured by the packages that use them.

</details>

<details>
<summary>Release compatibility</summary>

In `scitex` 2.30.8, the skills CLI imports `scitex_dev.skills`, but its pinned `scitex-dev` 0.28.0 does not provide that module. Read the package-owned skill files directly for that release. The compatibility and interface updates are tracked in [#387](https://github.com/scitex-ai/scitex-python/pull/387).

</details>

## Provenance

**Record Forward. Verify Backward.**

[scitex-clew](https://github.com/scitex-ai/scitex-clew) records source data and inputs–executable–outputs relationships. Verification follows recorded dependencies back toward source data. Consult the owning package's integration and session guidance to enable the tracking appropriate to your workflow.

## Documentation and contributing

- [API reference](https://scitex-python.readthedocs.io/en/latest/api/index.html)
- [Questions and ideas](https://github.com/scitex-ai/scitex-python/discussions)
- [Bugs and feature requests](https://github.com/scitex-ai/scitex-python/issues)
- [Contributing guide](CONTRIBUTING.md) and [Contributor License Agreement](CLA.md)

## License

This package is licensed under [AGPL-3.0](LICENSE), with commercial licensing described in the [CLA](CLA.md). Check each leaf package's license for its terms.

## Part of SciTeX

`scitex` is part of [SciTeX](https://scitex.ai), providing the Python umbrella and integration entry points.

>Four Freedoms for Research
>
>0. The freedom to **run** your research anywhere — your machine, your terms.
>1. The freedom to **study** how every step works — from raw data to final manuscript.
>2. The freedom to **redistribute** your workflows, not just your papers.
>3. The freedom to **modify** any module and share improvements with the community.
>
>AGPL-3.0 — because we believe research infrastructure deserves the same freedoms as the software it runs on.

<p align="center">
  <a href="https://scitex.ai"><img src="https://raw.githubusercontent.com/scitex-ai/.github/7dcc33cc93d44983710e5e3b19a73853766c2483/profile/assets/scitex-icon.png" alt="SciTeX" width="40"></a>
</p>
