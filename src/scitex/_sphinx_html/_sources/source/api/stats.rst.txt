Stats Module (``stx.stats``)
============================

23 statistical tests with effect sizes, confidence intervals, and
publication-ready formatting.

Quick Reference
---------------

.. code-block:: python

    import scitex as stx
    import numpy as np

    g1 = np.random.normal(0, 1, 50)
    g2 = np.random.normal(0.5, 1, 50)

    # Run a test
    result = stx.stats.test_ttest_ind(g1, g2)

    # Result is a flat dict with all details
    print(result["statistic"])     # t-statistic
    print(result["pvalue"])        # p-value
    print(result["effect_size"])   # Cohen's d
    print(result["stars"])         # Significance stars

    # Get as DataFrame or LaTeX
    df = stx.stats.test_ttest_ind(g1, g2, return_as="dataframe")
    tex = stx.stats.test_ttest_ind(g1, g2, return_as="latex")

Available Tests
---------------

**Parametric**

- ``test_ttest_1samp(data, popmean)`` -- One-sample t-test
- ``test_ttest_ind(g1, g2)`` -- Independent two-sample t-test
- ``test_ttest_rel(g1, g2)`` -- Paired t-test
- ``test_anova(*groups)`` -- One-way ANOVA
- ``test_anova_2way(data, factor1, factor2)`` -- Two-way ANOVA
- ``test_anova_rm(data, groups)`` -- Repeated measures ANOVA

**Non-parametric**

- ``test_mannwhitneyu(g1, g2)`` -- Mann-Whitney U test
- ``test_wilcoxon(g1, g2)`` -- Wilcoxon signed-rank test
- ``test_kruskal(*groups)`` -- Kruskal-Wallis H test
- ``test_friedman(*groups)`` -- Friedman test
- ``test_brunner_munzel(g1, g2)`` -- Brunner-Munzel test

**Correlation**

- ``test_pearson(x, y)`` -- Pearson correlation
- ``test_spearman(x, y)`` -- Spearman rank correlation
- ``test_kendall(x, y)`` -- Kendall tau correlation
- ``test_theilsen(x, y)`` -- Theil-Sen robust regression

**Categorical**

- ``test_chi2(observed)`` -- Chi-squared test
- ``test_fisher(table)`` -- Fisher's exact test
- ``test_mcnemar(table)`` -- McNemar test
- ``test_cochran_q(*groups)`` -- Cochran's Q test

**Normality**

- ``test_shapiro(data)`` -- Shapiro-Wilk test
- ``test_ks_1samp(data)`` -- One-sample Kolmogorov-Smirnov test
- ``test_ks_2samp(x, y)`` -- Two-sample Kolmogorov-Smirnov test
- ``test_normality(*samples)`` -- Multi-sample normality check

Seaborn-Style Data Parameter
----------------------------

All two-sample and one-sample tests accept an optional ``data`` parameter
for DataFrame/CSV column resolution (like seaborn):

.. code-block:: python

   import pandas as pd

   df = pd.read_csv("experiment.csv")

   # Two-sample: column names as x/y
   result = stx.stats.test_ttest_ind(x="before", y="after", data=df)

   # One-sample: column name as x
   result = stx.stats.test_shapiro(x="scores", data=df)

   # Multi-group: value + group columns
   result = stx.stats.test_anova(data=df, value_col="score", group_col="treatment")

   # Also works with CSV path
   result = stx.stats.test_ttest_ind(x="col1", y="col2", data="data.csv")

Test Recommendation
-------------------

Not sure which test to use? Let SciTeX recommend:

.. code-block:: python

    recommendations = stx.stats.recommend_tests(
        n_groups=2,
        sample_sizes=[30, 35],
        outcome_type="continuous",
        paired=False,
    )

Output Formats
--------------

Every test supports ``return_as`` parameter:

- ``"dict"`` (default) -- Returns plain dict with all results
- ``"dataframe"`` -- Returns pandas DataFrame

Descriptive Statistics
----------------------

.. code-block:: python

    stx.stats.describe(data)                    # mean, std, median, IQR, etc.
    stx.stats.effect_sizes.cohens_d(g1, g2)     # Cohen's d
    stx.stats.test_normality(g1, g2)            # Multi-sample normality
    stx.stats.p_to_stars(0.003)                 # "**"

Multiple Comparison Correction
------------------------------

.. code-block:: python

    corrected = stx.stats.correct_pvalues(
        [0.01, 0.03, 0.05, 0.001],
        method="fdr_bh",
    )

Post-hoc Tests
--------------

.. code-block:: python

    stx.stats.posthoc_test(
        [g1, g2, g3],
        group_names=["Control", "Treatment A", "Treatment B"],
        method="tukey",
    )

API Reference
-------------

.. automodule:: scitex.stats
   :members:
