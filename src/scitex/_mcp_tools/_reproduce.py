#!/usr/bin/env python3
# Timestamp: 2026-02-11
# File: src/scitex/_mcp_tools/_reproduce.py

"""MCP call → Python script translator.

Converts logged MCP tool calls into standalone Python scripts
for reproducibility and auditing.

Usage::

    from scitex._mcp_tools._reproduce import reproduce

    script = reproduce("stats_run_test", test_name="ttest_ind",
                       data_file="exp.csv", columns=["ctrl", "treat"])
    print(script)
"""


__all__ = ["reproduce", "list_reproducible"]

# =============================================================================
# Name mapping for stats (MCP name → Python function path)
# =============================================================================

_STATS_FUNC_MAP = {
    "ttest_ind": "test_ttest_ind",
    "ttest_paired": "test_ttest_rel",
    "ttest_1samp": "test_ttest_1samp",
    "anova": "test_anova",
    "anova_rm": "test_anova_rm",
    "anova_2way": "test_anova_2way",
    "brunner_munzel": "test_brunner_munzel",
    "mannwhitneyu": "test_mannwhitneyu",
    "wilcoxon": "test_wilcoxon",
    "kruskal": "test_kruskal",
    "friedman": "test_friedman",
    "pearson": "test_pearson",
    "spearman": "test_spearman",
    "kendall": "test_kendall",
    "theilsen": "test_theilsen",
    "chi2": "test_chi2",
    "fisher_exact": "test_fisher",
    "mcnemar": "test_mcnemar",
    "cochran_q": "test_cochran_q",
    "shapiro": "test_shapiro",
    "normality": "test_normality",
    "ks_1samp": "test_ks_1samp",
    "ks_2samp": "test_ks_2samp",
}


def reproduce(tool_name: str, **kwargs) -> str:
    """Convert an MCP tool call to a standalone Python script.

    Parameters
    ----------
    tool_name : str
        MCP tool name (e.g., "stats_run_test", "plt_plot").
    **kwargs
        The exact arguments passed to the MCP tool.

    Returns
    -------
    str
        Python script string.
    """
    if tool_name in _TEMPLATES:
        return _TEMPLATES[tool_name](kwargs)
    return f"# No reproduction template for: {tool_name}\n# kwargs: {kwargs}\n"


def list_reproducible() -> list[str]:
    """Return tool names that have reproduction templates."""
    return sorted(_TEMPLATES.keys())


# =============================================================================
# Templates - one function per MCP tool
# =============================================================================


def _stats_run_test(kw: dict) -> str:
    test_name = kw.get("test_name", "ttest_ind")
    func_name = _STATS_FUNC_MAP.get(test_name, f"test_{test_name}")
    alt = kw.get("alternative", "two-sided")

    if kw.get("data_file"):
        cols = kw.get("columns", [])
        col_args = ", ".join(f'df["{c}"]' for c in cols)
        return (
            f"import scitex as stx\n"
            f"\n"
            f'df = stx.io.load("{kw["data_file"]}")\n'
            f'result = stx.stats.tests.{func_name}({col_args}, alternative="{alt}")\n'
            f"print(result)\n"
        )

    groups = kw.get("data", [])
    lines = ["import numpy as np", "import scitex as stx", ""]
    for i, g in enumerate(groups):
        lines.append(f"g{i} = np.array({g})")
    args = ", ".join(f"g{i}" for i in range(len(groups)))
    lines.append(f'result = stx.stats.tests.{func_name}({args}, alternative="{alt}")')
    lines.append("print(result)")
    return "\n".join(lines) + "\n"


def _stats_describe(kw: dict) -> str:
    data = kw.get("data", [])
    return (
        f"import numpy as np\n"
        f"import scitex as stx\n"
        f"\n"
        f"data = np.array({data})\n"
        f"result = stx.stats.describe(data)\n"
        f"print(result)\n"
    )


def _stats_effect_size(kw: dict) -> str:
    g1 = kw.get("group1", [])
    g2 = kw.get("group2", [])
    measure = kw.get("measure", "cohens_d")
    return (
        f"import numpy as np\n"
        f"from scitex.stats.effect_sizes import {measure}\n"
        f"\n"
        f"g1 = np.array({g1})\n"
        f"g2 = np.array({g2})\n"
        f"result = {measure}(g1, g2)\n"
        f"print(result)\n"
    )


