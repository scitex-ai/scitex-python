#!/usr/bin/env python3
"""
SciTeX CLI - Stats Commands (Statistical Analysis)

Provides statistical testing, test recommendation, and result management.
"""

import sys
from pathlib import Path

import click


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.option("--help-recursive", is_flag=True, help="Show help for all subcommands")
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
@click.pass_context
def stats(ctx, help_recursive, as_json):
    """
    Statistical analysis and testing utilities

    \b
    Commands:
      recommend     Get recommended statistical tests for your data
      describe      Compute descriptive statistics
      save          Save statistical results to bundle
      load          Load statistical results from bundle

    \b
    Examples:
      scitex stats recommend --n-groups 2 --design between
      scitex stats describe data.csv
      scitex stats save results.json --output analysis.stats
    """
    if help_recursive:
        _print_help_recursive(ctx)
        ctx.exit(0)
    elif ctx.invoked_subcommand is None:
        if as_json:
            from . import group_to_json

            group_to_json(ctx, stats)
        else:
            click.echo(ctx.get_help())


def _print_help_recursive(ctx):
    """Print help for all commands recursively."""
    fake_parent = click.Context(click.Group(), info_name="scitex")
    parent_ctx = click.Context(stats, info_name="stats", parent=fake_parent)
    click.secho("━━━ scitex stats ━━━", fg="cyan", bold=True)
    click.echo(stats.get_help(parent_ctx))
    for name in sorted(stats.list_commands(ctx) or []):
        cmd = stats.get_command(ctx, name)
        if cmd is None:
            continue
        click.echo()
        click.secho(f"━━━ scitex stats {name} ━━━", fg="cyan", bold=True)
        with click.Context(cmd, info_name=name, parent=parent_ctx) as sub_ctx:
            click.echo(cmd.get_help(sub_ctx))


