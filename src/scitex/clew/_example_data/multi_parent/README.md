# Multi-Parent DAG Example

Demonstrates multi-parent DAG tracking and verification in `scitex.clew`.

## Pipeline

```
01_generate_subjects  ──→ subjects.csv  ──┐
02_generate_stimuli   ──→ stimuli.csv   ──┼──→ 03_run_experiment ──→ raw_data.csv
04_load_covariates    ──→ covariates.csv──┘          │
                                                     ├──→ 05_analyze_behavior ──→ behavior.csv ──┐
                                                     └──→ 06_analyze_neural   ──→ neural.csv   ──┤
                                                          (+ covariates.csv)                      │
                                                                                                  ↓
                                                                                   07_merge_results ──→ combined.csv
                                                                                          │
                                                                                   08_make_figures  ──→ figure1.png
                                                                                                       figure2.png
```

Multi-parent nodes:
- `03_run_experiment`: 3 parents (subjects, stimuli, covariates)
- `06_analyze_neural`: 2 parents (raw_data, covariates)
- `07_merge_results`: 2 parents (behavior, neural)

## Quick Start

```bash
./00_run_all.sh --clean
```

## What It Demonstrates

1. **Multi-parent tracking** - `stx.io.load()` from multiple upstream outputs auto-links all parents
2. **DAG verification** - `stx.clew.dag([file1, file2])` traces back through the full diamond
3. **Claims** - `stx.clew.add_claim()` registers scientific claims tied to source files
4. **Claims-to-DAG** - `stx.clew.verify_claims_dag()` builds DAG from all registered claims
5. **DAG rendering** - `render_dag("dag.html", target_files=[...])` generates interactive HTML

## CLI Commands

```bash
# After running the pipeline
scitex clew status
scitex clew dag 08_make_figures_out/figure1.png 08_make_figures_out/figure2.png
scitex clew render dag.html -f 08_make_figures_out/figure1.png -f 08_make_figures_out/figure2.png
scitex clew dag --claims
```
