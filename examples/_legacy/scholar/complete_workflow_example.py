#!/usr/bin/env python3
"""Example: Complete 10-step automated literature search workflow."""

import asyncio
from pathlib import Path
from datetime import datetime
from scitex.scholar import Scholar
from scitex.scholar.auth import AuthenticationManager, OpenAthensAuthenticator
from scitex.scholar.resolve_dois import ResumableDOIResolver
from scitex.scholar.open_url import ResumableOpenURLResolver
from scitex.scholar.enrichment import ResumableMetadataEnricher
from scitex.scholar.validation import PDFValidator
from scitex.scholar.database import PaperDatabase
from scitex.scholar.search import SemanticSearchEngine


async def complete_workflow_example():
    """Demonstrate the complete 10-step Scholar workflow."""

    print("=== SciTeX Scholar - Complete Workflow Example ===")
    print("=" * 60)
    print("This demonstrates all 10 steps of automated literature search\n")

    # Configuration
    config = {
        "openathens_email": "user@university.edu",  # Update with your email
        "openathens_password": None,  # Will prompt if needed
        "openurl_resolver": "https://unimelb.hosted.exlibrisgroup.com/primo-explore/openurl",
        "bibtex_file": "./papers.bib",
        "output_dir": "./scholar_output",
    }

    # Create output directory
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize Scholar
    scholar = Scholar()

    # ========================================
    # STEP 1-2: Authentication & Cookie Management
    # ========================================
    print("\n" + "="*60)
    print("STEPS 1-2: OpenAthens Authentication with Cookie Persistence")
    print("="*60)

    # Note: In practice, authentication happens automatically when needed
    # This shows manual setup for demonstration
    auth_manager = AuthenticationManager()

    # Add OpenAthens authenticator
    openathens = OpenAthensAuthenticator(
        email=config["openathens_email"],
        password=config["openathens_password"]
    )
    auth_manager.add_authenticator("openathens", openathens)

    print("✓ Authentication manager configured")
    print("✓ Cookies will be automatically saved for future sessions")

    # ========================================
    # STEP 3: Load BibTeX
    # ========================================
    print("\n" + "="*60)
    print("STEP 3: Load Papers from BibTeX")
    print("="*60)

    bibtex_path = Path(config["bibtex_file"])
    if bibtex_path.exists():
        papers = scholar.load_bibtex(bibtex_path)
        print(f"✓ Loaded {len(papers)} papers from {bibtex_path}")
    else:
        # Create sample BibTeX for demo
        print("Creating sample BibTeX file...")
        sample_bib = """
@article{smith2024deep,
  title={Deep Learning for Climate Change Prediction},
  author={Smith, Jane and Doe, John},
  journal={Nature Climate Change},
  year={2024}
}

@article{brown2024transformer,
  title={Transformer Models in Scientific Computing},
  author={Brown, Alice},
  journal={Science},
  year={2024}
}

@article{wilson2023machine,
  title={Machine Learning for Weather Forecasting},
  author={Wilson, Bob and Davis, Carol},
  journal={Weather and Forecasting},
  year={2023}
}
"""
        bibtex_path.write_text(sample_bib)
        papers = scholar.load_bibtex(bibtex_path)
        print(f"✓ Created and loaded {len(papers)} sample papers")

    # Display loaded papers
    for i, paper in enumerate(papers[:3], 1):
        print(f"  {i}. {paper.title} ({paper.year})")

    # ========================================
    # STEP 4: Resolve DOIs (Resumable)
    # ========================================
    print("\n" + "="*60)
    print("STEP 4: Resolve DOIs from Paper Information (Resumable)")
    print("="*60)

    resolver = ResumableDOIResolver(
        progress_file=output_dir / "doi_resolution_progress.json"
    )

    print("Resolving DOIs with progress tracking...")
    doi_results = resolver.resolve_batch(papers)

    resolved_count = sum(1 for doi in doi_results.values() if doi)
    print(f"✓ Resolved {resolved_count}/{len(papers)} DOIs")

    # Update papers with DOIs
    for paper, doi in zip(papers, doi_results.values()):
        if doi and not paper.doi:
            paper.doi = doi

    # ========================================
    # STEP 5: Resolve Publisher URLs (Resumable)
    # ========================================
    print("\n" + "="*60)
    print("STEP 5: Resolve Publisher URLs via OpenURL (Resumable)")
    print("="*60)

    url_resolver = ResumableOpenURLResolver(
        auth_manager=auth_manager,
        resolver_url=config["openurl_resolver"],
        progress_file=output_dir / "url_resolution_progress.json"
    )

    # Get DOIs for resolution
    dois_to_resolve = [p.doi for p in papers if p.doi]

    if dois_to_resolve:
        print(f"Resolving URLs for {len(dois_to_resolve)} DOIs...")
        url_results = await url_resolver.resolve_from_dois_async(dois_to_resolve)

        resolved_urls = sum(1 for url in url_results.values() if url)
        print(f"✓ Resolved {resolved_urls}/{len(dois_to_resolve)} URLs")

        # Update papers with URLs
        for paper in papers:
            if paper.doi and paper.doi in url_results:
                paper.url = url_results[paper.doi]

    # ========================================
    # STEP 6: Enrich Metadata (Resumable)
    # ========================================
    print("\n" + "="*60)
    print("STEP 6: Enrich Papers with Metadata (Resumable)")
    print("="*60)

    enricher = ResumableMetadataEnricher(
        progress_file=output_dir / "enrichment_progress.json"
    )

    print("Enriching with impact factors and citations...")
    enriched_papers = enricher.enrich_batch(
        papers,
        add_impact_factors=True,
        add_citations=True,
        add_abstracts=True
    )

    # Show enrichment results
    enriched_count = sum(1 for p in enriched_papers if p.impact_factor or p.citation_count)
    print(f"✓ Enriched {enriched_count}/{len(papers)} papers")

    # Save enriched bibliography
    enriched_bib = output_dir / "papers_enriched.bib"
    enriched_papers.to_bibtex(enriched_bib)
    print(f"✓ Saved enriched bibliography to {enriched_bib}")

    # ========================================
    # STEP 7: Download PDFs with Crawl4AI
    # ========================================
    print("\n" + "="*60)
    print("STEP 7: Download PDFs using Crawl4AI")
    print("="*60)

    pdf_dir = output_dir / "pdfs"
    pdf_dir.mkdir(exist_ok=True)

    print(f"Downloading PDFs to {pdf_dir}...")
    download_results = await scholar.download_pdfs_async(
        enriched_papers,
        download_dir=pdf_dir,
        max_workers=3
    )

    successful_downloads = sum(1 for r in download_results.values() if r.get("success"))
    print(f"✓ Downloaded {successful_downloads}/{len(papers)} PDFs")

    # ========================================
    # STEP 8: Validate PDFs
    # ========================================
    print("\n" + "="*60)
    print("STEP 8: Validate Downloaded PDFs")
    print("="*60)

    validator = PDFValidator(cache_results=True)

    # Validate all downloaded PDFs
    validation_results = {}
    for paper in enriched_papers:
        if paper.doi in download_results and download_results[paper.doi].get("success"):
            pdf_path = download_results[paper.doi]["path"]
            if Path(pdf_path).exists():
                validation = validator.validate(pdf_path)
                validation_results[paper.doi] = validation

    valid_pdfs = sum(1 for v in validation_results.values() if v.is_valid and v.is_complete)
    print(f"✓ Validated PDFs: {valid_pdfs}/{len(validation_results)} complete and valid")

    # Generate validation report
    if validation_results:
        report_path = output_dir / "validation_report.txt"
        report = validator.generate_report(
            {doi: v for doi, v in validation_results.items()},
            report_path
        )
        print(f"✓ Saved validation report to {report_path}")

    # ========================================
    # STEP 9: Organize in Database
    # ========================================
    print("\n" + "="*60)
    print("STEP 9: Organize Papers in Database")
    print("="*60)

    db = PaperDatabase(output_dir / "database")

    # Import papers to database
    entry_ids = db.import_from_papers(enriched_papers)
    print(f"✓ Added {len(entry_ids)} papers to database")

    # Update with download and validation info
    for i, (paper, entry_id) in enumerate(zip(enriched_papers, entry_ids)):
        entry = db.get_entry(entry_id)

        # Update download status
        if paper.doi in download_results:
            if download_results[paper.doi].get("success"):
                entry.download_status = "downloaded"
                entry.pdf_path = download_results[paper.doi]["path"]
                entry.downloaded_date = datetime.now()

                # Update validation status
                if paper.doi in validation_results:
                    entry.update_from_validation(validation_results[paper.doi])
            else:
                entry.download_status = "failed"

        # Save updates
        db.update_entry(entry_id, entry.to_dict())

    # Organize PDFs by year/journal
    print("\nOrganizing PDFs by year and journal...")
    organized_count = 0
    for entry_id in entry_ids:
        entry = db.get_entry(entry_id)
        if entry.pdf_path and Path(entry.pdf_path).exists():
            try:
                new_path = db.organize_pdf(entry_id, entry.pdf_path, "year_journal")
                organized_count += 1
            except Exception as e:
                print(f"  Failed to organize {entry_id}: {e}")

    print(f"✓ Organized {organized_count} PDFs")

    # ========================================
    # STEP 10: Semantic Search
    # ========================================
    print("\n" + "="*60)
    print("STEP 10: Build Semantic Search Index")
    print("="*60)

    engine = SemanticSearchEngine(
        database=db,
        model_name="all-MiniLM-L6-v2"
    )

    # Index all papers
    print("Indexing papers for semantic search...")
    index_stats = engine.index_papers()
    print(f"✓ Indexed {index_stats['indexed']} papers")

    # Demonstrate search capabilities
    print("\nDemonstrating search capabilities:")

    # 1. Natural language search
    query = "machine learning climate prediction"
    print(f"\n1. Searching for: '{query}'")
    search_results = engine.search_by_text(query, k=3)

    for i, (paper, score) in enumerate(search_results, 1):
        print(f"   {i}. [{score:.3f}] {paper.title}")

    # 2. Find similar papers
    if entry_ids:
        print(f"\n2. Finding papers similar to: {db.get_entry(entry_ids[0]).title}")
        similar = engine.find_similar_papers(entry_ids[0], k=3)

        for i, (paper, similarity) in enumerate(similar, 1):
            print(f"   {i}. [{similarity:.3f}] {paper.title}")

    # 3. Get recommendations
    if len(entry_ids) >= 2:
        print(f"\n3. Getting recommendations based on {len(entry_ids[:2])} papers")
        recommendations = engine.recommend_papers(entry_ids[:2], k=3)

        for i, (paper, score) in enumerate(recommendations, 1):
            print(f"   {i}. [{score:.3f}] {paper.title}")

    # ========================================
    # Summary
    # ========================================
    print("\n" + "="*60)
    print("WORKFLOW COMPLETE - Summary")
    print("="*60)

    stats = db.get_statistics()
    print(f"✓ Total papers in database: {stats['total_entries']}")
    print(f"✓ Papers with DOIs: {stats['index_stats']['total_dois']}")
    print(f"✓ Downloaded PDFs: {stats['pdf_stats']['total']}")
    print(f"✓ Valid PDFs: {stats['pdf_stats']['valid']}")
    print(f"✓ Searchable PDFs: {stats['pdf_stats']['searchable']}")
    print(f"✓ Papers indexed for search: {engine.get_statistics()['indexed_entries']}")

    print(f"\nAll outputs saved to: {output_dir}")
    print("  - database/: Organized paper database")
    print("  - pdfs/: Downloaded and organized PDFs")
    print("  - papers_enriched.bib: Enriched bibliography")
    print("  - validation_report.txt: PDF validation results")


