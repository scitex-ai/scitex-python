#!/usr/bin/env python3
# Timestamp: 2026-01-08
# File: src/scitex/scholar/_mcp.handlers.py
# ----------------------------------------

"""Handler implementations for the scitex-scholar MCP server."""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path

__all__ = [
    "search_papers_handler",
    "resolve_dois_handler",
    "enrich_bibtex_handler",
    "download_pdf_handler",
    "download_pdfs_batch_handler",
    "get_library_status_handler",
    "parse_bibtex_handler",
    "validate_pdfs_handler",
    "resolve_openurls_handler",
    "authenticate_handler",
    "check_auth_status_handler",
    "logout_handler",
    "export_papers_handler",
    "create_project_handler",
    "list_projects_handler",
    "add_papers_to_project_handler",
    "parse_pdf_content_handler",
]


def _get_scholar_dir() -> Path:
    """Get the scholar data directory."""
    base_dir = Path(os.getenv("SCITEX_DIR", Path.home() / ".scitex"))
    scholar_dir = base_dir / "scholar"
    scholar_dir.mkdir(parents=True, exist_ok=True)
    return scholar_dir


def _ensure_scholar():
    """Ensure Scholar module is available and return instance."""
    try:
        from scitex.scholar import Scholar

        return Scholar()
    except ImportError as e:
        raise RuntimeError(f"Scholar module not available: {e}")


