#!/usr/bin/env python3
"""
SciTeX CLI - Template Commands (Project Scaffolding)

Provides project template cloning and management.
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
def template(ctx, help_recursive, as_json):
    """
    Project template scaffolding

    \b
    Project Templates (clone):
      research      - Full scientific workflow structure
      pip-project   - Pip-installable Python package
      singularity   - Container-based project
      paper         - Academic paper writing template

    \b
    Code Templates (get):
      session       - @stx.session script with CONFIG docs (priority)
      io            - stx.io save/load patterns (priority)
      config        - YAML configuration file
      session-minimal/plot/stats - Variants
      module        - Standard Python module
      all           - All templates combined

    \b
    Examples:
      scitex template get session                 # Session script template
      scitex template get io                      # I/O operations template
      scitex template get all                     # All templates
      scitex template get session -o script.py   # Save to file
    """
    if help_recursive:
        _print_help_recursive(ctx)
        ctx.exit(0)
    elif ctx.invoked_subcommand is None:
        if as_json:
            from . import group_to_json

            group_to_json(ctx, template)
        else:
            click.echo(ctx.get_help())


def _print_help_recursive(ctx):
    """Print help for all commands recursively."""
    fake_parent = click.Context(click.Group(), info_name="scitex")
    parent_ctx = click.Context(template, info_name="template", parent=fake_parent)
    click.secho("━━━ scitex template ━━━", fg="cyan", bold=True)
    click.echo(template.get_help(parent_ctx))
    for name in sorted(template.list_commands(ctx) or []):
        cmd = template.get_command(ctx, name)
        if cmd is None:
            continue
        click.echo()
        click.secho(f"━━━ scitex template {name} ━━━", fg="cyan", bold=True)
        with click.Context(cmd, info_name=name, parent=parent_ctx) as sub_ctx:
            click.echo(cmd.get_help(sub_ctx))


@template.command(name="list")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def list_templates(as_json):
    """
    List available project templates

    \b
    Example:
      scitex template list
      scitex template list --json
    """
    try:
        from scitex.template import get_available_templates_info

        templates = get_available_templates_info()

        if as_json:
            from scitex_dev import Result

            click.echo(Result(success=True, data=templates).to_json())
        else:
            click.secho("Available SciTeX Templates", fg="cyan", bold=True)
            click.echo("=" * 60)

            for tmpl in templates:
                click.echo()
                click.secho(f"{tmpl['name']} ({tmpl['id']})", fg="green", bold=True)
                click.echo(f"  {tmpl['description']}")
                click.echo(f"  Use case: {tmpl['use_case']}")
                click.echo(f"  GitHub: {tmpl['github_url']}")
                if tmpl.get("features"):
                    click.echo("  Features:")
                    for feature in tmpl["features"][:3]:  # Show first 3
                        click.echo(f"    - {feature}")

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@template.command()
@click.argument(
    "template_type",
    type=click.Choice(["research", "minimal", "pip-project", "singularity", "paper"]),
)
@click.argument("destination", type=click.Path())
@click.option(
    "--git-strategy",
    "-g",
    type=click.Choice(["child", "parent", "origin", "none"]),
    default="child",
    help="Git initialization strategy (default: child)",
)
@click.option("--branch", "-b", help="Specific branch to clone")
@click.option("--tag", "-t", help="Specific tag/release to clone")
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
@click.option(
    "--dry-run", is_flag=True, help="Show what would be done without making changes."
)
def clone(template_type, destination, git_strategy, branch, tag, as_json, dry_run):
    """
    Clone a project template

    \b
    Template Types:
      research    - Full scientific workflow (scripts, data, docs, results)
      minimal     - Minimal SciTeX structure (writer, scholar, visualizer)
      pip-project - Python package (src, tests, docs, CI/CD)
      singularity - Container-based (definition files, build scripts)
      paper       - Academic paper (LaTeX, BibTeX, figures)

    \b
    Git Strategies:
      child  - Create isolated git in project directory (default)
      parent - Use parent git repository
      origin - Preserve template's original git history
      none   - Disable git initialization

    \b
    Examples:
      scitex template clone research ./my-research
      scitex template clone minimal ./my-project
      scitex template clone pip-project ./my-package --git-strategy parent
      scitex template clone paper ./manuscript --branch develop
    """
    # Validate mutual exclusivity
    if branch and tag:
        click.echo("Error: Cannot specify both --branch and --tag", err=True)
        sys.exit(1)

    # Convert git_strategy 'none' to None
    if git_strategy == "none":
        git_strategy = None

    clone_kwargs = dict(
        template_id=template_type,
        project_dir=destination,
        git_strategy=git_strategy,
        branch=branch,
        tag=tag,
    )

    if dry_run:
        click.echo(f"[dry-run] Would clone '{template_type}' to {destination}")
        click.echo(f"[dry-run] git_strategy={git_strategy}, branch={branch}, tag={tag}")
        return

    if as_json:
        from scitex_dev import wrap_as_cli

        from scitex.template import clone_template as _clone_template

        wrap_as_cli(_clone_template, as_json=True, **clone_kwargs)
        return

    try:
        from scitex.template import clone_template as _clone_template

        click.echo(f"Cloning {template_type} template to {destination}...")

        result = _clone_template(**clone_kwargs)

        if result:
            dest_path = Path(destination).absolute()
            click.secho("Successfully cloned template!", fg="green")
            click.echo()
            click.echo(f"Location: {dest_path}")
            click.echo()
            click.echo("Next steps:")
            click.echo(f"  cd {destination}")

            if template_type == "research":
                click.echo("  # Start your research project")
                click.echo("  # Edit scripts/, data/, docs/")
            elif template_type == "pip-project":
                click.echo("  # Develop your package")
                click.echo("  pip install -e .")
                click.echo("  pytest")
            elif template_type == "singularity":
                click.echo("  # Build your container")
                click.echo("  singularity build container.sif Singularity.def")
            elif template_type == "paper":
                click.echo("  # Write your paper")
                click.echo("  scitex writer compile manuscript")
        else:
            click.secho("Failed to clone template", fg="red", err=True)
            sys.exit(1)

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@template.command()
@click.argument(
    "template_id",
    type=click.Choice(
        [
            # Core templates (priority 1-3)
            "session",
            "io",
            "config",
            # Session variants
            "session-minimal",
            "session-plot",
            "session-stats",
            # Module template
            "module",
            # Module usage templates
            "plt",
            "stats",
            "scholar",
            "audio",
            "capture",
            "diagram",
            "canvas",
            "writer",
            # All templates
            "all",
        ]
    ),
)
@click.option(
    "--output", "-o", type=click.Path(), help="Save to file instead of printing"
)
@click.option("--docstring", "-d", help="Custom docstring for the template")
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
def get(template_id, output, docstring, as_json):
    """
    Get a code template (print or save to file)

    \b
    Core Templates (priority 1-3):
      session         - Full @stx.session script with CONFIG docs
      io              - stx.io.save/load patterns (30+ formats)
      config          - YAML configuration file

    \b
    Session Variants:
      session-minimal - Minimal session script
      session-plot    - Plotting-focused session script
      session-stats   - Statistical analysis script
      module          - Standard Python module

    \b
    Module Usage Templates:
      plt             - stx.plt plotting usage
      stats           - stx.stats statistical analysis
      scholar         - stx.scholar literature management
      audio           - stx.audio text-to-speech
      capture         - stx.capture screenshots
      diagram         - stx.diagram Mermaid/Graphviz
      canvas          - stx.canvas figure composition
      writer          - stx.writer LaTeX compilation

    \b
    All:
      all             - All templates combined

    \b
    Examples:
      scitex template get session              # Print to stdout
      scitex template get io                   # I/O operations template
      scitex template get all                  # All templates
      scitex template get session -o script.py # Save to file
    """
    if as_json:
        from scitex_dev import wrap_as_cli

        def _get():
            if template_id == "all":
                from scitex.template import get_all_templates

                return get_all_templates()
            else:
                from scitex.template import get_code_template

                return get_code_template(
                    template_id,
                    filepath=output if output else None,
                    docstring=docstring,
                )

        wrap_as_cli(_get, as_json=True)
        return

    try:
        if template_id == "all":
            from scitex.template import get_all_templates

            content = get_all_templates()
        else:
            from scitex.template import get_code_template

            filepath = output if output else None
            content = get_code_template(
                template_id, filepath=filepath, docstring=docstring
            )

        if output:
            # Save to file
            out_path = Path(output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(content)
            click.secho(f"Template saved: {out_path}", fg="green")
        else:
            # Print to stdout
            click.echo(content)

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@template.command()
@click.argument("template_id")
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
def info(template_id, as_json):
    """
    Show detailed information about a template

    \b
    Example:
      scitex template info research
      scitex template info pip-project
    """
    if as_json:
        from scitex_dev import wrap_as_cli

        def _info():
            from scitex.template import get_available_templates_info

            templates = get_available_templates_info()
            for tmpl in templates:
                if (
                    tmpl["id"] == template_id
                    or tmpl["name"].lower() == template_id.lower()
                ):
                    return tmpl
            raise LookupError(f"Template '{template_id}' not found")

        wrap_as_cli(_info, as_json=True)
        return

    try:
        from scitex.template import get_available_templates_info

        templates = get_available_templates_info()

        # Find matching template
        template_info = None
        for tmpl in templates:
            if tmpl["id"] == template_id or tmpl["name"].lower() == template_id.lower():
                template_info = tmpl
                break

        if not template_info:
            click.secho(f"Template '{template_id}' not found", fg="red", err=True)
            click.echo("Available templates:")
            for tmpl in templates:
                click.echo(f"  - {tmpl['id']}")
            sys.exit(1)

        click.secho(f"Template: {template_info['name']}", fg="cyan", bold=True)
        click.echo("=" * 50)
        click.echo()
        click.echo(f"ID: {template_info['id']}")
        click.echo(f"Description: {template_info['description']}")
        click.echo(f"Use case: {template_info['use_case']}")
        click.echo(f"GitHub: {template_info['github_url']}")
        click.echo()
        click.secho("Features:", fg="yellow")
        for feature in template_info.get("features", []):
            click.echo(f"  - {feature}")
        click.echo()
        click.echo("Clone with:")
        click.secho(
            f"  scitex template clone {template_info['id']} ./my-project", fg="green"
        )

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


if __name__ == "__main__":
    template()