def _stats_normality_test(kw: dict) -> str:
    data = kw.get("data", [])
    method = kw.get("method", "shapiro")
    func_name = _STATS_FUNC_MAP.get(method, f"test_{method}")
    return (
        f"import numpy as np\n"
        f"import scitex as stx\n"
        f"\n"
        f"data = np.array({data})\n"
        f"result = stx.stats.tests.{func_name}(data)\n"
        f"print(result)\n"
    )


def _stats_power_analysis(kw: dict) -> str:
    return (
        f"from scitex.stats.power import power_analysis\n"
        f"\n"
        f"result = power_analysis(\n"
        f'    test_type="{kw.get("test_type", "ttest")}",\n'
        f"    effect_size={kw.get('effect_size', 0.5)},\n"
        f"    alpha={kw.get('alpha', 0.05)},\n"
        f"    power={kw.get('power', 0.8)},\n"
        f"    n={kw.get('n', 'None')},\n"
        f"    n_groups={kw.get('n_groups', 2)},\n"
        f")\n"
        f"print(result)\n"
    )


def _stats_correct_pvalues(kw: dict) -> str:
    pvalues = kw.get("pvalues", [])
    method = kw.get("method", "fdr_bh")
    alpha = kw.get("alpha", 0.05)
    return (
        f"from scitex.stats.correct import correct_pvalues\n"
        f"\n"
        f"pvalues = {pvalues}\n"
        f'corrected = correct_pvalues(pvalues, method="{method}", alpha={alpha})\n'
        f"print(corrected)\n"
    )


def _stats_recommend_tests(kw: dict) -> str:
    return (
        f"from scitex.stats.auto import StatContext, recommend_tests\n"
        f"\n"
        f"ctx = StatContext(\n"
        f"    n_groups={kw.get('n_groups', 2)},\n"
        f"    sample_sizes={kw.get('sample_sizes', 'None')},\n"
        f'    outcome_type="{kw.get("outcome_type", "continuous")}",\n'
        f'    design="{kw.get("design", "between")}",\n'
        f"    paired={kw.get('paired', False)},\n"
        f")\n"
        f"tests = recommend_tests(ctx, top_k={kw.get('top_k', 3)})\n"
        f"print(tests)\n"
    )


def _plt_plot(kw: dict) -> str:
    import json

    spec = kw.get("spec", {})
    output = kw.get("output_path", "figure.png")
    dpi = kw.get("dpi", 300)
    spec_str = json.dumps(spec, indent=4)
    return (
        f"from figrecipe import plot\n"
        f"\n"
        f"spec = {spec_str}\n"
        f"\n"
        f'plot(spec, output_path="{output}", dpi={dpi})\n'
    )


def _plt_compose(kw: dict) -> str:
    import json

    sources = kw.get("sources", [])
    output = kw.get("output_path", "composed.png")
    layout = kw.get("layout", "horizontal")
    sources_str = json.dumps(sources, indent=4)
    return (
        f"from figrecipe import compose\n"
        f"\n"
        f"sources = {sources_str}\n"
        f"\n"
        f'compose(sources, output_path="{output}", layout="{layout}")\n'
    )


def _plt_reproduce(kw: dict) -> str:
    recipe = kw.get("recipe_path", "recipe.yaml")
    output = kw.get("output_path", "reproduced.png")
    return (
        f"from figrecipe import reproduce\n"
        f"\n"
        f'reproduce("{recipe}", output_path="{output}")\n'
    )


def _plt_list_styles(kw: dict) -> str:
    return (
        "from figrecipe import list_styles\n\nstyles = list_styles()\nprint(styles)\n"
    )


def _plt_load_style(kw: dict) -> str:
    style = kw.get("style", "SCITEX")
    dark = kw.get("dark", False)
    return f'from figrecipe import load_style\n\nload_style("{style}", dark={dark})\n'


# =============================================================================
# Registry
# =============================================================================

_TEMPLATES = {
    # Stats tools
    "stats_run_test": _stats_run_test,
    "stats_describe": _stats_describe,
    "stats_effect_size": _stats_effect_size,
    "stats_normality_test": _stats_normality_test,
    "stats_power_analysis": _stats_power_analysis,
    "stats_correct_pvalues": _stats_correct_pvalues,
    "stats_recommend_tests": _stats_recommend_tests,
    # Plt tools
    "plt_plot": _plt_plot,
    "plt_compose": _plt_compose,
    "plt_reproduce": _plt_reproduce,
    "plt_list_styles": _plt_list_styles,
    "plt_load_style": _plt_load_style,
}


# EOF
