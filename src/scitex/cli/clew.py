#!/usr/bin/env python3
# Timestamp: "2026-02-01 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/cli/clew.py
"""
SciTeX CLI - Clew Commands (Hash-based verification).

Provides commands for tracking and verifying reproducibility of computations.
"""

import sys
from pathlib import Path

import click


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.option("--help-recursive", is_flag=True, help="Show help for all subcommands")
@click.pass_context
def clew(ctx, help_recursive):
    """
    Hash-based verification for reproducible science.

    \b
    Commands:
      list      List all tracked runs with verification status
      run       Verify a specific session run
      chain     Verify dependency chain for a target file
      dag       Verify multi-target DAG or all claims
      status    Show changed files (like git status)
      stats     Show database statistics

    \b
    Examples:
      scitex clew list                          # List all runs
      scitex clew run 2025Y-11M-18D-09h12m03s   # Verify specific run
      scitex clew chain ./results/figure3.png  # Trace back to source
      scitex clew dag report.json figure1.png  # Verify multi-target DAG
      scitex clew status                        # Show changes
    """
    if help_recursive:
        _print_help_recursive(ctx)
        ctx.exit(0)
    elif ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


def _print_help_recursive(ctx):
    """Print help for all commands recursively."""
    fake_parent = click.Context(click.Group(), info_name="scitex")
    parent_ctx = click.Context(clew, info_name="clew", parent=fake_parent)
    click.secho("━━━ scitex clew ━━━", fg="cyan", bold=True)
    click.echo(clew.get_help(parent_ctx))
    for name in sorted(clew.list_commands(ctx) or []):
        cmd = clew.get_command(ctx, name)
        if cmd is None:
            continue
        click.echo()
        click.secho(f"━━━ scitex clew {name} ━━━", fg="cyan", bold=True)
        with click.Context(cmd, info_name=name, parent=parent_ctx) as sub_ctx:
            click.echo(cmd.get_help(sub_ctx))


@clew.command("list")
@click.option(
    "--limit", "-n", type=int, default=50, help="Maximum number of runs to show"
)
@click.option(
    "--filter-status",
    "-s",
    type=click.Choice(["all", "success", "failed", "running"]),
    default="all",
    help="Filter by run status",
)
@click.option("--no-verify", is_flag=True, help="Skip verification (faster)")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def list_runs(limit, filter_status, no_verify, as_json):
    """
    List all tracked runs with verification status.

    \b
    Examples:
      scitex clew list                    # List all runs
      scitex clew list -n 10              # Limit to 10 runs
      scitex clew list -s success         # Only successful runs
      scitex clew list --no-verify        # Skip verification (faster)
    """
    try:
        from scitex.clew import format_list, get_db

        db = get_db()
        status_filter = None if filter_status == "all" else filter_status
        runs = db.list_runs(status=status_filter, limit=limit)

        if as_json:
            import json

            output = []
            for run in runs:
                output.append(
                    {
                        "session_id": run["session_id"],
                        "script_path": run.get("script_path"),
                        "status": run.get("status"),
                        "started_at": run.get("started_at"),
                        "finished_at": run.get("finished_at"),
                    }
                )
            click.echo(json.dumps(output, indent=2))
        else:
            if not runs:
                click.echo("No tracked runs found.")
                click.echo(
                    "\nTo start tracking, use @stx.session decorator with stx.io."
                )
                return

            output = format_list(runs, verify=not no_verify)
            click.echo(output)
            click.echo(f"\nShowing {len(runs)} runs (use --limit to change)")

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@clew.command("run")
@click.argument("targets", nargs=-1, required=True)
@click.option("--rerun", is_flag=True, help="Re-execute script and compare (L2)")
@click.option(
    "--register", is_flag=True, help="Register hashes with Clew Registry (L3)"
)
@click.option("-v", "--verbose", is_flag=True, help="Show detailed file information")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def verify_run_cmd(targets, rerun, register, verbose, as_json):
    """
    Verify session run(s).

    TARGETS can be (one or multiple):
    - A session ID: 2025Y-11M-18D-09h12m03s_HmH5
    - A script path: ./script.py (latest run of this script)
    - An artifact path: ./results/figure3.png (session that produced it)

    \b
    Verification Levels:
      (default)   L1 — compare stored hashes vs current files
      --rerun     L2 — re-execute pipeline and compare
      --register  L3 — L2 + register hashes with Clew Registry

    \b
    Examples:
      scitex clew run 2025Y-11M-18D-09h12m03s_HmH5
      scitex clew run ./results/figure3.png
      scitex clew run ./script.py --rerun
      scitex clew run ./script.py --register
    """
    try:
        from scitex.clew import format_run_verification, verify_by_rerun, verify_run

        results = []
        for target in targets:
            if rerun or register:
                verification = verify_by_rerun(target)
            else:
                verification = verify_run(target)
            results.append(verification)

        if register:
            from scitex.clew import get_registry

            registry = get_registry()
            for v in results:
                if v.is_verified:
                    try:
                        registry.register_session(v.session_id)
                        if not as_json:
                            click.secho(f"  L3: registered {v.session_id}", fg="cyan")
                    except Exception as e:
                        click.secho(
                            f"  L3: registration failed for {v.session_id}: {e}",
                            fg="yellow",
                            err=True,
                        )

        if as_json:
            import json

            output = [
                {
                    "session_id": v.session_id,
                    "script_path": v.script_path,
                    "status": v.status.value,
                    "level": v.level.value,
                    "is_verified": v.is_verified,
                }
                for v in results
            ]
            click.echo(json.dumps(output, indent=2))
        else:
            all_verified = True
            for v in results:
                badge = "\u2713\u2713" if v.level.value == "rerun" else "\u2713"
                if v.is_verified:
                    click.secho(f"{badge} {v.session_id}", fg="green")
                else:
                    click.secho(f"\u2717 {v.session_id}", fg="red")
                    all_verified = False
                if verbose:
                    click.echo(format_run_verification(v, verbose=True))

            if not all_verified:
                sys.exit(1)

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