@stats.command()
@click.option(
    "--n-groups", "-n", type=int, required=True, help="Number of groups to compare"
)
@click.option(
    "--sample-sizes",
    "-s",
    multiple=True,
    type=int,
    help="Sample size for each group (can specify multiple times)",
)
@click.option(
    "--outcome-type",
    "-o",
    type=click.Choice(["continuous", "binary", "ordinal", "count", "time_to_event"]),
    default="continuous",
    help="Type of outcome variable (default: continuous)",
)
@click.option(
    "--design",
    "-d",
    type=click.Choice(["between", "within", "mixed"]),
    default="between",
    help="Study design (default: between)",
)
@click.option("--paired", is_flag=True, help="Whether measurements are paired")
@click.option("--has-control", is_flag=True, help="Whether there is a control group")
@click.option("--n-factors", type=int, default=1, help="Number of factors (default: 1)")
@click.option(
    "--top-k", "-k", type=int, default=3, help="Number of recommendations (default: 3)"
)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def recommend(
    n_groups,
    sample_sizes,
    outcome_type,
    design,
    paired,
    has_control,
    n_factors,
    top_k,
    as_json,
):
    """
    Get recommended statistical tests for your experimental design

    \b
    Examples:
      # Two-group comparison
      scitex stats recommend --n-groups 2 --sample-sizes 30 --sample-sizes 32

      # Three-group ANOVA
      scitex stats recommend --n-groups 3 --design between

      # Paired t-test scenario
      scitex stats recommend --n-groups 2 --paired --design within

      # Binary outcome (chi-square)
      scitex stats recommend --n-groups 2 --outcome-type binary
    """
    try:
        from scitex.stats import StatContext, recommend_tests

        # Build context
        ctx = StatContext(
            n_groups=n_groups,
            sample_sizes=list(sample_sizes) if sample_sizes else [30] * n_groups,
            outcome_type=outcome_type,
            design=design,
            paired=paired,
            has_control_group=has_control,
            n_factors=n_factors,
        )

        tests = recommend_tests(ctx, top_k=top_k)

        if as_json:
            from scitex_dev import Result

            output = {
                "context": {
                    "n_groups": n_groups,
                    "sample_sizes": (
                        list(sample_sizes) if sample_sizes else [30] * n_groups
                    ),
                    "outcome_type": outcome_type,
                    "design": design,
                    "paired": paired,
                    "has_control_group": has_control,
                    "n_factors": n_factors,
                },
                "recommended_tests": tests,
            }
            click.echo(Result(success=True, data=output).to_json())
        else:
            click.secho("Recommended Statistical Tests", fg="cyan", bold=True)
            click.echo("=" * 40)
            click.echo("\nContext:")
            click.echo(f"  Groups: {n_groups}")
            click.echo(f"  Design: {design}")
            click.echo(f"  Outcome: {outcome_type}")
            click.echo(f"  Paired: {paired}")
            click.echo(f"\nTop {top_k} Recommendations:")
            for i, test in enumerate(tests, 1):
                click.secho(f"  {i}. {test}", fg="green")

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@stats.command()
@click.argument("data_path", type=click.Path(exists=True))
@click.option("--column", "-c", multiple=True, help="Specific column(s) to describe")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def describe(data_path, column, as_json):
    """
    Compute descriptive statistics for data

    \b
    Examples:
      scitex stats describe data.csv
      scitex stats describe data.csv --column age --column score
      scitex stats describe data.csv --json
    """
    try:
        import pandas as pd

        from scitex.stats import describe as describe_data

        # Load data
        path = Path(data_path)
        if path.suffix == ".csv":
            df = pd.read_csv(path)
        elif path.suffix in (".xls", ".xlsx"):
            df = pd.read_excel(path)
        elif path.suffix == ".json":
            df = pd.read_json(path)
        else:
            click.secho(f"Unsupported file format: {path.suffix}", fg="red", err=True)
            sys.exit(1)

        # Filter columns if specified
        if column:
            df = df[list(column)]

        # Get descriptive stats
        result = describe_data(df)

        if as_json:
            from scitex_dev import Result

            data = result.to_dict() if hasattr(result, "to_dict") else result
            click.echo(Result(success=True, data=data).to_json())
        else:
            click.secho(f"Descriptive Statistics: {path.name}", fg="cyan", bold=True)
            click.echo("=" * 50)
            click.echo(result)

    except ImportError:
        click.secho(
            "Error: pandas required. Install: pip install pandas", fg="red", err=True
        )
        sys.exit(1)
    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@stats.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    required=True,
    help="Output bundle path (.stats)",
)
@click.option("--as-zip", is_flag=True, help="Save as ZIP archive")
@click.option(
    "--dry-run", is_flag=True, help="Show what would be saved without writing"
)
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
def save(input_path, output, as_zip, dry_run, as_json):
    """
    Save statistical results to a SciTeX bundle

    \b
    Examples:
      scitex stats save results.json --output analysis.stats
      scitex stats save comparisons.json --output analysis.stats --as-zip
      scitex stats save results.json --output analysis.stats --dry-run
    """
    if dry_run:
        click.echo(f"[dry-run] Would save {input_path} -> {output}")
        if as_zip:
            click.echo("[dry-run] Format: ZIP archive")
        return

    try:
        import json

        from scitex.stats import save_stats

        # Load input
        with open(input_path) as f:
            data = json.load(f)

        # Handle different input formats
        if isinstance(data, list):
            comparisons = data
        elif isinstance(data, dict) and "comparisons" in data:
            comparisons = data["comparisons"]
        else:
            comparisons = [data]

        # Save bundle
        result_path = save_stats(comparisons, output, as_zip=as_zip)
        if as_json:
            from scitex_dev import Result

            click.echo(Result(success=True, data={"path": str(result_path)}).to_json())
        else:
            click.secho(f"Stats bundle saved: {result_path}", fg="green")

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@stats.command()
@click.argument("bundle_path", type=click.Path(exists=True))
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def load(bundle_path, as_json):
    """
    Load statistical results from a SciTeX bundle

    \b
    Examples:
      scitex stats load analysis.stats
      scitex stats load analysis.stats --json
    """
    try:
        from scitex.stats import load_stats

        data = load_stats(bundle_path)

        if as_json:
            from scitex_dev import Result

            click.echo(Result(success=True, data=data).to_json())
        else:
            click.secho(f"Statistics Bundle: {bundle_path}", fg="cyan", bold=True)
            click.echo("=" * 50)

            comparisons = data.get("comparisons", [])
            click.echo(f"\nComparisons ({len(comparisons)}):")
            for comp in comparisons:
                name = comp.get("name", "unnamed")
                method = comp.get("method", "unknown")
                p_val = comp.get("p_value", "N/A")
                formatted = comp.get("formatted", "")
                click.echo(f"  - {name}: {method}, p={p_val} {formatted}")

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@stats.command()
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
def tests(as_json):
    """
    List available statistical tests

    \b
    Example:
      scitex stats tests
    """
    try:
        from scitex.stats import TEST_RULES

        # Group by category
        categories = {}
        for rule in TEST_RULES:
            cat = getattr(rule, "category", "other")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(rule.name)

        if as_json:
            from scitex_dev import Result

            click.echo(Result(success=True, data=categories).to_json())
            return

        click.secho("Available Statistical Tests", fg="cyan", bold=True)
        click.echo("=" * 50)

        for cat, tests_list in sorted(categories.items()):
            click.secho(f"\n{cat.title()}:", fg="yellow")
            for test in sorted(tests_list):
                click.echo(f"  - {test}")

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@stats.command("list-python-apis")
@click.option("-v", "--verbose", count=True, help="Verbosity: -v +doc, -vv full doc")
@click.option("-d", "--max-depth", type=int, default=5, help="Max recursion depth")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def list_python_apis(ctx, verbose, max_depth, as_json):
    """List Python APIs (alias for: scitex introspect api scitex.stats)."""
    from scitex.cli.introspect import api

    ctx.invoke(
        api,
        dotted_path="scitex.stats",
        verbose=verbose,
        max_depth=max_depth,
        as_json=as_json,
    )


# Wire in sub-module commands
from scitex.cli._stats_mcp import register_mcp_commands

register_mcp_commands(stats)


if __name__ == "__main__":
    stats()
