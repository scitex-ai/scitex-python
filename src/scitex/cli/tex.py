#!/usr/bin/env python3
"""
SciTeX CLI - TeX Commands (LaTeX Operations)

Provides LaTeX compilation and preview utilities.
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
def tex(ctx, help_recursive, as_json):
    """
    LaTeX compilation and utilities

    \b
    Commands:
      compile    Compile LaTeX document to PDF
      preview    Preview LaTeX document
      to-vec     Convert to vector format (SVG/PDF)

    \b
    Examples:
      scitex tex compile paper.tex
      scitex tex preview paper.tex
      scitex tex to-vec figure.tex --format svg
    """
    if help_recursive:
        _print_help_recursive(ctx)
        ctx.exit(0)
    elif ctx.invoked_subcommand is None:
        if as_json:
            from . import group_to_json

            group_to_json(ctx, tex)
        else:
            click.echo(ctx.get_help())


def _print_help_recursive(ctx):
    """Print help for all commands recursively."""
    fake_parent = click.Context(click.Group(), info_name="scitex")
    parent_ctx = click.Context(tex, info_name="tex", parent=fake_parent)
    click.secho("━━━ scitex tex ━━━", fg="cyan", bold=True)
    click.echo(tex.get_help(parent_ctx))
    for name in sorted(tex.list_commands(ctx) or []):
        cmd = tex.get_command(ctx, name)
        if cmd is None:
            continue
        click.echo()
        click.secho(f"━━━ scitex tex {name} ━━━", fg="cyan", bold=True)
        with click.Context(cmd, info_name=name, parent=parent_ctx) as sub_ctx:
            click.echo(cmd.get_help(sub_ctx))


@tex.command()
@click.argument("tex_file", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output PDF path")
@click.option(
    "--engine",
    "-e",
    type=click.Choice(["pdflatex", "xelatex", "lualatex"]),
    default="pdflatex",
    help="LaTeX engine (default: pdflatex)",
)
@click.option(
    "--clean", "-c", is_flag=True, help="Clean auxiliary files after compilation"
)
@click.option(
    "--timeout",
    type=int,
    default=300,
    help="Compilation timeout in seconds (default: 300)",
)
@click.option("--verbose", "-v", is_flag=True, help="Show detailed compilation output")
def compile(tex_file, output, engine, clean, timeout, verbose):
    """
    Compile LaTeX document to PDF

    \b
    Examples:
      scitex tex compile paper.tex
      scitex tex compile paper.tex --output ./output/paper.pdf
      scitex tex compile paper.tex --engine xelatex
      scitex tex compile paper.tex --clean --verbose
    """
    try:
        from scitex.tex import compile_tex

        path = Path(tex_file)
        click.echo(f"Compiling: {path.name}")

        result = compile_tex(
            tex_path=path,
            output_path=output,
            engine=engine,
            timeout=timeout,
        )

        if result.success:
            click.secho("Compilation successful!", fg="green")
            click.echo(f"PDF: {result.output_pdf}")

            if clean:
                # Clean auxiliary files
                aux_extensions = [
                    ".aux",
                    ".log",
                    ".out",
                    ".toc",
                    ".bbl",
                    ".blg",
                    ".fls",
                    ".fdb_latexmk",
                ]
                for ext in aux_extensions:
                    aux_file = path.with_suffix(ext)
                    if aux_file.exists():
                        aux_file.unlink()
                click.echo("Auxiliary files cleaned")
        else:
            click.secho(
                f"Compilation failed (exit code {result.exit_code})", fg="red", err=True
            )
            if result.errors and verbose:
                click.echo("\nErrors:")
                for error in result.errors[:10]:
                    click.echo(f"  {error}")
            sys.exit(result.exit_code)

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@tex.command()
@click.argument("tex_file", type=click.Path(exists=True))
@click.option("--viewer", "-v", help="PDF viewer to use (default: system default)")
def preview(tex_file, viewer):
    """
    Preview LaTeX document (compile and open)

    \b
    Examples:
      scitex tex preview paper.tex
      scitex tex preview paper.tex --viewer evince
    """
    try:
        from scitex.tex import preview as tex_preview

        path = Path(tex_file)
        click.echo(f"Previewing: {path.name}")

        tex_preview(path, viewer=viewer)

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@tex.command("to-vec")
@click.argument("tex_file", type=click.Path(exists=True))
@click.option(
    "--format",
    "-f",
    "fmt",
    type=click.Choice(["svg", "pdf", "eps"]),
    default="svg",
    help="Output format (default: svg)",
)
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def to_vec(tex_file, fmt, output):
    """
    Convert LaTeX to vector format

    \b
    Useful for embedding equations and figures in other documents.

    \b
    Examples:
      scitex tex to-vec equation.tex
      scitex tex to-vec equation.tex --format pdf
      scitex tex to-vec figure.tex --output ./vectors/fig.svg
    """
    try:
        from scitex.tex import to_vec as convert_to_vec

        path = Path(tex_file)
        click.echo(f"Converting: {path.name} -> {fmt.upper()}")

        if output:
            output_path = Path(output)
        else:
            output_path = path.with_suffix(f".{fmt}")

        result = convert_to_vec(path, output_path, format=fmt)

        if result:
            click.secho("Conversion successful!", fg="green")
            click.echo(f"Output: {result}")
        else:
            click.secho("Conversion failed", fg="red", err=True)
            sys.exit(1)

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@tex.command()
@click.argument("tex_file", type=click.Path(exists=True))
def check(tex_file):
    """
    Check LaTeX document for common issues

    \b
    Checks:
      - Missing packages
      - Undefined references
      - Overfull/underfull boxes
      - Citation warnings

    \b
    Example:
      scitex tex check paper.tex
    """
    try:
        import subprocess
        from pathlib import Path

        path = Path(tex_file)
        click.echo(f"Checking: {path.name}")

        # Run LaTeX in draft mode to check
        result = subprocess.run(
            ["pdflatex", "-draftmode", "-interaction=nonstopmode", str(path)],
            capture_output=True,
            text=True,
            cwd=path.parent,
            timeout=60,
        )

        # Parse log for issues
        log_file = path.with_suffix(".log")
        issues = {
            "warnings": [],
            "errors": [],
            "overfull": [],
            "undefined": [],
        }

        if log_file.exists():
            with open(log_file) as f:
                for line in f:
                    if "Warning:" in line:
                        issues["warnings"].append(line.strip())
                    elif "Error:" in line or "!" in line[:2]:
                        issues["errors"].append(line.strip())
                    elif "Overfull" in line or "Underfull" in line:
                        issues["overfull"].append(line.strip())
                    elif "undefined" in line.lower():
                        issues["undefined"].append(line.strip())

        # Report
        total_issues = sum(len(v) for v in issues.values())

        if total_issues == 0:
            click.secho("No issues found!", fg="green")
        else:
            click.secho(f"Found {total_issues} issue(s):", fg="yellow")

            if issues["errors"]:
                click.secho(f"\nErrors ({len(issues['errors'])}):", fg="red")
                for err in issues["errors"][:5]:
                    click.echo(f"  {err}")

            if issues["undefined"]:
                click.secho(
                    f"\nUndefined References ({len(issues['undefined'])}):", fg="yellow"
                )
                for ref in issues["undefined"][:5]:
                    click.echo(f"  {ref}")

            if issues["overfull"]:
                click.secho(
                    f"\nOverfull/Underfull Boxes ({len(issues['overfull'])}):",
                    fg="yellow",
                )
                for box in issues["overfull"][:5]:
                    click.echo(f"  {box}")

            if issues["warnings"]:
                click.secho(f"\nWarnings ({len(issues['warnings'])}):", fg="yellow")
                for warn in issues["warnings"][:5]:
                    click.echo(f"  {warn}")

    except subprocess.TimeoutExpired:
        click.secho("Check timed out", fg="yellow")
    except FileNotFoundError:
        click.secho("Error: pdflatex not found. Install TeX Live.", fg="red", err=True)
        sys.exit(1)
    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


if __name__ == "__main__":
    tex()
