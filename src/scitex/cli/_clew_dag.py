#!/usr/bin/env python3
# Timestamp: "2026-03-04 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/cli/_clew_dag.py
"""CLI commands for multi-target DAG verification."""

import sys
from pathlib import Path

import click


def register_dag_commands(clew_group):
    """Register DAG-related commands on the clew CLI group."""

    @clew_group.command("dag")
    @click.argument("target_files", nargs=-1)
    @click.option("--claims", is_flag=True, help="Build DAG from all registered claims")
    @click.option("-v", "--verbose", is_flag=True, help="Show detailed information")
    @click.option("--mermaid", is_flag=True, help="Output as Mermaid diagram")
    @click.option("--json", "as_json", is_flag=True, help="Output as JSON")
    def dag_cmd(target_files, claims, verbose, mermaid, as_json):
        """
        Verify the full DAG for multiple target files or claims.

        Traces back through all sessions that produced the target files,
        collecting the full multi-parent DAG.

        \b
        Examples:
          scitex clew dag report.json figure1.png
          scitex clew dag --claims
          scitex clew dag report.json --mermaid
        """
        try:
            if not target_files and not claims:
                click.secho(
                    "Error: Specify target files or --claims", fg="red", err=True
                )
                sys.exit(1)

            if claims:
                from scitex.clew import verify_claims_dag

                dag_result = verify_claims_dag()
            else:
                from scitex.clew import verify_dag

                target_list = [str(Path(f).resolve()) for f in target_files]
                dag_result = verify_dag(target_list)

            if mermaid:
                from scitex.clew import generate_mermaid_dag

                target_list = (
                    [str(Path(f).resolve()) for f in target_files]
                    if target_files
                    else None
                )
                output = generate_mermaid_dag(
                    target_files=target_list,
                    claims=claims,
                )
                click.echo(output)
            elif as_json:
                import json

                output = {
                    "target_files": dag_result.target_files,
                    "status": dag_result.status.value,
                    "is_verified": dag_result.is_verified,
                    "topological_order": dag_result.topological_order,
                    "runs": [
                        {
                            "session_id": r.session_id,
                            "script_path": r.script_path,
                            "status": r.status.value,
                            "is_verified": r.is_verified,
                        }
                        for r in dag_result.runs
                    ],
                    "edges": [{"parent": p, "child": c} for p, c in dag_result.edges],
                }
                click.echo(json.dumps(output, indent=2))
            else:
                click.secho(
                    f"DAG: {len(dag_result.runs)} runs, {len(dag_result.edges)} edges",
                    fg="cyan",
                    bold=True,
                )
                for r in dag_result.runs:
                    badge = "\u2713" if r.is_verified else "\u2717"
                    color = "green" if r.is_verified else "red"
                    script = Path(r.script_path).name if r.script_path else "unknown"
                    click.secho(
                        f"  {badge} {script} ({r.session_id[:20]}...)", fg=color
                    )

                if dag_result.is_verified:
                    click.echo()
                    click.secho("\u2713 DAG fully verified!", fg="green")
                else:
                    click.echo()
                    click.secho("\u2717 DAG verification failed", fg="red")
                    if dag_result.failed_runs:
                        click.echo(
                            f"  {len(dag_result.failed_runs)} run(s) have issues"
                        )
                    sys.exit(1)

        except Exception as e:
            click.secho(f"Error: {e}", fg="red", err=True)
            sys.exit(1)
