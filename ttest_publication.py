"""Publication-ready independent-samples t-test with effect size and CI."""

from dataclasses import dataclass

import numpy as np
from scipy import stats

import scitex as stx


@dataclass
class TTestResult:
    """Publication-ready t-test result."""

    # Test statistics
    t_stat: float
    p_value: float
    df: int

    # Effect size
    cohens_d: float
    d_ci_lower: float
    d_ci_upper: float

    # Normality
    shapiro_p1: float
    shapiro_p2: float
    normality_violated: bool

    # Descriptive statistics
    mean_1: float
    mean_2: float
    std_1: float
    std_2: float
    n_1: int
    n_2: int

    def __str__(self) -> str:
        """Publication-ready formatted output."""
        normality = "VIOLATED" if self.normality_violated else "OK"

        return (
            f"Independent-Samples t-Test Results\n"
            f"{'=' * 50}\n\n"
            f"Test Statistics:\n"
            f"  t({self.df}) = {self.t_stat:.3f}, p = {self.p_value:.4f}\n"
            f"  Cohens d = {self.cohens_d:.3f}, 95% CI [{self.d_ci_lower:.3f}, {self.d_ci_upper:.3f}]\n\n"
            f"Descriptive Statistics:\n"
            f"  Group 1: M = {self.mean_1:.3f}, SD = {self.std_1:.3f}, n = {self.n_1}\n"
            f"  Group 2: M = {self.mean_2:.3f}, SD = {self.std_2:.3f}, n = {self.n_2}\n\n"
            f"Normality (Shapiro-Wilk):\n"
            f"  Group 1: p = {self.shapiro_p1:.4f}\n"
            f"  Group 2: p = {self.shapiro_p2:.4f}\n"
            f"  Status: {normality}\n"
        )


def ttest_publication(
    array1: np.ndarray,
    array2: np.ndarray,
    alpha: float = 0.05,
) -> TTestResult:
    """
    Run publication-ready independent-samples t-test.

    Performs:
    - Shapiro-Wilk normality test on both groups
    - Independent-samples t-test (assumes equal variances for simplicity)
    - Cohen's d with bootstrapped 95% CI
    - Structured output formatting

    Args:
        array1: First group (numpy array)
        array2: Second group (numpy array)
        alpha: Significance level (default 0.05)

    Returns
    -------
        TTestResult with all statistics, effect sizes, and CIs
    """
    array1 = np.asarray(array1)
    array2 = np.asarray(array2)

    # Normality tests
    _, p_shapiro_1 = stats.shapiro(array1)
    _, p_shapiro_2 = stats.shapiro(array2)
    normality_ok = (p_shapiro_1 > alpha) and (p_shapiro_2 > alpha)

    # Independent samples t-test
    t_stat, p_value = stats.ttest_ind(array1, array2)
    df = len(array1) + len(array2) - 2

    # Cohen's d
    n1, n2 = len(array1), len(array2)
    mean1, mean2 = np.mean(array1), np.mean(array2)
    std1, std2 = np.std(array1, ddof=1), np.std(array2, ddof=1)

    # Pooled standard deviation
    pooled_std = np.sqrt(((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2))
    cohens_d = (mean1 - mean2) / pooled_std

    # 95% CI for Cohen's d via bootstrap
    n_bootstrap = 10000
    np.random.seed(42)
    d_values = []
    for _ in range(n_bootstrap):
        sample1 = np.random.choice(array1, size=n1, replace=True)
        sample2 = np.random.choice(array2, size=n2, replace=True)
        mean1_b = np.mean(sample1)
        mean2_b = np.mean(sample2)
        std1_b = np.std(sample1, ddof=1)
        std2_b = np.std(sample2, ddof=1)
        pooled_std_b = np.sqrt(
            ((n1 - 1) * std1_b**2 + (n2 - 1) * std2_b**2) / (n1 + n2 - 2)
        )
        d_values.append((mean1_b - mean2_b) / pooled_std_b)

    d_ci_lower = np.percentile(d_values, 2.5)
    d_ci_upper = np.percentile(d_values, 97.5)

    return TTestResult(
        t_stat=t_stat,
        p_value=p_value,
        df=df,
        cohens_d=cohens_d,
        d_ci_lower=d_ci_lower,
        d_ci_upper=d_ci_upper,
        shapiro_p1=p_shapiro_1,
        shapiro_p2=p_shapiro_2,
        normality_violated=not normality_ok,
        mean_1=mean1,
        mean_2=mean2,
        std_1=std1,
        std_2=std2,
        n_1=n1,
        n_2=n2,
    )


@stx.session
def main() -> int:
    """Example usage."""
    np.random.seed(0)
    group1 = np.random.normal(100, 15, 30)
    group2 = np.random.normal(105, 15, 35)

    result = ttest_publication(group1, group2)
    print(result)
    return 0


if __name__ == "__main__":
    main()