@clew.command("chain")
@click.argument("target_file", type=click.Path(exists=True))
@click.option("-v", "--verbose", is_flag=True, help="Show detailed information")
@click.option("--mermaid", is_flag=True, help="Output as Mermaid diagram")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def verify_chain_cmd(target_file, verbose, mermaid, as_json):
    """
    Verify the dependency chain for a target file.

    Traces back through all sessions that contributed to producing
    the target file and verifies each one.

    \b
    Examples:
      scitex clew chain ./results/figure3.png
      scitex clew chain ./results/figure3.png -v
      scitex clew chain ./results/figure3.png --mermaid
    """
    try:
        from scitex.clew import (
            format_chain_verification,
            generate_mermaid_dag,
            verify_chain,
        )

        chain = verify_chain(target_file)

        if mermaid:
            output = generate_mermaid_dag(target_file=str(Path(target_file).resolve()))
            click.echo(output)
        elif as_json:
            import json

            output = {
                "target_file": chain.target_file,
                "status": chain.status.value,
                "is_verified": chain.is_verified,
                "runs": [
                    {
                        "session_id": r.session_id,
                        "script_path": r.script_path,
                        "status": r.status.value,
                        "is_verified": r.is_verified,
                    }
                    for r in chain.runs
                ],
            }
            click.echo(json.dumps(output, indent=2))
        else:
            output = format_chain_verification(chain, verbose=verbose)
            click.echo(output)

            if chain.is_verified:
                click.echo()
                click.secho("\u2713 Chain fully verified!", fg="green")
            else:
                click.echo()
                click.secho("\u2717 Chain verification failed", fg="red")
                if chain.failed_runs:
                    click.echo(f"  {len(chain.failed_runs)} run(s) have issues")
                sys.exit(1)

    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)


# Wire in sub-module commands
from scitex.cli._clew_claims import register_claim_commands
from scitex.cli._clew_dag import register_dag_commands
from scitex.cli._clew_misc import register_misc_commands

register_dag_commands(clew)
register_claim_commands(clew)
register_misc_commands(clew)


if __name__ == "__main__":
    clew()
