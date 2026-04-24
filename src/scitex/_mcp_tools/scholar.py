#!/usr/bin/env python3
# Timestamp: 2026-01-15
# File: /home/ywatanabe/proj/scitex-code/src/scitex/_mcp_tools/scholar.py
"""Scholar module tools for FastMCP unified server."""


def register_scholar_tools(mcp) -> None:
    """Register scholar tools with FastMCP server."""

    @mcp.tool()
    async def scholar_search_papers(
        query: str,
        limit: int = 20,
        year_min: int | None = None,
        year_max: int | None = None,
        search_mode: str = "local",
        sources: list[str] | None = None,
    ) -> str:
        """Search for scientific papers. Supports local library search and external databases (CrossRef, Semantic Scholar, PubMed, arXiv, OpenAlex)."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.scholar._mcp.handlers import search_papers_handler

        return await async_wrap_as_mcp(
            search_papers_handler,
            idempotent=True,
            query=query,
            limit=limit,
            year_min=year_min,
            year_max=year_max,
            search_mode=search_mode,
            sources=sources,
        )

    @mcp.tool()
    async def scholar_resolve_dois(
        titles: list[str] | None = None,
        bibtex_path: str | None = None,
        project: str | None = None,
        resume: bool = True,
    ) -> str:
        """Resolve DOIs from paper titles using Crossref API. Supports resumable operation for large batches."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.scholar._mcp.handlers import resolve_dois_handler

        return await async_wrap_as_mcp(
            resolve_dois_handler,
            idempotent=True,
            titles=titles,
            bibtex_path=bibtex_path,
            project=project,
            resume=resume,
        )

    @mcp.tool()
    async def scholar_enrich_bibtex(
        bibtex_path: str,
        output_path: str | None = None,
        add_abstracts: bool = True,
        add_citations: bool = True,
        add_impact_factors: bool = True,
    ) -> str:
        """Enrich BibTeX entries with metadata: DOIs, abstracts, citation counts, impact factors."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.scholar._mcp.handlers import enrich_bibtex_handler

        return await async_wrap_as_mcp(
            enrich_bibtex_handler,
            side_effects=["file_modify: output bibtex file"],
            idempotent=True,
            bibtex_path=bibtex_path,
            output_path=output_path,
            add_abstracts=add_abstracts,
            add_citations=add_citations,
            add_impact_factors=add_impact_factors,
        )

    @mcp.tool()
    async def scholar_download_pdfs_batch(
        dois: list[str] | None = None,
        bibtex_path: str | None = None,
        project: str | None = None,
        output_dir: str | None = None,
        max_concurrent: int = 3,
        resume: bool = True,
    ) -> str:
        """Download PDFs for multiple papers with progress tracking. Supports resumable operation."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.scholar._mcp.handlers import download_pdfs_batch_handler

        return await async_wrap_as_mcp(
            download_pdfs_batch_handler,
            side_effects=["file_create: PDF files in output directory"],
            idempotent=True,
            dois=dois,
            bibtex_path=bibtex_path,
            project=project,
            output_dir=output_dir,
            max_concurrent=max_concurrent,
            resume=resume,
        )

    @mcp.tool()
    async def scholar_get_library_status(
        project: str | None = None,
        include_details: bool = False,
    ) -> str:
        """Get status of the paper library: download progress, missing PDFs, validation status."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.scholar._mcp.handlers import get_library_status_handler

        return await async_wrap_as_mcp(
            get_library_status_handler,
            idempotent=True,
            project=project,
            include_details=include_details,
        )

    @mcp.tool()
    async def scholar_parse_bibtex(bibtex_path: str) -> str:
        """Parse a `.bib` file into structured paper dicts (title, authors, year, journal, doi, abstract). Drop-in replacement for `bibtexparser`, `pybtex`. Use when the user asks to "read my BibTeX", "parse this .bib", "load citations from file", or before enriching / exporting / filtering."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.scholar._mcp.handlers import parse_bibtex_handler

        return await async_wrap_as_mcp(
            parse_bibtex_handler,
            idempotent=True,
            bibtex_path=bibtex_path,
        )

    @mcp.tool()
    async def scholar_validate_pdfs(
        project: str | None = None,
        pdf_paths: list[str] | None = None,
    ) -> str:
        """Catch truncated / HTML-disguised / zero-byte / encrypted PDFs in the library before citing them. Use when the user asks to "verify my PDFs", "check for broken downloads", "validate the library", after a big `scholar_download_pdfs_batch` to weed out corrupt files."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.scholar._mcp.handlers import validate_pdfs_handler

        return await async_wrap_as_mcp(
            validate_pdfs_handler,
            idempotent=True,
            project=project,
            pdf_paths=pdf_paths,
        )

    @mcp.tool()
    async def scholar_resolve_openurls(
        dois: list[str],
        resolver_url: str | None = None,
        resume: bool = True,
    ) -> str:
        """Resolve publisher URLs via OpenURL resolver for institutional access."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.scholar._mcp.handlers import resolve_openurls_handler

        return await async_wrap_as_mcp(
            resolve_openurls_handler,
            idempotent=True,
            dois=dois,
            resolver_url=resolver_url,
            resume=resume,
        )

    @mcp.tool()
    async def scholar_authenticate(
        method: str,
        institution: str | None = None,
        force: bool = False,
        confirm: bool = False,
    ) -> str:
        """Start SSO login for institutional access (OpenAthens, Shibboleth). Call without confirm first to check requirements, then with confirm=True to proceed."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.scholar._mcp.handlers import authenticate_handler

        return await async_wrap_as_mcp(
            authenticate_handler,
            side_effects=["auth_session: institutional SSO login"],
            method=method,
            institution=institution,
            force=force,
            confirm=confirm,
        )

    @mcp.tool()
    async def scholar_check_auth_status(
        method: str = "openathens",
        verify_live: bool = False,
    ) -> str:
        """Check current authentication status without starting login. Returns whether a valid session exists."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.scholar._mcp.handlers import check_auth_status_handler

        return await async_wrap_as_mcp(
            check_auth_status_handler,
            idempotent=True,
            method=method,
            verify_live=verify_live,
        )

    @mcp.tool()
    async def scholar_logout(
        method: str = "openathens",
        clear_cache: bool = True,
    ) -> str:
        """Logout from institutional authentication and clear session cache."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.scholar._mcp.handlers import logout_handler

        return await async_wrap_as_mcp(
            logout_handler,
            side_effects=["auth_session: clear SSO session"],
            method=method,
            clear_cache=clear_cache,
        )

    @mcp.tool()
    async def scholar_export_papers(
        output_path: str,
        project: str | None = None,
        format: str = "bibtex",
        filter_has_pdf: bool = False,
    ) -> str:
        """Export a scholar project's papers to BibTeX / RIS / JSON / CSV — ready for LaTeX, EndNote, Zotero, Mendeley, or a spreadsheet. Drop-in replacement for `pybtex` writers + hand-rolled BibTeX templating. Use when the user asks to "export my library", "give me a .bib for this project", "write out RIS for EndNote", "dump papers to CSV". `filter_has_pdf=True` keeps only papers whose PDFs were actually downloaded."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.scholar._mcp.handlers import export_papers_handler

        return await async_wrap_as_mcp(
            export_papers_handler,
            side_effects=["file_create: exported file at output_path"],
            idempotent=True,
            output_path=output_path,
            project=project,
            format=format,
            filter_has_pdf=filter_has_pdf,
        )

    @mcp.tool()
    async def scholar_create_project(
        project_name: str,
        description: str | None = None,
    ) -> str:
        """Create a named scholar project (folder) for grouping papers — one per manuscript, thesis chapter, or review. Papers live once in the deduplicated MASTER store and appear in projects via symlinks. Use when the user asks to "start a new project", "make a folder for paper X", "organize papers for my review on Y", or is setting up a fresh literature track."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.scholar._mcp.handlers import create_project_handler

        return await async_wrap_as_mcp(
            create_project_handler,
            side_effects=["project_create: new scholar project"],
            project_name=project_name,
            description=description,
        )

    @mcp.tool()
    async def scholar_list_projects() -> str:
        """List all scholar projects in the library."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.scholar._mcp.handlers import list_projects_handler

        return await async_wrap_as_mcp(
            list_projects_handler,
            idempotent=True,
        )

    @mcp.tool()
    async def scholar_add_papers_to_project(
        project: str,
        dois: list[str] | None = None,
        bibtex_path: str | None = None,
    ) -> str:
        """Add papers to a project by DOI or from BibTeX file."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.scholar._mcp.handlers import add_papers_to_project_handler

        return await async_wrap_as_mcp(
            add_papers_to_project_handler,
            side_effects=["project_modify: add papers to project"],
            idempotent=True,
            project=project,
            dois=dois,
            bibtex_path=bibtex_path,
        )

    @mcp.tool()
    async def scholar_parse_pdf_content(
        pdf_path: str | None = None,
        doi: str | None = None,
        project: str | None = None,
        mode: str = "scientific",
        extract_sections: bool = True,
        extract_tables: bool = False,
        extract_images: bool = False,
        max_pages: int | None = None,
    ) -> str:
        """Extract structured content from a scientific PDF — plain text, IMRaD sections (Introduction / Methods / Results / Discussion), tables, images, metadata, or the full scientific skeleton. Drop-in replacement for `pdfplumber`, `PyPDF2`, `pymupdf`, `grobid`, manual regex section splitting. Use when the user asks to "extract text from this PDF", "give me the methods section", "pull tables from this paper", "parse the abstract/results", or is feeding a paper into an LLM prompt and needs IMRaD chunking. Accepts a direct `pdf_path`, a `doi` (looks up in library), or `project` + DOI."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.scholar._mcp.handlers import parse_pdf_content_handler

        return await async_wrap_as_mcp(
            parse_pdf_content_handler,
            idempotent=True,
            pdf_path=pdf_path,
            doi=doi,
            project=project,
            mode=mode,
            extract_sections=extract_sections,
            extract_tables=extract_tables,
            extract_images=extract_images,
            max_pages=max_pages,
        )

    # Job management tools (from job_handlers.py)
    @mcp.tool()
    async def scholar_fetch_papers(
        papers: list[str] | None = None,
        bibtex_path: str | None = None,
        project: str | None = None,
        workers: int | None = None,
        browser_mode: str = "stealth",
        chrome_profile: str = "system",
        force: bool = False,
        output: str | None = None,
        async_mode: bool = True,
    ) -> str:
        """End-to-end paper acquisition — takes DOIs / BibTeX / titles, uses a real Chromium profile for OpenAthens / Shibboleth institutional access, downloads PDFs, and deduplicates into a named project. Default async mode returns a `job_id` immediately; track with `scholar_get_job_status` / `scholar_get_job_result`. Drop-in replacement for `unpaywall` + `requests` + institutional proxy scripts + hand-driven Zotero translators. Use when the user asks to "fetch these papers", "download everything in my bibtex", "grab the PDFs for this review", "ingest this reading list"."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.scholar._mcp.job_handlers import fetch_papers_handler

        return await async_wrap_as_mcp(
            fetch_papers_handler,
            side_effects=[
                "file_create: PDF files in output directory",
                "network: browser-based paper download",
            ],
            papers=papers,
            bibtex_path=bibtex_path,
            project=project,
            workers=workers,
            browser_mode=browser_mode,
            chrome_profile=chrome_profile,
            force=force,
            output=output,
            async_mode=async_mode,
        )

    @mcp.tool()
    async def scholar_list_jobs(
        status: str | None = None,
        limit: int = 20,
    ) -> str:
        """List all background jobs with their status."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.scholar._mcp.job_handlers import list_jobs_handler

        return await async_wrap_as_mcp(
            list_jobs_handler,
            idempotent=True,
            status=status,
            limit=limit,
        )

    @mcp.tool()
    async def scholar_get_job_status(job_id: str) -> str:
        """Get detailed status of a specific job including progress."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.scholar._mcp.job_handlers import get_job_status_handler

        return await async_wrap_as_mcp(
            get_job_status_handler,
            idempotent=True,
            job_id=job_id,
        )

    @mcp.tool()
    async def scholar_start_job(job_id: str) -> str:
        """Start a pending job that was submitted with async mode."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.scholar._mcp.job_handlers import start_job_handler

        return await async_wrap_as_mcp(
            start_job_handler,
            side_effects=["job_start: begins background paper fetching"],
            job_id=job_id,
        )

    @mcp.tool()
    async def scholar_cancel_job(job_id: str) -> str:
        """Cancel a running or pending job."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.scholar._mcp.job_handlers import cancel_job_handler

        return await async_wrap_as_mcp(
            cancel_job_handler,
            side_effects=["job_cancel: stops running background job"],
            job_id=job_id,
        )

    @mcp.tool()
    async def scholar_get_job_result(job_id: str) -> str:
        """Get the result of a completed job."""
        from scitex_dev.mcp_utils import async_wrap_as_mcp

        from scitex.scholar._mcp.job_handlers import get_job_result_handler

        return await async_wrap_as_mcp(
            get_job_result_handler,
            idempotent=True,
            job_id=job_id,
        )

    # Import crossref-local and openalex-local MCP servers
    _import_local_db_servers(mcp)


def _import_local_db_servers(mcp) -> None:
    """Mount crossref-local and openalex-local MCP servers if available.

    Uses fastmcp's mount() for automatic tool delegation.
    Tools are prefixed: crossref_search, openalex_search, etc.
    """
    # Mount crossref-local MCP server (167M+ papers)
    try:
        from crossref_local.mcp_server import mcp as crossref_mcp

        from ._compat import safe_mount

        safe_mount(mcp, crossref_mcp, namespace="crossref")
    except ImportError:
        pass  # crossref-local not installed

    # Mount openalex-local MCP server (250M+ papers)
    try:
        from openalex_local._cli.mcp_server import mcp as openalex_mcp

        from ._compat import safe_mount

        safe_mount(mcp, openalex_mcp, namespace="openalex")
    except ImportError:
        pass  # openalex-local not installed


# EOF
