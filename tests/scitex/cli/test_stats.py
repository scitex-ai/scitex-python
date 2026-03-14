#!/usr/bin/env python3
"""Tests for scitex.cli.stats - Statistical analysis CLI commands."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from scitex.cli.stats import stats


class TestStatsGroup:
    """Tests for the stats command group."""

    def test_stats_help(self):
        """Test that stats help is displayed correctly."""
        runner = CliRunner()
        result = runner.invoke(stats, ["--help"])
        assert result.exit_code == 0
        assert "Statistical analysis" in result.output

    def test_stats_has_subcommands(self):
        """Test that all expected subcommands are registered."""
        runner = CliRunner()
        result = runner.invoke(stats, ["--help"])
        expected_commands = ["recommend", "describe", "save", "load", "tests"]
        for cmd in expected_commands:
            assert cmd in result.output, f"Command '{cmd}' not found in stats help"


class TestStatsRecommend:
    """Tests for the stats recommend command."""

    def test_recommend_basic(self):
        """Test recommend command with basic options."""
        runner = CliRunner()
        with patch("scitex.stats.StatContext") as mock_ctx:
            with patch("scitex.stats.recommend_tests") as mock_recommend:
                mock_recommend.return_value = ["t-test", "Mann-Whitney U"]
                result = runner.invoke(
                    stats,
                    [
                        "recommend",
                        "--n-groups",
                        "2",
                        "--outcome-type",
                        "continuous",
                    ],
                )
                assert result.exit_code == 0
                assert "Recommended" in result.output
                mock_recommend.assert_called_once()

    def test_recommend_json(self):
        """Test recommend command with --json flag."""
        runner = CliRunner()
        with patch("scitex.stats.StatContext") as mock_ctx:
            with patch("scitex.stats.recommend_tests") as mock_recommend:
                mock_recommend.return_value = ["ANOVA", "Kruskal-Wallis"]
                result = runner.invoke(
                    stats,
                    [
                        "recommend",
                        "--n-groups",
                        "3",
                        "--outcome-type",
                        "continuous",
                        "--json",
                    ],
                )
                assert result.exit_code == 0
                output = json.loads(result.output)
                data = output.get("data", output)
                assert "recommended_tests" in data

    def test_recommend_with_paired(self):
        """Test recommend command with paired flag."""
        runner = CliRunner()
        with patch("scitex.stats.StatContext") as mock_ctx:
            with patch("scitex.stats.recommend_tests") as mock_recommend:
                mock_recommend.return_value = ["paired t-test"]
                result = runner.invoke(
                    stats,
                    [
                        "recommend",
                        "--n-groups",
                        "2",
                        "--outcome-type",
                        "continuous",
                        "--design",
                        "within",
                        "--paired",
                    ],
                )
                assert result.exit_code == 0

    def test_recommend_categorical(self):
        """Test recommend command with categorical outcome."""
        runner = CliRunner()
        with patch("scitex.stats.StatContext") as mock_ctx:
            with patch("scitex.stats.recommend_tests") as mock_recommend:
                mock_recommend.return_value = ["chi-square"]
                result = runner.invoke(
                    stats,
                    [
                        "recommend",
                        "--n-groups",
                        "2",
                        "--outcome-type",
                        "binary",
                    ],
                )
                assert result.exit_code == 0


class TestStatsDescribe:
    """Tests for the stats describe command."""

    def test_describe_with_file(self):
        """Test describe command with data file."""
        runner = CliRunner()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("a,b,c\n1,2,3\n4,5,6\n7,8,9\n")
            temp_path = f.name

        try:
            with patch("scitex.stats.describe") as mock_describe:
                import pandas as pd

                mock_describe.return_value = pd.DataFrame(
                    {"count": [3, 3, 3], "mean": [4.0, 5.0, 6.0]}
                )
                result = runner.invoke(stats, ["describe", temp_path])
                assert result.exit_code == 0
                assert "Descriptive Statistics" in result.output
        finally:
            os.unlink(temp_path)

    def test_describe_json(self):
        """Test describe command with --json flag."""
        runner = CliRunner()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("a,b\n1,2\n3,4\n")
            temp_path = f.name

        try:
            with patch("scitex.stats.describe") as mock_describe:
                mock_describe.return_value = {"count": 2, "mean": 2.5}
                result = runner.invoke(stats, ["describe", temp_path, "--json"])
                assert result.exit_code == 0
                output = json.loads(result.output)
                data = output.get("data", output)
                assert "count" in data
        finally:
            os.unlink(temp_path)

    def test_describe_with_column(self):
        """Test describe command with specific column."""
        runner = CliRunner()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("a,b\n1,2\n3,4\n")
            temp_path = f.name

        try:
            with patch("scitex.stats.describe") as mock_describe:
                mock_describe.return_value = {"count": 2}
                result = runner.invoke(stats, ["describe", temp_path, "--column", "a"])
                assert result.exit_code == 0
        finally:
            os.unlink(temp_path)


class TestStatsSave:
    """Tests for the stats save command."""

    def test_save_basic(self):
        """Test save command."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input JSON file
            input_path = os.path.join(tmpdir, "input.json")
            with open(input_path, "w") as f:
                json.dump({"test": "t-test", "p_value": 0.05}, f)

            output_path = os.path.join(tmpdir, "stats.stats")
            with patch("scitex.stats.save_stats") as mock_save:
                mock_save.return_value = output_path
                result = runner.invoke(
                    stats,
                    ["save", input_path, "--output", output_path],
                )
                assert result.exit_code == 0
                assert "saved" in result.output.lower()

    def test_save_with_as_zip(self):
        """Test save command with --as-zip flag."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, "input.json")
            with open(input_path, "w") as f:
                json.dump([{"test": "t-test", "p_value": 0.05}], f)

            output_path = os.path.join(tmpdir, "stats.stats")
            with patch("scitex.stats.save_stats") as mock_save:
                mock_save.return_value = output_path
                result = runner.invoke(
                    stats,
                    ["save", input_path, "--output", output_path, "--as-zip"],
                )
                assert result.exit_code == 0


class TestStatsLoad:
    """Tests for the stats load command."""

    def test_load_basic(self):
        """Test load command."""
        runner = CliRunner()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".stats", delete=False) as f:
            f.write('{"comparisons": [{"name": "test", "p_value": 0.05}]}')
            temp_path = f.name

        try:
            with patch("scitex.stats.load_stats") as mock_load:
                mock_load.return_value = {
                    "comparisons": [
                        {"name": "test", "method": "t-test", "p_value": 0.05}
                    ]
                }
                result = runner.invoke(stats, ["load", temp_path])
                assert result.exit_code == 0
                assert "Statistics Bundle" in result.output
        finally:
            os.unlink(temp_path)

    def test_load_json(self):
        """Test load command with --json flag."""
        runner = CliRunner()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".stats", delete=False) as f:
            f.write('{"p_value": 0.05}')
            temp_path = f.name

        try:
            with patch("scitex.stats.load_stats") as mock_load:
                mock_load.return_value = {"comparisons": [], "p_value": 0.05}
                result = runner.invoke(stats, ["load", temp_path, "--json"])
                assert result.exit_code == 0
                output = json.loads(result.output)
                data = output.get("data", output)
                assert "p_value" in data or "comparisons" in data
        finally:
            os.unlink(temp_path)


class TestStatsTests:
    """Tests for the stats tests command."""

    def test_tests_list(self):
        """Test tests list command."""
        runner = CliRunner()
        with patch("scitex.stats.TEST_RULES") as mock_rules:
            mock_rule = MagicMock()
            mock_rule.category = "parametric"
            mock_rule.name = "t-test"
            mock_rules.__iter__ = lambda self: iter([mock_rule])
            result = runner.invoke(stats, ["tests"])
            assert result.exit_code == 0
            assert "Available Statistical Tests" in result.output


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/cli/stats.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# """
# SciTeX CLI - Stats Commands (Statistical Analysis)
#
# Provides statistical testing, test recommendation, and result management.
# """
#
# import sys
# from pathlib import Path
#
# import click
#
#
# @click.group(context_settings={"help_option_names": ["-h", "--help"]})
# def stats():
#     """
#     Statistical analysis and testing utilities
#
#     \b
#     Commands:
#       recommend     Get recommended statistical tests for your data
#       describe      Compute descriptive statistics
#       save          Save statistical results to bundle
#       load          Load statistical results from bundle
#
#     \b
#     Examples:
#       scitex stats recommend --n-groups 2 --design between
#       scitex stats describe data.csv
#       scitex stats save results.json --output analysis.stats
#     """
#     pass
#
#
# @stats.command()
# @click.option(
#     "--n-groups", "-n", type=int, required=True, help="Number of groups to compare"
# )
# @click.option(
#     "--sample-sizes",
#     "-s",
#     multiple=True,
#     type=int,
#     help="Sample size for each group (can specify multiple times)",
# )
# @click.option(
#     "--outcome-type",
#     "-o",
#     type=click.Choice(["continuous", "binary", "ordinal", "count", "time_to_event"]),
#     default="continuous",
#     help="Type of outcome variable (default: continuous)",
# )
# @click.option(
#     "--design",
#     "-d",
#     type=click.Choice(["between", "within", "mixed"]),
#     default="between",
#     help="Study design (default: between)",
# )
# @click.option("--paired", is_flag=True, help="Whether measurements are paired")
# @click.option("--has-control", is_flag=True, help="Whether there is a control group")
# @click.option("--n-factors", type=int, default=1, help="Number of factors (default: 1)")
# @click.option(
#     "--top-k", "-k", type=int, default=3, help="Number of recommendations (default: 3)"
# )
# @click.option("--json", "as_json", is_flag=True, help="Output as JSON")
# def recommend(
#     n_groups,
#     sample_sizes,
#     outcome_type,
#     design,
#     paired,
#     has_control,
#     n_factors,
#     top_k,
#     as_json,
# ):
#     """
#     Get recommended statistical tests for your experimental design
#
#     \b
#     Examples:
#       # Two-group comparison
#       scitex stats recommend --n-groups 2 --sample-sizes 30 --sample-sizes 32
#
#       # Three-group ANOVA
#       scitex stats recommend --n-groups 3 --design between
#
#       # Paired t-test scenario
#       scitex stats recommend --n-groups 2 --paired --design within
#
#       # Binary outcome (chi-square)
#       scitex stats recommend --n-groups 2 --outcome-type binary
#     """
#     try:
#         from scitex.stats import StatContext, recommend_tests
#
#         # Build context
#         ctx = StatContext(
#             n_groups=n_groups,
#             sample_sizes=list(sample_sizes) if sample_sizes else [30] * n_groups,
#             outcome_type=outcome_type,
#             design=design,
#             paired=paired,
#             has_control_group=has_control,
#             n_factors=n_factors,
#         )
#
#         tests = recommend_tests(ctx, top_k=top_k)
#
#         if as_json:
#             import json
#
#             output = {
#                 "context": {
#                     "n_groups": n_groups,
#                     "sample_sizes": list(sample_sizes)
#                     if sample_sizes
#                     else [30] * n_groups,
#                     "outcome_type": outcome_type,
#                     "design": design,
#                     "paired": paired,
#                     "has_control_group": has_control,
#                     "n_factors": n_factors,
#                 },
#                 "recommended_tests": tests,
#             }
#             click.echo(json.dumps(output, indent=2))
#         else:
#             click.secho("Recommended Statistical Tests", fg="cyan", bold=True)
#             click.echo("=" * 40)
#             click.echo("\nContext:")
#             click.echo(f"  Groups: {n_groups}")
#             click.echo(f"  Design: {design}")
#             click.echo(f"  Outcome: {outcome_type}")
#             click.echo(f"  Paired: {paired}")
#             click.echo(f"\nTop {top_k} Recommendations:")
#             for i, test in enumerate(tests, 1):
#                 click.secho(f"  {i}. {test}", fg="green")
#
#     except Exception as e:
#         click.secho(f"Error: {e}", fg="red", err=True)
#         sys.exit(1)
#
#
# @stats.command()
# @click.argument("data_path", type=click.Path(exists=True))
# @click.option("--column", "-c", multiple=True, help="Specific column(s) to describe")
# @click.option("--json", "as_json", is_flag=True, help="Output as JSON")
# def describe(data_path, column, as_json):
#     """
#     Compute descriptive statistics for data
#
#     \b
#     Examples:
#       scitex stats describe data.csv
#       scitex stats describe data.csv --column age --column score
#       scitex stats describe data.csv --json
#     """
#     try:
#         import pandas as pd
#
#         from scitex.stats import describe as describe_data
#
#         # Load data
#         path = Path(data_path)
#         if path.suffix == ".csv":
#             df = pd.read_csv(path)
#         elif path.suffix in (".xls", ".xlsx"):
#             df = pd.read_excel(path)
#         elif path.suffix == ".json":
#             df = pd.read_json(path)
#         else:
#             click.secho(f"Unsupported file format: {path.suffix}", fg="red", err=True)
#             sys.exit(1)
#
#         # Filter columns if specified
#         if column:
#             df = df[list(column)]
#
#         # Get descriptive stats
#         result = describe_data(df)
#
#         if as_json:
#             import json
#
#             # Convert to JSON-serializable format
#             if hasattr(result, "to_dict"):
#                 click.echo(json.dumps(result.to_dict(), indent=2, default=str))
#             else:
#                 click.echo(json.dumps(result, indent=2, default=str))
#         else:
#             click.secho(f"Descriptive Statistics: {path.name}", fg="cyan", bold=True)
#             click.echo("=" * 50)
#             click.echo(result)
#
#     except ImportError:
#         click.secho(
#             "Error: pandas required. Install: pip install pandas", fg="red", err=True
#         )
#         sys.exit(1)
#     except Exception as e:
#         click.secho(f"Error: {e}", fg="red", err=True)
#         sys.exit(1)
#
#
# @stats.command()
# @click.argument("input_path", type=click.Path(exists=True))
# @click.option(
#     "--output",
#     "-o",
#     type=click.Path(),
#     required=True,
#     help="Output bundle path (.stats)",
# )
# @click.option("--as-zip", is_flag=True, help="Save as ZIP archive")
# def save(input_path, output, as_zip):
#     """
#     Save statistical results to a SciTeX bundle
#
#     \b
#     Examples:
#       scitex stats save results.json --output analysis.stats
#       scitex stats save comparisons.json --output analysis.stats --as-zip
#     """
#     try:
#         import json
#
#         from scitex.stats import save_stats
#
#         # Load input
#         with open(input_path) as f:
#             data = json.load(f)
#
#         # Handle different input formats
#         if isinstance(data, list):
#             comparisons = data
#         elif isinstance(data, dict) and "comparisons" in data:
#             comparisons = data["comparisons"]
#         else:
#             comparisons = [data]
#
#         # Save bundle
#         result_path = save_stats(comparisons, output, as_zip=as_zip)
#         click.secho(f"Stats bundle saved: {result_path}", fg="green")
#
#     except Exception as e:
#         click.secho(f"Error: {e}", fg="red", err=True)
#         sys.exit(1)
#
#
# @stats.command()
# @click.argument("bundle_path", type=click.Path(exists=True))
# @click.option("--json", "as_json", is_flag=True, help="Output as JSON")
# def load(bundle_path, as_json):
#     """
#     Load statistical results from a SciTeX bundle
#
#     \b
#     Examples:
#       scitex stats load analysis.stats
#       scitex stats load analysis.stats --json
#     """
#     try:
#         from scitex.stats import load_stats
#
#         data = load_stats(bundle_path)
#
#         if as_json:
#             import json
#
#             click.echo(json.dumps(data, indent=2, default=str))
#         else:
#             click.secho(f"Statistics Bundle: {bundle_path}", fg="cyan", bold=True)
#             click.echo("=" * 50)
#
#             comparisons = data.get("comparisons", [])
#             click.echo(f"\nComparisons ({len(comparisons)}):")
#             for comp in comparisons:
#                 name = comp.get("name", "unnamed")
#                 method = comp.get("method", "unknown")
#                 p_val = comp.get("p_value", "N/A")
#                 formatted = comp.get("formatted", "")
#                 click.echo(f"  - {name}: {method}, p={p_val} {formatted}")
#
#     except Exception as e:
#         click.secho(f"Error: {e}", fg="red", err=True)
#         sys.exit(1)
#
#
# @stats.command()
# def tests():
#     """
#     List available statistical tests
#
#     \b
#     Example:
#       scitex stats tests
#     """
#     try:
#         from scitex.stats import TEST_RULES
#
#         click.secho("Available Statistical Tests", fg="cyan", bold=True)
#         click.echo("=" * 50)
#
#         # Group by category
#         categories = {}
#         for rule in TEST_RULES:
#             cat = getattr(rule, "category", "other")
#             if cat not in categories:
#                 categories[cat] = []
#             categories[cat].append(rule.name)
#
#         for cat, tests_list in sorted(categories.items()):
#             click.secho(f"\n{cat.title()}:", fg="yellow")
#             for test in sorted(tests_list):
#                 click.echo(f"  - {test}")
#
#     except Exception as e:
#         click.secho(f"Error: {e}", fg="red", err=True)
#         sys.exit(1)
#
#
# if __name__ == "__main__":
#     stats()

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/scitex-code/src/scitex/cli/stats.py
# --------------------------------------------------------------------------------
