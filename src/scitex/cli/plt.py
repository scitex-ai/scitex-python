#!/usr/bin/env python3
# Timestamp: 2026-01-25
# File: /home/ywatanabe/proj/scitex-python/src/scitex/cli/plt.py

"""
SciTeX CLI - Plot Commands

Thin wrapper around figrecipe CLI for reproducible matplotlib figures.
All commands delegate to figrecipe for reproducibility.
"""

import subprocess
import sys

import click


def _run_figrecipe(*args) -> int:
    """Run figrecipe CLI command."""
    cmd = [sys.executable, "-m", "figrecipe"]
    cmd.extend(args)

    result = subprocess.run(cmd)
    return result.returncode


def _check_figrecipe() -> bool:
    """Check if figrecipe is available."""
    try:
        import figrecipe  # noqa: F401

        return True
    except ImportError:
        return False


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
def plt(ctx, help_recursive, as_json):
    """
    Plot and figure management (powered by figrecipe)

    \b
    Commands:
      plot       - Create figure from YAML/JSON spec
      edit       - Launch interactive GUI editor
      compose    - Combine multiple figures
      crop       - Crop whitespace from images
      reproduce  - Reproduce figure from recipe
      validate   - Validate recipe reproducibility
      diagram    - Create diagrams (flowcharts, etc.)

    \b
    Examples:
      scitex plt plot spec.yaml -o fig.png
      scitex plt edit
      scitex plt compose a.png b.png -o combined.png
      scitex plt reproduce recipe.yaml

    \b
    Note: Wraps figrecipe CLI. Run 'figrecipe --help' for full options.
    """
    if not _check_figrecipe():
        click.secho("Error: figrecipe not installed", fg="red", err=True)
        click.echo("\nInstall with: pip install figrecipe")
        ctx.exit(1)

    if help_recursive:
        from . import print_help_recursive

        print_help_recursive(ctx, plt)
        ctx.exit(0)
    elif ctx.invoked_subcommand is None:
        if as_json:
            from . import group_to_json

            group_to_json(ctx, plt)
        else:
            click.echo(ctx.get_help())


@plt.command()
@click.argument("spec_file", type=click.Path(exists=True))
@click.option("-o", "--output", required=True, help="Output file path")
@click.option("--dpi", type=int, default=300, help="DPI for raster output")
@click.option("--no-recipe", is_flag=True, help="Don't save YAML recipe")
@click.option(
    "--dry-run", is_flag=True, help="Show what would be done without making changes"
)
def plot(spec_file, output, dpi, no_recipe, dry_run):
    """
    Create a figure from a declarative YAML/JSON spec.

    \b
    Examples:
      scitex plt plot spec.yaml -o fig.png
      scitex plt plot spec.json -o fig.pdf --dpi 600
    """
    if dry_run:
        click.echo(f"[dry-run] Would create plot from spec: {spec_file} -> {output}")
        return
    args = ["plot", spec_file, "-o", output, "--dpi", str(dpi)]
    if no_recipe:
        args.append("--no-recipe")
    sys.exit(_run_figrecipe(*args))


@plt.command()
@click.argument("recipe_file", type=click.Path(exists=True), required=False)
def edit(recipe_file):
    """
    Launch interactive GUI editor.

    \b
    Examples:
      scitex plt edit                  # Open blank editor
      scitex plt edit recipe.yaml      # Open existing recipe
    """
    args = ["edit"]
    if recipe_file:
        args.append(recipe_file)
    sys.exit(_run_figrecipe(*args))


@plt.command()
@click.argument("sources", nargs=-1, required=True, type=click.Path(exists=True))
@click.option("-o", "--output", required=True, help="Output file path")
@click.option(
    "-l",
    "--layout",
    type=click.Choice(["horizontal", "vertical", "grid"]),
    default="horizontal",
    help="Layout mode",
)
@click.option("--gap", type=float, default=5, help="Gap between panels (mm)")
@click.option("--dpi", type=int, default=300, help="DPI for output")
@click.option("--no-labels", is_flag=True, help="Don't add panel labels (A, B, C)")
@click.option("--caption", help="Figure caption")
@click.option(
    "--dry-run", is_flag=True, help="Show what would be done without making changes"
)
def compose(sources, output, layout, gap, dpi, no_labels, caption, dry_run):
    """
    Compose multiple figures into one.

    \b
    Examples:
      scitex plt compose a.png b.png -o combined.png
      scitex plt compose *.png -o fig.pdf --layout grid
      scitex plt compose a.yaml b.yaml -o fig.png --gap 10
    """
    if dry_run:
        click.echo(f"[dry-run] Would compose {len(sources)} figures -> {output}")
        return
    args = ["compose"]
    args.extend(sources)
    args.extend(
        ["-o", output, "--layout", layout, "--gap", str(gap), "--dpi", str(dpi)]
    )
    if no_labels:
        args.append("--no-labels")
    if caption:
        args.extend(["--caption", caption])
    sys.exit(_run_figrecipe(*args))


