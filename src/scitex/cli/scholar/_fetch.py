#!/usr/bin/env python3
# Timestamp: 2026-01-14
# File: src/scitex/cli/scholar/_fetch.py
# ----------------------------------------

"""Fetch command for Scholar CLI."""

from __future__ import annotations

import asyncio
import sys
from datetime import datetime
from pathlib import Path

import click
from scitex_dev import ErrorCode, classify_exception

from scitex import logging

from ._utils import output_json

logger = logging.getLogger(__name__)


def _error_dict(error: str | Exception, code: ErrorCode | None = None) -> dict:
    """Build an error dict with classified error_code."""
    if code is None and isinstance(error, Exception):
        code = classify_exception(error)
    elif code is None:
        code = ErrorCode.VALIDATION
    return {
        "success": False,
        "error": str(error),
        "error_code": code.value,
    }


@click.command()
@click.argument("papers", nargs=-1)
@click.option(
    "--from-bibtex",
    "bibtex_file",
    type=click.Path(exists=True),
    help="Import papers from BibTeX file",
)
@click.option("--project", "-p", help="Project name for organizing papers")
@click.option(
    "--workers", "-w", type=int, default=None, help="Number of parallel workers"
)
@click.option(
    "--browser-mode",
    type=click.Choice(["stealth", "interactive"]),
    default="stealth",
    help="Browser mode for PDF download",
)
@click.option("--chrome-profile", default="system", help="Chrome profile name")
@click.option("--force", "-f", is_flag=True, help="Force re-download")
@click.option("--output", "-o", help="Output path for enriched BibTeX")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
@click.option("--async", "async_mode", is_flag=True, help="Run in background")
def fetch(
    papers,
    bibtex_file,
    project,
    workers,
    browser_mode,
    chrome_profile,
    force,
    output,
    json_output,
    async_mode,
):
    """
    Fetch papers to your library

    \b
    Examples:
        scitex scholar fetch "10.1038/nature12373"
        scitex scholar fetch "10.1038/nature12373" --json
        scitex scholar fetch "10.1038/nature12373" --async
        scitex scholar fetch --from-bibtex papers.bib --project myresearch
    """
    if not papers and not bibtex_file:
        error_msg = "Provide DOIs/titles or use --from-bibtex"
        if json_output:
            output_json(_error_dict(error_msg))
        else:
            click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)

    if papers and bibtex_file:
        error_msg = "Cannot mix positional arguments with --from-bibtex"
        if json_output:
            output_json(_error_dict(error_msg))
        else:
            click.echo(f"Error: {error_msg}", err=True)
        sys.exit(1)

    if async_mode:
        _fetch_async(
            papers=list(papers) if papers else None,
            bibtex_file=bibtex_file,
            project=project,
            workers=workers,
            browser_mode=browser_mode,
            chrome_profile=chrome_profile,
            force=force,
            output=output,
            json_output=json_output,
        )
        return

    if bibtex_file:
        result = _add_from_bibtex(
            bibtex_file,
            project,
            workers,
            browser_mode,
            chrome_profile,
            output,
            json_output,
        )
    else:
        papers = list(papers)
        if workers is None:
            workers = min(len(papers), 4)

        if len(papers) == 1:
            result = _add_single(
                papers[0], project, browser_mode, chrome_profile, force, json_output
            )
        else:
            result = _add_multiple(
                papers, project, workers, browser_mode, chrome_profile, json_output
            )

    if json_output:
        output_json(result)
    elif not result.get("success"):
        sys.exit(1)


