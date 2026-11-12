#!/usr/bin/env python3
"""
SciTeX CLI - Resource Commands (System Monitoring).

Provides system resource monitoring and specifications.
"""

import copy
import csv
import json
import sys

import click
from scitex_dev.ecosystem import CliHelp, Example, SpecCommand, SpecGroup


@click.group(
    cls=SpecGroup,
    help_spec=CliHelp(
        summary="Read system specifications and measured resource usage.",
        examples=(
            Example("{prog} show-specs --json", "Read system specifications."),
            Example("{prog} show-usage --json", "Read a measured resource sample."),
            Example("{prog} monitor --count 2", "Display two measured samples."),
        ),
    ),
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
def resource(ctx, help_recursive, as_json):
    """Display resource commands or recursively inspect their help."""
    if help_recursive:
        _print_help_recursive(ctx)
        ctx.exit(0)
    elif ctx.invoked_subcommand is None:
        if as_json:
            from . import group_to_json

            group_to_json(ctx, resource)
        else:
            click.echo(ctx.get_help())


def _print_help_recursive(ctx):
    """Print help for all commands recursively."""
    click.secho(f"━━━ {ctx.command_path} ━━━", fg="cyan", bold=True)
    click.echo(resource.get_help(ctx))
    for name in sorted(resource.list_commands(ctx) or []):
        cmd = resource.get_command(ctx, name)
        if cmd is None or cmd.hidden:
            continue
        click.echo()
        click.secho(f"━━━ {ctx.command_path} {name} ━━━", fg="cyan", bold=True)
        with click.Context(cmd, info_name=name, parent=ctx) as sub_ctx:
            click.echo(cmd.get_help(sub_ctx))


@resource.command(
    "show-specs",
    cls=SpecCommand,
    help_spec=CliHelp(
        summary="Show system specifications from the installed resource provider.",
        examples=(
            Example("{prog} --json", "Read all specification categories as JSON."),
            Example(
                "{prog} --category cpu --category memory", "Read selected categories."
            ),
        ),
    ),
)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.option(
    "--category",
    "-c",
    multiple=True,
    type=click.Choice(["cpu", "memory", "disk", "network", "gpu", "os", "python"]),
    help="Specific category to show",
)
def specs(as_json, category):
    """Read system specifications from the installed provider."""
    try:
        from scitex.resource import get_specs

        specs_data = get_specs()

        # Filter categories if specified
        if category:
            category_map = {
                "cpu": "_cpu_info",
                "memory": "_memory_info",
                "disk": "_disk_info",
                "network": "_network_info",
                "gpu": "_supple_nvidia_info",
                "os": "_supple_os_info",
                "python": "_supple_python_info",
            }
            filtered = {}
            for cat in category:
                key = category_map.get(cat, cat)
                if key in specs_data:
                    filtered[key] = specs_data[key]
                elif cat in specs_data:
                    filtered[cat] = specs_data[cat]
            specs_data = filtered

        if as_json:
            import json

            click.echo(json.dumps(specs_data, indent=2, default=str))
        else:
            click.secho("System Specifications", fg="cyan", bold=True)
            click.echo("=" * 50)

            for section, data in specs_data.items():
                section_name = (
                    section.replace("_info", "").replace("_supple_", "").upper()
                )
                click.secho(f"\n{section_name}:", fg="yellow")
                if isinstance(data, dict):
                    for key, value in data.items():
                        click.echo(f"  {key}: {value}")
                else:
                    click.echo(f"  {data}")

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


def _read_processor_usage():
    """Read the provider's single-row DataFrame without inventing measurements."""
    from scitex.resource import get_processor_usages

    frame = get_processor_usages()
    if len(frame) != 1:
        raise ValueError("Expected one resource sample from get_processor_usages")
    samples = json.loads(frame.to_json(orient="records", date_format="iso"))
    return frame, samples


def _format_measurement(value):
    return "N/A" if value is None else f"{value:.1f}"


@resource.command(
    "show-usage",
    cls=SpecCommand,
    help_spec=CliHelp(
        summary="Show measured CPU/GPU percentages and RAM/VRAM usage in GiB.",
        examples=(
            Example("{prog}", "Display the current resource sample with its units."),
            Example("{prog} --json", "Return structured samples in a Result envelope."),
        ),
    ),
)
@click.option(
    "--json", "as_json", is_flag=True, help="Output a structured Result envelope"
)
def usage(as_json):
    """Display measured resource samples with their original units."""
    try:
        frame, samples = _read_processor_usage()
        if as_json:
            from scitex_dev import Result

            click.echo(Result(success=True, data={"samples": samples}).to_json())
        else:
            click.secho("Resource Usage", fg="cyan", bold=True)
            click.echo(frame.to_string(index=False))
    except Exception as error:
        if as_json:
            from scitex_dev import Result

            click.echo(Result(success=False, error=str(error)).to_json())
        else:
            click.secho(f"Error: {error}", fg="red", err=True)
        sys.exit(1)


@resource.command(
    cls=SpecCommand,
    help_spec=CliHelp(
        summary="Monitor CPU/GPU percentages and RAM/VRAM usage in GiB.",
        description=(
            "Omit --count to continue until interrupted. Counts and intervals must be positive.",
        ),
        examples=(
            Example("{prog} --count 2", "Display two samples and stop."),
            Example(
                "{prog} --count 10 --interval 1 --log measurements.csv",
                "Write ten samples with provider units to CSV.",
            ),
        ),
    ),
)
@click.option(
    "--interval",
    "-i",
    type=click.FloatRange(min=0, min_open=True),
    default=2.0,
    help="Update interval in seconds (default: 2.0)",
)
@click.option(
    "--count",
    "-n",
    type=click.IntRange(min=1),
    help="Number of updates (default: continuous)",
)
@click.option("--log", "-l", type=click.Path(), help="Log to file")
def monitor(interval, count, log):
    """Display resource samples and optionally write their measurements to CSV."""
    try:
        import time

        click.echo(f"Monitoring resources (interval: {interval}s)")
        click.echo("Press Ctrl+C to stop")
        click.echo()

        log_file = None
        writer = None
        if log:
            log_file = open(log, "w", newline="", encoding="utf-8")

        iteration = 0
        try:
            while True:
                if count and iteration >= count:
                    break

                _, samples = _read_processor_usage()
                sample = samples[0]

                click.echo(
                    f"[{sample['Timestamp']}] CPU: {_format_measurement(sample['CPU [%]'])}%  "
                    f"RAM: {_format_measurement(sample['RAM [GiB]'])} GiB  "
                    f"GPU: {_format_measurement(sample['GPU [%]'])}%  "
                    f"VRAM: {_format_measurement(sample['VRAM [GiB]'])} GiB"
                )

                if log_file:
                    if writer is None:
                        writer = csv.DictWriter(log_file, fieldnames=list(sample))
                        writer.writeheader()
                    writer.writerow(sample)
                    log_file.flush()

                iteration += 1
                if count is None or iteration < count:
                    time.sleep(interval)

        except KeyboardInterrupt:
            click.echo("\nMonitoring stopped")
        finally:
            if log_file:
                log_file.close()
                click.echo(f"Log saved: {log}")

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


# Keep older explicit invocations while advertising the canonical read verbs.
for _legacy_name, _canonical in (("specs", specs), ("usage", usage)):
    _alias = copy.copy(_canonical)
    _alias.name = _legacy_name
    _alias.hidden = True
    resource.add_command(_alias)


if __name__ == "__main__":
    resource()