@plt.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("-o", "--output", help="Output file (default: overwrites input)")
@click.option("--margin", type=float, default=1, help="Margin to keep (mm)")
@click.option(
    "--dry-run", is_flag=True, help="Show what would be done without making changes"
)
def crop(input_file, output, margin, dry_run):
    """
    Crop whitespace from an image.

    \b
    Examples:
      scitex plt crop figure.png
      scitex plt crop figure.png -o cropped.png --margin 2
    """
    if dry_run:
        dest = output if output else input_file
        click.echo(f"[dry-run] Would crop whitespace from {input_file} -> {dest}")
        return
    args = ["crop", input_file, "--margin", str(margin)]
    if output:
        args.extend(["-o", output])
    sys.exit(_run_figrecipe(*args))


@plt.command()
@click.argument("recipe_file", type=click.Path(exists=True))
@click.option("-o", "--output", help="Output file path")
@click.option(
    "--format", "fmt", type=click.Choice(["png", "pdf", "svg"]), help="Output format"
)
@click.option("--dpi", type=int, default=300, help="DPI for raster output")
@click.option(
    "--dry-run", is_flag=True, help="Show what would be done without making changes"
)
def reproduce(recipe_file, output, fmt, dpi, dry_run):
    """
    Reproduce a figure from a YAML recipe.

    \b
    Examples:
      scitex plt reproduce recipe.yaml
      scitex plt reproduce recipe.yaml -o new_fig.pdf
    """
    if dry_run:
        click.echo(f"[dry-run] Would reproduce figure from recipe: {recipe_file}")
        return
    args = ["reproduce", recipe_file, "--dpi", str(dpi)]
    if output:
        args.extend(["-o", output])
    if fmt:
        args.extend(["--format", fmt])
    sys.exit(_run_figrecipe(*args))


@plt.command()
@click.argument("recipe_file", type=click.Path(exists=True))
@click.option("--threshold", type=float, default=100, help="MSE threshold")
def validate(recipe_file, threshold):
    """
    Validate that a recipe reproduces its original figure.

    \b
    Examples:
      scitex plt validate recipe.yaml
      scitex plt validate recipe.yaml --threshold 50
    """
    args = ["validate", recipe_file, "--threshold", str(threshold)]
    sys.exit(_run_figrecipe(*args))


@plt.command()
@click.argument("spec_file", type=click.Path(exists=True))
@click.option("-o", "--output", help="Output file path")
@click.option(
    "--format", "fmt", type=click.Choice(["mermaid", "graphviz"]), default="mermaid"
)
def diagram(spec_file, output, fmt):
    """
    Create diagrams (flowcharts, pipelines, etc.)

    \b
    Examples:
      scitex plt diagram workflow.yaml
      scitex plt diagram pipeline.yaml -o diagram.png --format graphviz
    """
    args = ["diagram", spec_file, "--format", fmt]
    if output:
        args.extend(["-o", output])
    sys.exit(_run_figrecipe(*args))


@plt.command()
@click.argument("recipe_file", type=click.Path(exists=True))
@click.option("-v", "--verbose", is_flag=True, help="Show detailed info")
def info(recipe_file, verbose):
    """
    Show information about a recipe.

    \b
    Examples:
      scitex plt info recipe.yaml
      scitex plt info recipe.yaml --verbose
    """
    args = ["info", recipe_file]
    if verbose:
        args.append("--verbose")
    sys.exit(_run_figrecipe(*args))


@plt.command()
@click.argument("recipe_file", type=click.Path(exists=True))
@click.option("-o", "--output", help="Output file for extracted data")
def extract(recipe_file, output):
    """
    Extract plotted data arrays from a recipe.

    \b
    Examples:
      scitex plt extract recipe.yaml
      scitex plt extract recipe.yaml -o data.json
    """
    args = ["extract", recipe_file]
    if output:
        args.extend(["-o", output])
    sys.exit(_run_figrecipe(*args))