def _fetch_async(
    papers,
    bibtex_file,
    project,
    workers,
    browser_mode,
    chrome_profile,
    force,
    output,
    json_output,
):
    """Submit fetch job and start it in a background subprocess."""
    import subprocess

    from scitex.scholar.jobs import JobManager, JobType

    manager = JobManager()

    if bibtex_file:
        job_type = JobType.FETCH_BIBTEX
        params = {
            "bibtex_path": str(bibtex_file),
            "project": project,
            "output_path": output,
            "workers": workers or 4,
            "browser_mode": browser_mode,
            "chrome_profile": chrome_profile,
        }
    elif len(papers) == 1:
        job_type = JobType.FETCH
        params = {
            "doi_or_title": papers[0],
            "project": project,
            "browser_mode": browser_mode,
            "chrome_profile": chrome_profile,
            "force": force,
        }
    else:
        job_type = "fetch_multiple"
        params = {
            "papers": papers,
            "project": project,
            "workers": workers or min(len(papers), 4),
            "browser_mode": browser_mode,
            "chrome_profile": chrome_profile,
        }

    # Submit job (creates pending job file)
    job_id = manager.submit(job_type=job_type, params=params)
    job_type_str = job_type.value if hasattr(job_type, "value") else job_type

    # Start job in background subprocess
    subprocess.Popen(
        [sys.executable, "-m", "scitex", "scholar", "jobs", "start", job_id],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    result = {
        "success": True,
        "job_id": job_id,
        "job_type": job_type_str,
        "status": "running",
        "message": f"Job started in background. Check: scitex scholar jobs status {job_id}",
    }

    if json_output:
        output_json(result)
    else:
        click.echo(f"Job started: {job_id}")
        click.echo(f"Check status: scitex scholar jobs status {job_id}")


def _add_single(
    doi_or_title, project, browser_mode, chrome_profile, force, json_output
):
    """Add a single paper to library."""
    from scitex.scholar.pipelines import ScholarPipelineSingle

    if not json_output:
        logger.info(f"Fetching: {doi_or_title}")

    async def run():
        pipeline = ScholarPipelineSingle(
            browser_mode=browser_mode,
            chrome_profile=chrome_profile,
        )
        paper, symlink_path = await pipeline.process_single_paper(
            doi_or_title=doi_or_title,
            project=project,
            force=force,
        )

        # Granular success flags
        has_doi = bool(paper and paper.metadata.id.doi)
        has_metadata = bool(paper and paper.metadata.basic.title)
        has_pdf = bool(symlink_path)
        has_content = bool(
            paper
            and hasattr(paper, "container")
            and paper.container.pdf_size_bytes
            and paper.container.pdf_size_bytes > 0
        )
        pdf_method = None
        if paper and paper.metadata.path.pdfs_engines:
            pdf_method = paper.metadata.path.pdfs_engines[0]

        return {
            "success": has_pdf,  # Overall success = PDF obtained
            "success_doi": has_doi,
            "success_metadata": has_metadata,
            "success_pdf": has_pdf,
            "success_content": has_content,
            "pdf_method": pdf_method,
            "message": (
                "Paper fetched"
                if has_pdf
                else "Metadata fetched but PDF not downloaded"
            ),
            "doi": paper.metadata.id.doi if paper else None,
            "title": paper.metadata.basic.title if paper else None,
            "path": str(symlink_path) if symlink_path else None,
            "has_pdf": has_pdf,
            "timestamp": datetime.now().isoformat(),
        }

    try:
        result = asyncio.run(run())
        if not json_output:
            logger.success("Paper fetched")
            if result.get("path"):
                logger.info(f"  Location: {result['path']}")
        return result
    except KeyboardInterrupt:
        return _error_dict("Interrupted by user", ErrorCode.INTERNAL)
    except Exception as e:
        if not json_output:
            logger.error(f"Failed: {e}")
        return _error_dict(e)


def _add_multiple(papers, project, workers, browser_mode, chrome_profile, json_output):
    """Add multiple papers to library in parallel."""
    from scitex.scholar.pipelines import ScholarPipelineParallel

    if not json_output:
        logger.info(f"Fetching {len(papers)} papers ({workers} workers)")

    async def run():
        pipeline = ScholarPipelineParallel(
            num_workers=workers,
            browser_mode=browser_mode,
            base_chrome_profile=chrome_profile,
        )
        results = await pipeline.process_papers_from_list_async(
            doi_or_title_list=papers,
            project=project,
        )
        paper_results = []
        for paper in results:
            if paper:
                paper_results.append(
                    {
                        "doi": paper.metadata.id.doi,
                        "title": paper.metadata.basic.title,
                        "success": True,
                    }
                )
            else:
                paper_results.append({"success": False})

        return {
            "success": True,
            "message": f"{len(results)} papers fetched",
            "total": len(papers),
            "fetched": len([r for r in paper_results if r.get("success")]),
            "failed": len([r for r in paper_results if not r.get("success")]),
            "papers": paper_results,
            "timestamp": datetime.now().isoformat(),
        }

    try:
        result = asyncio.run(run())
        if not json_output:
            logger.success(f"{result['fetched']} papers fetched")
        return result
    except KeyboardInterrupt:
        return _error_dict("Interrupted by user", ErrorCode.INTERNAL)
    except Exception as e:
        if not json_output:
            logger.error(f"Failed: {e}")
        return _error_dict(e)


def _add_from_bibtex(
    bibtex_file, project, workers, browser_mode, chrome_profile, output, json_output
):
    """Fetch papers from BibTeX file."""
    from scitex.scholar.pipelines import ScholarPipelineBibTeX

    bibtex_path = Path(bibtex_file)
    workers = workers or 4

    if not json_output:
        logger.info(f"Fetching papers from: {bibtex_path.name}")

    async def run():
        pipeline = ScholarPipelineBibTeX(
            num_workers=workers,
            browser_mode=browser_mode,
            base_chrome_profile=chrome_profile,
        )
        results = await pipeline.process_bibtex_file_async(
            bibtex_path=bibtex_path,
            project=project,
            output_bibtex_path=output,
        )
        return {
            "success": True,
            "message": f"{len(results)} papers fetched from BibTeX",
            "bibtex_path": str(bibtex_path),
            "output_path": output,
            "total": len(results),
            "timestamp": datetime.now().isoformat(),
        }

    try:
        result = asyncio.run(run())
        if not json_output:
            logger.success(f"{result['total']} papers fetched from BibTeX")
            if output:
                logger.info(f"  Enriched BibTeX: {output}")
        return result
    except KeyboardInterrupt:
        return _error_dict("Interrupted by user", ErrorCode.INTERNAL)
    except Exception as e:
        if not json_output:
            logger.error(f"Failed: {e}")
        return _error_dict(e)


# EOF
