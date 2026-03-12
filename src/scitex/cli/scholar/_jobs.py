#!/usr/bin/env python3
# Timestamp: 2026-01-14
# File: src/scitex/cli/scholar/_jobs.py
# ----------------------------------------

"""Jobs subcommands for Scholar CLI."""

from __future__ import annotations

import asyncio
import json
import sys

import click
from scitex_dev import ErrorCode

from ._utils import output_json

_NOT_FOUND = ErrorCode.FILE_NOT_FOUND.value
_CONFLICT = ErrorCode.CONFLICT.value
_INTERNAL = ErrorCode.INTERNAL.value
_CONFIG = ErrorCode.CONFIG.value


@click.group(invoke_without_command=True)
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as structured JSON (Result envelope).",
)
@click.pass_context
def jobs(ctx, as_json):
    """
    Manage background jobs

    \b
    Examples:
        scitex scholar jobs list
        scitex scholar jobs status <job_id>
        scitex scholar jobs start <job_id>
        scitex scholar jobs cancel <job_id>
    """
    if ctx.invoked_subcommand is None:
        if as_json:
            from scitex.cli import group_to_json

            group_to_json(ctx, jobs)
        else:
            click.echo(ctx.get_help())


@jobs.command("list")
@click.option(
    "--status",
    type=click.Choice(["pending", "running", "completed", "failed", "cancelled"]),
    help="Filter by status",
)
@click.option("--limit", "-n", type=int, default=20, help="Maximum jobs to show")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
def jobs_list(status, limit, json_output):
    """List all jobs."""
    from scitex.scholar.jobs import JobManager

    manager = JobManager()
    job_list = manager.list_jobs(status=status, limit=limit)

    result = {"success": True, "count": len(job_list), "jobs": job_list}

    if json_output:
        output_json(result)
    else:
        if not job_list:
            click.echo("No jobs found")
            return

        click.echo(f"\nJobs ({len(job_list)}):\n")
        for job in job_list:
            status_str = job["status"].upper()
            progress = job.get("progress", {})
            percent = progress.get("percent", 0)

            if job["status"] == "running":
                status_display = f"{status_str} ({percent:.0f}%)"
            else:
                status_display = status_str

            click.echo(f"  {job['job_id']}  {status_display:15}  {job['job_type']}")


@jobs.command("status")
@click.argument("job_id")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
def jobs_status(job_id, json_output):
    """Check job status."""
    from scitex.scholar.jobs import JobManager

    manager = JobManager()
    status = manager.get_status(job_id)

    if not status:
        result = {
            "success": False,
            "error": f"Job '{job_id}' not found",
            "error_code": _NOT_FOUND,
        }
        if json_output:
            output_json(result)
        else:
            click.echo(f"Job '{job_id}' not found", err=True)
        sys.exit(1)

    result = {"success": True, **status}

    if json_output:
        output_json(result)
    else:
        click.echo(f"\nJob: {job_id}")
        click.echo(f"Type: {status['job_type']}")
        click.echo(f"Status: {status['status'].upper()}")

        progress = status.get("progress", {})
        if progress.get("total"):
            click.echo(
                f"Progress: {progress['completed']}/{progress['total']} "
                f"({progress['percent']:.1f}%)"
            )
            if progress.get("current_item"):
                click.echo(f"Current: {progress['current_item']}")

        if status.get("error"):
            click.echo(f"Error: {status['error']}")

        if status.get("duration_seconds"):
            click.echo(f"Duration: {status['duration_seconds']:.1f}s")