@plt.command()
@click.argument("action", type=click.Choice(["list", "show", "set"]), default="list")
@click.argument("style_name", required=False)
def style(action, style_name):
    """
    Manage figure styles and presets.

    \b
    Examples:
      scitex plt style list              # List available styles
      scitex plt style show nature       # Show style details
      scitex plt style set publication   # Set default style
    """
    args = ["style", action]
    if style_name:
        args.append(style_name)
    sys.exit(_run_figrecipe(*args))


@plt.command()
@click.option("--check", is_flag=True, help="Check font availability")
def fonts(check):
    """
    List or check available fonts.

    \b
    Examples:
      scitex plt fonts
      scitex plt fonts --check
    """
    args = ["fonts"]
    if check:
        args.append("--check")
    sys.exit(_run_figrecipe(*args))


@plt.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("-o", "--output", required=True, help="Output file path")
@click.option("--format", "fmt", help="Output format (inferred from extension)")
@click.option(
    "--dry-run", is_flag=True, help="Show what would be done without making changes"
)
def convert(input_file, output, fmt, dry_run):
    """
    Convert between figure formats.

    \b
    Examples:
      scitex plt convert fig.png -o fig.pdf
      scitex plt convert fig.svg -o fig.png
    """
    if dry_run:
        import os

        in_fmt = fmt or os.path.splitext(input_file)[1].lstrip(".")
        out_fmt = os.path.splitext(output)[1].lstrip(".")
        click.echo(
            f"[dry-run] Would convert {input_file} ({in_fmt}) -> {output} ({out_fmt})"
        )
        return
    args = ["convert", input_file, "-o", output]
    if fmt:
        args.extend(["--format", fmt])
    sys.exit(_run_figrecipe(*args))


@plt.group(invoke_without_command=True)
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
@click.pass_context
def mcp(ctx, as_json):
    """
    MCP (Model Context Protocol) server operations

    \b
    Commands:
      start      - Start the MCP server
      doctor     - Check MCP server health
      list-tools - List available MCP tools
      info       - Show MCP server information
      install    - Show installation instructions

    \b
    Examples:
      scitex plt mcp start
      scitex plt mcp doctor
    """
    if ctx.invoked_subcommand is None:
        if as_json:
            from . import group_to_json

            group_to_json(ctx, mcp)
        else:
            click.echo(ctx.get_help())


@mcp.command()
@click.option("--host", default="0.0.0.0", help="Host for HTTP transport")
@click.option("--port", default=8087, type=int, help="Port for HTTP transport")
def start(host, port):
    """
    Start the MCP server

    \b
    Example:
      scitex plt mcp start
      scitex plt mcp start --port 8087
    """
    sys.exit(_run_figrecipe("mcp", "run", "--host", host, "--port", str(port)))


@mcp.command()
def doctor():
    """
    Check MCP server health

    \b
    Example:
      scitex plt mcp doctor
    """
    sys.exit(_run_figrecipe("mcp", "doctor"))


@mcp.command("list-tools")
def list_tools_mcp():
    """
    List available MCP tools

    \b
    Example:
      scitex plt mcp list-tools
    """
    sys.exit(_run_figrecipe("mcp", "list-tools"))


@mcp.command()
def info():
    """
    Show MCP server information

    \b
    Example:
      scitex plt mcp info
    """
    sys.exit(_run_figrecipe("mcp", "info"))


@mcp.command()
def install():
    """
    Show installation instructions

    \b
    Example:
      scitex plt mcp install
    """
    sys.exit(_run_figrecipe("mcp", "install"))


@plt.command("list-python-apis")
@click.option("-v", "--verbose", count=True, help="Verbosity: -v +doc, -vv full doc")
@click.option("-d", "--max-depth", type=int, default=5, help="Max recursion depth")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def list_python_apis(ctx, verbose, max_depth, as_json):
    """List Python APIs (alias for: scitex introspect api scitex.plt)."""
    from scitex.cli.introspect import api

    ctx.invoke(
        api,
        dotted_path="scitex.plt",
        verbose=verbose,
        max_depth=max_depth,
        as_json=as_json,
    )


if __name__ == "__main__":
    plt()

# EOF
