---
skill: stats.tests
description: 23 statistical tests — parametric, nonparametric, correlation, categorical, normality.
---

# stx.stats — statistical tests

All 23 test functions are re-exported from `scitex-stats` (the standalone package). They follow a uniform call signature and return a dict with consistent keys.

## Common return keys

Every test function returns a dict containing at minimum:

| key | type | description |
|---|---|---|
| `method` | dict | `{"name": "t-test", "variant": "independent", "parameters": {}}` |
| `results` | dict | `{"statistic": 2.5, "statistic_name": "t", "p_value": 0.03, ...}` |
| `results.effect_size` | dict | `{"name": "d", "value": 0.8, "ci_lower": 0.2, "ci_upper": 1.4}` |
| `results.significant` | bool | `True` if `p_value < alpha` |
| `results.alpha` | float | significance level (default 0.05) |

### return_as parameter

All test functions accept `return_as`:

```python
result = stx.stats.test_ttest_ind(g1, g2)                      # dict (default)
result = stx.stats.test_ttest_ind(g1, g2, return_as="dataframe") # pd.DataFrame
result = stx.stats.test_ttest_ind(g1, g2, return_as="latex")     # LaTeX string
result = stx.stats.test_ttest_ind(g1, g2, return_as="dict")      # same as default
```

## Parametric tests (6)

```python
import numpy as np
import scitex as stx

g1 = np.random.randn(30)
g2 = np.random.randn(30) + 0.5
g3 = np.random.randn(30) + 1.0

# Independent t-test
result = stx.stats.test_ttest_ind(g1, g2)

# Paired t-test
result = stx.stats.test_ttest_rel(g1, g2)

# One-sample t-test (against a population mean)
result = stx.stats.test_ttest_1samp(g1, popmean=0.0)

# One-way ANOVA
result = stx.stats.test_anova(g1, g2, g3)

# Repeated measures ANOVA
# groups is a 2D array: rows=subjects, cols=conditions
result = stx.stats.test_anova_rm(groups_matrix)

# Two-way ANOVA
result = stx.stats.test_anova_2way(data, factor_a, factor_b)
```

## Nonparametric tests (5)

```python
# Wilcoxon signed-rank (paired)
result = stx.stats.test_wilcoxon(g1, g2)

# Mann-Whitney U (independent)
result = stx.stats.test_mannwhitneyu(g1, g2)

# Kruskal-Wallis (k independent groups)
result = stx.stats.test_kruskal(g1, g2, g3)

# Friedman (repeated measures, k conditions)
result = stx.stats.test_friedman(groups_matrix)

# Brunner-Munzel (robust two-sample)
result = stx.stats.test_brunner_munzel(g1, g2)
```

## Correlation tests (4)

```python
x = np.random.randn(50)
y = x + np.random.randn(50) * 0.5

# Pearson correlation
result = stx.stats.test_pearson(x, y)

# Spearman rank correlation
result = stx.stats.test_spearman(x, y)

# Kendall tau
result = stx.stats.test_kendall(x, y)

# Theil-Sen robust linear regression
result = stx.stats.test_theilsen(x, y)
```

## Categorical tests (4)

```python
obs = np.array([[10, 20], [15, 25]])

# Chi-squared
result = stx.stats.test_chi2(obs)

# Fisher's exact (2x2 only)
result = stx.stats.test_fisher(obs)

# McNemar (paired binary outcomes)
result = stx.stats.test_mcnemar(obs)

# Cochran's Q (multiple paired binary conditions)
result = stx.stats.test_cochran_q(binary_matrix)
```

## Normality tests (4)

```python
data = np.random.randn(100)

# Shapiro-Wilk
result = stx.stats.test_shapiro(data)

# General normality test (runs multiple tests)
result = stx.stats.test_normality(data)

# Kolmogorov-Smirnov (one-sample)
result = stx.stats.test_ks_1samp(data, cdf="norm")

# Kolmogorov-Smirnov (two-sample)
result = stx.stats.test_ks_2samp(g1, g2)
```

## Universal dispatcher

`run_test` lets you select a test by name string — useful when the test is
determined at runtime:

```python
result = stx.stats.run_test("ttest_ind", g1, g2)
result = stx.stats.run_test("mannwhitneyu", g1, g2)
result = stx.stats.run_test("kruskal", g1, g2, g3)
```

List all available test names:

```python
names = stx.stats.available_tests()
```

## JSON serialization

```python
# Convert result to JSON-safe dict (handles numpy dtypes, non-finite floats)
json_safe = stx.stats.to_json_safe(result)
import json
json.dumps(json_safe)
```
