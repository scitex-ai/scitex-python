# Changelog

All notable changes to SciTeX will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **scitex.media re-export rerouted to `figrecipe.media`** (Phase B of the
  scitex-gen full retirement wave; operator-confirmed). This reneges
  ADR-0001, which had scheduled media for scitex-etc. Operator's view: media
  belongs with figure rendering, not with the etc catch-all. `scitex-etc`
  retains only `count_grids` / `yield_grids` / `search`.
  - `figrecipe>=0.29.0` is required (was `==0.28.20`); bumped at all three
    pin sites (top-level core deps, the `[plt]` extra group, the `[dev]`
    group).
  - `scitex-etc==0.2.0` is kept; the package shipped media in `0.2.0` but
    the scitex-etc develop branch will retarget 0.2.0 to drop media + wait_key
    (moving to figrecipe and scitex-parallel respectively).
  - `_DEFAULT_BRANDED` and the lazy-module loader both now point `media` at
    `figrecipe.media`.

## [2.30.0] - 2026-05-31

### Changed
- **Umbrella decomposition campaign**: `scitex.<x>` modules are now thin branded aliases to their owning standalone packages instead of in-tree shim directories. Dropped the in-tree shim dirs for `errors` (→ `scitex_logging`), `torch` (→ `scitex_linalg`), `stats` (→ `scitex_stats`), `diagram` (→ `figrecipe.diagram`), `clew` (→ `scitex_clew`), `tunnel` (→ `scitex_ssh`), `rng`/`verify`. `scitex.utils` is now a thin re-export aggregator that distributes implementations to their owning packages. Env-loading delegates to `scitex-config`.
- **Linter**: `scitex.linter` (and the more-consistent `scitex.dev.linter`) now resolve to the real engine `scitex_dev.linter`. Two stale registrations that kept routing to the archived `scitex_linter` distribution were removed (#306).

### Removed
- **`scitex-core` dependency**: dropped from `pyproject.toml`; all former `scitex-core` contents are standalonized. Enables public-archiving of `scitex-core`. (#299)
- **`scitex.utils.verify_scitex_format`**: removed; superseded by the `scitex-dev` linter. (#300)
- Dropped 10 redundant legacy MCP bridge files now covered by registry auto-mount.

### Fixed
- **CI test matrix**: greened the chronic-red umbrella matrix — switched to `uv` resolver, CPU-only torch, dropped coverage-triggered segfaults, and added a retry-on-incomplete-report guard for the non-deterministic C-extension shutdown segfault. (#303, #304, #305)
- Bumped sibling pins for PS-170 freshness (`scitex-dev` 0.15.0, et al.).

## [2.29.3] - 2026-05-23

### Fixed
- **Dependency pins**: Restore `>=` minima for sibling `scitex-*` deps (was exact `==`, which referenced unpublished versions like `scitex-config==0.3.3` and broke `pip install scitex` with ResolutionImpossible). Fixes #282. The 2.29.0 and 2.29.1 PyPI releases shipped the broken `==` pins; 2.29.3 is the corrected release.

## [2.28.13] - 2026-04-30

### Changed
- **Umbrella simplification (Tier 2 batch 6)**: Collapsed 8 leaf-duplicate dirs (`benchmark`, `context`, `cv`, `introspect`, `msword`, `os`, `security`, `tex`) into eager-mounted external pointers. Trimmed ~hundreds of LOC from `src/scitex/`.

### Fixed
- **Import-path regression**: Re-added 4 tiny shim dirs (`ml`, `reproduce`, `rng`, `verify`) so `import scitex.ml` etc. continue to work alongside the existing `scitex.<aliased>` proxy. Each shim emits a `DeprecationWarning` then re-exports from the canonical location (`scitex.ai`, `scitex.repro`, `scitex.clew`).

## [2.28.5 – 2.28.12] - 2026-04-30

### Changed
- **Umbrella simplification (Tier 1 + Tier 2 batches 1–5)**: Collapsed 21 pure re-export directories — `dt`, `etc`, `gists`, `audit`, `compat`, `repro`, `app`, `scholar`, `dict`, `notebook`, `str`, `logging`, `browser`, `parallel`, `path`, `db`, `audio`, `types`, `template`, plus 4 deprecated alias dirs — into eager-mounted external pointers in `src/scitex/__init__.py`. ~8,000 lines removed across 8 PyPI releases.
- **Pin tightening**: Tightened `>=` floors for ~30 standalone packages whose APIs are now load-bearing for the umbrella (one PyPI install pulls a known-compatible matrix).

## [2.28.0 – 2.28.4] - 2026-04-28

### Fixed
- **License classifier**: Drop legacy `License :: OSI Approved` trove classifier — PEP 639 + setuptools ≥80 reject it (E5C13).
- **DSP/gen edge cases**: `gen.to_even` handles 0-d numpy/torch arrays via `.item()`; `dsp.design_filter` coerces tensor `fs` to scalar before `int()`; Hilbert + signal_fn cascade preserves `float64` dtype.
- **Stats compatibility shim**: Register `scitex_stats._utils` at `scitex.stats._utils` sys.modules path so downstream `from scitex.stats._utils import X` keeps working post-extraction.

## [2.27.0 – 2.27.3] - 2026-03-25 — 2026-03-29

### Added
- **Module-level `_skills/`**: 302 sub-skill files across 70 modules, surfacing per-API guidance to MCP clients.
- **Skills CLI**: `scitex skills get all` dumps every sub-skill, not just `SKILL.md`.
- **Notebook**: Unified migration mode for Jupyter → SciTeX conversion.
- **Template**: `list-code-templates` CLI command.

### Changed
- **Skills layout**: Cleaned legacy `skills/` directory; module-level `_skills/<short>/` is now the source of truth (later moved to scitex-dev in 2.28.x).
- **CLI skills export**: Clean `--param` handling, frontmatter normalised.

## [2.26.0] - 2026-03-23

### Added
- **Browser**: `save-as-pdf` tool with cookie-banner dismissal; playwright-cli runtime detection.
- **Browser skills**: First-class `_skills/browser/` set.

### Fixed
- **FastMCP compatibility**: `mount(..., namespace=)` for FastMCP 3.x and `mount(..., prefix=)` for 2.x via `_compat.safe_mount`.

## [2.25.0 – 2.25.10] - 2026-03 (multiple patches)

### Added
- Lazy-loaded module skeletons for `introspect`, `sh`, `os`, `cv`, `ui`, `git`, `schema`, `canvas`, `security`, `benchmark`, `bridge`, `browser`, `compat`, `cli`.
- **`scitex-pkg audit`** CLI for venv drift detection + auto-fix.

### Fixed
- Numerous lazy-loader, optional-dep, and deprecation-warning fixes (see git log between v2.25.0 and v2.26.0 for the full punch list).

## [2.22.0 – 2.24.0] - 2026-03

### Added
- **First wave of standalone-package extractions** (#51, #206): `etc`, `compat`, `audit`, `parallel`, `types`, `gists`, `path`, `repro`, `db`, `scholar`, `dict`, `logging`, `browser`, `str` and others — umbrella now delegates to dedicated PyPI packages with try/except fallbacks for unpublished ones.
- **Notebook unified migration mode**, **template list-code-templates**, **scholar `clean_abstract` re-export**.

### Fixed
- Default `autolayout=False` in plt + session (#214); CLI warns when top-level `--json` is given with a subcommand (#211); session final-message differentiated by `exit_status` (#145); decorators lazy-import `joblib`; io lazy-imports `flask` (#441); LazyGroup tolerant of optional-dep leaks (#279).

## [2.21.0] - 2026-02-27

### Added
- **Media classify**: Add graphviz (.dot, .gv) and .mermaid extensions to media type detection
- **MCP handlers**: Project handler improvements

## [2.19.3] - 2026-02-24

### Added
- **`scitex.git.ls_remote()`**: Get remote ref commit hash via `git ls-remote`
- **`scitex.git.get_head_hash()`**: Get local repo HEAD commit hash
- **Smart template cache**: Validates cache by comparing local vs remote commit hashes; auto-invalidates stale cache

## [2.19.0] - 2026-02-22

### Added
- **`build_from_dois()`**: Build citation networks from multiple seed DOIs with batch scoring
- **`build_from_query()`**: Build citation networks from text queries via local DB search
- **Batch SQL optimization**: `get_combined_similarity_scores_batch()` — O(4) queries instead of O(4N)
- **HTTP parallel batch**: `ThreadPoolExecutor` parallelism for HTTP-mode batch scoring (up to 20 workers)
- **`is_seed` flag**: PaperNode now tracks whether it's a seed paper
- **`seed_dois` field**: CitationGraph stores all seed DOIs for multi-seed graphs

## [Unreleased]

### Changed
- **Module Refactoring**: Cleaned up root-level namespace, moved items to appropriate modules
  - `INJECTED` sentinel → `scitex.session.INJECTED` (backward-compatible with deprecation warning)
  - `show_install_guide()` → `scitex.dev.show_install_guide()` (backward-compatible with deprecation warning)
  - `Diagram` class → `scitex.diagram.Diagram` (backward-compatible with deprecation warning)
  - `ci()` (confidence interval) → `scitex.stats.descriptive.ci` (also available via `stx.gen.ci`)

### Added
- **New Lazy Modules**: Added missing modules to root namespace
  - `introspect`, `sh`, `os`, `cv`, `ui`, `git`, `schema`, `canvas`, `security`, `benchmark`, `bridge`, `browser`, `compat`, `cli`

### Migration Map

| Before (Deprecated)          | After (Recommended)              |
|------------------------------|----------------------------------|
| `stx.INJECTED`               | `stx.session.INJECTED`           |
| `stx.show_install_guide()`   | `stx.dev.show_install_guide()`   |
| `stx.Diagram`                | `stx.diagram.Diagram`            |
| `stx.gen.ci()`               | `stx.stats.descriptive.ci()`     |
| `stx.gen.inspect_module()`   | `stx.introspect.inspect_module()`|
| `stx.gen.check_host()`       | `stx.os.check_host()`            |
| `stx.gen.is_host()`          | `stx.os.is_host()`               |
| `stx.gen.verify_host()`      | `stx.os.verify_host()`           |
| `stx.gen.detect_environment()`| `stx.context.detect_environment()`|
| `stx.gen.is_notebook()`      | `stx.context.is_notebook()`      |
| `stx.gen.is_script()`        | `stx.context.is_script()`        |
| `stx.gen.get_notebook_path()`| `stx.context.get_notebook_path()`|
| `stx.gen.run_shellcommand()` | `stx.sh.run_shellcommand()`      |
| `stx.gen.run_shellscript()`  | `stx.sh.run_shellscript()`       |
| `stx.gen.title_case()`       | `stx.str.title_case()`           |

## [2.14.0] - 2026-01-15

### Added
- **Unified MCP Server**: Single FastMCP server with 106 tools across 10 modules
  - `scitex mcp list`: List all tools with column-aligned output
  - `scitex mcp doctor`: Check server health and configuration
  - `scitex mcp serve`: Start server (stdio/sse/http transports)
  - `scitex mcp help-recursive`: Show help for all MCP commands
- **Scholar Module**: Expanded from 5 to 23 MCP tools
  - Added: enrich_bibtex, download_pdf, download_pdfs_batch, parse_bibtex
  - Added: validate_pdfs, resolve_openurls, authenticate, check_auth_status
  - Added: logout, export_papers, add_papers_to_project, parse_pdf_content
  - Added job handlers: fetch_papers, list_jobs, get_job_status, start_job, cancel_job, get_job_result
- **MCP CLI Tests**: 10 new tests for mcp CLI commands

### Changed
- **MCP Architecture**: Consolidated into `_mcp_tools/` subpackage
- **Test Naming**: Renamed MCP tests to module-prefixed convention (e.g., `test_audio_handlers.py`)

### Removed
- Legacy module-specific MCP files (consolidated into unified server)

### Fixed
- Release workflow: Simplified version check (pyproject.toml only)
- Gitignore: Added `script_out/`, `.monitor_repository.sh.log`

## [2.13.0] - 2026-01-08

### Changed
- **Renamed `rng_manager` → `rng`**: Shorter, NumPy-aligned naming convention
  - `stx.session.start()` now returns `rng` instead of `rng_manager`
  - All examples, docs, and tests updated to use new naming
- **MCP Servers**: Added graceful dependency handling with `MCP_AVAILABLE` flag
  - Servers now provide helpful installation instructions when `mcp` package missing

### Added
- **GitHub Actions**: Install time benchmark workflow with GitHub Pages deployment
  - Dynamic shields.io badges for all modules at `badges/<module>.json`
  - Weekly scheduled benchmarks and release-triggered runs
- **README**: Per-module install time badges in all module tables

### Fixed
- **README**: Removed stray `</details>` tag, fixed `stx.io.load` example

## [2.12.0] - 2026-01-08

### Added
- **MCP Servers**: Integrated MCP (Model Context Protocol) servers for LLM integration
  - `scholar`: Literature management with BibTeX operations, DOI resolution (11 tools)
  - `stats`: Statistical testing with auto-recommendation, power analysis (10 tools)
  - `template`: Project scaffolding from templates (4 tools)
  - `plt`: Publication-quality plotting with style management (6 tools)
  - `canvas`: Multi-panel figure composition (7 tools)
  - `diagram`: Paper-optimized diagram generation with Mermaid/Graphviz (7 tools)
- **CLI Commands**: 7 new CLI command groups (113 new tests)
  - `audio`: Text-to-speech (speak, backends, check, stop)
  - `capture`: Screenshot/monitoring (snap, start, stop, gif, info, window)
  - `repro`: Reproducibility tools (gen-id, gen-timestamp, hash, seed)
  - `resource`: System monitoring (specs, usage, monitor)
  - `stats`: Statistical analysis (recommend, describe, save, load, tests)
  - `template`: Project scaffolding (list, clone, info)
  - `tex`: LaTeX operations (compile, preview, to-vec, check)
- **Web Module**: New `download_images` function for batch image downloading with size filtering

### Removed
- **Obsolete MCP Servers**: Removed standalone `src/mcp_servers/` directory (18 servers, ~44K lines)
  - Replaced by integrated module structure at `src/scitex/<module>/mcp_server.py`

### Changed
- MCP server entry points now follow pattern: `scitex-<module>` (e.g., `scitex-scholar`, `scitex-stats`)

## [2.11.0] - 2026-01-08

### Breaking Changes
- **Removed Modules**: Deprecated `fig`, `fts`, and `compat` modules have been removed
- **Canvas API**: `position`/`size` parameters renamed to `xy_mm`/`size_mm` for clarity

### Changed
- Removed legacy `Pltz*` aliases and terminology
- Reorganized maintenance scripts into `dependencies/` directory
- Simplified path module implementations
- Added installation time benchmark scripts

### Documentation
- Updated README with uv recommendations
- Consolidated visualization documentation into `docs/visualization/`

## [2.10.3] - 2026-01-06

### Fixed
- **Dependency**: Add direct `llvmlite>=0.39.0` constraint to force Python 3.11+ compatible version
  - `umap-learn>=0.5.4` alone was insufficient; `pynndescent` still pulled old `llvmlite==0.36.0`

## [2.10.2] - 2026-01-06

### Fixed
- **Dependency**: Pin `umap-learn>=0.5.4` for Python 3.11+ compatibility (llvmlite issue)

## [2.10.1] - 2026-01-06

### Fixed
- **Documentation**: Updated README to recommend `scitex[all]` as primary installation

## [2.10.0] - 2026-01-05

### Added
- **CI/CD Infrastructure**: Separate workflow files for all 41 modules
- **Datetime Module**: New `datetime` module with `dt` alias for time operations
- **Comprehensive Test Suites**: Major test improvements across modules
  - AI module: 577 tests passing
  - NN module: 498 tests passing
  - IO module: 506 tests passing
  - Writer module: 414 tests (expanded from 276)
  - CLI module: 201 tests
  - SH module: 149 tests
  - Scholar module: Core and storage tests

### Changed
- **License**: Updated to AGPL-3.0
- Updated README with improved installation section
- Reorganized project structure (removed unused externals directory)

### Fixed
- HTML tag order and markdown link syntax in README
- DSP module test failures (reduced from 154 to 78)
- Resource module test failures and source bugs
- Repro module JAX circular import bug
- Web module tests and source bugs
- Gen module tests improvements

### Security
- Added .env.zenrows to .gitignore to prevent credential commits

## [2.9.0] - 2025-12-28

### Added
- **FTS Bundle System**: New node kinds for annotations and images
  - `text` kind for text annotations with fontsize, fontweight, alignment
  - `shape` kind for shapes (rectangle, ellipse, arrow, line) with styling
  - `image` kind for embedded images
- **Node Categories**: Clear categorization of node kinds
  - DATA_LEAF_KINDS: plot, table, stats (require payload data files)
  - ANNOTATION_LEAF_KINDS: text, shape (no payload required)
  - IMAGE_LEAF_KINDS: image (require payload image file)
  - COMPOSITE_KINDS: figure (contain children)
- **Theme Enhancements**: FigureTitle and Caption dataclasses for attribute access
- **Matplotlib Analysis Tools**: Signature analysis tools in `dev/plt/mpl/`
- **CI/CD Improvements**: Added module-specific coverage targets

### Changed
- Reorganized demo plotters to `dev/plt/demo_plotters/` subdirectory
- Updated FTS examples to use new `kind` attribute instead of `type`
- Theme figure_title and caption now use dataclass attribute access

### Fixed
- Various import and attribute access fixes across modules
- Stats module now has optional torch dependency with numpy fallback

### Removed
- Deprecated VIS planning documentation (now in .gitignore)

## [2.8.1] - 2025-12-27

### Changed
- Made torch optional in stats module with numpy fallback
- Added cross-process FIFO queue for MCP audio server

## [2.8.0] - 2025-12-20

### Added
- FTS bundle examples
- Updated existing examples for FTS compatibility
- Tests for FTS refactoring

### Changed
- Core modules updated for FTS integration
- Consolidated error and warning classes in logging module
