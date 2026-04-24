# Additional SciTeX Modules

Companion doc to the main [README.md](../README.md). Covers re-exported
downstream modules not featured in the main Quick Start.

## `scitex.audio` — Text-to-Speech with Fallback Backends

Multi-backend TTS for experiment narration, pipeline announcements, or
accessibility. Backends ordered by quality:

- **ElevenLabs** — paid, highest quality
- **LuxTTS** — offline, voice-cloning, 48 kHz, near-realtime on CPU
- **gTTS** — free, online
- **pyttsx3** — offline, espeak

```python
import scitex as stx
stx.audio.speak("Training run complete. Accuracy ninety-four percent.")
stx.audio.speak("Offline please", backend="pyttsx3")      # Force offline
stx.audio.speak("Report", output_path="report.mp3", play=False)  # TTS to file
```

```bash
scitex audio speak "Analysis finished"
```

## `scitex.dataset` — Scientific Dataset Fetcher

Fetch neuroscience and biomedical datasets from OpenNeuro (BIDS), DANDI,
PhysioNet, GEO, ChEMBL, ClinicalTrials.gov via a uniform API.

```python
import scitex as stx
ds = stx.dataset.neuroscience.openneuro.fetch_all_datasets(max_datasets=10)   # BIDS MRI/EEG
stx.dataset.neuroscience.dandi.fetch_all_datasets(max_datasets=10)             # Ephys / imaging
stx.dataset.neuroscience.physionet.fetch_all_datasets(max_datasets=10)         # Clinical waveforms
hits = stx.dataset.search_datasets(ds, text_query="phase-amplitude coupling")
```

## `scitex.container` — Apptainer / Docker Management

Reproducible HPC containers — build, version, rollback, env snapshot.

```python
import scitex as stx
stx.container.build(def_name="recipe")                  # Builds versioned SIF
stx.container.switch_version("2.19.5")                  # Atomic active-SIF flip
stx.container.rollback()                                # Revert to previous version
snap = stx.container.env_snapshot()                     # Full env for papers
```

## `scitex.tunnel` — Persistent SSH Reverse Tunnels

NAT traversal for lab machines — autossh-backed systemd service.

```python
import scitex as stx
stx.tunnel.setup(port=8888, bastion_server="gw.example.com")
stx.tunnel.status()                                     # {"8888": "active"}
stx.tunnel.remove(port=8888)
```

## `scitex.linter` — Convention Checker (47 rules)

Lint SciTeX projects for ecosystem conventions — `stx.io.save` usage,
matplotlib prefs, CONFIGS naming, import hygiene. Complements ruff/flake8.

```python
import scitex as stx
issues = stx.linter.lint_file("src/")
for i in issues:
    print(f"{i.filepath}:{i.line} [{i.rule.id}] {i.message}")
```

```bash
scitex linter check src/
```

## `scitex.repro` — Seed Everything + Array Hashing

One call seeds random, NumPy, PyTorch, TensorFlow; generate run-IDs and
deterministic array hashes for experiment fingerprinting.

```python
import scitex as stx
rng = stx.repro.RandomStateManager(seed=42)             # Seeds all frameworks
run_id = stx.repro.gen_ID()                             # "20260423_2155_abc12345"
digest = stx.repro.hash_array(np_array)                 # Deterministic SHA
```

## `scitex.parallel` — Threaded Map with tqdm

Drop-in parallel map for I/O-bound work — HTTP fetches, file reads, API calls.

```python
import scitex as stx
results = stx.parallel.run(download, [(u,) for u in urls], n_jobs=-1)
```

## Utility Modules

Lower-level SciTeX utilities re-exported under the umbrella:

| Module | Purpose | Key API |
|--------|---------|---------|
| `stx.path` | Project-aware paths | `find_git_root`, `get_spath`, `create_relative_symlink` |
| `stx.str` | Text / LaTeX fallback / colored prints | `printc`, `safe_latex_render`, `grep` |
| `stx.dict` | `DotDict` + safe merge / flatten | `DotDict`, `safe_merge`, `flatten` |
| `stx.logging` | stdlib-logging + SUCCESS/FAIL + `SciTeXError` | `getLogger`, `warn_deprecated`, `Tee` |
| `stx.types` | Union type aliases + predicates | `ArrayLike`, `ColorLike`, `is_array_like` |
| `stx.db` | SQLite3 / PostgreSQL wrapper w/ ndarray BLOBs | `SQLite3`, `PostgreSQL`, `delete_duplicates` |
| `stx.audit` | Unified security scan (bandit / shellcheck / pip-audit) | `audit()` |
| `stx.browser` | Playwright helpers for scraping | `save_as_pdf`, `click_with_fallbacks_async` |
| `stx.compat` | Deprecation shims | `@deprecated`, `notify` legacy alias |
| `stx.etc` | Terminal keypress helpers | `wait_key`, `count` |

See the [Full API reference](https://scitex-python.readthedocs.io/en/latest/api/index.html)
for complete signatures.
