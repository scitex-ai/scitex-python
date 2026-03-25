---
skill: stats.auto_and_descriptive
description: Automatic test recommendation, p-value formatting, multiple comparison correction, and descriptive statistics.
---

# stx.stats — auto, descriptive, and formatting

## Automatic test recommendation

`recommend_tests` inspects the input data and returns a ranked list of
appropriate statistical tests based on sample size, normality, and number of
groups.

```python
import numpy as np
import scitex as stx

g1 = np.random.randn(30)
g2 = np.random.randn(30) + 0.5

# Get ranked test recommendations
recommendations = stx.stats.recommend_tests(g1, g2)
# Returns list of test name strings, most appropriate first
# e.g. ["ttest_ind", "mannwhitneyu", ...]

# Check applicability of a specific test
applicable = stx.stats.check_applicable("ttest_ind", g1, g2)
# Returns bool or dict with reason
```

## StatContext and TestRule

```python
from scitex.stats import StatContext, TestRule

# StatContext — information about data properties
ctx = StatContext(samples=[g1, g2])
print(ctx.n_groups, ctx.is_paired, ctx.is_normal)

# TestRule — conditions under which a test applies
rule = TestRule(name="ttest_ind", requires_normal=True, n_groups=2)
```

## p-value formatting

```python
# Convert p-value to significance stars
stars = stx.stats.p_to_stars(0.001)   # "***"
stars = stx.stats.p_to_stars(0.01)    # "**"
stars = stx.stats.p_to_stars(0.04)    # "*"
stars = stx.stats.p_to_stars(0.2)     # "ns"

# Get style object for a significance level
style = stx.stats.get_stat_style(p_value=0.001)
# Returns StatStyle with color, symbol, label fields
```

## Multiple comparison correction

```python
p_values = [0.01, 0.04, 0.001, 0.2, 0.06]

# Bonferroni correction
corrected = stx.stats.correct(p_values, method="bonferroni")

# Benjamini-Hochberg (FDR) correction
corrected = stx.stats.correct(p_values, method="fdr_bh")

# Holm-Bonferroni
corrected = stx.stats.correct(p_values, method="holm")

# Returns numpy array of corrected p-values in same order as input
```

## Descriptive statistics

```python
data = np.random.randn(100)

# Summary statistics dict
summary = stx.stats.describe(data)
# Keys: mean, std, median, iqr, min, max, n, skew, kurtosis

# Descriptive submodule — individual functions
ci = stx.stats.descriptive.ci(data, alpha=0.05)       # 95% CI tuple
sem = stx.stats.descriptive.sem(data)                 # standard error
iqr = stx.stats.descriptive.iqr(data)                 # interquartile range
```

## Effect sizes

```python
g1 = np.random.randn(30)
g2 = np.random.randn(30) + 0.8

# Cohen's d (two independent groups)
d = stx.stats.effect_sizes.cohen_d(g1, g2)

# Eta-squared (from ANOVA F and df)
eta2 = stx.stats.effect_sizes.eta_squared(F=4.5, df_between=2, df_within=87)

# Glass's delta
delta = stx.stats.effect_sizes.glass_delta(g1, g2)

# Odds ratio (from 2x2 contingency table)
obs = np.array([[10, 20], [5, 40]])
or_val = stx.stats.effect_sizes.odds_ratio(obs)
```

## Power analysis

```python
# Compute statistical power given effect size, sample size, alpha
power = stx.stats.power(effect_size=0.5, n=30, alpha=0.05)

# power submodule for extended analyses
n_needed = stx.stats.power.sample_size(
    effect_size=0.5, power=0.8, alpha=0.05, test="ttest_ind"
)
```

## Auto submodule internals (advanced)

The `auto` submodule provides the pipeline used by `recommend_tests`. You can
access its components for custom workflows:

```python
from scitex.stats.auto import TEST_RULES   # All decision rules
from scitex.stats.auto import get_menu_items  # UI-facing item list
from scitex.stats.auto import format_test_line  # Format a result line

# These are also exposed at module level with private names:
from scitex.stats import _TEST_RULES, _get_menu_items, _format_test_line
```