def print_workflow_steps():
    """Print overview of the 10-step workflow."""

    print("\n" + "="*60)
    print("The 10-Step Scholar Workflow")
    print("="*60)

    steps = [
        ("1-2", "Authentication", "OpenAthens login with cookie persistence"),
        ("3", "Load BibTeX", "Parse bibliography files"),
        ("4", "Resolve DOIs", "Find DOIs from titles (resumable)"),
        ("5", "Resolve URLs", "Get publisher URLs via OpenURL (resumable)"),
        ("6", "Enrich Metadata", "Add impact factors, citations (resumable)"),
        ("7", "Download PDFs", "Crawl4AI for anti-bot bypass"),
        ("8", "Validate PDFs", "Check completeness and readability"),
        ("9", "Database", "Organize papers with metadata"),
        ("10", "Semantic Search", "AI-powered paper discovery")
    ]

    for step, name, description in steps:
        print(f"Step {step}: {name}")
        print(f"         {description}")

    print("\nEach step builds on the previous ones to create a complete")
    print("automated literature search and management system.")


if __name__ == "__main__":
    # Print workflow overview
    print_workflow_steps()

    # Run complete workflow
    print("\n" + "="*60)
    print("Starting Complete Workflow Demo...")
    print("="*60)

    try:
        asyncio.run(complete_workflow_example())
    except KeyboardInterrupt:
        print("\n\nWorkflow interrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        print("Note: Some steps may require:")
        print("  - Valid OpenAthens credentials")
        print("  - Internet connection")
        print("  - Optional packages (sentence-transformers, faiss-cpu)")

    print("\n\nThis example demonstrates the complete Scholar workflow.")
    print("In practice, you can:")
    print("  - Run individual steps as needed")
    print("  - Resume interrupted operations")
    print("  - Customize each step's parameters")
    print("  - Use the MCP interface for integration with Claude")