async def search_papers_handler(
    query: str,
    sources: list[str] | None = None,
    limit: int = 20,
    year_min: int | None = None,
    year_max: int | None = None,
    search_mode: str = "local",  # "local", "external", or "both"
) -> dict:
    """Search for scientific papers.

    Args:
        query: Search query string
        sources: Sources to search (crossref, semantic_scholar, pubmed, arxiv, openalex)
        limit: Maximum number of results
        year_min: Minimum publication year
        year_max: Maximum publication year
        search_mode: "local" (library only), "external" (online databases), or "both"
    """
    try:
        results = []
        sources_used = []

        # Local library search
        if search_mode in ("local", "both"):
            from scitex.scholar import Scholar

            loop = asyncio.get_running_loop()
            scholar = Scholar()

            def do_local_search():
                papers = scholar.search_across_projects(query)
                filtered = []
                for paper in papers:
                    paper_year = paper.metadata.basic.year
                    if year_min and paper_year and paper_year < year_min:
                        continue
                    if year_max and paper_year and paper_year > year_max:
                        continue
                    filtered.append(paper)
                    if len(filtered) >= limit:
                        break
                return filtered

            local_papers = await loop.run_in_executor(None, do_local_search)

            for paper in local_papers:
                results.append(
                    {
                        "title": paper.metadata.basic.title,
                        "authors": (
                            paper.metadata.basic.authors[:5]
                            if paper.metadata.basic.authors
                            else []
                        ),
                        "year": paper.metadata.basic.year,
                        "doi": paper.metadata.id.doi,
                        "journal": paper.metadata.publication.journal,
                        "abstract": (
                            paper.metadata.basic.abstract[:300] + "..."
                            if paper.metadata.basic.abstract
                            and len(paper.metadata.basic.abstract) > 300
                            else paper.metadata.basic.abstract
                        ),
                        "citation_count": paper.metadata.citation_count.total,
                        "source": "local_library",
                    }
                )
            sources_used.append("local_library")

        # External search via ScholarSearchEngine
        if search_mode in ("external", "both"):
            try:
                from scitex.scholar.search_engines.ScholarSearchEngine import (
                    ScholarSearchEngine,
                )

                engine = ScholarSearchEngine(default_mode="parallel")

                # Build filters
                filters = {}
                if year_min:
                    filters["year_start"] = year_min
                if year_max:
                    filters["year_end"] = year_max

                # Execute external search
                external_result = await engine.search(
                    query=query,
                    filters=filters,
                    max_results=limit,
                )

                # Process external results
                for paper in external_result.get("results", []):
                    # Avoid duplicates by DOI
                    doi = paper.get("doi")
                    if doi and any(r.get("doi") == doi for r in results):
                        continue

                    results.append(
                        {
                            "title": paper.get("title"),
                            "authors": paper.get("authors", [])[:5],
                            "year": paper.get("year"),
                            "doi": doi,
                            "journal": paper.get("journal"),
                            "abstract": (
                                paper.get("abstract", "")[:300] + "..."
                                if paper.get("abstract")
                                and len(paper.get("abstract", "")) > 300
                                else paper.get("abstract")
                            ),
                            "citation_count": paper.get("citation_count"),
                            "source": paper.get("source", "external"),
                        }
                    )

                # Add sources used
                sources_used.extend(engine.get_supported_engines())

            except Exception as e:
                # If external search fails, log but continue with local results
                if search_mode == "external":
                    return {"success": False, "error": f"External search failed: {e}"}

        return {
            "success": True,
            "count": len(results),
            "query": query,
            "search_mode": search_mode,
            "sources_used": sources_used,
            "papers": results[:limit],
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


async def resolve_dois_handler(
    bibtex_path: str | None = None,
    titles: list[str] | None = None,
    resume: bool = True,
    project: str | None = None,
) -> dict:
    """Resolve DOIs from paper titles using process_paper.

    Uses Scholar.process_paper_async which resolves DOIs via Crossref API.
    """
    try:
        from scitex.scholar import Scholar

        scholar = Scholar(project=project) if project else Scholar()
        resolved = []
        failed = []

        if bibtex_path:
            # Load papers from BibTeX and resolve DOIs
            papers = scholar.load_bibtex(bibtex_path)

            for paper in papers:
                title = paper.metadata.basic.title
                doi = paper.metadata.id.doi

                if doi:
                    # Already has DOI
                    resolved.append({"title": title, "doi": doi, "source": "existing"})
                elif title:
                    # Try to resolve DOI using process_paper
                    try:
                        processed = await scholar.process_paper_async(title=title)
                        if processed and processed.metadata.id.doi:
                            resolved.append(
                                {
                                    "title": title,
                                    "doi": processed.metadata.id.doi,
                                    "source": "crossref",
                                }
                            )
                        else:
                            failed.append({"title": title, "reason": "No DOI found"})
                    except Exception as e:
                        failed.append({"title": title, "reason": str(e)})
                else:
                    failed.append({"title": "(no title)", "reason": "Missing title"})

            total = len(papers)

        elif titles:
            for title in titles:
                try:
                    processed = await scholar.process_paper_async(title=title)
                    if processed and processed.metadata.id.doi:
                        resolved.append(
                            {
                                "title": title,
                                "doi": processed.metadata.id.doi,
                                "source": "crossref",
                            }
                        )
                    else:
                        failed.append({"title": title, "reason": "No DOI found"})
                except Exception as e:
                    failed.append({"title": title, "reason": str(e)})

            total = len(titles)

        else:
            return {
                "success": False,
                "error": "Either bibtex_path or titles required",
            }

        return {
            "success": True,
            "resolved": resolved,
            "failed": failed,
            "total": total,
            "resolved_count": len(resolved),
            "failed_count": len(failed),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


async def enrich_bibtex_handler(
    bibtex_path: str,
    output_path: str | None = None,
    add_abstracts: bool = True,
    add_citations: bool = True,
    add_impact_factors: bool = True,
) -> dict:
    """Enrich BibTeX entries with metadata using Scholar.enrich_papers().

    Args:
        bibtex_path: Path to BibTeX file to enrich
        output_path: Output path for enriched BibTeX (auto-generated if None)
        add_abstracts: Whether to add abstracts
        add_citations: Whether to add citation counts
        add_impact_factors: Whether to add journal impact factors
    """
    try:
        from scitex.scholar import Scholar

        loop = asyncio.get_running_loop()
        scholar = Scholar()

        def do_enrich():
            # Load papers from BibTeX
            papers = scholar.load_bibtex(bibtex_path)

            # Count papers before enrichment
            before_stats = {
                "with_abstract": sum(1 for p in papers if p.metadata.basic.abstract),
                "with_citations": sum(
                    1 for p in papers if p.metadata.citation_count.total
                ),
                "with_impact_factor": sum(
                    1 for p in papers if p.metadata.publication.impact_factor
                ),
            }

            # Use scholar's enrich_papers method (correct API)
            enriched_papers = scholar.enrich_papers(papers)

            # Save to output using correct API
            out_path = output_path or bibtex_path.replace(".bib", "-enriched.bib")
            scholar.save_papers_as_bibtex(enriched_papers, out_path)

            # Count papers after enrichment
            summary = {
                "total": len(enriched_papers),
                "with_doi": sum(1 for p in enriched_papers if p.metadata.id.doi),
                "with_abstract": sum(
                    1 for p in enriched_papers if p.metadata.basic.abstract
                ),
                "with_citations": sum(
                    1 for p in enriched_papers if p.metadata.citation_count.total
                ),
                "with_impact_factor": sum(
                    1 for p in enriched_papers if p.metadata.publication.impact_factor
                ),
                "enriched": {
                    "abstracts_added": sum(
                        1 for p in enriched_papers if p.metadata.basic.abstract
                    )
                    - before_stats["with_abstract"],
                    "citations_added": sum(
                        1 for p in enriched_papers if p.metadata.citation_count.total
                    )
                    - before_stats["with_citations"],
                    "impact_factors_added": sum(
                        1
                        for p in enriched_papers
                        if p.metadata.publication.impact_factor
                    )
                    - before_stats["with_impact_factor"],
                },
            }

            return {"output_path": out_path, "summary": summary}

        result = await loop.run_in_executor(None, do_enrich)

        return {
            "success": True,
            **result,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


async def download_pdf_handler(
    doi: str,
    output_dir: str = "./pdfs",
    auth_method: str = "none",
) -> dict:
    """Download a PDF using authenticated browser.

    Delegates to ScholarPipelineSingle which has proper AuthenticationGateway
    support for institutional access to paywalled content.

    Args:
        doi: DOI of the paper to download
        output_dir: Output directory (stored in library by default)
        auth_method: Authentication method ("none", "openathens", "shibboleth")
    """
    try:
        import hashlib

        from scitex.scholar.pipelines import ScholarPipelineSingle

        # Use ScholarPipelineSingle - same as CLI, has AuthenticationGateway
        pipeline = ScholarPipelineSingle(
            browser_mode="stealth",
            chrome_profile="system",
        )

        # Process paper through full pipeline with authentication
        # Returns (paper, symlink_path) tuple
        paper, _symlink_path = await pipeline.process_single_paper(
            doi_or_title=doi,
            project=None,
            force=False,
        )

        # Compute paper ID from DOI (same algorithm as pipeline)
        paper_id = hashlib.md5(f"DOI:{doi}".encode()).hexdigest()[:8].upper()

        # Construct PDF path directly from library structure
        library_dir = _get_scholar_dir() / "library" / "MASTER"
        paper_dir = library_dir / paper_id

        # Find PDF file in paper directory
        pdf_path = None
        if paper_dir and paper_dir.exists():
            for pdf_file in paper_dir.glob("*.pdf"):
                pdf_path = pdf_file
                break

        if pdf_path and pdf_path.exists():
            return {
                "success": True,
                "doi": doi,
                "path": str(pdf_path),
                "paper_id": paper_id,
                "title": paper.metadata.basic.title,
                "timestamp": datetime.now().isoformat(),
            }
        else:
            return {
                "success": False,
                "doi": doi,
                "error": "PDF not downloaded (may require manual access)",
                "paper_id": paper_id,
                "title": paper.metadata.basic.title,
                "pdf_urls_found": paper.metadata.url.pdfs or [],
            }

    except Exception as e:
        return {"success": False, "doi": doi, "error": str(e)}


async def download_pdfs_batch_handler(
    dois: list[str] | None = None,
    bibtex_path: str | None = None,
    project: str | None = None,
    output_dir: str | None = None,
    max_concurrent: int = 3,
    resume: bool = True,
) -> dict:
    """Download PDFs for multiple papers using ScholarPipelineParallel.

    Delegates to ScholarPipelineParallel which has proper AuthenticationGateway
    support for institutional access to paywalled content.
    """
    try:
        from scitex.scholar import Scholar
        from scitex.scholar.pipelines import ScholarPipelineParallel

        # Collect DOIs
        doi_list = []
        skipped = []

        if bibtex_path:
            scholar = Scholar()
            papers = scholar.load_bibtex(bibtex_path)
            for paper in papers:
                if paper.metadata.id.doi:
                    doi_list.append(paper.metadata.id.doi)
                else:
                    skipped.append(
                        {
                            "title": paper.metadata.basic.title or "(no title)",
                            "reason": "No DOI",
                        }
                    )
        elif dois:
            doi_list = dois
        else:
            return {
                "success": False,
                "error": "Either dois or bibtex_path required",
            }

        if not doi_list:
            return {
                "success": True,
                "total_dois": 0,
                "downloaded": [],
                "downloaded_count": 0,
                "failed": [],
                "failed_count": 0,
                "skipped": skipped,
                "skipped_count": len(skipped),
                "timestamp": datetime.now().isoformat(),
            }

        # Use ScholarPipelineParallel - same as CLI, has AuthenticationGateway
        pipeline = ScholarPipelineParallel(
            num_workers=max_concurrent,
            browser_mode="stealth",
            base_chrome_profile="system",
        )

        # Process papers through parallel pipeline with authentication
        papers = await pipeline.process_papers_from_list_async(
            doi_or_title_list=doi_list,
            project=project,
        )

        # Collect results
        downloaded = []
        failed = []
        processed_dois = set()
        library_dir = _get_scholar_dir() / "library" / "MASTER"

        for paper in papers:
            if paper is None:
                continue

            doi = paper.metadata.id.doi
            processed_dois.add(doi)

            # Compute paper ID from DOI (same algorithm as pipeline)
            paper_id = hashlib.md5(f"DOI:{doi}".encode()).hexdigest()[:8].upper()
            paper_dir = library_dir / paper_id

            # Find PDF file in paper directory
            pdf_path = None
            if paper_dir and paper_dir.exists():
                for pdf_file in paper_dir.glob("*.pdf"):
                    pdf_path = pdf_file
                    break

            if pdf_path and pdf_path.exists():
                downloaded.append(
                    {
                        "doi": doi,
                        "path": str(pdf_path),
                        "paper_id": paper_id,
                        "title": paper.metadata.basic.title,
                    }
                )
            else:
                failed.append(
                    {
                        "doi": doi,
                        "reason": "PDF not downloaded",
                        "paper_id": paper_id,
                    }
                )

        # Add DOIs that weren't processed at all
        for doi in doi_list:
            if doi not in processed_dois:
                failed.append({"doi": doi, "reason": "Processing failed"})

        return {
            "success": True,
            "total_dois": len(doi_list),
            "downloaded": downloaded,
            "downloaded_count": len(downloaded),
            "failed": failed,
            "failed_count": len(failed),
            "skipped": skipped,
            "skipped_count": len(skipped),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_library_status_handler(
    project: str | None = None,
    include_details: bool = False,
) -> dict:
    """Get library status."""
    try:
        library_dir = _get_scholar_dir() / "library"

        if project:
            project_dir = library_dir / project
        else:
            project_dir = library_dir

        if not project_dir.exists():
            return {
                "success": True,
                "exists": False,
                "message": f"Library directory not found: {project_dir}",
            }

        # Count PDFs
        pdf_files = list(project_dir.rglob("*.pdf"))
        metadata_files = list(project_dir.rglob("metadata.json"))

        status = {
            "success": True,
            "exists": True,
            "path": str(project_dir),
            "pdf_count": len(pdf_files),
            "entry_count": len(metadata_files),
            "timestamp": datetime.now().isoformat(),
        }

        if include_details:
            entries = []
            for meta_file in metadata_files[:50]:  # Limit to 50 for performance
                try:
                    with open(meta_file) as f:
                        meta = json.load(f)
                    pdf_exists = any(
                        (meta_file.parent / f).exists()
                        for f in meta_file.parent.glob("*.pdf")
                    )
                    entries.append(
                        {
                            "id": meta_file.parent.name,
                            "title": meta.get("title", "Unknown"),
                            "doi": meta.get("doi"),
                            "has_pdf": pdf_exists,
                        }
                    )
                except Exception:
                    pass

            status["entries"] = entries

        return status

    except Exception as e:
        return {"success": False, "error": str(e)}


async def parse_bibtex_handler(bibtex_path: str) -> dict:
    """Parse a BibTeX file."""
    try:
        from scitex.scholar import Scholar

        loop = asyncio.get_running_loop()
        scholar = Scholar()

        def do_parse():
            papers = scholar.load_bibtex(bibtex_path)
            return papers

        papers = await loop.run_in_executor(None, do_parse)

        results = []
        for paper in papers:
            authors = paper.metadata.basic.authors or []
            results.append(
                {
                    "title": paper.metadata.basic.title,
                    "authors": authors[:5] if authors else [],
                    "year": paper.metadata.basic.year,
                    "doi": paper.metadata.id.doi,
                    "journal": paper.metadata.publication.journal,
                    "bibtex_key": getattr(paper, "bibtex_key", None),
                }
            )

        return {
            "success": True,
            "count": len(results),
            "path": bibtex_path,
            "papers": results,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


async def validate_pdfs_handler(
    project: str | None = None,
    pdf_paths: list[str] | None = None,
) -> dict:
    """Validate PDF files."""
    try:
        from pypdf import PdfReader

        if pdf_paths:
            paths = [Path(p) for p in pdf_paths]
        elif project:
            library_dir = _get_scholar_dir() / "library" / project
            paths = list(library_dir.rglob("*.pdf"))
        else:
            library_dir = _get_scholar_dir() / "library"
            paths = list(library_dir.rglob("*.pdf"))

        results = {
            "total": len(paths),
            "valid": [],
            "invalid": [],
        }

        for pdf_path in paths:
            try:
                reader = PdfReader(str(pdf_path))
                page_count = len(reader.pages)

                # Check if it has text content
                has_text = False
                if page_count > 0:
                    text = reader.pages[0].extract_text()
                    has_text = bool(text and len(text.strip()) > 100)

                results["valid"].append(
                    {
                        "path": str(pdf_path),
                        "pages": page_count,
                        "has_text": has_text,
                        "size_kb": round(pdf_path.stat().st_size / 1024, 2),
                    }
                )
            except Exception as e:
                results["invalid"].append(
                    {
                        "path": str(pdf_path),
                        "error": str(e),
                    }
                )

        return {
            "success": True,
            **results,
            "valid_count": len(results["valid"]),
            "invalid_count": len(results["invalid"]),
            "timestamp": datetime.now().isoformat(),
        }

    except ImportError:
        return {"success": False, "error": "pypdf not installed"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def resolve_openurls_handler(
    dois: list[str],
    resolver_url: str | None = None,
    resume: bool = True,
) -> dict:
    """Resolve OpenURLs for DOIs using OpenURLResolver with browser automation.

    This uses the institutional OpenURL resolver to get access URLs for papers.
    Requires browser context for navigation.

    Args:
        dois: List of DOIs to resolve
        resolver_url: Custom OpenURL resolver URL (uses config default if None)
        resume: Whether to skip already resolved DOIs
    """
    try:
        from scitex.scholar.auth import ScholarAuthManager
        from scitex.scholar.auth.gateway import OpenURLResolver
        from scitex.scholar.browser import ScholarBrowserManager
        from scitex.scholar.config import ScholarConfig

        config = ScholarConfig.load()
        auth_manager = ScholarAuthManager()
        browser_manager = ScholarBrowserManager(
            auth_manager=auth_manager,
            chrome_profile_name="system",
            browser_mode="stealth",
        )

        results = {
            "resolved": [],
            "failed": [],
        }

        try:
            # Get authenticated browser context
            (
                browser,
                context,
            ) = await browser_manager.get_authenticated_browser_and_context_async()

            # Create OpenURL resolver
            openurl_resolver = OpenURLResolver(config=config)

            # Create a page for resolution
            page = await context.new_page()

            try:
                for doi in dois:
                    try:
                        # Resolve OpenURL for this DOI using browser
                        resolved_url = await openurl_resolver.resolve_doi(doi, page)
                        if resolved_url and resolved_url != "skipped":
                            results["resolved"].append(
                                {"doi": doi, "url": resolved_url}
                            )
                        else:
                            results["failed"].append(
                                {"doi": doi, "reason": "No URL resolved"}
                            )
                    except Exception as e:
                        results["failed"].append({"doi": doi, "reason": str(e)})
            finally:
                await page.close()

        finally:
            await browser_manager.close()

        return {
            "success": True,
            **results,
            "total": len(dois),
            "resolved_count": len(results["resolved"]),
            "failed_count": len(results["failed"]),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


async def authenticate_handler(
    method: str,
    institution: str | None = None,
    force: bool = False,
    confirm: bool = False,
) -> dict:
    """Authenticate with institutional access (OpenAthens, Shibboleth).

    This opens a browser window for SSO login. The process:
    1. Opens browser to authentication provider
    2. Automates login if credentials are configured
    3. Waits for 2FA approval if required
    4. Stores session cookies for future use

    Args:
        method: Authentication method ("openathens" or "shibboleth")
        institution: Institution identifier (e.g., "unimelb")
        force: Force re-authentication even if session exists
        confirm: Set to True to proceed with authentication after reviewing requirements
    """
    try:
        # Get email from environment based on method
        email_env_map = {
            "openathens": "SCITEX_SCHOLAR_OPENATHENS_EMAIL",
            "shibboleth": "SCITEX_SCHOLAR_SHIBBOLETH_EMAIL",
            "ezproxy": "SCITEX_SCHOLAR_EZPROXY_EMAIL",
        }
        sso_env_vars = ["UNIMELB_SSO_USERNAME", "UNIMELB_SSO_PASSWORD"]

        email_var = email_env_map.get(method)
        email = os.getenv(email_var) if email_var else None

        # Check environment variables
        env_status = {
            "email_configured": bool(email),
            "email_var": email_var,
            "email": email if email else None,
            "sso_username_set": bool(os.getenv("UNIMELB_SSO_USERNAME")),
            "sso_password_set": bool(os.getenv("UNIMELB_SSO_PASSWORD")),
        }

        # If confirm=False, return requirements check (don't start login yet)
        if not confirm:
            requirements_met = email is not None

            return {
                "success": True,
                "status": "awaiting_confirmation",
                "method": method,
                "message": "Please review requirements before starting SSO login",
                "requirements": {
                    "email_configured": env_status["email_configured"],
                    "email": env_status["email"],
                    "sso_automation_available": (
                        env_status["sso_username_set"]
                        and env_status["sso_password_set"]
                    ),
                },
                "warnings": (
                    []
                    if requirements_met
                    else [f"Environment variable {email_var} is NOT set"]
                ),
                "instructions": [
                    "A browser window will open for SSO login",
                    "If SSO credentials are set, login will be automated",
                    "You may need to approve 2FA on your device",
                    "Do NOT close the browser until authentication completes",
                ],
                "next_step": (
                    f"Call authenticate(method='{method}', confirm=True) to proceed"
                    if requirements_met
                    else f"Set {email_var} first, then call with confirm=True"
                ),
                "timestamp": datetime.now().isoformat(),
            }

        # confirm=True - proceed with authentication
        if not email:
            return {
                "success": False,
                "error": f"Environment variable {email_var} not set. "
                f"Please set your institutional email first.",
                "hint": f"export {email_var}='your.email@institution.edu'",
            }

        from scitex.scholar.auth import ScholarAuthManager

        # Create auth manager with appropriate email
        auth_kwargs = {f"email_{method}": email}
        auth_manager = ScholarAuthManager(**auth_kwargs)

        # Check if already authenticated (unless force)
        if not force:
            is_auth = await auth_manager.is_authenticate_async(verify_live=True)
            if is_auth:
                return {
                    "success": True,
                    "method": method,
                    "status": "already_authenticated",
                    "message": "Using existing valid session",
                    "email": email,
                    "timestamp": datetime.now().isoformat(),
                }

        # Perform authentication (opens browser)
        auth_result = await auth_manager.authenticate_async(provider_name=method)

        if auth_result:
            # Get session info
            provider = auth_manager.get_active_provider()
            session_info = {}
            if hasattr(provider, "get_session_info_async"):
                session_info = await provider.get_session_info_async()

            return {
                "success": True,
                "method": method,
                "status": "authenticated",
                "message": "Authentication successful",
                "email": email,
                "session_expires": session_info.get("expiry"),
                "cookies_count": len(auth_result.get("cookies", [])),
                "timestamp": datetime.now().isoformat(),
            }
        else:
            return {
                "success": False,
                "method": method,
                "status": "failed",
                "error": "Authentication failed or was cancelled",
            }

    except Exception as e:
        return {"success": False, "error": str(e)}


async def check_auth_status_handler(
    method: str = "openathens",
    verify_live: bool = False,
) -> dict:
    """Check current authentication status without starting login.

    Args:
        method: Authentication method to check ("openathens", "shibboleth", "ezproxy")
        verify_live: If True, verify session is still valid with remote server
    """
    try:
        from scitex.scholar.auth import ScholarAuthManager

        # Get email from environment
        email_env_map = {
            "openathens": "SCITEX_SCHOLAR_OPENATHENS_EMAIL",
            "shibboleth": "SCITEX_SCHOLAR_SHIBBOLETH_EMAIL",
            "ezproxy": "SCITEX_SCHOLAR_EZPROXY_EMAIL",
        }

        email_var = email_env_map.get(method)
        email = os.getenv(email_var) if email_var else None

        if not email:
            return {
                "success": True,
                "authenticated": False,
                "method": method,
                "reason": f"No email configured ({email_var} not set)",
                "timestamp": datetime.now().isoformat(),
            }

        # Create auth manager
        auth_kwargs = {f"email_{method}": email}
        auth_manager = ScholarAuthManager(**auth_kwargs)

        # Check authentication status
        is_auth = await auth_manager.is_authenticate_async(verify_live=verify_live)

        result = {
            "success": True,
            "authenticated": is_auth,
            "method": method,
            "email": email,
            "verified_live": verify_live,
            "timestamp": datetime.now().isoformat(),
        }

        if is_auth:
            # Get session details
            provider = auth_manager.get_active_provider()
            if hasattr(provider, "get_session_info_async"):
                session_info = await provider.get_session_info_async()
                result["session_expires"] = session_info.get("expiry")
                result["cookies_count"] = session_info.get("cookies_count", 0)

        return result

    except Exception as e:
        return {"success": False, "error": str(e)}


async def logout_handler(
    method: str = "openathens",
    clear_cache: bool = True,
) -> dict:
    """Logout from institutional authentication and clear session.

    Args:
        method: Authentication method to logout from
        clear_cache: If True, also clear cached session files
    """
    try:
        from scitex.scholar.auth import ScholarAuthManager

        email_env_map = {
            "openathens": "SCITEX_SCHOLAR_OPENATHENS_EMAIL",
            "shibboleth": "SCITEX_SCHOLAR_SHIBBOLETH_EMAIL",
            "ezproxy": "SCITEX_SCHOLAR_EZPROXY_EMAIL",
        }

        email_var = email_env_map.get(method)
        email = os.getenv(email_var) if email_var else None

        if email:
            auth_kwargs = {f"email_{method}": email}
            auth_manager = ScholarAuthManager(**auth_kwargs)
            await auth_manager.logout_async()

        # Clear cache files if requested
        if clear_cache:
            cache_dir = _get_scholar_dir() / "cache" / method
            if cache_dir.exists():
                import shutil

                shutil.rmtree(cache_dir, ignore_errors=True)

        return {
            "success": True,
            "method": method,
            "cache_cleared": clear_cache,
            "message": f"Logged out from {method}",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


async def export_papers_handler(
    output_path: str,
    project: str | None = None,
    format: str = "bibtex",
    filter_has_pdf: bool = False,
) -> dict:
    """Export papers to various formats.

    Args:
        output_path: Path to save the exported file
        project: Project name to export (exports all if None)
        format: Export format (bibtex, json, csv, ris)
        filter_has_pdf: If True, only export papers with PDFs
    """
    try:
        from scitex.scholar import Scholar

        loop = asyncio.get_running_loop()
        scholar = Scholar(project=project) if project else Scholar()

        def do_export():
            # Get papers from project using load_project
            papers = scholar.load_project(project=project)

            if filter_has_pdf:
                # Filter papers that have PDF paths
                filtered = []
                for p in papers:
                    if p.metadata.path.pdfs and len(p.metadata.path.pdfs) > 0:
                        filtered.append(p)
                papers = type(papers)(filtered, project=project)

            # Export based on format
            out_path = Path(output_path)
            out_path.parent.mkdir(parents=True, exist_ok=True)

            if format == "bibtex":
                scholar.save_papers_as_bibtex(papers, str(out_path))
            elif format == "json":
                with open(out_path, "w") as f:
                    json.dump([p.to_dict() for p in papers], f, indent=2)
            elif format == "csv":
                import csv

                with open(out_path, "w", newline="") as f:
                    writer = csv.DictWriter(
                        f, fieldnames=["title", "authors", "year", "doi", "journal"]
                    )
                    writer.writeheader()
                    for p in papers:
                        authors = p.metadata.basic.authors or []
                        writer.writerow(
                            {
                                "title": p.metadata.basic.title,
                                "authors": ("; ".join(authors[:3]) if authors else ""),
                                "year": p.metadata.basic.year,
                                "doi": p.metadata.id.doi,
                                "journal": p.metadata.publication.journal,
                            }
                        )
            elif format == "ris":
                # RIS format not directly supported, use BibTeX as fallback
                scholar.save_papers_as_bibtex(papers, str(out_path))

            return {"count": len(papers), "path": str(out_path)}

        result = await loop.run_in_executor(None, do_export)

        return {
            "success": True,
            "format": format,
            **result,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


async def create_project_handler(
    project_name: str,
    description: str | None = None,
) -> dict:
    """Create a new scholar project for organizing papers.

    Args:
        project_name: Name of the project to create
        description: Optional project description
    """
    try:
        library_dir = _get_scholar_dir() / "library"
        project_dir = library_dir / project_name

        if project_dir.exists():
            return {
                "success": False,
                "error": f"Project '{project_name}' already exists",
                "path": str(project_dir),
            }

        # Create project directory
        project_dir.mkdir(parents=True, exist_ok=True)

        # Create project info file
        info_dir = project_dir / "info"
        info_dir.mkdir(exist_ok=True)

        project_info = {
            "name": project_name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "paper_count": 0,
        }

        info_file = info_dir / "project.json"
        with open(info_file, "w") as f:
            json.dump(project_info, f, indent=2)

        return {
            "success": True,
            "project": project_name,
            "path": str(project_dir),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


async def list_projects_handler() -> dict:
    """List all scholar projects."""
    try:
        library_dir = _get_scholar_dir() / "library"

        if not library_dir.exists():
            return {
                "success": True,
                "count": 0,
                "projects": [],
            }

        projects = []
        for item in library_dir.iterdir():
            if item.is_dir() and item.name != "MASTER":
                # Count papers (symlinks or directories with metadata.json)
                paper_count = 0
                for sub in item.iterdir():
                    if sub.is_symlink() or (
                        sub.is_dir() and (sub / "metadata.json").exists()
                    ):
                        paper_count += 1

                # Check for project info
                info_file = item / "info" / "project.json"
                description = None
                if info_file.exists():
                    with open(info_file) as f:
                        info = json.load(f)
                        description = info.get("description")

                projects.append(
                    {
                        "name": item.name,
                        "description": description,
                        "paper_count": paper_count,
                        "path": str(item),
                    }
                )

        return {
            "success": True,
            "count": len(projects),
            "projects": projects,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


async def add_papers_to_project_handler(
    project: str,
    dois: list[str] | None = None,
    bibtex_path: str | None = None,
) -> dict:
    """Add papers to a project by DOI or from BibTeX file.

    Args:
        project: Target project name
        dois: List of DOIs to add
        bibtex_path: Path to BibTeX file with papers to add
    """
    try:
        from scitex.scholar import Scholar

        loop = asyncio.get_running_loop()
        scholar = Scholar(project=project)

        def do_add():
            added = []
            failed = []

            if bibtex_path:
                # Load papers from BibTeX
                papers = scholar.load_bibtex(bibtex_path)
                for paper in papers:
                    try:
                        # Save to library (this creates symlinks from project to MASTER)
                        scholar.save_papers_to_library([paper])
                        added.append(
                            {
                                "title": paper.metadata.basic.title,
                                "doi": paper.metadata.id.doi,
                            }
                        )
                    except Exception as e:
                        failed.append(
                            {
                                "title": paper.metadata.basic.title,
                                "error": str(e),
                            }
                        )

            elif dois:
                for doi in dois:
                    try:
                        # Create paper from DOI and save
                        from scitex.scholar.core import Paper

                        paper = Paper(doi=doi)
                        scholar.save_papers_to_library([paper])
                        added.append({"doi": doi})
                    except Exception as e:
                        failed.append({"doi": doi, "error": str(e)})

            return {"added": added, "failed": failed}

        result = await loop.run_in_executor(None, do_add)

        return {
            "success": True,
            "project": project,
            **result,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


async def parse_pdf_content_handler(
    pdf_path: str | None = None,
    doi: str | None = None,
    project: str | None = None,
    mode: str = "scientific",
    extract_sections: bool = True,
    extract_tables: bool = False,
    extract_images: bool = False,
    max_pages: int | None = None,
) -> dict:
    """Parse PDF content to extract text, sections, tables, and metadata.

    Args:
        pdf_path: Direct path to PDF file
        doi: DOI to find PDF in library
        project: Project name to search for PDF
        mode: Extraction mode - "text", "sections", "tables", "images",
              "metadata", "pages", "scientific", or "full"
        extract_sections: Whether to parse IMRaD sections
        extract_tables: Whether to extract tables
        extract_images: Whether to extract images
        max_pages: Maximum pages to process (None = all)
    """
    try:
        loop = asyncio.get_running_loop()

        def do_parse():
            target_path = None

            # Find PDF path
            if pdf_path:
                target_path = Path(pdf_path)
            elif doi:
                # Search library for PDF by DOI
                library_dir = _get_scholar_dir() / "library"
                master_dir = library_dir / "MASTER"

                if master_dir.exists():
                    for paper_dir in master_dir.iterdir():
                        if paper_dir.is_dir():
                            meta_file = paper_dir / "metadata.json"
                            if meta_file.exists():
                                with open(meta_file) as f:
                                    meta = json.load(f)
                                if meta.get("doi") == doi:
                                    pdf_files = list(paper_dir.glob("*.pdf"))
                                    if pdf_files:
                                        target_path = pdf_files[0]
                                        break

            if not target_path or not target_path.exists():
                return {
                    "error": f"PDF not found: {pdf_path or doi}",
                    "searched_library": bool(doi),
                }

            # Use scitex.io PDF loader
            try:
                from scitex.io import load

                result = load(str(target_path), mode=mode)

                # Build response based on mode
                parsed = {
                    "path": str(target_path),
                    "mode": mode,
                    "file_size_kb": round(target_path.stat().st_size / 1024, 2),
                }

                if mode == "text":
                    parsed["text"] = (
                        result[:5000] + "..." if len(result) > 5000 else result
                    )
                    parsed["text_length"] = len(result)

                elif mode == "sections":
                    parsed["sections"] = {}
                    for section_name, content in result.items():
                        if content:
                            parsed["sections"][section_name] = (
                                content[:1000] + "..."
                                if len(content) > 1000
                                else content
                            )

                elif mode == "metadata":
                    parsed["metadata"] = result

                elif mode == "pages":
                    parsed["page_count"] = len(result)
                    parsed["pages"] = [
                        {
                            "page": i + 1,
                            "text_preview": (
                                text[:500] + "..." if len(text) > 500 else text
                            ),
                        }
                        for i, text in enumerate(result[:5])
                    ]

                elif mode == "tables":
                    parsed["table_count"] = len(result) if result else 0
                    parsed["tables"] = result[:5] if result else []

                elif mode == "scientific":
                    # Scientific mode returns structured paper data
                    parsed["title"] = result.get("title")
                    parsed["abstract"] = result.get("abstract")
                    parsed["sections"] = {
                        k: v[:500] + "..." if v and len(v) > 500 else v
                        for k, v in result.get("sections", {}).items()
                    }
                    parsed["references_count"] = len(result.get("references", []))

                elif mode == "full":
                    # Full mode - summarize all components
                    parsed["text_length"] = len(result.get("text", ""))
                    parsed["sections"] = list(result.get("sections", {}).keys())
                    parsed["metadata"] = result.get("metadata", {})
                    parsed["page_count"] = len(result.get("pages", []))
                    parsed["table_count"] = len(result.get("tables", []))

                return parsed

            except ImportError:
                # Fallback to pypdf if scitex.io not available
                from pypdf import PdfReader

                reader = PdfReader(str(target_path))
                page_count = len(reader.pages)

                text_content = []
                for i, page in enumerate(reader.pages):
                    if max_pages and i >= max_pages:
                        break
                    text_content.append(page.extract_text() or "")

                full_text = "\n\n".join(text_content)

                return {
                    "path": str(target_path),
                    "mode": "text",
                    "page_count": page_count,
                    "text": (
                        full_text[:5000] + "..." if len(full_text) > 5000 else full_text
                    ),
                    "text_length": len(full_text),
                    "fallback": "pypdf",
                }

        result = await loop.run_in_executor(None, do_parse)

        if "error" in result:
            return {"success": False, **result}

        return {
            "success": True,
            **result,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


# EOF
