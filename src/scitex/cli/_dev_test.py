#!/usr/bin/env python3
# Timestamp: 2026-02-14
# File: scitex/cli/_dev_test.py

"""CLI command for running tests locally and on HPC."""

import click


@click.command("test")
@click.argument("module", default="")
@click.option("--hpc", is_flag=True, help="Run on HPC (Spartan) via Slurm")
@click.option(
    "--async", "async_mode", is_flag=True, help="Submit async sbatch (returns job ID)"
)
@click.option("--poll", is_flag=True, help="Check HPC job status once")
@click.option("--watch", is_flag=True, help="Poll HPC job until done")
@click.option("--result", is_flag=True, help="Fetch HPC test output")
@click.option("--fast", is_flag=True, help="Skip @slow tests")
@click.option(
    "-n",
    "--parallel",
    default="auto",
    show_default=True,
    help="Parallel workers (0 to disable)",
)
@click.option("-c", "--coverage", is_flag=True, help="Enable coverage reporting")
@click.option("-x", "--exitfirst", is_flag=True, help="Stop on first failure")
@click.option("-k", "--pattern", default="", help="Test name pattern filter")
@click.option("--changed", is_flag=True, help="Tests for git-changed files (testmon)")
@click.option("--lf", is_flag=True, help="Re-run last-failed tests only")
@click.option("--job-id", default="", help="Job ID for --poll/--result")
@click.option(
    "--hpc-cpus",
    default=None,
    type=int,
    help="HPC CPUs per task [env: SCITEX_DEV_TEST_CPUS, default: 16]",
)
@click.option(
    "--hpc-partition",
    default=None,
    help="Slurm partition [env: SCITEX_DEV_TEST_PARTITION, default: sapphire]",
)
@click.option(
    "--hpc-time",
    default=None,
    help="Slurm time limit [env: SCITEX_DEV_TEST_TIME, default: 00:20:00]",
)
@click.option(
    "--hpc-mem",
    default=None,
    help="Slurm memory limit [env: SCITEX_DEV_TEST_MEM, default: 128G]",
)
@click.option(
    "--watch-interval",
    default=15,
    type=int,
    show_default=True,
    help="Watch polling interval (seconds)",
)
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def test(
    module,
    hpc,
    async_mode,
    poll,
    watch,
    result,
    fast,
    parallel,
    coverage,
    exitfirst,
    pattern,
    changed,
    lf,
    job_id,
    watch_interval,
    hpc_cpus,
    hpc_partition,
    hpc_time,
    hpc_mem,
    as_json,
):
    """
    Run project tests locally or on HPC.

    \b
    Auto-detects project root via git. Uses pytest with parallel execution
    by default. For HPC mode, syncs via rsync and runs via Slurm.

    \b
    Local examples:
      scitex dev test                  # Full suite, auto-parallel
      scitex dev test stats            # Single module
      scitex dev test --fast           # Skip slow tests
      scitex dev test --lf             # Re-run last failures
      scitex dev test -x -k 'test_io' # Stop first, filter by name
      scitex dev test -n 0             # No parallelism
      scitex dev test --coverage       # With coverage

    \b
    HPC examples:
      scitex dev test --hpc                   # Blocking srun
      scitex dev test --hpc --async           # sbatch, returns job ID
      scitex dev test --hpc --poll            # Check status once
      scitex dev test --hpc --watch           # Poll until done
      scitex dev test --hpc --result          # Fetch output
      scitex dev test --hpc -n 64             # 64 cores
      scitex dev test --hpc --hpc-cpus 32     # 32 CPUs
      scitex dev test stats --hpc             # Single module on HPC
    """
    import json as json_module

    from scitex._dev._test import (
        TestConfig,
        _check_ssh,
        _get_hpc_config,
        fetch_hpc_result,
        poll_hpc_job,
        run_hpc_sbatch,
        run_hpc_srun,
        run_local,
        sync_to_hpc,
    )

    config = TestConfig(
        module=module,
        parallel=parallel,
        fast=fast,
        coverage=coverage,
        exitfirst=exitfirst,
        pattern=pattern,
        changed=changed,
        last_failed=lf,
        hpc_cpus=hpc_cpus,
        hpc_partition=hpc_partition,
        hpc_time=hpc_time,
        hpc_mem=hpc_mem,
    )

    # HPC: watch mode (blocking poll loop)
    if watch:
        from scitex._dev._test import watch_hpc_job

        hpc_cfg = _get_hpc_config(config)
        click.secho(f"Watching HPC job (every {watch_interval}s)...", fg="cyan")
        info = watch_hpc_job(
            job_id=job_id or None,
            hpc_host=hpc_cfg["host"],
            interval=watch_interval,
        )
        if as_json:
            click.echo(json_module.dumps(info, indent=2))
        else:
            _print_poll_result(info)
        return

    # HPC: poll mode
    if poll:
        hpc_cfg = _get_hpc_config(config)
        click.secho("Polling HPC job...", fg="cyan")
        info = poll_hpc_job(job_id=job_id or None, hpc_host=hpc_cfg["host"])
        if as_json:
            click.echo(json_module.dumps(info, indent=2))
        else:
            _print_poll_result(info)
        return

    # HPC: result mode
    if result:
        hpc_cfg = _get_hpc_config(config)
        click.secho("Fetching HPC test output...", fg="cyan")
        output = fetch_hpc_result(job_id=job_id or None, hpc_host=hpc_cfg["host"])
        if output:
            click.echo(output)
        else:
            click.secho("No output found.", fg="red")
            raise SystemExit(1)
        return

    # HPC: run mode
    if hpc or async_mode:
        hpc_cfg = _get_hpc_config(config)
        host = hpc_cfg["host"]

        click.secho(f"Checking SSH to {host}...", fg="cyan")
        if not _check_ssh(host):
            click.secho(f"Cannot connect to {host}", fg="red")
            raise SystemExit(255)

        click.secho(f"Syncing to {host}...", fg="cyan")
        if not sync_to_hpc(config):
            click.secho("rsync failed", fg="red")
            raise SystemExit(1)
        click.secho("Sync complete", fg="green")

        if async_mode:
            click.secho("Submitting async job (sbatch)...", fg="cyan")
            jid = run_hpc_sbatch(config)
            if jid:
                click.secho(f"Job submitted: {jid}", fg="green")
                click.echo(f"  Poll:   scitex dev test --poll --job-id {jid}")
                click.echo(f"  Result: scitex dev test --result --job-id {jid}")
            else:
                click.secho("Failed to submit job", fg="red")
                raise SystemExit(1)
        else:
            cpus = hpc_cfg["cpus"]
            click.secho(
                f"Running on {host} (srun: {cpus} CPUs, {hpc_cfg['partition']})...",
                fg="cyan",
            )
            exit_code = run_hpc_srun(config)
            if exit_code == 0:
                click.secho("All tests passed on HPC", fg="green")
            else:
                click.secho(f"Tests failed (exit code: {exit_code})", fg="red")
            raise SystemExit(exit_code)
        return

    # Local mode
    module_str = f" [{module}]" if module else ""
    click.secho(f"Running tests{module_str}...", fg="cyan")
    exit_code = run_local(config)
    raise SystemExit(exit_code)


def _print_poll_result(info):
    """Print poll result in human-readable format."""
    state = info.get("state", "UNKNOWN")
    job_id = info.get("job_id", "?")

    color = {
        "COMPLETED": "green",
        "RUNNING": "cyan",
        "PENDING": "yellow",
        "FAILED": "red",
        "TIMEOUT": "red",
        "CANCELLED": "red",
    }.get(state, "white")

    click.secho(f"Job {job_id}: {state}", fg=color, bold=True)

    output = info.get("output")
    if output and state in ("COMPLETED", "FAILED"):
        lines = output.strip().split("\n")
        tail = lines[-20:] if len(lines) > 20 else lines
        click.echo()
        for line in tail:
            click.echo(line)

    if state == "COMPLETED":
        raise SystemExit(0)
    elif state in ("FAILED", "TIMEOUT", "CANCELLED"):
        raise SystemExit(1)
    else:
        raise SystemExit(2)


# EOF