@jobs.command("start")
@click.argument("job_id")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
def jobs_start(job_id, json_output):
    """Start a pending job."""
    from scitex.scholar.jobs import JobManager, get_executor

    manager = JobManager()
    job = manager.get_job(job_id)

    if not job:
        result = {
            "success": False,
            "error": f"Job '{job_id}' not found",
            "error_code": _NOT_FOUND,
        }
        if json_output:
            output_json(result)
        else:
            click.echo(f"Job '{job_id}' not found", err=True)
        sys.exit(1)

    if job.status.value != "pending":
        result = {
            "success": False,
            "error": f"Job is {job.status.value}, not pending",
            "error_code": _CONFLICT,
        }
        if json_output:
            output_json(result)
        else:
            click.echo(f"Job is {job.status.value}, not pending", err=True)
        sys.exit(1)

    job_type = job.job_type.value if hasattr(job.job_type, "value") else job.job_type
    executor = get_executor(job_type)

    if not executor:
        result = {
            "success": False,
            "error": f"No executor for job type: {job_type}",
            "error_code": _CONFIG,
        }
        if json_output:
            output_json(result)
        else:
            click.echo(f"No executor for job type: {job_type}", err=True)
        sys.exit(1)

    if not json_output:
        click.echo(f"Starting job {job_id}...")

    async def run_job():
        job.start()
        job.save(manager.jobs_dir)

        try:
            result = await executor(
                **job.params,
                progress_callback=lambda **kwargs: _update_progress(
                    manager, job, json_output, **kwargs
                ),
            )
            job.complete(result)
        except Exception as e:
            job.fail(str(e))

        job.save(manager.jobs_dir)
        return job.to_dict()

    try:
        final_result = asyncio.run(run_job())
        if json_output:
            output_json({"success": True, **final_result})
        else:
            if final_result.get("status") == "completed":
                click.echo(f"\nJob {job_id} completed successfully")
            else:
                click.echo(f"\nJob {job_id} failed: {final_result.get('error')}")

    except KeyboardInterrupt:
        job.cancel()
        job.save(manager.jobs_dir)
        if json_output:
            output_json(
                {
                    "success": False,
                    "error": "Cancelled by user",
                    "error_code": _INTERNAL,
                }
            )
        else:
            click.echo("\nJob cancelled by user")
        sys.exit(1)


def _update_progress(manager, job, json_output, **kwargs):
    """Update job progress and optionally show it."""
    job.update_progress(**kwargs)
    job.save(manager.jobs_dir)

    if not json_output and kwargs.get("message"):
        progress = job.progress
        if progress.total:
            click.echo(
                f"\r  Progress: {progress.completed}/{progress.total} "
                f"({progress.percent:.0f}%) - {kwargs.get('message', '')}",
                nl=False,
            )


@jobs.command("cancel")
@click.argument("job_id")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
def jobs_cancel(job_id, json_output):
    """Cancel a running or pending job."""
    from scitex.scholar.jobs import JobManager

    manager = JobManager()

    async def do_cancel():
        return await manager.cancel(job_id)

    cancelled = asyncio.run(do_cancel())

    if cancelled:
        result = {"success": True, "job_id": job_id, "message": "Job cancelled"}
    else:
        result = {
            "success": False,
            "error": f"Could not cancel job '{job_id}' (not found or finished)",
            "error_code": _CONFLICT,
        }

    if json_output:
        output_json(result)
    else:
        if cancelled:
            click.echo(f"Job {job_id} cancelled")
        else:
            click.echo(result["error"], err=True)
            sys.exit(1)


@jobs.command("result")
@click.argument("job_id")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
def jobs_result(job_id, json_output):
    """Get result of a completed job."""
    from scitex.scholar.jobs import JobManager

    manager = JobManager()
    job = manager.get_job(job_id)

    if not job:
        result = {
            "success": False,
            "error": f"Job '{job_id}' not found",
            "error_code": _NOT_FOUND,
        }
        if json_output:
            output_json(result)
        else:
            click.echo(f"Job '{job_id}' not found", err=True)
        sys.exit(1)

    if not job.is_finished:
        result = {
            "success": False,
            "error": f"Job is still {job.status.value}",
            "error_code": _CONFLICT,
        }
        if json_output:
            output_json(result)
        else:
            click.echo(f"Job is still {job.status.value}", err=True)
        sys.exit(1)

    if job.result:
        result = {"success": True, "job_id": job_id, "result": job.result}
    else:
        result = {
            "success": False,
            "error": job.error or "No result available",
            "error_code": _INTERNAL,
        }

    if json_output:
        output_json(result)
    else:
        if job.result:
            click.echo(f"\nResult for job {job_id}:")
            click.echo(json.dumps(job.result, indent=2, default=str))
        else:
            click.echo(f"Job failed: {job.error}", err=True)
            sys.exit(1)


@jobs.command("clean")
@click.option("--max-age", type=int, default=24, help="Delete jobs older than N hours")
@click.option("--keep-failed", is_flag=True, help="Keep failed jobs")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
def jobs_clean(max_age, keep_failed, json_output):
    """Clean up old completed jobs."""
    from scitex.scholar.jobs import JobManager

    manager = JobManager()
    deleted = manager.cleanup_old_jobs(max_age_hours=max_age, keep_failed=keep_failed)

    result = {
        "success": True,
        "deleted": deleted,
        "max_age_hours": max_age,
        "kept_failed": keep_failed,
    }

    if json_output:
        output_json(result)
    else:
        click.echo(f"Deleted {deleted} old jobs")


# EOF
