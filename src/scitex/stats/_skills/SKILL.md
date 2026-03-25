---
name: stx.stats
description: Publication-ready statistical tests — 23 tests with effect sizes, power analysis, and multiple comparison correction.
---

# stx.stats — index

`scitex.stats` is a thin re-export wrapper over the `scitex-stats` standalone package. The core test functions, descriptive statistics, effect sizes, and power analysis all live in `scitex-stats`. `scitex.stats` adds bundle save/load, figrecipe plot annotation, and the `Stats` schema conversion — all of which depend on `scitex.io.bundle`.

## Sub-skills

| File | Topic |
|---|---|
| [01_tests.md](01_tests.md) | 23 statistical test functions — parametric, nonparametric, correlation, categorical, normality |
| [02_auto_and_descriptive.md](02_auto_and_descriptive.md) | Test recommendation, p-value stars, multiple comparison correction, descriptive stats, effect sizes |
| [03_scitex_integration.md](03_scitex_integration.md) | Bundle save/load, figrecipe annotation, Stats schema, `test_result_to_stats` |

## Quick reference

```python
import numpy as np
import scitex as stx

g1 = np.random.randn(30)
g2 = np.random.randn(30) + 0.5

# Run a test
result = stx.stats.test_ttest_ind(g1, g2)
result = stx.stats.test_mannwhitneyu(g1, g2)
result = stx.stats.test_anova(g1, g2, g3)

# Different output formats
df_result = stx.stats.test_ttest_ind(g1, g2, return_as="dataframe")
tex       = stx.stats.test_anova(g1, g2, g3, return_as="latex")

# Auto-select test
recommendations = stx.stats.recommend_tests(g1, g2)
result = stx.stats.run_test("ttest_ind", g1, g2)

# Format results
stars = stx.stats.p_to_stars(result["results"]["p_value"])

# Multiple comparison correction
corrected = stx.stats.correct([0.01, 0.04, 0.001], method="bonferroni")

# Effect size and power
d     = stx.stats.effect_sizes.cohen_d(g1, g2)
power = stx.stats.power(effect_size=0.5, n=30, alpha=0.05)

# Save as bundle
stx.stats.save_stats([result], "analysis.stats.zip", as_zip=True)

# Load bundle
data = stx.stats.load_stats("analysis.stats.zip")
# data["comparisons"] is a list of flat result dicts

# Annotate a plot
import scitex.plt as plt
fig, ax = plt.subplots()
stx.stats.annotate(ax, result, positions={"ctrl": 0, "trt": 1}, style="stars")

# Or load and annotate in one call
stx.stats.load_and_annotate(ax, "analysis.stats.zip")
```

## 23 tests at a glance

| Category | Functions |
|---|---|
| Parametric (6) | `test_ttest_ind`, `test_ttest_rel`, `test_ttest_1samp`, `test_anova`, `test_anova_rm`, `test_anova_2way` |
| Nonparametric (5) | `test_wilcoxon`, `test_mannwhitneyu`, `test_kruskal`, `test_friedman`, `test_brunner_munzel` |
| Correlation (4) | `test_pearson`, `test_spearman`, `test_kendall`, `test_theilsen` |
| Categorical (4) | `test_chi2`, `test_fisher`, `test_mcnemar`, `test_cochran_q` |
| Normality (4) | `test_shapiro`, `test_normality`, `test_ks_1samp`, `test_ks_2samp` |

## Architecture note

`scitex/stats/__init__.py` does `from scitex_stats import *` followed by explicit named imports for IDE support. The scitex-specific additions are in `_integration.py` (bundle, `annotate`) and `_figrecipe_integration.py` (`to_figrecipe`, `load_and_annotate`), both imported at the bottom of `__init__.py`.
