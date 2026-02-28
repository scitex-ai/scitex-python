#!/usr/bin/env python3
# Timestamp: 2026-01-15
# File: /home/ywatanabe/proj/scitex-code/src/scitex/_mcp_tools/stats.py
"""Stats module tools for FastMCP unified server."""


import json
from typing import List, Optional


def _json(data: dict) -> str:
    return json.dumps(data, indent=2, default=str)


def register_stats_tools(mcp) -> None:  # noqa: C901
    """Register stats tools with FastMCP server."""

    @mcp.tool()
    async def stats_recommend_tests(
        n_groups: int = 2,
        sample_sizes: Optional[List[int]] = None,
        outcome_type: str = "continuous",
        design: str = "between",
        paired: bool = False,
        has_control_group: bool = False,
        top_k: int = 3,
    ) -> str:
        """[stats] Recommend appropriate statistical tests based on data characteristics."""
        from scitex.stats._mcp.handlers import recommend_tests_handler

        result = await recommend_tests_handler(
            n_groups=n_groups,
            sample_sizes=sample_sizes,
            outcome_type=outcome_type,
            design=design,
            paired=paired,
            has_control_group=has_control_group,
            top_k=top_k,
        )
        return _json(result)

    @mcp.tool()
    async def stats_run_test(
        test_name: str,
        data: Optional[List[List[float]]] = None,
        data_file: Optional[str] = None,
        columns: Optional[List[str]] = None,
        alternative: str = "two-sided",
    ) -> str:
        """[stats] Execute a statistical test on provided data."""
        from scitex.stats._mcp.handlers import run_test_handler

        result = await run_test_handler(
            test_name=test_name,
            data=data,
            data_file=data_file,
            columns=columns,
            alternative=alternative,
        )
        return _json(result)

    @mcp.tool()
    async def stats_format_results(
        test_name: str,
        statistic: float,
        p_value: float,
        df: Optional[float] = None,
        effect_size: Optional[float] = None,
        effect_size_name: Optional[str] = None,
        style: str = "apa",
        ci_lower: Optional[float] = None,
        ci_upper: Optional[float] = None,
    ) -> str:
        """[stats] Format statistical results in journal style (APA, Nature, etc.)."""
        from scitex.stats._mcp.handlers import format_results_handler

        result = await format_results_handler(
            test_name=test_name,
            statistic=statistic,
            p_value=p_value,
            df=df,
            effect_size=effect_size,
            effect_size_name=effect_size_name,
            style=style,
            ci_lower=ci_lower,
            ci_upper=ci_upper,
        )
        return _json(result)

    @mcp.tool()
    async def stats_power_analysis(
        test_type: str = "ttest",
        effect_size: Optional[float] = None,
        alpha: float = 0.05,
        power: float = 0.8,
        n: Optional[int] = None,
        n_groups: int = 2,
        ratio: float = 1.0,
    ) -> str:
        """[stats] Calculate statistical power or required sample size."""
        from scitex.stats._mcp.handlers import power_analysis_handler

        result = await power_analysis_handler(
            test_type=test_type,
            effect_size=effect_size,
            alpha=alpha,
            power=power,
            n=n,
            n_groups=n_groups,
            ratio=ratio,
        )
        return _json(result)

    @mcp.tool()
    async def stats_correct_pvalues(
        pvalues: List[float],
        method: str = "fdr_bh",
        alpha: float = 0.05,
    ) -> str:
        """[stats] Apply multiple comparison correction to p-values."""
        from scitex.stats._mcp.handlers import correct_pvalues_handler

        result = await correct_pvalues_handler(
            pvalues=pvalues,
            method=method,
            alpha=alpha,
        )
        return _json(result)

    @mcp.tool()
    async def stats_describe(
        data: List[float],
        percentiles: Optional[List[float]] = None,
    ) -> str:
        """[stats] Calculate descriptive statistics for data."""
        from scitex.stats._mcp.handlers import describe_handler

        result = await describe_handler(
            data=data,
            percentiles=percentiles,
        )
        return _json(result)

    @mcp.tool()
    async def stats_effect_size(
        group1: List[float],
        group2: List[float],
        measure: str = "cohens_d",
        pooled: bool = True,
    ) -> str:
        """[stats] Calculate effect size between groups."""
        from scitex.stats._mcp.handlers import effect_size_handler

        result = await effect_size_handler(
            group1=group1,
            group2=group2,
            measure=measure,
            pooled=pooled,
        )
        return _json(result)

    @mcp.tool()
    async def stats_normality_test(
        data: List[float],
        method: str = "shapiro",
    ) -> str:
        """[stats] Test whether data follows a normal distribution."""
        from scitex.stats._mcp.handlers import normality_test_handler

        result = await normality_test_handler(
            data=data,
            method=method,
        )
        return _json(result)

    @mcp.tool()
    async def stats_posthoc_test(
        groups: List[List[float]],
        group_names: Optional[List[str]] = None,
        method: str = "tukey",
        control_group: int = 0,
    ) -> str:
        """[stats] Run post-hoc pairwise comparisons after significant ANOVA/Kruskal."""
        from scitex.stats._mcp.handlers import posthoc_test_handler

        result = await posthoc_test_handler(
            groups=groups,
            group_names=group_names,
            method=method,
            control_group=control_group,
        )
        return _json(result)

    @mcp.tool()
    async def stats_p_to_stars(
        p_value: float,
        thresholds: Optional[List[float]] = None,
    ) -> str:
        """[stats] Convert p-value to significance stars (*, **, ***, ns)."""
        from scitex.stats._mcp.handlers import p_to_stars_handler

        result = await p_to_stars_handler(
            p_value=p_value,
            thresholds=thresholds,
        )
        return _json(result)


# EOF
