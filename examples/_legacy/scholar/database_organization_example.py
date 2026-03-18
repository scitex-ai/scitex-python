#!/usr/bin/env python3
"""Example: Organize papers in database after download and validation."""

import asyncio
from pathlib import Path
from scitex.scholar import Scholar
from scitex.scholar.database import PaperDatabase
from scitex.scholar.validation import PDFValidator


async def database_organization_example():
    """Demonstrate database organization workflow."""

    print("=== SciTeX Scholar - Database Organization Example ===\n")

    # Initialize components
    scholar = Scholar()
    db = PaperDatabase()
    validator = PDFValidator()

    # Step 1: Load papers from BibTeX
    print("1. Loading papers from BibTeX...")
    print("-" * 50)

    bibtex_path = Path("./papers.bib")
    if bibtex_path.exists():
        papers = scholar.load_bibtex(bibtex_path)
        print(f"Loaded {len(papers)} papers")

        # Import to database
        entry_ids = db.import_from_papers(papers)
        print(f"Imported {len(entry_ids)} entries to database")
    else:
        print(f"BibTeX file not found: {bibtex_path}")
        # Create sample entries for demo
        from scitex.scholar import Paper
        papers = [
            Paper(
                title="Deep Learning for Climate Modeling",
                authors=["Jane Smith", "John Doe"],
                year=2024,
                journal="Nature Climate Change",
                doi="10.1038/s41558-024-1234"
            ),
            Paper(
                title="Quantum Computing Applications",
                authors=["Alice Brown", "Bob Wilson"],
                year=2023,
                journal="Science",
                doi="10.1126/science.abc1234"
            )
        ]
        entry_ids = db.import_from_papers(papers)

    # Step 2: Simulate download results
    print("\n2. Processing downloaded PDFs...")
    print("-" * 50)

    # In real workflow, these would come from download step
    download_results = {
        entry_ids[0]: {
            "success": True,
            "path": "./downloads/paper1.pdf"
        },
        entry_ids[1]: {
            "success": True,
            "path": "./downloads/paper2.pdf"
        }
    }

    # Step 3: Validate and organize PDFs
    print("\n3. Validating and organizing PDFs...")
    print("-" * 50)

    for entry_id, result in download_results.items():
        if result.get("success") and result.get("path"):
            pdf_path = Path(result["path"])

            # Skip if file doesn't exist (demo)
            if not pdf_path.exists():
                print(f"  Skipping {entry_id} - file not found")
                continue

            # Validate PDF
            validation = validator.validate(pdf_path)

            # Update database with validation results
            entry = db.get_entry(entry_id)
            entry.update_from_validation(validation)

            # Update download status
            updates = {
                "download_status": "downloaded" if validation.is_valid else "invalid",
                "downloaded_date": entry.downloaded_date or datetime.now()
            }
            db.update_entry(entry_id, updates)

            # Organize PDF if valid
            if validation.is_valid:
                try:
                    new_path = db.organize_pdf(
                        entry_id,
                        pdf_path,
                        organization="year_journal"
                    )
                    print(f"  ✓ Organized: {new_path}")
                except Exception as e:
                    print(f"  ✗ Failed to organize: {e}")
            else:
                print(f"  ✗ Invalid PDF: {validation.errors}")

    # Step 4: Search and filter
    print("\n4. Searching database...")
    print("-" * 50)

    # Search by year
    results = db.search(year=2024)
    print(f"\nPapers from 2024: {len(results)}")
    for entry_id, entry in results[:3]:
        print(f"  - {entry}")

    # Search by status
    downloaded = db.search(status="downloaded")
    print(f"\nSuccessfully downloaded: {len(downloaded)}")

    # Search by validation status
    valid_pdfs = [
        (id, e) for id, e in db.entries.items()
        if e.pdf_valid
    ]
    print(f"Valid PDFs: {len(valid_pdfs)}")

    # Step 5: Export organized collection
    print("\n5. Exporting collections...")
    print("-" * 50)

    # Export all 2024 papers
    if results:
        export_ids = [id for id, _ in results]
        export_path = db.export_to_bibtex(
            "./exports/papers_2024.bib",
            export_ids
        )
        print(f"Exported to: {export_path}")

    # Export database summary
    json_path = db.export_to_json("./exports/database_snapshot.json")
    print(f"JSON export: {json_path}")

    # Step 6: Database statistics
    print("\n6. Database Statistics")
    print("-" * 50)

    stats = db.get_statistics()
    print(f"Total entries: {stats['total_entries']}")
    print(f"PDF statistics:")
    print(f"  - Total PDFs: {stats['pdf_stats']['total']}")
    print(f"  - Valid: {stats['pdf_stats']['valid']}")
    print(f"  - Complete: {stats['pdf_stats']['complete']}")
    print(f"  - Searchable: {stats['pdf_stats']['searchable']}")

    print(f"\nDownload status:")
    for status, count in stats['download_stats'].items():
        print(f"  - {status}: {count}")

    # Show top journals
    if stats['journal_distribution']:
        print(f"\nTop journals:")
        sorted_journals = sorted(
            stats['journal_distribution'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        for journal, count in sorted_journals[:5]:
            print(f"  - {journal}: {count} papers")

    # Step 7: Cleanup
    print("\n7. Database Maintenance")
    print("-" * 50)

    # Find orphaned PDFs
    orphans = db.cleanup_orphaned_pdfs(dry_run=True)
    if orphans:
        print(f"Found {len(orphans)} orphaned PDFs")
        for orphan in orphans[:5]:
            print(f"  - {orphan}")
    else:
        print("No orphaned PDFs found")


def demonstrate_advanced_features():
    """Show advanced database features."""

    print("\n\n=== Advanced Database Features ===\n")

    db = PaperDatabase()

    # Tags and collections
    print("1. Using tags and collections:")
    print("-" * 50)

    # Add tags to entries
    for entry_id, entry in list(db.entries.items())[:3]:
        db.update_entry(entry_id, {
            "tags": ["machine-learning", "climate"],
            "collections": ["PhD Research", "Review Papers"]
        })

    # Search by tag
    ml_papers = db.search(tag="machine-learning")
    print(f"Papers tagged 'machine-learning': {len(ml_papers)}")

    # Search by collection
    phd_papers = db.search(collection="PhD Research")
    print(f"Papers in 'PhD Research': {len(phd_papers)}")

    # Multi-criteria search
    print("\n2. Multi-criteria search:")
    print("-" * 50)

    results = db.search(
        year=2024,
        tag="climate",
        status="downloaded"
    )
    print(f"2024 climate papers (downloaded): {len(results)}")

    # Custom organization
    print("\n3. Custom PDF organization schemes:")
    print("-" * 50)

    print("Available schemes:")
    print("  - year_journal: /2024/Nature/paper.pdf")
    print("  - year_author: /2024/Smith/paper.pdf")
    print("  - flat: /paper.pdf")

    # Database location
    print(f"\n4. Database location: {db.database_dir}")
    print("Directory structure:")
    for subdir in ["data", "pdfs", "indices", "exports"]:
        path = db.database_dir / subdir
        if path.exists():
            file_count = len(list(path.iterdir()))
            print(f"  - {subdir}/: {file_count} items")


if __name__ == "__main__":
    # Need to import datetime for the example
    from datetime import datetime

    # Run main example
    asyncio.run(database_organization_example())

    # Show advanced features
    demonstrate_advanced_features()

    print("\n\nNote: This example demonstrates the complete workflow:")
    print("1. Import papers from BibTeX")
    print("2. Track download results")
    print("3. Validate PDFs")
    print("4. Organize files by year/journal")
    print("5. Search and export collections")
    print("6. View statistics")
    print("7. Maintain database")
